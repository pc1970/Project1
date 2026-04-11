---
name: pdf
description: >
  PDF Processing skill for Claude Code. Handles text extraction, table parsing,
  form filling, PDF merging and splitting, and annotation.
  TRIGGER when: user references a .pdf file; asks to extract text, parse tables,
  fill a form, merge/split PDFs, or annotate a PDF; or says "process a PDF".
---

# PDF Processing Skill

Handle PDF operations: text extraction, table parsing, form filling, merging/splitting, and annotation.

## Prerequisites

Install required libraries before starting. Check what is already installed before installing.

```bash
pip install pdfplumber pymupdf pypdf reportlab
```

- **pdfplumber** — text extraction and table parsing
- **pymupdf (fitz)** — annotation, form filling, merging/splitting
- **pypdf** — merging, splitting, metadata
- **reportlab** — generating new PDFs and overlays

## Workflow

Make a todo list for all the tasks in this workflow and work on them one after another.

---

### 1. Identify the Operation

Determine which operation(s) the user needs:

| User intent | Operation |
|---|---|
| "extract text", "read the PDF", "get the content" | Text Extraction |
| "parse tables", "get the data", "extract tables" | Table Parsing |
| "fill the form", "fill in fields" | Form Filling |
| "merge", "combine PDFs", "join PDFs" | PDF Merging |
| "split", "separate pages", "extract pages" | PDF Splitting |
| "annotate", "highlight", "add comments", "add notes" | Annotation |

If unclear, ask the user which operation they need before proceeding.

---

### 2. Text Extraction

Use `pdfplumber` for accurate text extraction including layout preservation.

```python
import pdfplumber

def extract_text(pdf_path: str, pages: list[int] | None = None) -> str:
    """Extract text from a PDF. pages is 0-indexed; None means all pages."""
    with pdfplumber.open(pdf_path) as pdf:
        target_pages = [pdf.pages[i] for i in pages] if pages else pdf.pages
        return "\n\n".join(
            f"--- Page {page.page_number} ---\n{page.extract_text() or ''}"
            for page in target_pages
        )

text = extract_text("document.pdf")
print(text)
```

**Tips:**
- Use `page.extract_text(layout=True)` to preserve column/whitespace layout.
- For scanned PDFs (images), warn the user that OCR is required and suggest `pytesseract` + `pdf2image`.

---

### 3. Table Parsing

Use `pdfplumber` for table detection and extraction.

```python
import pdfplumber
import csv

def extract_tables(pdf_path: str, output_csv: str | None = None) -> list[list[list]]:
    """Extract all tables from a PDF. Optionally save to CSV."""
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            all_tables.extend(tables)

    if output_csv and all_tables:
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            for table in all_tables:
                writer.writerows(table)
                writer.writerow([])  # blank row between tables

    return all_tables

tables = extract_tables("report.pdf", output_csv="tables.csv")
print(f"Found {len(tables)} table(s)")
```

**Tips:**
- If table boundaries are detected incorrectly, use `page.extract_table(table_settings={...})` with custom settings.
- For complex tables, try `table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}`.

---

### 4. Form Filling

Use `pymupdf` (fitz) to fill interactive PDF form fields.

```python
import fitz  # pymupdf

def fill_pdf_form(input_path: str, output_path: str, field_values: dict[str, str]) -> None:
    """Fill PDF form fields. field_values maps field name to value."""
    doc = fitz.open(input_path)
    for page in doc:
        for field in page.widgets():
            if field.field_name in field_values:
                field.field_value = field_values[field.field_name]
                field.update()
    doc.save(output_path)
    doc.close()

# First, inspect available fields:
def list_form_fields(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    fields = []
    for page in doc:
        for widget in page.widgets():
            fields.append(f"{widget.field_name!r} (type: {widget.field_type_string})")
    doc.close()
    return fields

print(list_form_fields("form.pdf"))

fill_pdf_form("form.pdf", "form_filled.pdf", {
    "FirstName": "Jane",
    "LastName": "Doe",
    "Email": "jane@example.com",
})
```

**Tips:**
- Always list fields first with `list_form_fields()` before filling.
- For checkboxes, use `"Yes"` or `"Off"` as the value.
- Flatten the form after filling if the user doesn't need it to remain editable: `doc.save(output_path, deflate=True)`.

---

### 5. PDF Merging

Use `pypdf` for straightforward merging.

```python
from pypdf import PdfWriter

def merge_pdfs(input_paths: list[str], output_path: str) -> None:
    """Merge multiple PDFs into one, in order."""
    writer = PdfWriter()
    for path in input_paths:
        writer.append(path)
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Merged {len(input_paths)} files → {output_path}")

merge_pdfs(["part1.pdf", "part2.pdf", "part3.pdf"], "merged.pdf")
```

