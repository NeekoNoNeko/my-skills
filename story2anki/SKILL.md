---
name: story2anki
description: >-
  当用户要求将 Markdown 文件导出到 Anki、生成闪卡、从结构化文本创建 Anki 卡片、
  或制作 .apkg 牌组包时**必须**触发。comprehensible-storyteller 生成故事后
  **总是需要**调用此技能导出到 Anki 进行间隔重复复习。是 CLI 生成的学习内容与
  Anki 之间的专用桥梁，不涉及其他工具时也应触发。
---

# Markdown 转 Anki 导入器

将 Markdown 文件按 `#` 标题拆分为 Anki 卡片，生成 `.apkg` 文件。支持单文件、目录批量合并、AnkiConnect 自动导入。

## When to Use

- 用户要求"导出到 Anki"、"生成闪卡"、"制作 .apkg"、"导入 Anki"
- comprehensible-storyteller 生成故事后需要导出为间隔重复卡片
- 拥有含 `{{c1::...}}` 填空标记的 Markdown 文件需要转为 Anki 牌组
- 需要将单文件或整个目录的 Markdown 批量合并为一个 .apkg

## 工作流程

### 1. 解析输入

从用户消息中提取以下参数：

| 参数 | 说明 | 默认值 |
|---|---|---|
| **输入路径** | `.md` 文件路径，或包含 `.md` 的目录路径 | 必填 |
| **牌组名称** | Anki 中显示的牌组名 | `story2anki` |
| **标签** | 附加标签（可选） | 无 |
| **输出路径** | 生成的 `.apkg` 保存位置 | 单文件：同名；目录：需指定 |
| **自动导入** | 是否通过 AnkiConnect 自动导入 Anki | 否 |
| **自动清理** | 导入成功后是否删除 `.apkg` 文件 | 否 |

### 2. 解析 Markdown 文件

对每个 `.md` 文件执行以下步骤：

1. 读取文件内容（UTF-8 编码）
2. 提取 YAML frontmatter 中的 `tags:`
3. 按 `# 标题` 分割为独立章节（`#` 必须在行首）
4. 保留 `{{c1::...}}` 填空标记用于 Cloze 卡片
5. 自动以文件名（不含扩展名）作为标签（如 `contemplate.md` → `#contemplate`）
6. 全部生成 Cloze（填空卡）格式

### 3. 生成 .apkg

1. 使用 genanki 库创建 Anki 牌组包
2. Cloze 卡片：正文存入 **Text** 字段，`{{c1::目标词}}` 自动渲染为空白
3. 标签 = YAML tags + 文件名标签 + 命令行 `--tags`

### 4. 导入 Anki（可选）

支持两种导入方式：

- **自动导入**（推荐）：需安装 AnkiConnect 插件（代码 2055492159），运行脚本时加 `--anki` 参数
  - 脚本自动创建牌组并导入卡片
  - 加 `--cleanup` 可在导入成功后自动删除 `.apkg` 文件
- **手动导入**：打开 Anki → **文件 → 导入**（或 **File → Import**），选择生成的 `.apkg` 文件即可

## 卡片格式

### Cloze（填空卡）

使用 Anki 填空卡模型，遵循"从上下文推断词义"的可理解输入原则：

- **Text 字段**: 包含 `{{c1::目标词}}` 标记的故事全文
  - **正面**: 自动将目标词显示为空白 `___`，需从上下文推断
  - **背面**: 显示完整故事，目标词高亮突出
- **Extra 字段**: 自动添加第一个 `{{c1::word}}` 的美式发音音频（`[sound:word.wav]`），点击即可发音
- **设计理念**: Anki 不是"词义记忆器"，而是"提醒你按时读下一篇故事"的定时器

### Tags（标签）

- 自动添加**文件名**作为标签（如 `contemplate.md` → `#contemplate`）
- 同一文件的所有卡片共享同一标签，方便在 Anki 中集中复习或按词导出
- 额外来源：YAML frontmatter 中的 tags + `--tags` 命令行参数

## 配合 comprehensible-storyteller

由 comprehensible-storyteller 生成的生词故事文件（含 `{{c1::目标词}}` 标记）可直接生成 .apkg 导入 Anki，形成可理解输入填空卡。

