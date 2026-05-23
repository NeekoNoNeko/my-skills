#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ANKI_CONNECT_URL = "http://localhost:8765"


def anki_connect(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    try:
        req = urllib.request.Request(ANKI_CONNECT_URL, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        if result.get("error"):
            raise RuntimeError(f"AnkiConnect error: {result['error']}")
        return result.get("result")
    except urllib.error.URLError:
        print("Error: Cannot connect to AnkiConnect. Make sure Anki is running with AnkiConnect plugin installed.")
        sys.exit(1)


def parse_markdown(filepath):
    content = Path(filepath).read_text(encoding="utf-8")

    tags = []
    body = content

    # Parse YAML frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter = content[3:end].strip()
            body = content[end + 3:].strip()
            for line in frontmatter.splitlines():
                stripped = line.strip()
                if stripped.startswith("tags:"):
                    rest = stripped[5:].strip()
                    if rest.startswith("["):
                        tags = [t.strip().strip('"').strip("'") for t in rest[1:-1].split(",") if t.strip()]
                    elif rest == "":
                        continue
                    else:
                        tags = [rest.strip().strip('"').strip("'")]
            if not tags:
                in_tags = False
                for line in frontmatter.splitlines():
                    if line.strip().startswith("tags:"):
                        in_tags = True
                    elif in_tags:
                        m = re.match(r'\s*-\s*(.+)', line)
                        if m:
                            tags.append(m.group(1).strip().strip('"').strip("'"))
                        else:
                            in_tags = False

    sections = re.split(r'\n(?=# )', body)
    notes = []
    base_name = Path(filepath).stem

    for section in sections:
        section = section.strip()
        if not section:
            continue
        title_match = re.match(r'# (.+)', section)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        body_text = section[title_match.end():].strip()

        # Detect cloze markers {{c1::...}}
        has_cloze = bool(re.search(r'\{\{c\d+::', body_text))
        if has_cloze:
            notes.append({
                "type": "cloze",
                "text": body_text,
                "tags": tags,
            })
        else:
            notes.append({
                "type": "basic",
                "front": f"{base_name}-{title}",
                "back": body_text,
                "tags": tags,
            })

    return notes


def ensure_deck(deck_name):
    decks = anki_connect("deckNames") or []
    if deck_name not in decks:
        anki_connect("createDeck", deck=deck_name)
        print(f"Created deck: {deck_name}")


def ensure_model(model_name, is_cloze):
    models = anki_connect("modelNames") or []
    if model_name not in models:
        fields = ["Text", "Extra"] if is_cloze else ["Front", "Back"]
        anki_connect("createModel",
                     modelName=model_name,
                     inOrderFields=fields,
                     css=".card { font-family: Arial; font-size: 16px; text-align: left; }",
                     isCloze=is_cloze)
        print(f"Created {'cloze' if is_cloze else 'basic'} model: {model_name}")


def add_notes(deck_name, basic_model, cloze_model, notes, target_tags):
    added = 0
    skipped = 0
    for i, note in enumerate(notes, 1):
        all_tags = list(set(note["tags"] + target_tags))
        if note["type"] == "cloze":
            result = anki_connect("addNote", note={
                "deckName": deck_name,
                "modelName": cloze_model,
                "fields": {"Text": note["text"], "Extra": ""},
                "tags": all_tags,
                "options": {"allowDuplicate": False},
            })
            label = note["text"][:60]
        else:
            result = anki_connect("addNote", note={
                "deckName": deck_name,
                "modelName": basic_model,
                "fields": {"Front": note["front"], "Back": note["back"]},
                "tags": all_tags,
                "options": {"allowDuplicate": False},
            })
            label = note["front"]

        if result is not None:
            added += 1
            status = "Added"
        else:
            skipped += 1
            status = "Skipped (duplicate)"
        print(f"  [{i}/{len(notes)}] {status}: {label}")
    return added, skipped


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_md_to_anki.py <markdown_file> [--deck <deck_name>] [--tags <tag1,tag2>]")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    deck_name = "story2anki"
    extra_tags = []

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--deck" and i + 1 < len(sys.argv):
            deck_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--tags" and i + 1 < len(sys.argv):
            extra_tags = [t.strip() for t in sys.argv[i + 1].split(",") if t.strip()]
            i += 2
        else:
            i += 1

    print(f"Parsing: {filepath}")
    notes = parse_markdown(filepath)
    print(f"Found {len(notes)} sections")

    has_cloze = any(n["type"] == "cloze" for n in notes)
    has_basic = any(n["type"] == "basic" for n in notes)

    print(f"Connecting to AnkiConnect...")
    ensure_deck(deck_name)

    # Use fixed model names (not deck-dependent) to avoid model bloat
    basic_model = "story2anki-Basic"
    cloze_model = "story2anki-Cloze"
    if has_basic:
        ensure_model(basic_model, is_cloze=False)
    if has_cloze:
        ensure_model(cloze_model, is_cloze=True)

    print(f"Importing to deck '{deck_name}'...")
    added, skipped = add_notes(deck_name, basic_model, cloze_model, notes, extra_tags)
    print(f"Done! Added {added} cards, skipped {skipped} duplicates.")


if __name__ == "__main__":
    main()
