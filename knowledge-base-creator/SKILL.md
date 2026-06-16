---
name: knowledge-base-creator
description: >
  知识库创建指南 — 指导 agent 仿照 `mathematical-knowledge-base` 的格式，
  为不同科目创建新的知识库技能（SKILL.md + 按章节组织的参考文档）。
  
  当用户说"帮我为XX教材创建一个知识库"、"仿照数学知识库给XX建一个"、
  "build a knowledge base for this textbook"、"create a new subject skill" 时，
  使用本 Skill 来指导创建流程。
  
  前置要求：教材文档已经用 `chapter-organizer` 技能处理完毕，
  每个章节的 .md 文件和图片已经按 MinerU 格式整理好。
  本 Skill 不处理原始 MinerU 输出（那由 `chapter-organizer` 负责），
  它从已整理好的章节文档出发，生成完整的知识库技能。
compatibility:
  require_tools:
    - Read
    - Glob
    - Write
    - Bash
on:
  # 创建知识库相关
  - 创建知识库
  - 新建知识库
  - 知识库技能
  - 创建参考书知识库
  - 教材知识库
  - 建一个XX的知识库
  - 仿照数学知识库创建
  - 给XX教材建知识库
  - 生成知识库技能
  # 创建新 skill 相关
  - create knowledge base
  - new knowledge base skill
  - build a knowledge base
  - create skill from textbook
  - knowledge base template
  - setup subject skill
  - create reference skill
  - textbook reference system
  # 建设/搭建相关
  - 搭建知识库
  - 建立新技能
  - 科目知识库
  - 学科知识库
  - 书本知识库
---
# Knowledge Base Creator — 知识库创建指南

## 用途

本 Skill 指导 agent **创建新的科目知识库技能**，仿照 `mathematical-knowledge-base` 的格式。

它帮助你将已经处理好的教材章节文档，组织成完整的知识库技能，使 agent 能像查数学知识库一样，
查定义、定理、公式、证明和例题。

**输出物：** 一个新的 skill 目录，包含：
- `SKILL.md` — 技能定义文件（frontmatter + 行为指南 + 文档结构表）
- `references/<subject>/<textbook>/` — 按章节组织的教材文档
- `<Textbook-Name>-outline.md` — 全书知识点大纲

> **本 Skill 不处理原始 MinerU 输出。** 如果你有 raw MinerU 文档（带 full.md 和 images/），
> 请先使用 `chapter-organizer` 技能按章节整理，再回到这里。
> 见下方「与 chapter-organizer 的关系」一节。

---

## 前置条件 (Prerequisites)

在开始之前，请确认以下条件全部满足：

| # | 条件 | 检查方法 |
|---|------|----------|
| 1 | `chapter-organizer` 技能已经运行过，教材章节已按 MinerU 格式整理 | 每个章节有独立目录，内有同名的 `.md` 文件和 `images/` 文件夹 |
| 2 | 所有章节图片引用完好 | `.md` 文件中的 `![](images/hash.jpg)` 对应的文件存在于 `images/` 目录 |
| 3 | 你知道以下信息 | 科目名称（如 physics/chemistry/biology）、教材全名及版本、章节目录结构 |

如果以上条件不满足，**先停下来**，告诉用户需要先运行 `chapter-organizer` 技能处理教材。

---

## 工作流程 (Workflow)

按以下 7 个步骤创建知识库。如果中间发现某步可以直接推进（如用户已给定了 skill 名称），不必机械执行全部步骤。

### Step 1: 确定科目与教材

与用户确认以下信息（如果用户已经说清楚则直接使用）：

| 信息 | 示例 |
|------|------|
| 科目（subject，单英语小写词） | `physics` |
| 教材全名及版本 | `University Physics 15th edition` |
| skill 目录名（kebab-case） | `physics-knowledge-base` |
| 有哪些章节 | 列表确认全部章节编号和名称 |

> **命名规则：** `skill 目录名` = `<subject>-knowledge-base`。如 `physics-knowledge-base`。
> 如果用户有特别命名要求，按用户要求来。

### Step 2: 创建目录结构

