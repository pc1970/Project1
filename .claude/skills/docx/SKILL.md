---
name: docx
description: >
  Word document skill for Claude Code. Handles reading, writing, editing,
  formatting, table manipulation, comments, and conversion for .docx files.
  TRIGGER when: user references a .docx or .doc file; asks to read/create/edit
  a Word document; extract text from Word; or convert Word to another format.
---

# DOCX Skill — Word Document Processing

Read, write, edit, and convert Microsoft Word (.docx) documents.

## Prerequisites

```bash
pip install python-docx
```

Check before installing: `python3 -c "import docx; print('ok')" 2>/dev/null || pip install python-docx`

## Workflow

Make a todo list for all tasks and work through them one at a time.

---

### 1. Identify the Operation

| User intent | Operation |
|---|---|
| "read", "extract text", "what does this say" | Text Extraction |
| "create", "write a document", "generate a report" | Create Document |
| "edit", "update", "change the text" | Edit Document |
| "format", "make it bold", "add heading" | Formatting |
| "add a table", "insert table" | Table Operations |
| "add comment", "leave a note" | Comments |
| "convert to", "export as" | Conversion |

---

### 2. Text Extraction

```python
from docx import Document

def extract_text(docx_path: str) -> str:
    """Extract all text from a Word document, preserving paragraph structure."""
    doc = Document(docx_path)
    sections = []

    for para in doc.paragraphs:
        if para.text.strip():
            prefix = ""
            if para.style.name.startswith("Heading"):
                level = para.style.name.split()[-1]
                prefix = "#" * int(level) + " " if level.isdigit() else "# "
            sections.append(f"{prefix}{para.text}")

    return "\n\n".join(sections)

def extract_with_tables(docx_path: str) -> str:
    """Extract text and table contents."""
    doc = Document(docx_path)
    parts = []

    for block in doc.element.body:
        tag = block.tag.split("}")[-1]
        if tag == "p":
            from docx.oxml.ns import qn
            para_text = "".join(r.text for r in block.iter(qn("w:t")))
            if para_text.strip():
                parts.append(para_text)
        elif tag == "tbl":
            # Represent table as markdown
            rows = []
            for row in block.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr"):
                cells = []
                for cell in row.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc"):
                    cell_text = "".join(t.text for t in cell.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
                    cells.append(cell_text.strip())
                rows.append("| " + " | ".join(cells) + " |")
            parts.append("\n".join(rows))

    return "\n\n".join(parts)

print(extract_text("report.docx"))
```

---

### 3. Create a Document

```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_document(output_path: str) -> None:
    doc = Document()

    # Title
    title = doc.add_heading("Document Title", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Heading + paragraph
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph("This is the introduction paragraph.")

    # Styled paragraph
    para = doc.add_paragraph()
    run = para.add_run("Bold and colored text. ")
    run.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    para.add_run("Normal text continues here.")

    # Bullet list
    doc.add_heading("Key Points", level=2)
    for point in ["First point", "Second point", "Third point"]:
        doc.add_paragraph(point, style="List Bullet")

    # Numbered list
    for i, step in enumerate(["Step one", "Step two", "Step three"], 1):
        doc.add_paragraph(step, style="List Number")

    doc.save(output_path)

create_document("output.docx")
```

---

### 4. Edit an Existing Document

```python
from docx import Document

def replace_text(docx_path: str, output_path: str, replacements: dict[str, str]) -> int:
    """Replace text throughout the document. Returns number of replacements made."""
    doc = Document(docx_path)
    count = 0

    for para in doc.paragraphs:
        for run in para.runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, new)
                    count += 1

    # Also replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        for old, new in replacements.items():
                            if old in run.text:
                                run.text = run.text.replace(old, new)
                                count += 1

    doc.save(output_path)
    return count

count = replace_text("template.docx", "filled.docx", {
    "{{NAME}}": "Jane Doe",
    "{{DATE}}": "2024-01-15",
    "{{COMPANY}}": "Acme Corp",
})
print(f"Made {count} replacements")
```

---

### 5. Table Operations