## Markdown 格式要求

- 每个故事以 `# 标题` 开头（**必须**位于行首，前面不能有任何字符）
- ❌ `|# 标题` → 不会被识别为章节
- ❌ ` # 标题` → 前导空格同样无法识别
- ❌ `#标题` → 缺少空格
- 支持 YAML frontmatter 中的 `tags:`

## 环境要求

- **Python** 3.8+
- **genanki** >= 0.13: `pip install genanki`
  - 0.13+ 使用 dict 风格 API（`{"name": "FieldName"}`），旧版 `Field()`/`Template()` 已移除
  - 如需检查版本: `pip show genanki`
- **pyttsx3**（可选，用于单词发音）: `pip install pyttsx3`
  - 未安装时自动跳过音频生成，不影响卡片生成
  - 仅在 Windows 上生效（使用 SAPI5）
- **AnkiConnect**（可选，自动导入需要）: Anki 插件代码 2055492159

## 边界情况处理

| 情况 | 处理方式 |
|---|---|
| 文件编码非 UTF-8 | 报错并跳过该文件 |
| 文件无有效章节 | 警告并跳过 |
| 目录模式下无 `.md` 文件 | 报错退出 |
| 输出路径已存在同名 `.apkg` | 直接覆盖 |
| Markdown 中含 `{{c1::...}}` 填空标记 | 保留，正常渲染为 Cloze 填空卡 |
| 无填空标记的章节 | 仍生成 Cloze 卡，文本原样展示，无音频 |
| 文件名含特殊字符 | 按原样作为标签 |
| AnkiConnect 未运行 | 提示手动导入，不中断流程 |
| AnkiConnect 导入时牌组不存在 | 自动创建牌组 |
| genanki 版本过旧（< 0.13） | 报错提示升级 |
| 多个文件合并时标签冲突 | 取并集去重 |
| 导入失败（`--cleanup` 已启用） | 保留 `.apkg` 不删除，提示用户手动处理 |
| pyttsx3 未安装 | 跳过音频生成，不影响卡片正常生成 |
| 音频生成失败（单个单词） | 输出警告，跳过该单词音频 |
| 卡片有多个 `{{c1::}}` 标记 | 只取第一个词生成美式发音音频 |

## 快速参考

```bash
# 脚本位于 skills/story2anki/scripts/ 下
cd <skill-dir>  # 替换为 skill 实际路径

# 单文件 → 填空卡（自动添加 #contemplate 标签）
python scripts/import_md_to_anki.py output/contemplate.md --deck 词汇故事 --tags 词汇

# 目录批量 → 合并为一个牌组（各文件自带文件名标签）+ 自动导入 Anki
python scripts/import_md_to_anki.py ./词汇/ --deck 词汇故事 --tags 词汇 -o all_vocab.apkg --anki

# 目录批量 + 自动导入 + 导入后清理 .apkg
python scripts/import_md_to_anki.py ./词汇/ --deck 词汇故事 --tags 词汇 -o all_vocab.apkg --anki --cleanup
```

## Troubleshooting

| 问题 | 解决方法 |
|---|---|
| `No module named genanki` | 运行 `pip install genanki` |
| `module 'genanki' has no attribute 'Field'` | genanki >= 0.13 已移除 `Field()`/`Template()`，升级即可 |
| 导入 Anki 后卡片空白 | 确认 Markdown 文件编码为 UTF-8 |
| 章节数少于预期 | 检查 `#` 前是否有 `|` 或其他前缀字符 |
| 同一个词的所有卡片没有同一标签 | 确认文件名正确（如 `contemplate.md` → 自动添加 `#contemplate`），已导入的卡片需删除后重新导入 |
| 想重新导入 | 设置 → 管理笔记模板 → 牌组 → 删除，再重新导入 |
| Windows 下输出乱码 | `chcp 65001` 切换终端编码 |
| 卡片背面没有发音按钮 | 运行 `pip install pyttsx3` 安装 TTS 引擎 |
| 发音是英式而非美式 | 检查系统 TTS 语音列表中是否包含 `en_US` 选项 |