```bash
mkdir -p d:\workspace\my-skills\<skill-name>\
mkdir -p d:\workspace\my-skills\<skill-name>\references\<subject>\<textbook-slug>\
```

**目录命名示例：**
```
d:\workspace\my-skills\
  physics-knowledge-base\
    SKILL.md                    ← 稍后创建
    references\
      physics\
        University-Physics-15e\  ← 章节放这里
```

### Step 3: 整理章节文档

将已有章节目录复制到 `references/<subject>/<textbook-slug>/` 下。

如果章节目录来自 `chapter-organizer` 的输出，它们已经符合命名规范：
```
Chapter-1-Units-and-Physical-Quantities/
  Chapter-1-Units-and-Physical-Quantities.md
  images/     ← MinerU 图片（哈希命名 .jpg）
```

复制完成后，检查每个章节目录是否包含：
- [ ] 一个 `.md` 文件（文件名与目录名相同）
- [ ] 一个 `images/` 文件夹（可能有图片，也可能为空）
- [ ] 没有其他多余文件

### Step 4: 创建大纲文件

在教材根目录下创建 `<Textbook-Name>-outline.md`。

**创建方法：**
1. 读取每个章节的 `.md` 文件
2. 提取所有 `#` / `##` / `###` 标题，保留英文原文
3. 按章节顺序组织成大纲格式

**大纲格式模板：**
```markdown
# 科目中文名 — English Textbook Title 知识点大纲

教材：Author, *Title*, Edition
整理日期：YYYY-MM-DD

---

## Chapter 1: Title (英文标题)

### 1.1 Section Name（英文节名）
- 知识点 1（Key Term in English）
- 知识点 2（Another Term）
- 重要公式：$$ equation $$

### 1.2 Next Section
...

---

## Chapter 2: Title
...
```

> **注意：** 大纲只需包含标题和知识点概览，不需要完整推导和例题。
> 详细内容留给各章节的 `.md` 文件。
> 如果要写公式，用 `$$...$$` 行间公式格式。

**参考范例：** 可以读取 `mathematical-knowledge-base/references/calculus/Calculus-Early-Transcendentals-9e/Calculus-Early-Transcendentals-9e-outline.md`
查看具体的大纲格式示例。

### Step 5: 编写 SKILL.md Frontmatter

在 `<skill-name>/SKILL.md` 中写入 YAML 前置元数据。

**frontmatter 模版：**
```yaml
---
name: <skill-name>              # 必须与目录名一致
description: >
  <科目中文名>知识库 — <介绍文字>
  
  涵盖 <教材名>，共 N 章...
  
  当用户提到 <科目相关概念>、或问"查一下XX"、"讲一下XX定理"、"XX公式是什么"时，
  **优先使用本 Skill** 查阅教材原文...
compatibility:
  require_tools:
    - Read
    - Glob
on:
  # 主题相关关键词
  - <科目中文名>
  - <科目英文名>
  - <教材关键词>
  # 具体概念
  - <概念1>
  - <概念2>
  ...
---
```

**命名规则：**
- `name` 必须是 kebab-case，与目录名完全一致
- `description` 使用 `>-` YAML 块标量（多行文本）
- `compatibility.require_tools` 始终为 `[Read, Glob]`（消费型技能只读不写）
- `on` 列表至少包括：
  - 科目中文名、英文名
  - 教材关键词（作者名、书名缩写）
  - 主要分支/专题
  - 搜索常见句式（"查XX"、"XX是什么"、"XX公式"、"XX定理"）
  - 按主题分组，用 YAML 注释 `# 主题名称` 分隔

> ⚠️ 注意：工具名是 `Glob`（不是 `Glob`），确保拼写正确。

### Step 6: 编写 SKILL.md 正文

正文包含以下 6 个主要部分，用 `---` 分隔：

#### 6.1 用途
介绍知识库覆盖的教材、适用场景。写法和 `mathematical-knowledge-base` 的「用途」部分一致：
- 列教材全名、作者、版本
- 说明适用场景（查概念、查公式、系统复习等）
- 强调优先使用本 Skill 查阅原文