**Tips:**
- To merge specific page ranges: `writer.append("file.pdf", pages=(0, 5))` (0-indexed, exclusive end).
- Preserve bookmarks/outlines with `writer.append(..., import_outline=True)`.

---

### 6. PDF Splitting

Use `pypdf` to split a PDF by page ranges or into individual pages.

```python
from pypdf import PdfReader, PdfWriter

def split_pdf_by_ranges(input_path: str, ranges: list[tuple[int, int]], output_prefix: str) -> list[str]:
    """
    Split a PDF into chunks by page ranges.
    ranges: list of (start, end) tuples — 0-indexed, end is exclusive.
    Returns list of output file paths.
    """
    reader = PdfReader(input_path)
    output_paths = []
    for i, (start, end) in enumerate(ranges):
        writer = PdfWriter()
        for page_num in range(start, min(end, len(reader.pages))):
            writer.add_page(reader.pages[page_num])
        out_path = f"{output_prefix}_part{i + 1}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        output_paths.append(out_path)
    return output_paths

def split_pdf_into_pages(input_path: str, output_dir: str) -> list[str]:
    """Split every page into its own PDF file."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    paths = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(output_dir, f"page_{i + 1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        paths.append(out_path)
    return paths

# Example: split pages 1-10 and 11-20 (0-indexed: 0-10, 10-20)
split_pdf_by_ranges("document.pdf", [(0, 10), (10, 20)], "output")
```

---

### 7. Annotation

Use `pymupdf` to add highlights, underlines, comments (sticky notes), or freetext annotations.

```python
import fitz  # pymupdf

def highlight_text(pdf_path: str, output_path: str, search_text: str, color: tuple = (1, 1, 0)) -> int:
    """Highlight all occurrences of search_text. color is RGB 0-1 float. Returns match count."""
    doc = fitz.open(pdf_path)
    count = 0
    for page in doc:
        instances = page.search_for(search_text)
        for rect in instances:
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=color)
            annot.update()
            count += 1
    doc.save(output_path)
    doc.close()
    return count

def add_sticky_note(pdf_path: str, output_path: str, page_num: int, x: float, y: float, content: str) -> None:
    """Add a sticky note (text comment) at (x, y) on the given page (0-indexed)."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    point = fitz.Point(x, y)
    annot = page.add_text_annot(point, content)
    annot.update()
    doc.save(output_path)
    doc.close()

def add_freetext(pdf_path: str, output_path: str, page_num: int, rect: tuple, text: str, fontsize: int = 12) -> None:
    """Add a freetext (visible text box) annotation."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    annot = page.add_freetext_annot(fitz.Rect(*rect), text, fontsize=fontsize)
    annot.update()
    doc.save(output_path)
    doc.close()

# Highlight all occurrences of "important"
count = highlight_text("document.pdf", "annotated.pdf", "important")
print(f"Highlighted {count} occurrences")

# Add a note on page 1 at position (100, 200)
add_sticky_note("document.pdf", "annotated.pdf", page_num=0, x=100, y=200, content="Review this section")
```

**Annotation types available via pymupdf:**
- `page.add_highlight_annot(rect)` — yellow highlight
- `page.add_underline_annot(rect)` — underline
- `page.add_strikeout_annot(rect)` — strikethrough
- `page.add_text_annot(point, text)` — sticky note
- `page.add_freetext_annot(rect, text)` — visible text box
- `page.add_rect_annot(rect)` — rectangle border

---

## Error Handling

Handle these common errors gracefully:

```python
import fitz
from pypdf.errors import PdfReadError

# Encrypted/password-protected PDFs
def open_pdf_safe(path: str, password: str | None = None):
    doc = fitz.open(path)
    if doc.is_encrypted:
        if password is None:
            raise ValueError(f"PDF is encrypted. Please provide a password.")
        if not doc.authenticate(password):
            raise ValueError("Incorrect password.")
    return doc

# Corrupted PDFs
try:
    reader = PdfReader("file.pdf")
except PdfReadError as e:
    print(f"Could not read PDF: {e}")
```

**Common issues:**
- **Encrypted PDF** → ask the user for the password
- **Scanned PDF with no text layer** → warn about OCR requirement
- **Large PDFs** → process in chunks; warn user about memory usage
- **Corrupted PDF** → report the error clearly and suggest re-exporting from source

---

## Wrap Up

After completing the operation, report back to the user with:

1. **Operation performed** and input/output file paths
2. **Results summary** — e.g., pages processed, tables found, fields filled, annotations added
3. **Output file location**
4. Any **warnings or limitations** (e.g., scanned pages skipped, fields not found)

Example summary format:

```
Operation: Text Extraction
Input:      report.pdf (12 pages)
Output:     report_text.txt
Pages processed: 12/12
Characters extracted: 48,302
Notes: Page 7 contained only an image and was skipped.
```
