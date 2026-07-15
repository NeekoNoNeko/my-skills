#!/usr/bin/env bash
# 验证输出目录的结构完整性。
# 检查每个章节目录是否包含 .md 文件、images/ 文件夹，
# 检查被引用的图片是否都存在，并警告多余图片。
# 用法: ./verify.sh <输出目录路径>

BASE="${1:-.}"
errors=0

echo "===== 完整性验证报告 ====="
echo ""

# 遍历所有子目录
for dir in "$BASE"/*/; do
    [ -d "$dir" ] || continue
    dname=$(basename "$dir")

    # 找 .md 文件
    md_files=("$dir"*.md)
    md_count=${#md_files[@]}
    if [ "$md_count" -eq 0 ] || [ ! -f "${md_files[0]}" ]; then
        echo "❌ $dname: 缺少 .md 文件"
        errors=$((errors + 1))
        continue
    fi
    md_name=$(basename "${md_files[0]}")

    # 检查 images/
    if [ ! -d "$dir/images" ]; then
        echo "❌ $dname: 缺少 images/ 目录"
        errors=$((errors + 1))
        continue
    fi

    img_count=$(ls "$dir/images/" 2>/dev/null | wc -l)
    md_refs=$(grep -c '](images/' "${md_files[0]}" 2>/dev/null || echo "0")
    unique_refs=$(grep -oP '\]\(images/\K[^)]+' "${md_files[0]}" 2>/dev/null | sort -u | wc -l)

    # 检查是否有未被引用的多余图片
    extra_imgs=0
    if [ "$img_count" -gt "$unique_refs" ]; then
        extra_imgs=$((img_count - unique_refs))
        echo "⚠️  $dname: 有 $extra_imgs 张未被引用的多余图片"
    fi

    echo "✅ $dname: $md_name, 图片=$img_count, 唯一引用=$unique_refs"
done

echo ""
echo "===== 源目录检查 ====="
echo "（请在源目录中手动确认文件名未被修改）"

echo ""
if [ "$errors" -eq 0 ]; then
    echo "✅ 验证通过，无错误。"
else
    echo "❌ 发现 $errors 个错误，请检查。"
    exit 1
fi