#### 6.2 Agent 行为指南
编写 6 步工作流程（参考 `mathematical-knowledge-base` 的「Agent 行为指南」）：

```
1. 识别领域：判断问题属于哪个分支/专题
2. 查大纲定位：先读大纲文件找到对应章节
3. 读取章节文件：定位到具体章节读 .md 文件
4. 交叉引用：如果依赖前置知识，主动回溯
5. 组织回答：中文回答 + 英文术语 + LaTeX 公式
6. 找不到时：诚实告知，不编造
```

根据科目特点调整步骤（如物理可能需要更多公式推导、化学需要结构式等）。

#### 6.3 文档结构
核心部分。用 3 列表格列出所有章节：

| 目录 | 内容 | 前置依赖 |
|------|------|----------|
| `ch01-XXX/` | 1.1–1.X 内容概述 | 无 / 前置章节 |

**编写要点：**
- 每一行对应一个章节目录
- 「内容」列：节号范围 + 核心知识点
- 「前置依赖」列：依赖的章节号，没有就写"无"
- 如果有多本教材，用二级标题 `### 教材1`、`### 教材2` 分组
- 如有前言/附录，单独列表放在正文之前/之后

#### 6.4 使用方法
说明 agent 如何导航文档（先读大纲 → 定位章节 → 读 .md → 看图片）。

#### 6.5 回答模板
提供概念解释的标准格式（参考 `mathematical-knowledge-base` 的「回答模板」）：

```
## [概念名称]（英文术语）

### 定义
[用中文给出定义，首次出现的英文术语保留原文]

### 公式
$$ [LaTeX 公式] $$

### 直观理解 / 直觉（Intuition）
[用一句话解释本质]

### 典型应用 / 例题
[教材中的典型例题或实际应用场景]

### 相关概念
[关联到其他章节的知识点]
```

#### 6.6 注意事项
- 回答默认用中文，关键术语保留英文原文
- 公式使用 LaTeX 格式（`$...$` 行内，`$$...$$` 行间）
- 图片保存在各章节 `images/` 子目录，用相对路径引用
- 如果概念涉及前置知识，主动回溯相关章节
- 知识库未覆盖的问题，如实告知，不编造

### Step 7: 验证新技能

创建完成后，执行以下验证：

```bash
# 1. 结构完整性检查
ls <skill-name>/SKILL.md
ls <skill-name>/references/<subject>/<textbook>/
ls <skill-name>/references/<subject>/<textbook>/*-outline.md

# 2. 章节完整性检查
for dir in <skill-name>/references/<subject>/<textbook>/ch*/; do
  name=$(basename "$dir")
  [ -f "$dir/$name.md" ] && echo "✓ $name" || echo "✗ $name (missing .md)"
  [ -d "$dir/images" ] && echo "  ✓ has images/" || echo "  ✗ missing images/"
done
```

- [ ] 所有章节目录都有 `.md` 文件（文件名=目录名）
- [ ] 所有章节目录都有 `images/` 文件夹
- [ ] 大纲文件存在且内容完整
- [ ] SKILL.md 的 frontmatter YAML 格式正确
- [ ] `on` 列表关键词能覆盖常见查询方式
- [ ] 文档结构表中的路径与实际目录一致

---

## 目录结构模板 (Directory Structure Template)

新建知识库的最终目录结构应如下所示：

```
<skill-name>/                              ← kebab-case，如 physics-knowledge-base
  SKILL.md                                 ← 技能定义文件
  references/                              ← 参考文档根目录
    <subject>/                             ← 单英语小写词，如 physics
      <textbook-slug>/                     ← 教材名slug，如 University-Physics-15e
        <Textbook-Name>-outline.md         ← 知识点大纲文件
        Chapter-1-Name/                    ← 章节目录（来自 chapter-organizer）
          Chapter-1-Name.md
          images/
            a1b2c3...jpg
        Chapter-2-Name/
          Chapter-2-Name.md
          images/
        ...
```

示例（以物理为例）：
```
physics-knowledge-base/
  SKILL.md
  references/
    physics/
      University-Physics-15e/
        University-Physics-15e-outline.md
        Chapter-1-Units-and-Physical-Quantities/
          Chapter-1-Units-and-Physical-Quantities.md
          images/
        Chapter-2-Motion-Along-a-Straight-Line/
          Chapter-2-Motion-Along-a-Straight-Line.md
          images/
        ...
```

