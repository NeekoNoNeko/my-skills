---
name: chapter-organizer
description: >
  整理教材章节 Markdown 文件，支持平铺 .md 文件和 MinerU 嵌套目录
  （每个目录含 full.md + images/）两种场景。按章节重命名文件、提取所有章节标题
  生成知识点大纲，并选择性复制被引用的图片到输出目录。适用于用户说"整理一下这本书的md"、
  "按章节重命名这些文件"、"生成知识点大纲"、"提取章节标题"、"处理mineru输出"、
  "把full.md按章节整理"、"整理教材图片"、"批量重命名md文件"、"整理电子书的md"等场景。
  注意：遇到带 images/ 文件夹的 MinerU 输出时更要主动使用此技能，因为图片保留是它区别于普通重命名的关键能力。
on:
  - rename textbook files
  - chapter outline
  - 重命名章节文件
  - 生成知识点大纲
  - 整理教材md文件
  - 整理md
  - mineru 整理
  - 图片保留
  - 课本整理
  - 批量重命名 md
  - full.md 整理
  - 电子书整理
---

# Chapter Organizer - 教材章节文件整理与大纲生成 Skill

## 功能概述

批量处理一套教材的 Markdown 章节文件，完成以下操作：

1. **重命名** —— 按【Chapter-X-Description】格式为每个文件赋予有意义的英文名
2. **选择性复制图片** —— 解析 `.md` 中的 `![](images/xxx.jpg)` 引用，只复制被引用的图片，避免搬运 MinerU 输出的无关图片
3. **生成大纲** —— 提取所有文件的章节标题，汇总为完整的知识点大纲

## 适用场景

- **场景 A（平铺）**：若干 `.md` 文件直接放在同一目录（如 `1.md`、`2.md`、`Preface.md`），每个文件对应教材的一章
- **场景 B（MinerU 嵌套）**：教材经 MinerU 处理后，每个章节是一个子目录，内含 `full.md` + `images/` + JSON 辅助文件
- 你想让文件名反映章节号和主要内容，且图片引用不受影响

## ⚠️ 核心原则

1. **绝不修改源文件和原文件夹名** —— 用 `cp` 而非 `mv`，所有变更在新输出目录中进行。原因：源目录是 MinerU 原始输出，一旦改名或修改就无法追溯到原始 PDF。
2. **图片必须与 .md 文件保持在同一目录层级** —— `![](images/xxx.jpg)` 是相对路径，Markdown 渲染器从 .md 文件位置解析 `images/`。层级错乱则图片断裂。
3. **仅复制 .md 中实际引用的图片** —— 解析 `![](images/xxx.jpg)` 提取文件名，只复制被引用的图片到输出目录。MinerU 输出的 `images/` 往往包含大量 OCR 切图碎片，全部搬运会污染输出目录且浪费空间。

---

## 通用流程概览

```
源目录/                    输出目录/
├── raw_dir_1/      ──→    ├── Chapter-1-xxx/
│   ├── full.md            │   ├── Chapter-1-xxx.md
│   └── images/ (全部)     │   └── images/ (仅被引用的图片)
├── raw_dir_2/      ──→    ├── Chapter-2-yyy/
│   ├── full.md            │   ├── Chapter-2-yyy.md
│   └── images/ (全部)     │   └── images/ (仅被引用的图片)
└── ...                    ├── ...
                           └── Book-Name-outline.md
```

输出目录建在 **源目录内部**（如 `源目录/Book-Name/`），使项目自包含。输出目录名只用教材名概述内容，不带"整理"字样（如 `Introduction-to-Probability` 而非 `Introduction-to-Probability-章节整理`）。

---

## 场景 A：平铺 .md 文件

### 1. 了解文件内容

```bash
for f in *.md; do
  echo "=== $f ==="
  grep -E '^# [^#]' "$f" | grep -vi 'figure\|example\|solution\|table' | head -3
done
```

### 2. 创建输出目录并复制重命名

```bash
mkdir -p "../Book-Name"
cp "1.md" "../Book-Name/Chapter-1-Main-Content.md"
cp "Preface.md" "../Book-Name/Preface.md"
```

命名格式：
- **带编号**：`Chapter-X-Main-Content.md`
- **无编号**：`Preface.md`、`Appendix.md`、`Index.md`

### 3. 提取标题 → 跳到"生成知识点大纲"

---

## 场景 B：MinerU 嵌套目录（含 full.md + images/）

```
源目录/
├── PDF-HASH1/
│   ├── full.md       ← 章内容
│   ├── images/       ← 该章所有图片
│   ├── *_model.json  ← MinerU 辅助文件（忽略）
│   └── *_origin.pdf  ← 原始 PDF（忽略）
├── PDF-HASH2/ ...
```

### 1. 了解每个目录对应的章节

```bash
for dir in */; do
  md="$dir/full.md"
  [ -f "$md" ] && echo "=== $dir ===" && grep -m1 '^# ' "$md"
done
# 再用二级标题确认章节编号：
for dir in */; do
  md="$dir/full.md"
  [ -f "$md" ] && echo "=== $dir ===" && grep -E '^## [[:digit:]]' "$md" | head -3
done
```

### 2. 建立章节映射

