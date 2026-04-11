# Superpowers Marketplace

A catalog of Claude Code skills you can browse and install with the `/plugin` skill.

## Usage

```
/plugin list              — browse all available skills
/plugin search <query>    — search by name, tag, or description
/plugin info <name>       — show full details for a skill
/plugin install <name>    — install a skill to ~/.claude/skills/
/plugin uninstall <name>  — remove an installed skill
/plugin installed         — list currently installed skills
```

## Available Skills

| Skill | Category | Description |
|---|---|---|
| `pdf` | documents | PDF text extraction, tables, forms, merge/split, annotation |
| `docx` | documents | Word document read/write/edit/format/convert |
| `xlsx` | documents | Excel spreadsheets, formulas, charts, CSV/JSON export |
| `pptx` | documents | PowerPoint slides, images, notes, outlines |
| `office` | documents | Master router for all office formats + batch conversion |

## Catalog

The skill catalog lives at `.claude-plugin/marketplace.json`.
To add a new skill to the marketplace, add an entry to that file.