---

## 命名规范 (Naming Conventions)

| 项目 | 规范 | 示例 |
|------|------|------|
| Skill 目录 | `lowercase-kebab-case` | `physics-knowledge-base` |
| SKILL.md 文件名 | 始终为 `SKILL.md` | `SKILL.md` |
| 科目目录 | 单个英语小写词 | `physics`、`chemistry`、`biology` |
| 教材目录 | `Title-Case-With-Hyphens-And-Edition` | `University-Physics-15e` |
| 章节目录 | 来自 `chapter-organizer` 输出 | `Chapter-1-Units-and-Physical-Quantities` |
| 章节 .md 文件 | 与父目录同名 | `Chapter-1-Units-and-Physical-Quantities.md` |
| 大纲文件 | `<Textbook-Name>-outline.md` | `University-Physics-15e-outline.md` |
| 图片目录 | `images/` | 每个章节目录下的 `images/` |
| 图片文件名 | MinerU 哈希值 | `a1b2c3d4e5f6...jpg` |

**特殊目录建议：**
- **前言/序言**：要么放在 `Preface/Preface.md`，要么用 `00-Preface/00-Preface.md`（数字前缀保证排序）
- **附录**：用 `Appendix-A-Name/Appendix-A-Name.md` 或统一放入 `appendices/appendices.md`
- **索引**：用 `index/index.md`
- **特殊函数/公式表**：用 `special-functions/special-functions.md`

---

## SKILL.md 编写规范 (SKILL.md Authoring Conventions)

### Frontmatter 规范

| 字段 | 要求 |
|------|------|
| `name` | 必须与目录名完全一致，kebab-case |
| `description` | 使用 `>-` YAML 块标量；中英双语；包含触发条件和优先使用指令；不超过 500 字 |
| `compatibility.require_tools` | 消费型技能始终 `[Read, Glob]` |
| `on` | 至少 15–25 个关键词；中英双语；按主题用 YAML 注释分组 |

### 正文规范

- 每个主要部分用 `---` 分隔
- 文档结构表使用 GFM 管道表格，3 列：`目录 | 内容 | 前置依赖`
- 前置依赖栏：引用章节号（如"第1章"、"第1-3章"），基础章节写"无"
- 回答模板用代码块（` ``` `）展示
- 注意事项必须包含：默认语言、英文术语保留、LaTeX 格式、图片路径、回溯依赖原则、诚实告知

### 触发关键词覆盖原则

`on` 列表的关键词应覆盖以下几类：

1. **科目名** — 中英文（如"物理"、"Physics"）
2. **教材标识** — 作者名、书名缩写（如"Young"、"University Physics"）
3. **主要概念** — 该学科的典型专题（如"力学"、"热学"、"电磁学"、"optics"、"quantum"）
4. **查询句式** — 如"查XX概念"、"XX公式"、"XX定理"、"什么是XX"、"derive"、"prove"
5. **操作动词** — 如"计算"、"推导"、"证明"、"求"、"find"、"solve"

---

## 大纲文件编写指南 (Outline File Guide)

大纲文件的目的是帮助 agent **快速定位知识点所在的章节**。

### 格式规范

```markdown
# 物理 — University Physics 知识点大纲

教材：Young & Freedman, *University Physics with Modern Physics*, 15th Edition
整理日期：2026-06-16

---

## Chapter 1: Units, Physical Quantities, and Vectors（单位、物理量与向量）

### 1.1 The Nature of Physics（物理学的本质）
- 物理学的研究范畴（physics）
- 理论与实验的关系

### 1.2 Solving Physics Problems（解决物理问题）
- 单位制与 SI 单位（SI units）
- 量纲分析（dimensional analysis）
- 有效数字（significant figures）

### 1.3 Standards and Units（标准与单位）
- 长度、质量、时间的基本单位
- 国际单位制 SI

---

