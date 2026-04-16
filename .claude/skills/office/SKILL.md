---
name: office
description: >
  Master Office Documents skill for Claude Code. Routes to the correct
  sub-skill based on file type and handles cross-format conversion between
  all office document types: .docx, .xlsx, .pptx, .pdf, .csv, .odt, .ods,
  .odp, .rtf, and plain text.
  TRIGGER when: user references any office document without specifying a skill;
  asks to convert between document formats; or needs to process multiple
  document types at once.
---

# Office Skill — Master Document Router

Detect file type and route to the correct sub-skill. Handle cross-format
conversions and batch operations across all office document types.

## Prerequisites

Install all office document libraries at once:

```bash
pip install python-docx openpyxl python-pptx pymupdf pypdf pdfplumber pandas reportlab odfpy striprtf
```

Or install selectively based on the file types involved.

| Library | Handles |
|---|---|
| `python-docx` | .docx read/write |
| `openpyxl` | .xlsx read/write |
| `python-pptx` | .pptx read/write |
| `pymupdf` | .pdf read/annotate/form-fill |
| `pypdf` | .pdf merge/split |
| `pdfplumber` | .pdf table extraction |
| `pandas` | .csv, .xlsx data analysis |
| `odfpy` | .odt, .ods, .odp (OpenDocument) — may fail on Debian; use `pandas engine="odf"` for .ods |
| `striprtf` | .rtf text extraction |

## Workflow

Make a todo list and work through tasks one at a time.

---

### 1. Detect File Type and Route

```python
import os

def detect_format(file_path: str) -> str:
    """Detect document format from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return {
        ".docx": "docx", ".doc": "doc-legacy",
        ".xlsx": "xlsx", ".xls": "xls-legacy",
        ".pptx": "pptx", ".ppt": "ppt-legacy",
        ".pdf":  "pdf",
        ".csv":  "csv",
        ".odt":  "odt", ".ods": "ods", ".odp": "odp",
        ".rtf":  "rtf",
        ".txt":  "txt", ".md": "markdown",
    }.get(ext, "unknown")
```

**Routing table:**

| Format | Use skill / library |
|---|---|
| `.docx` | → `docx` skill (`python-docx`) |
| `.xlsx` | → `xlsx` skill (`openpyxl`, `pandas`) |
| `.pptx` | → `pptx` skill (`python-pptx`) |
| `.pdf` | → `pdf` skill (`pymupdf`, `pypdf`) |
| `.csv` | → `pandas` directly |
| `.odt/.ods/.odp` | → `odfpy` (see Section 4) |
| `.rtf` | → `striprtf` (see Section 5) |
| `.doc/.xls/.ppt` | → convert with LibreOffice first |

If the format is a legacy format (`.doc`, `.xls`, `.ppt`), convert it first:
```bash
libreoffice --headless --convert-to docx file.doc
libreoffice --headless --convert-to xlsx file.xls
libreoffice --headless --convert-to pptx file.ppt
```

---

### 2. Universal Text Extractor

Extract text from any office format with a single function:

```python
import os

def extract_text_any(file_path: str) -> str:
    """Extract text from any supported office format."""
    fmt = detect_format(file_path)

    if fmt == "docx":
        from docx import Document
        doc = Document(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    elif fmt == "xlsx":
        import pandas as pd
        df = pd.read_excel(file_path)
        return df.to_markdown(index=False)

    elif fmt == "pptx":
        from pptx import Presentation
        prs = Presentation(file_path)
        parts = []
        for i, slide in enumerate(prs.slides, 1):
            parts.append(f"--- Slide {i} ---")
            for shape in slide.shapes:
                if shape.has_text_frame:
                    parts.append(shape.text_frame.text)
        return "\n".join(parts)

    elif fmt == "pdf":
        import fitz
        with fitz.open(file_path) as doc:
            return "\n\n".join(
                f"--- Page {i+1} ---\n{page.get_text().strip()}"
                for i, page in enumerate(doc)
            )

    elif fmt == "csv":
        import pandas as pd
        return pd.read_csv(file_path).to_markdown(index=False)

    elif fmt in ("odt", "odp"):
        from odf.opendocument import load
        from odf.text import P
        doc = load(file_path)
        return "\n".join(str(p) for p in doc.getElementsByType(P) if str(p).strip())

    elif fmt == "ods":
        import pandas as pd
        return pd.read_excel(file_path, engine="odf").to_markdown(index=False)

    elif fmt == "rtf":
        from striprtf.striprtf import rtf_to_text
        with open(file_path) as f:
            return rtf_to_text(f.read())

    elif fmt in ("txt", "markdown"):
        with open(file_path) as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported format: {file_path}")

# Use it:
text = extract_text_any("report.docx")
text = extract_text_any("data.xlsx")
text = extract_text_any("slides.pptx")
text = extract_text_any("document.pdf")
```

