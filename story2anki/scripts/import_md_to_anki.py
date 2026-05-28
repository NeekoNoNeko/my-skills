#!/usr/bin/env python3
"""将 Markdown 文件按 # 章节拆分为 Anki 卡片，生成 .apkg 文件。

用法:
  # 单个文件 → 单个 .apkg
  python import_md_to_anki.py file.md --deck 牌组名 --tags tag1,tag2

  # 目录批量 → 合并为一个 .apkg
  python import_md_to_anki.py ./词汇/ --deck 词汇故事 --tags 词汇 -o all.apkg

  # 生成后自动导入 Anki（需安装 AnkiConnect 插件）
  python import_md_to_anki.py file.md --anki

  # 自动导入 + 导入成功后删除 .apkg
  python import_md_to_anki.py file.md --anki --cleanup
"""
import hashlib
import json
import re
import sys
import tempfile
import urllib.request
import shutil
from pathlib import Path

_CLOZE_HASH = int(hashlib.md5("story2anki-Cloze".encode()).hexdigest()[:8], 16)

ANKI_CONNECT_URL = "http://127.0.0.1:8765"


def _check_genanki():
    """检查 genanki 版本兼容性 (>= 0.13 使用 dict 风格 API)。"""
    try:
        import genanki
    except ImportError:
        print("Error: 需要 genanki 库，请运行: pip install genanki")
        sys.exit(1)
    # 0.13+ 移除了 Field/Template 类，验证当前版本
    ver = tuple(int(v) for v in genanki.__version__.split(".")[:2])
    if ver < (0, 13):
        print(f"Error: genanki {genanki.__version__} 过旧，请升级: pip install --upgrade genanki")
        sys.exit(1)


def anki_connect(action, **params):
    """调用 AnkiConnect API，失败返回 None。"""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_CONNECT_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read())["result"]
    except Exception:
        return None


def extract_first_cloze_word(text):
    """提取文本中第一个 {{c1::word}} 里的单词。"""
    m = re.search(r'\{\{c1::(.+?)\}\}', text)
    return m.group(1).strip() if m else None


def sanitize_filename(name):
    """清理字符串使其适合作为文件名。"""
    name = name.lower().replace(' ', '_')
    return re.sub(r'[^a-z0-9_一-鿿]', '', name)


def generate_word_audio(words, output_dir):
    """用 edge-tts 并行生成单词的 WAV 音频文件。

    Args:
        words: 单词列表（可含重复，自动去重）
        output_dir: 输出目录

    Returns:
        dict: {原始单词: Path(音频文件)}
    """
    import asyncio
    import edge_tts

    unique_words = sorted(set(w for w in words if w))
    if not unique_words:
        return {}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    async def _generate_one(word, sem):
        async with sem:
            fname = sanitize_filename(word) + ".wav"
            wav_path = output_dir / fname
            if wav_path.exists():
                return word, wav_path
            communicate = edge_tts.Communicate(word, voice="en-US-JennyNeural")
            await communicate.save(str(wav_path))
            if wav_path.exists():
                print(f"  Audio: {word}")
                return word, wav_path
            else:
                print(f"  Warning: 无法生成音频: {word}")
                return word, None

    async def _run():
        sem = asyncio.Semaphore(10)  # 最多 10 个并发
        tasks = [_generate_one(w, sem) for w in unique_words]
        results = await asyncio.gather(*tasks)
        return {word: path for word, path in results if path}

    return asyncio.run(_run())


