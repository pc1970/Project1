---
name: office-tools
description: Meta-skill that groups the pdf, docx, xlsx, pptx, and office router skills under a single plugin for office-document workflows. Use when a task spans multiple office formats or when the user wants "the office toolkit".
---

# Office Tools

Umbrella skill for the office document toolkit.

## Included sub-skills

| Skill   | Handles                                |
|---------|----------------------------------------|
| pdf     | `.pdf` — extract, annotate, merge/split, forms |
| docx    | `.docx` — read, write, edit, tables    |
| xlsx    | `.xlsx`, `.xls`, `.csv` — formulas, charts, multi-sheet |
| pptx    | `.pptx` — slides, images, speaker notes |
| office  | cross-format conversion, `.rtf`, `.odf` routing |

## Dispatch

When invoked without a specific format, route to the `office` skill — it
auto-detects file type and delegates. For a known format, invoke the
dedicated skill directly to skip routing overhead.

## Dependencies

Installed by the project's SessionStart hook:
`python-docx`, `openpyxl`, `python-pptx`, `pymupdf`, `pypdf`,
`pdfplumber`, `pandas`, `reportlab`, `striprtf`.
