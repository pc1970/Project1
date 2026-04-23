---
name: office-convert
description: Convert an office document between formats (e.g. docx→pdf, xlsx→csv, pptx→pdf) using the office router skill.
argument-hint: <input-path> <output-format>
---

# /office-convert

Converts a single document between supported office formats.

## Usage

```
/office-convert <input-path> <output-format>
```

Examples:

```
/office-convert report.docx pdf
/office-convert data.xlsx csv
/office-convert deck.pptx pdf
```

## Behavior

1. Detects the source format from the file extension.
2. Invokes the `office` router skill to perform the conversion.
3. Writes the output alongside the input with the new extension and reports the path.