---

### 3. Cross-Format Conversion

#### Any office format → PDF (via LibreOffice)
```bash
libreoffice --headless --convert-to pdf --outdir ./output/ input.docx
libreoffice --headless --convert-to pdf --outdir ./output/ input.xlsx
libreoffice --headless --convert-to pdf --outdir ./output/ input.pptx
```

#### Python-based conversions (no LibreOffice needed)

```python
def docx_to_pdf_python(docx_path: str, pdf_path: str) -> None:
    """Approximate DOCX→PDF via text extraction + reportlab (layout not preserved)."""
    from docx import Document
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    doc = Document(docx_path)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    for para in doc.paragraphs:
        if not para.text.strip():
            y -= 12
            continue
        c.setFont("Helvetica-Bold" if para.style.name.startswith("Heading") else "Helvetica", 12)
        c.drawString(50, y, para.text[:100])  # truncate long lines
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()

def xlsx_to_csv_all_sheets(xlsx_path: str, output_dir: str) -> list[str]:
    """Export each sheet of an Excel file to its own CSV."""
    import pandas as pd, os
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    with pd.ExcelFile(xlsx_path) as xl:
        for sheet in xl.sheet_names:
            out = os.path.join(output_dir, f"{sheet}.csv")
            xl.parse(sheet).to_csv(out, index=False)
            paths.append(out)
    return paths

def pptx_to_docx_outline(pptx_path: str, docx_path: str) -> None:
    """Convert PPTX slide content into a Word document outline."""
    from pptx import Presentation
    from docx import Document

    prs = Presentation(pptx_path)
    doc = Document()

    for i, slide in enumerate(prs.slides, 1):
        title = slide.shapes.title.text if slide.shapes.title else f"Slide {i}"
        doc.add_heading(title, level=1)
        for shape in slide.shapes:
            if shape.has_text_frame and shape != slide.shapes.title:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        doc.add_paragraph(para.text, style="List Bullet")

    doc.save(docx_path)
```

---

### 4. OpenDocument Formats (.odt, .ods, .odp)

```python
from odf.opendocument import load, OpenDocumentText, OpenDocumentSpreadsheet
from odf.text import P, H
from odf.table import Table, TableRow, TableCell

def read_odt(odt_path: str) -> str:
    """Extract text from an OpenDocument Text file."""
    doc = load(odt_path)
    parts = []
    for elem in doc.text.childNodes:
        tag = elem.__class__.__name__
        if tag == "P":
            parts.append(str(elem))
        elif tag == "H":
            level = elem.getAttribute("outlinelevel") or "1"
            parts.append(f"{'#' * int(level)} {elem}")
    return "\n\n".join(p for p in parts if p.strip())

def read_ods(ods_path: str):
    """Read an OpenDocument Spreadsheet using pandas."""
    import pandas as pd
    return pd.read_excel(ods_path, engine="odf", sheet_name=None)  # all sheets
```

---

### 5. RTF Files

```python
def read_rtf(rtf_path: str) -> str:
    """Extract plain text from an RTF file."""
    from striprtf.striprtf import rtf_to_text
    with open(rtf_path, encoding="utf-8", errors="ignore") as f:
        return rtf_to_text(f.read())
```

