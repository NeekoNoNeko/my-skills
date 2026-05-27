---
name: excel-to-anki
description: Use when you have an Excel word list with 单词/词性/释义 columns and need to generate Anki .apkg flashcards with TTS audio — not for manual card creation, CSV input, or non-Chinese-learning decks
---

# Anki 单词卡组生成器

## Overview

从 Excel 单词表批量生成带美式发音的 Anki 卡组。核心原则：**先检查依赖和 Excel 表头 → 再跑脚本 → 出错先看 common mistakes**。不要跳过依赖安装就运行，不要假设 Excel 列名可以不匹配。

## Quick Reference

| 项目 | 值 |
|------|-----|
| 脚本 | `generate_anki.py`（同目录） |
| 依赖 | `pip install edge-tts genanki openpyxl` |
| TTS | edge-tts，默认 `en-US-JennyNeural` |
| 过滤规则 | 只处理 `known` 列为 `Selected` 的行 |
| 输出 | `.apkg` 文件，可直接导入 Anki |

## When to Use

- 有结构化 Excel 单词表，列名固定（单词、词性、释义、美式音标、英式音标、短语、短语释义、例句、例句释义、known）
- 需要批量生成发音并嵌入 Anki 卡片
- 单词量大（数百到上千），需要并行 TTS 加速

## When NOT to Use

- 手动创建少量卡片 → 直接用 Anki 客户端
- Excel 列名不标准或自行定义 → 先对齐列名再使用此技能
- 数据源是 CSV、JSON 等非 Excel 格式 → 先转为 .xlsx
- 不需要 TTS 音频 → 用 genanki 直接写脚本更简单
- 目标语言不是英语 → 需自行换 VOICE，但脚本结构可能不适用

## Excel 列要求

| 列名 | 必需 | 说明 |
|------|------|------|
| 单词 | ✅ | 英文单词，同时作为 TTS 输入 |
| known | ✅ | 仅值 `Selected` 的行会被处理 |
| 词性 | - | n./v./adj. 等 |
| 释义 | - | 中文释义，卡片背面显示 |
| 美式音标 | - | 卡片正面显示 |
| 英式音标 | - | 卡片正面显示 |
| 短语 | - | 背面条件显示 |
| 短语释义 | - | 背面条件显示 |
| 例句 | - | 背面条件显示 |
| 例句释义 | - | 背面条件显示 |

## 工作流

1. 安装依赖：`pip install edge-tts genanki openpyxl`
2. 将 Excel 放入脚本同目录，确认列名匹配
3. 修改脚本顶部 `EXCEL_PATH`、`OUTPUT_PATH`、`VOICE` 等配置
4. 运行 `python generate_anki.py`
5. 用 Anki 导入生成的 `.apkg` 文件

## 自定义

- **换音色**：修改 `VOICE`，用 `edge-tts --list-voices` 查看可用音色
- **调并发**：修改 `BATCH_SIZE`（8 稳妥，16 更快但可能被限流）
- **改卡片外观**：编辑 `CARD_CSS` / `FRONT` / `BACK`

## Common Mistakes

| 错误 | 原因 | 修复 |
|------|------|------|
| Excel 列名不匹配导致无单词导入 | 列名与脚本 `FIELD_NAMES` 不一致 | 检查 Excel 表头是否包含所有预期列名 |
| known 列填了但未被过滤 | 值不是精确的 `Selected`（大小写/空格） | 确认单元格值为 `Selected`，无前后空格 |
| TTS 全部失败 | 网络不通或 edge-tts 被限流 | 先手动 `edge-tts --text "hello" --write-media test.mp3` 验证基础连通 |
| 音频不播放 | mp3 文件名与 `[sound:...]` 标签不匹配，或文件未打包 | 检查 `media_files` 列表和音频目录路径 |
| ModuleNotFoundError | 未安装依赖 | `pip install edge-tts genanki openpyxl` |
| Python 版本不兼容 | edge-tts 需 Python 3.8+ | `python --version` 确认 |

## Red Flags

- **没安装依赖就开始调试脚本** — 先 `pip install` 三件套
- **Excel 列名改了但不改脚本** — 列名是硬编码的，不对齐就空跑
- **known 列用了其他标记（Yes/1/TRUE）而不是 Selected** — 只有 `Selected` 会被筛选
- **不检查音频缓存直接删 audio 目录** — 缓存避免重复 TTS 调用，别随意清空