| 源目录 | 目标章节名 |
|--------|-----------|
| `PDF-HASH-A/` | `Chapter-1-Probability-and-counting` |
| `PDF-HASH-B/` | `Chapter-2-Conditional-probability` |

### 3. 执行复制

**推荐优先使用脚本** `scripts/organize-mineru.ps1`，它会自动处理创建目录、复制重命名、引用图片筛选全流程：

```powershell
# 先定义章节映射，再调用脚本
$chapters = @{
    "源目录名1" = "Chapter-1-Name"
    "源目录名2" = "Chapter-2-Name"
}
.\scripts\organize-mineru.ps1 -SourceDir "源目录路径" -OutputDir "源目录路径/Book-Name" -ChapterMapping $chapters
```

> ⚠️ **PowerShell 字符串插坑点**：脚本中如果写 `"$chapterName: 文本"`，PowerShell 会把 `$chapterName:` 解析成驱动器限定引用（类似 `$env:Path`），导致报错 `InvalidVariableReferenceWithDrive`。**解决办法**：用 `$()` 子表达式包裹变量，写成 `"$($chapterName): 文本"`。当前脚本已采用此写法。

或手工执行：

```bash
base="源目录路径"
out="$base/Book-Name"
mkdir -p "$out"
declare -A chapters=(["源目录名1"]="Chapter-1-Name")
for src in "${!chapters[@]}"; do
  name="${chapters[$src]}"
  mkdir -p "$out/$name"
  # 复制 .md 并重命名
  cp "$base/$src/full.md" "$out/$name/$name.md"
  # 只复制 .md 中实际引用的图片
  mkdir -p "$out/$name/images"
  grep -oP '\]\(images/\K[^)]+' "$base/$src/full.md" | sort -u | while read -r img; do
    src_img="$base/$src/images/$img"
    [ -f "$src_img" ] && cp "$src_img" "$out/$name/images/"
  done
done
```

为什么要用 `cp` 而非 `mv`：`cp` 保留源目录不变，处理出错时可以重来。`mv` 会使源目录结构丢失。

为什么 `images/` 必须和 `.md` 同层：`full.md` 中的引用是 `![](images/hash.jpg)`。Markdown 渲染器从 `.md` 位置拼接此路径，所以 `images/` 必须是 `.md` 的**直接子目录**。

为什么只复制被引用的图片：MinerU 输出的 `images/` 目录通常包含大量 OCR 过程中产生的碎片图片（公式切图、页码、装饰元素等），大部分并未在 `.md` 中被引用。全部搬运会浪费磁盘空间并让输出目录杂乱。通过 `grep` 提取 `![](images/...)` 中的文件名，只复制有引用的图片即可。

### 4. 提取标题 → 跳到"生成知识点大纲"

---

## 生成知识点大纲（通用）

场景 A 和场景 B 汇合到此步骤。

**推荐使用脚本** `scripts/extract-titles.sh <输出目录>`，它能自动检测平铺/嵌套结构并提取标题。

或手工执行：

```bash
cd <输出目录>
for f in *.md; do
  echo "=== $f ==="
  grep -nE '^(# |## |### )' "$f" | grep -vi 'FIGURE\|Solution:\|Proof\.\|Simulating\|Exercises' | head -50
done
```

按以下格式组织大纲：

```markdown
# Book Name — Knowledge Outline

## Chapter 1: Main Content

### 1.1 Section Name
- 知识点条目
- 保留英文术语对照，便于查阅原书
```

包含：前言、各章、附录。不包含：练习、习题解答、R 代码输出等附属内容。大纲文件只保留在输出目录中，源目录不留副本。

---

## 验证

**推荐使用脚本** `scripts/verify.sh <输出目录>`，一键检查所有章节的 `.md`、`images/`、图片引用完整性。

或手工验证：

```bash
# 检查每个章节目录的 .md 和 images/
for dir in */; do
  md_files=("$dir"*.md)
  [ -f "${md_files[0]}" ] || { echo "❌ $dir: 缺少 .md"; continue; }
  # 检查被引用的图片是否都存在
  grep -oP '\]\(images/\K[^)]+' "${md_files[0]}" | while read -r img; do
    [ -f "$dir/images/$img" ] || echo "❌ $dir: 缺少图片 $img"
  done
  # 检查有无未被引用的多余图片
  img_count=$(ls "$dir/images/" 2>/dev/null | wc -l)
  ref_count=$(grep -oP '\]\(images/\K[^)]+' "${md_files[0]}" | sort -u | wc -l)
  echo "$dir: 图片=$img_count, 引用=$ref_count"
done
```

确认结果：
- 每个目录至少 1 个 `.md` 文件
- 每个目录有 `images/` 目录
- `.md` 中引用的每张图片在 `images/` 中都存在
- `images/` 中的图片数量 = 被引用的不重复图片数量（即没有多余图片）
- 源目录未被修改（目录名和文件名与原样一致）

---

## 命名惯例

| 原始 | 建议命名 |
|------|----------|
| `Preface.md` | `Preface.md` |
| Chapter 1 / `1.md` | `Chapter-1-Main-Content.md` |
| Appendix A / `A.md` | `Appendix-A-Title.md` |
| `Index.md` | `Index.md` |