---

### 6. Batch Processing

Process multiple files of mixed types at once:

```python
import os

def batch_extract(file_paths: list[str], output_dir: str) -> dict[str, str]:
    """Extract text from a list of mixed-format files. Returns {filename: text}."""
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    for path in file_paths:
        name = os.path.basename(path)
        try:
            text = extract_text_any(path)
            out_path = os.path.join(output_dir, name + ".txt")
            with open(out_path, "w") as f:
                f.write(text)
            results[name] = f"OK — {len(text)} chars → {out_path}"
        except Exception as e:
            results[name] = f"ERROR — {e}"

    return results

def batch_convert_to_pdf(input_dir: str, output_dir: str, extensions: list[str] | None = None) -> None:
    """Convert all matching files in a directory to PDF using LibreOffice."""
    import subprocess, glob
    os.makedirs(output_dir, exist_ok=True)
    exts = extensions or [".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"]
    files = [f for f in glob.glob(os.path.join(input_dir, "*")) if os.path.splitext(f)[1] in exts]
    if not files:
        print("No matching files found.")
        return
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir] + files,
        check=True
    )
    print(f"Converted {len(files)} file(s) to PDF in {output_dir}")
```

---

### 7. Inspect Any Document

Quick summary of any office file without full extraction:

```python
def inspect(file_path: str) -> dict:
    """Return metadata/structure summary of any office document."""
    fmt = detect_format(file_path)
    info = {"path": file_path, "format": fmt, "size_kb": round(os.path.getsize(file_path) / 1024, 1)}

    if fmt == "docx":
        from docx import Document
        doc = Document(file_path)
        info.update(paragraphs=len(doc.paragraphs), tables=len(doc.tables),
                    sections=len(doc.sections))

    elif fmt == "xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(file_path, read_only=True)
        info.update(sheets=wb.sheetnames)
        wb.close()

    elif fmt == "pptx":
        from pptx import Presentation
        prs = Presentation(file_path)
        info.update(slides=len(prs.slides),
                    slide_width_in=round(prs.slide_width.inches, 2),
                    slide_height_in=round(prs.slide_height.inches, 2))

    elif fmt == "pdf":
        import fitz
        with fitz.open(file_path) as doc:
            info.update(pages=len(doc), encrypted=doc.is_encrypted)

    elif fmt == "csv":
        import pandas as pd
        df = pd.read_csv(file_path, nrows=0)
        info.update(columns=list(df.columns))

    return info

import json
print(json.dumps(inspect("report.docx"), indent=2))
```

---

## Error Handling

```python
def safe_process(file_path: str) -> str:
    """Safely extract text from any document with full error context."""
    if not os.path.exists(file_path):
        return f"ERROR: File not found — {file_path}"

    fmt = detect_format(file_path)
    if fmt == "unknown":
        return f"ERROR: Unsupported format — {os.path.splitext(file_path)[1]}"

    if fmt in ("doc-legacy", "xls-legacy", "ppt-legacy"):
        return (f"ERROR: Legacy format '{fmt}' not directly supported. "
                f"Convert with: libreoffice --headless --convert-to "
                f"{'docx' if 'doc' in fmt else 'xlsx' if 'xls' in fmt else 'pptx'} {file_path}")

    try:
        return extract_text_any(file_path)
    except MemoryError:
        return "ERROR: File too large to process in memory. Try processing page by page."
    except Exception as e:
        return f"ERROR: {type(e).__name__} — {e}"
```

---

## Wrap Up

```
Operation: Batch Extract
Files processed: 8
  ✅ report.docx     → 12,840 chars
  ✅ data.xlsx       → 4 sheets, 1,203 rows
  ✅ slides.pptx     → 24 slides
  ✅ summary.pdf     → 6 pages, 8,204 chars
  ✅ contacts.csv    → 500 rows, 8 columns
  ✅ notes.odt       → 3,102 chars
  ✅ memo.rtf        → 892 chars
  ❌ old.doc         → legacy format, needs conversion
Output directory: ./extracted/
```
