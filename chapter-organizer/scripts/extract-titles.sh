#!/usr/bin/env bash
# 提取输出目录中所有章节 Markdown 文件的标题结构，用于生成知识点大纲。
# 用法: ./extract-titles.sh <输出目录路径>
# 示例: ./extract-titles.sh "C:\path\to\output"

BASE="${1:-.}"

# 场景 A：平铺 .md 文件
if ls "$BASE"/*.md &>/dev/null 2>&1 && [ -z "$(find "$BASE" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)" ]; then
    echo "检测到场景 A（平铺 .md 文件）"
    for f in "$BASE"/*.md; do
        [ "$(basename "$f")" = "outline.md" ] && continue
        echo "=== $(basename "$f") ==="
        grep -nE '^(# |## |### )' "$f" | grep -vi 'FIGURE\|Solution:\|Proof\.\|Simulating\|Exercises' | head -40
        echo ""
    done
    exit 0
fi

# 场景 B：MinerU 嵌套目录
echo "检测到场景 B（嵌套目录）"
for dir in "$BASE"/*/; do
    md="$dir$(basename "$dir").md"
    [ -f "$md" ] || continue
    echo "=== $(basename "$dir") ==="
    grep -nE '^(# |## |### )' "$md" | grep -vi 'FIGURE\|Solution:\|Proof\.\|Simulating\|Exercises' | head -50
    echo ""
done
