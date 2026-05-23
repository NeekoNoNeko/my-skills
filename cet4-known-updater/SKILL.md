---
name: cet4-known-updater
description: Update the `known` column in CET-4 core vocabulary Excel file based on a user's known-words JSON list
model: sonnet
trigger: cet4 CET-4 四级 known vocabulary excel 单词 更新
prompts:
  - role: user
    content: >-
      You are working in `D:\workspace\test`. Read the file `known_words.json`, extract the `known` array,
      then update `四级真题核心词.xlsx`:

      1. Read the Excel file with `pandas`.
      2. For each word in the `known` array, find matching rows in the `单词` column (case-insensitive).
      3. If the row's `known` column is `FALSE`, set it to `TRUE`.
      4. Save the Excel file in place (overwrite).
      5. Report: how many words were updated, and which (if any) were not found in the vocabulary list.

      Dependencies: `pandas`, `openpyxl`. Install if missing.
---

# CET-4 Known Word Updater

Updates the `known` column in `四级真题核心词.xlsx` based on a user-submitted JSON word list.

## Input

The user provides JSON (via file or message):

```json
{
  "known": ["abandon", "ability", "abroad", ...],
  "uncertain": [],
  "lastVocabulary": "四级真题核心词"
}
```

## Execution

| Step | Description |
|------|-------------|
| 1 | Ensure `D:\workspace\test\四级真题核心词.xlsx` exists with columns: `单词`, `known`, `释义`, `常用短语` |
| 2 | Read the known words array from user input |
| 3 | Case-insensitive match against the `单词` column |
| 4 | Update `known` from `FALSE` → `TRUE` for matches |
| 5 | Overwrite the Excel file |
| 6 | Report updated count + any unmatched words |

## Notes

- Matching is case-insensitive (`.lower()`)
- Overwrites the source file directly (no backup)
- Requires `pip install pandas openpyxl`
- Unmatched words are likely not in the current vocabulary list