def parse_markdown(filepath):
    """解析 .md 文件，返回笔记列表。

    章节以 `# 标题` 分割。标题前不能有任意前缀字符（如 `|#` 将无法识别）。
    支持 YAML frontmatter tags。自动将文件名（不含扩展名）作为标签添加到每张卡片。
    全部生成 Cloze（填空卡），保留 `{{c1::...}}` 填空标记。
    """
    content = Path(filepath).read_text(encoding="utf-8")
    tags = []
    body = content

    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter = content[3:end].strip()
            body = content[end + 3:].strip()
            for line in frontmatter.splitlines():
                stripped = line.strip()
                if stripped.startswith("tags:"):
                    rest = stripped[5:].strip()
                    if rest.startswith("["):
                        tags = [t.strip().strip('"').strip("'")
                                for t in rest[1:-1].split(",") if t.strip()]
                    elif not rest:
                        continue
                    else:
                        tags = [rest.strip().strip('"').strip("'")]
            if not tags:
                in_tags = False
                for line in frontmatter.splitlines():
                    if line.strip().startswith("tags:"):
                        in_tags = True
                    elif in_tags:
                        m = re.match(r'\s*-\s*(.+)', line)
                        if m:
                            tags.append(m.group(1).strip().strip('"').strip("'"))
                        else:
                            in_tags = False

    # 检查常见的 markdown 格式问题
    if re.search(r'(?m)^\|# ', body):
        print(f"  Warning: {filepath.name} 中存在 '|#' 格式问题，'#' 前有多余的 '|'，已自动修复")
        body = body.replace("|#", "#")

    sections = re.split(r'\n(?=# )', body)
    notes = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        title_match = re.match(r'# (.+)', section)
        if not title_match:
            continue
        body_text = section[title_match.end():].strip()

        # 始终使用 Cloze 格式，保留 {{c1::...}} 填空标记
        # 自动添加文件名作为标签（如 contemplate.md → #contemplate）
        audio_word = extract_first_cloze_word(body_text)
        file_tag = Path(filepath).stem
        notes.append({"type": "cloze",
                      "text": body_text,
                      "tags": list(tags) + [file_tag],
                      "audio_word": audio_word})
    return notes


def generate_apkg(notes, deck_name, extra_tags, output_path, audio_map=None):
    """将笔记列表写入 .apkg 文件。

    Args:
        audio_map: {单词: Path(音频文件)}，用于在卡片背面嵌入 [sound:...]
    """
    import genanki

    model = genanki.Model(
        _CLOZE_HASH, "story2anki-Cloze",
        fields=[{"name": "Text"}, {"name": "Extra"}],
        templates=[{"name": "Cloze 1", "qfmt": "{{cloze:Text}}",
                     "afmt": '{{cloze:Text}}<br>{{Extra}}'}],
        css=".card { font-family: Arial; font-size: 16px; text-align: left; }",
        model_type=genanki.Model.CLOZE)

    deck_id = int(hashlib.md5(deck_name.encode()).hexdigest()[:8], 16)
    deck = genanki.Deck(deck_id, deck_name)

    media_files = []
    if audio_map:
        media_files = [str(p) for p in audio_map.values()]

    for note in notes:
        all_tags = list(set(note["tags"] + extra_tags))
        extra = ""
        if audio_map and note.get("audio_word"):
            word = note["audio_word"]
            if word in audio_map:
                fname = sanitize_filename(word) + ".wav"
                extra = f"[sound:{fname}]"
        gnote = genanki.Note(model=model,
                             fields=[note["text"], extra],
                             tags=all_tags)
        deck.add_note(gnote)
        print(f"  Added: {note['text'][:60]}")

    package = genanki.Package(deck)
    if media_files:
        package.media_files = media_files
    package.write_to_file(output_path)
    return len(notes)


def auto_import(output_path, deck_name):
    """通过 AnkiConnect 自动导入 .apkg。"""
    print("\n检查 AnkiConnect ...")
    decks = anki_connect("deckNames")
    if decks is None:
        print("  AnkiConnect 不可用，请手动导入:")
        print(f"  打开 Anki → 文件 → 导入 → 选择 {output_path}")
        return False

    # 牌组名乱码修复：deleteDecks 使用准确的 unicode
    if deck_name not in decks:
        anki_connect("createDeck", deck=deck_name)
        print(f"  创建牌组: {deck_name}")

    result = anki_connect("importPackage", path=str(output_path))
    if result:
        # 重新查询卡片数
        cards = anki_connect("findCards", query=f'deck:"{deck_name}"')
        print(f"  [OK] 成功导入 {len(cards) if cards else '?'} 张卡片到牌组 [{deck_name}]")
        return True
    else:
        print("  [FAIL] AnkiConnect 导入失败，请手动导入")
        return False