## Chapter 2: Motion Along a Straight Line（直线运动）
...
```

### 编写要点

- H1：`# 中文Subject — English Textbook Title 知识点大纲`
- 包含教材元信息（作者、版本、整理日期）
- 每个章节用 `---` 分隔
- 章节标题用 `## Chapter X: Title（中文标题）`
- 节标题用 `### X.Y Section Name（中文节名）`
- 知识点用无序列表 `- 描述（English Term）`
- 只包含实质性内容标题（不列习题、不列代码输出）
- 如果某节有重要公式，可以用 `$$...$$` 简写，但不需要完整推导

---

## 验证 (Verification)

创建完成后，运行以下验证：

### 1. 目录结构检查
```
<skill-name>/SKILL.md                            ← 必须存在
<skill-name>/references/<subject>/<textbook>/     ← 必须存在
<skill-name>/references/<subject>/<textbook>/*-outline.md  ← 必须存在
```

### 2. 章节完整性检查
每个章节目录必须满足：
- 包含一个 `.md` 文件，**文件名与目录名完全一致**
- 包含 `images/` 目录（可以为空）

### 3. Frontmatter YAML 验证
用 `Read` 工具读取新建的 `SKILL.md`，检查：
- `name` 是否与目录名一致
- `description` 是否足够覆盖触发场景
- `on` 列表是否有足够的关键词覆盖
- `compatibility.require_tools` 是否写对了

### 4. 路径一致性检查
- 将「文档结构」表格中的路径与实际目录一一核对
- 大纲文件路径是否与目录中的文件名一致

### 5. 大纲完整性检查
- 大纲是否覆盖了所有列在「文档结构」表中的章节
- 是否有明显的缺漏（某章完全没出现在大纲中）

---

## 参考范例 (Reference Examples)

### 完整的参考技能

`mathematical-knowledge-base` 是本 Skill 的**标准参考实现**：
- 路径：`d:\workspace\my-skills\mathematical-knowledge-base\`
- 它覆盖概率论和微积分两个科目
- 是你要创建的知识库技能的模板

在编写新技能时，如果对本指南中的某部分不明确，可以直接读取 `mathematical-knowledge-base/SKILL.md` 查看具体写法。

### 关键参考文件路径

| 用途 | 文件路径 |
|------|----------|
| SKILL.md 完整格式参考 | `mathematical-knowledge-base/SKILL.md` |
| 大纲文件格式参考 | `mathematical-knowledge-base/references/calculus/Calculus-Early-Transcendentals-9e/Calculus-Early-Transcendentals-9e-outline.md` |
| 章节文件格式参考 | `mathematical-knowledge-base/references/calculus/Calculus-Early-Transcendentals-9e/ch02-Limits-and-Derivatives/ch02-Limits-and-Derivatives.md` |

---

## 与 chapter-organizer 的关系 (Relationship to Chapter-Organizer)

`chapter-organizer` 和 `knowledge-base-creator` 是两个衔接的技能，分工明确：

| 阶段 | 技能 | 职责 |
|------|------|------|
| **原始 MinerU → 章节** | `chapter-organizer` | 重命名文件、按章节整理、保留图片引用、验证完整性 |
| **章节 → 知识库系统** | `knowledge-base-creator`（本 Skill） | 创建 skill 目录、写 SKILL.md、生成大纲、验证 |
| **用户查询 → 回答** | 新创建的知识库 skill | 用户查询概念时查阅原文，组织回答 |

> ⚠️ **不要混淆两者：**
> - 如果用户拿来的还是 MinerU raw 输出（`full.md` + `images/`），用 `chapter-organizer`
> - 如果用户已经有整理好的章节目录，用本 Skill
> - 如果用户问概念问题，用已经建好的知识库 skill（比如 `mathematical-knowledge-base`），而不是这两个创建型技能

### 快速判断流程图

```
用户有教材文档？
├─ 是 raw MinerU 输出（full.md + images/）→ 用 chapter-organizer
├─ 已经是章节目录（chXX-Name/chXX-Name.md + images/）→ 用本 Skill 创建知识库
└─ 已经建好知识库（有 SKILL.md + references/）→ 直接用那个知识库查概念
```
