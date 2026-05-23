"""
四级真题核心词 - 更新 known 列工具
从外部 JSON 文件中读取已知单词列表，将 Excel 中对应单词的 known 列从 FALSE 改为 TRUE
"""

import json
import pandas as pd
from pathlib import Path

# ====== 配置 ======
EXCEL_PATH = Path(__file__).parent / "四级真题核心词.xlsx"
JSON_PATH = Path(__file__).parent / "known_words.json"
# =================


def main():
    print(f"正在读取文件: {EXCEL_PATH}")

    # 从外部 JSON 文件读取已知单词列表
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    known_words = data.get("known", [])
    print(f"从 {JSON_PATH} 加载了 {len(known_words)} 个已知单词")

    df = pd.read_excel(EXCEL_PATH)

    if "known" not in df.columns:
        print("错误: Excel 文件中没有找到 'known' 列")
        return

    print(f"原始数据: {len(df)} 行, known 列类型: {df['known'].dtype}")
    print(f"当前 known=True 的数量: {df['known'].sum()}")

    # 将 known_words 转为小写集合用于比对（忽略大小写）
    known_lower = {w.lower() for w in known_words}

    # 大小写不敏感匹配
    match_count = 0
    not_found = []

    for idx, row in df.iterrows():
        word = str(row["单词"]).strip()
        if word.lower() in known_lower:
            if not df.at[idx, "known"]:  # 如果当前是 False
                df.at[idx, "known"] = True
                match_count += 1

    # 找出未匹配的单词
    excel_words_lower = {str(w).strip().lower() for w in df["单词"]}
    for w in known_words:
        if w.lower() not in excel_words_lower:
            not_found.append(w)

    print(f"\n成功更新: {match_count} 个单词的 known 列已改为 TRUE")
    print(f"未在 Excel 中找到的单词 ({len(not_found)} 个):")
    for w in not_found:
        print(f"  - {w}")

    # 直接覆盖源文件
    df.to_excel(EXCEL_PATH, index=False)
    print(f"\n结果已保存(覆盖原文件): {EXCEL_PATH}")
    print(f"更新后 known=True 的数量: {df['known'].sum()}")


if __name__ == "__main__":
    main()