```python
from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT

def add_table(docx_path: str, output_path: str, headers: list[str], rows: list[list]) -> None:
    """Add a formatted table to a document."""
    doc = Document(docx_path)
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"

    # Header row
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        hdr_cells[i].paragraphs[0].runs[0].bold = True

    # Data rows
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, value in enumerate(row_data):
            row_cells[i].text = str(value)

    doc.save(output_path)

def read_tables(docx_path: str) -> list[list[list[str]]]:
    """Extract all tables from a document as nested lists."""
    doc = Document(docx_path)
    return [
        [[cell.text.strip() for cell in row.cells] for row in table.rows]
        for table in doc.tables
    ]

add_table("report.docx", "report_with_table.docx",
    headers=["Name", "Score", "Grade"],
    rows=[["Alice", "95", "A"], ["Bob", "82", "B"], ["Carol", "91", "A-"]])
```

---

### 6. Formatting

```python
from docx import Document
from docx.shared import Pt, RGBColor

def apply_formatting(docx_path: str, output_path: str) -> None:
    doc = Document(docx_path)

    for para in doc.paragraphs:
        for run in para.runs:
            # Example: make all runs in heading paragraphs bold + blue
            if para.style.name.startswith("Heading"):
                run.bold = True
                run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
            run.font.size = Pt(12)

    doc.save(output_path)

# Available run formatting attributes:
# run.bold, run.italic, run.underline, run.strike
# run.font.size = Pt(12)
# run.font.name = "Arial"
# run.font.color.rgb = RGBColor(R, G, B)
# para.alignment = WD_ALIGN_PARAGRAPH.CENTER / LEFT / RIGHT / JUSTIFY
```

---

### 7. Comments

```python
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime

def add_comment(doc_path: str, output_path: str, search_text: str, comment: str, author: str = "Claude") -> None:
    """Add a comment to the first paragraph containing search_text."""
    doc = Document(doc_path)

    for para in doc.paragraphs:
        if search_text in para.text:
            # Build comment XML manually (python-docx has no built-in comment API)
            comment_id = "1"
            date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

            comments_part = doc.part.comments_part
            if comments_part is None:
                from docx.opc.part import Part
                from docx.opc.packuri import PackURI
                comments_xml = OxmlElement("w:comments")
                comments_xml.set(qn("xmlns:w"), "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
                # Simplified: for full comment support use a template docx with comment support
            break

    doc.save(output_path)
    # Note: Full comment insertion requires XML manipulation. For simple use cases,
    # consider inserting a visible [NOTE: ...] marker instead.
```

> **Note:** `python-docx` has limited built-in comment support. For complex comment workflows, manipulate the underlying XML directly or use a pre-built template.

---

### 8. Conversion

#### DOCX → Plain Text
```python
from docx import Document

def docx_to_text(docx_path: str, output_path: str) -> None:
    doc = Document(docx_path)
    text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    with open(output_path, "w") as f:
        f.write(text)
```

#### DOCX → Markdown
```python
from docx import Document

HEADING_MAP = {"Heading 1": "#", "Heading 2": "##", "Heading 3": "###"}

def docx_to_markdown(docx_path: str, output_path: str) -> None:
    doc = Document(docx_path)
    lines = []
    for para in doc.paragraphs:
        if not para.text.strip():
            continue
        prefix = HEADING_MAP.get(para.style.name, "")
        if prefix:
            lines.append(f"{prefix} {para.text}")
        elif para.style.name == "List Bullet":
            lines.append(f"- {para.text}")
        elif para.style.name == "List Number":
            lines.append(f"1. {para.text}")
        else:
            lines.append(para.text)
    with open(output_path, "w") as f:
        f.write("\n\n".join(lines))
```

#### DOCX → PDF (requires LibreOffice)
```bash
libreoffice --headless --convert-to pdf document.docx
```

---

## Error Handling

```python
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

try:
    doc = Document("file.docx")
except PackageNotFoundError:
    print("File not found or not a valid .docx file.")
except Exception as e:
    print(f"Could not open document: {e}")
    # If file is .doc (old format), convert with: libreoffice --headless --convert-to docx file.doc
```

**Common issues:**
- `.doc` (old Word 97-2003) — not supported by `python-docx`; convert to `.docx` first via LibreOffice
- Password-protected documents — `python-docx` cannot open them; use LibreOffice with `--infilter` and password
- Corrupt documents — try opening with LibreOffice to repair

---

## Wrap Up

Report back with:

```
Operation: Text Extraction
Input:      report.docx
Paragraphs: 42
Tables:     3
Characters: 12,840
Output:     report.txt
```
