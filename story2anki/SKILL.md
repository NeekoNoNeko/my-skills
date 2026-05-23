---
name: story2anki
description: >-
  Imports markdown files into Anki flashcards via AnkiConnect.
  Use when the user asks to import a markdown file into Anki, split a markdown file by chapters into Anki cards,
  or mentions "导入" a markdown file to "anki".
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
- **Front**: `{filename}-{section title}` (e.g., `refuel-At the Gas Station`)
- **Back**: Full text of the section
- **Tags**: From YAML frontmatter + any extra tags

### Prerequisites
1. Anki must be running with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) plugin installed
2. Python 3.8+ required

## Example

```
python .claude/skills/story2anki/scripts/import_md_to_anki.py refuel.md --tags 词汇
```
