---
name: story2anki
description: >-
  Imports markdown files into Anki flashcards via AnkiConnect. Supports Cloze
  (填空卡) for comprehensible input vocabulary learning and Basic (基础卡) for
  general content. Automatically detects {{c1::...}} markers and chooses the
  correct note type. MUST trigger when: the user asks to import a markdown file
  into Anki, export vocabulary stories to Anki, sync generated content to Anki,
  says "导入" to "anki", mentions needing flashcards from a file, or wants to
  create Anki cards from structured text. Also triggers when
  comprehensible-storyteller has generated stories and the user needs spaced
  repetition review. This is the dedicated bridge between CLI-generated
  learning content and Anki.
---

# Markdown to Anki Importer

Splits a markdown file by `# ` headings and imports each section as an Anki flashcard via AnkiConnect.

## Usage

Run the Python script:

```bash
python .claude/skills/story2anki/scripts/import_md_to_anki.py <markdown_file> [--deck <deck_name>] [--tags <tag1,tag2>]
```

### Parameters
- `<markdown_file>`: Path to the markdown file to import (required)
- `--deck <deck_name>`: Anki deck name (default: `story2anki`)
- `--tags <tag1,tag2>`: Additional tags to apply to all cards (optional)

### Card format

脚本自动检测故事正文中是否包含 `{{c1::...}}` 填空标记，使用不同的 Anki 笔记模型：

#### 有填空标记 → Cloze（填空卡）

使用 Anki 填空卡模型，遵循"从上下文推断词义"的可理解输入原则：

- **Text 字段**: 包含 `{{c1::目标词}}` 标记的故事全文
  - **正面**: 自动将目标词显示为空白 `___`，需从上下文推断
  - **背面**: 显示完整故事，目标词高亮突出
- **设计理念**: Anki 不是"词义记忆器"，而是"提醒你按时读下一篇故事"的定时器

#### 无填空标记 → Basic（基础卡）

向后兼容模式，适用于一般内容：

- **正面**: `{文件名}-{章节标题}`（如 `refuel-At the Gas Station`）
- **背面**: 章节全文

#### Tags（通用）
- 来自 YAML frontmatter 中的 tags + `--tags` 额外标签

#### 配合 comprehensible-storyteller

由 comprehensible-storyteller 生成的生词故事文件（含 `{{c1::目标词}}` 标记）可直接导入 Anki，形成可理解输入填空卡。

### Prerequisites
1. **Anki** must be running with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) plugin installed
2. **Python** 3.8+ required

### Troubleshooting

| 问题 | 检查事项 |
|---|---|
| `Cannot connect to AnkiConnect` | Anki 未运行或 AnkiConnect 插件未安装。打开 Anki → 工具 → 插件 → 确保 AnkiConnect 已启用 |
| `Skipped (duplicate)` | 该卡片已存在于 Anki 中。脚本默认跳过重复，不会覆盖。如需重新导入，先在 Anki 中删除旧卡片 |
| 卡片显示异常 | 确认故事正文是纯文本，没有额外的 YAML frontmatter 干扰解析 |

## Example

导入 comprehensible-storyteller 生成的生词故事（含 `{{c1::...}}` 填空标记）：

```bash
python .claude/skills/story2anki/scripts/import_md_to_anki.py output/contemplate.md --deck 词汇故事 --tags 词汇,contemplate
```