def collect_markdown_files(path):
    """收集要处理的 .md 文件。"""
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.md"))
        if not files:
            print(f"Error: 目录中没有 .md 文件: {path}")
            sys.exit(1)
        return files
    elif p.is_file():
        return [p]
    else:
        print(f"Error: 路径不存在: {path}")
        sys.exit(1)


def main():
    _check_genanki()

    if len(sys.argv) < 2:
        print("Usage: python import_md_to_anki.py <path> [options]")
        print()
        print("  <path>             .md 文件路径 或 目录路径（自动扫描所有 .md 文件合并为一个 .apkg）")
        print("  --deck <name>      Anki 牌组名称 (默认: story2anki)")
        print("  --tags <a,b>       附加标签 (默认: 无)")
        print("  -o <file>          输出 .apkg 路径 (默认: <输入>.apkg)")
        print("  --anki             生成后通过 AnkiConnect 自动导入 Anki")
        print("  --cleanup          导入成功后删除 .apkg 文件（需配合 --anki）")
        print()
        print("示例:")
        print("  python import_md_to_anki.py note.md --deck 词汇 --tags 英语")
        print("  python import_md_to_anki.py ./词汇/ --deck 词汇故事 --tags 词汇 -o all.apkg --anki")
        print("  python import_md_to_anki.py ./词汇/ --deck 词汇 --anki --cleanup")
        sys.exit(1)

    # 收集文件
    md_files = collect_markdown_files(sys.argv[1])

    # 解析参数
    deck_name = "story2anki"
    extra_tags = []
    output_path = None
    do_auto_import = False
    do_cleanup = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--deck" and i + 1 < len(sys.argv):
            deck_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--tags" and i + 1 < len(sys.argv):
            extra_tags = [t.strip() for t in sys.argv[i + 1].split(",") if t.strip()]
            i += 2
        elif sys.argv[i] == "-o" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--anki":
            do_auto_import = True
            i += 1
        elif sys.argv[i] == "--cleanup":
            do_cleanup = True
            i += 1
        else:
            i += 1

    if output_path is None:
        if len(md_files) == 1:
            output_path = md_files[0].with_suffix(".apkg")
        else:
            output_path = Path("output.apkg")

    # 解析所有文件
    all_notes = []
    for fpath in md_files:
        try:
            notes = parse_markdown(fpath)
            all_notes.extend(notes)
            print(f"  {fpath.name}: {len(notes)} 张卡片")
        except Exception as e:
            print(f"  {fpath.name}: 错误 - {e}")

    if not all_notes:
        print("Error: 没有解析到任何卡片")
        sys.exit(1)

    print(f"\n总计 {len(all_notes)} 张卡片 → {output_path}")

    # 生成单词音频
    audio_map = {}
    words = [n.get("audio_word") for n in all_notes]
    if any(words):
        audio_dir = tempfile.mkdtemp(prefix="story2anki_audio_")
        try:
            audio_map = generate_word_audio(words, audio_dir)
        except Exception as e:
            print(f"  Warning: 音频生成失败 - {e}")

    generate_apkg(all_notes, deck_name, extra_tags, output_path, audio_map)

    # 清理临时音频目录
    if audio_map:
        shutil.rmtree(audio_dir, ignore_errors=True)
    print(f"[OK] 已生成: {output_path}")

    if do_auto_import:
        success = auto_import(output_path, deck_name)
        if success and do_cleanup:
            try:
                output_path.unlink()
                print(f"  Cleanup: 已删除 {output_path}")
            except Exception as e:
                print(f"  Cleanup: 删除失败 - {e}")


if __name__ == "__main__":
    main()
