---
name: pptx
description: >
  PowerPoint presentation skill for Claude Code. Handles reading, creating,
  editing slides, text boxes, images, charts, speaker notes, slide layouts,
  and conversion for .pptx files.
  TRIGGER when: user references a .pptx or .ppt file; asks to read/create/edit
  a presentation; extract slide content; add slides; or convert a presentation.
---

# PPTX Skill — PowerPoint Presentation Processing

Read, create, edit, and convert PowerPoint presentations (.pptx).

## Prerequisites

```bash
pip install python-pptx Pillow
```

Check before installing:
```bash
python3 -c "from pptx import Presentation; print('ok')" 2>/dev/null || pip install python-pptx
```

- **python-pptx** — full read/write support for `.pptx`
- **Pillow** — image handling and slide-to-image export support

> **Legacy .ppt (PowerPoint 97-2003):** Not supported by python-pptx.
> Convert first: `libreoffice --headless --convert-to pptx file.ppt`

## Workflow

Make a todo list for all tasks and work through them one at a time.

---

### 1. Identify the Operation

| User intent | Operation |
|---|---|
| "read", "extract text", "what's on slide N" | Text Extraction |
| "create", "make a presentation" | Create Presentation |
| "add a slide", "insert slide" | Add Slides |
| "edit", "update text" | Edit Content |
| "speaker notes", "presenter notes" | Notes |
| "add image", "insert picture" | Images |
| "convert", "export as images/PDF" | Conversion |

---

### 2. Text Extraction

```python
from pptx import Presentation

def extract_text(pptx_path: str) -> str:
    """Extract all text from all slides, including speaker notes."""
    prs = Presentation(pptx_path)
    slides_text = []

    for slide_num, slide in enumerate(prs.slides, 1):
        parts = [f"=== Slide {slide_num} ==="]

        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        parts.append(text)

        # Speaker notes
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                parts.append(f"[Notes: {notes}]")

        slides_text.append("\n".join(parts))

    return "\n\n".join(slides_text)

def get_slide_titles(pptx_path: str) -> list[str]:
    """Return a list of slide titles."""
    prs = Presentation(pptx_path)
    titles = []
    for slide in prs.slides:
        title = slide.shapes.title
        titles.append(title.text if title else "(no title)")
    return titles

print(extract_text("deck.pptx"))
print(get_slide_titles("deck.pptx"))
```

---

### 3. Create a Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def create_presentation(output_path: str, slides_data: list[dict]) -> None:
    """
    Create a presentation from a list of slide dicts.
    Each dict: {"title": str, "content": list[str], "notes": str (optional)}
    """
    prs = Presentation()
    # Slide dimensions: 16:9 widescreen
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    title_slide_layout = prs.slide_layouts[0]   # Title Slide
    content_layout = prs.slide_layouts[1]        # Title and Content
    blank_layout = prs.slide_layouts[6]          # Blank

    for i, slide_data in enumerate(slides_data):
        layout = title_slide_layout if i == 0 else content_layout
        slide = prs.slides.add_slide(layout)

        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = slide_data.get("title", "")

        # Set content (body placeholder)
        if len(slide.placeholders) > 1:
            body = slide.placeholders[1]
            tf = body.text_frame
            tf.clear()
            for j, point in enumerate(slide_data.get("content", [])):
                para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                para.text = point
                para.level = 0

        # Speaker notes
        if "notes" in slide_data:
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = slide_data["notes"]

    prs.save(output_path)

create_presentation("presentation.pptx", [
    {
        "title": "Quarterly Review",
        "content": ["Q4 2024 Results", "Presented by the Engineering Team"],
        "notes": "Welcome the audience and introduce the team."
    },
    {
        "title": "Key Metrics",
        "content": ["Revenue: +12% YoY", "Users: 1.4M active", "NPS Score: 72"],
        "notes": "Emphasize the NPS improvement from last quarter."
    },
    {
        "title": "Next Steps",
        "content": ["Launch v2.0 in Q1", "Expand to 3 new markets", "Hire 20 engineers"],
    },
])
```

---

### 4. Add or Edit Slides

```python
from pptx import Presentation
from pptx.util import Inches, Pt

def add_slide(pptx_path: str, output_path: str, title: str, content: list[str], position: int | None = None) -> None:
    """Add a new slide. position=None appends at the end."""
    prs = Presentation(pptx_path)
    layout = prs.slide_layouts[1]  # Title and Content
    slide = prs.slides.add_slide(layout)

    slide.shapes.title.text = title
    body = slide.placeholders[1].text_frame
    body.clear()
    for i, point in enumerate(content):
        para = body.paragraphs[0] if i == 0 else body.add_paragraph()
        para.text = point

    # Move slide to position if specified
    if position is not None:
        from pptx.oxml.ns import qn
        xml_slides = prs.slides._sldIdLst
        slides = list(xml_slides)
        xml_slides.remove(slides[-1])
        xml_slides.insert(position, slides[-1])

    prs.save(output_path)

def edit_slide_text(pptx_path: str, output_path: str, slide_index: int,
                    old_text: str, new_text: str) -> int:
    """Replace text on a specific slide (0-indexed). Returns replacement count."""
    prs = Presentation(pptx_path)
    slide = prs.slides[slide_index]
    count = 0
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if old_text in run.text:
                        run.text = run.text.replace(old_text, new_text)
                        count += 1
    prs.save(output_path)
    return count
```

---

### 5. Add Text Boxes and Shapes

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def add_text_box(pptx_path: str, output_path: str, slide_index: int,
                 text: str, left: float, top: float, width: float, height: float,
                 font_size: int = 18, bold: bool = False, color: tuple = (0, 0, 0)) -> None:
    """Add a text box to a slide. Dimensions in inches."""
    prs = Presentation(pptx_path)
    slide = prs.slides[slide_index]

    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    para = tf.paragraphs[0]
    run = para.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)

    prs.save(output_path)
```

---

### 6. Insert Images

```python
from pptx import Presentation
from pptx.util import Inches

def add_image(pptx_path: str, output_path: str, slide_index: int,
              image_path: str, left: float, top: float,
              width: float | None = None, height: float | None = None) -> None:
    """Insert an image on a slide. Dimensions in inches; None preserves aspect ratio."""
    prs = Presentation(pptx_path)
    slide = prs.slides[slide_index]

    slide.shapes.add_picture(
        image_path,
        Inches(left), Inches(top),
        width=Inches(width) if width else None,
        height=Inches(height) if height else None,
    )
    prs.save(output_path)
```

---

### 7. Speaker Notes

```python
from pptx import Presentation

def read_all_notes(pptx_path: str) -> list[tuple[int, str]]:
    """Return list of (slide_number, notes_text) for slides with notes."""
    prs = Presentation(pptx_path)
    return [
        (i + 1, slide.notes_slide.notes_text_frame.text.strip())
        for i, slide in enumerate(prs.slides)
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip()
    ]

def set_notes(pptx_path: str, output_path: str, slide_index: int, notes: str) -> None:
    prs = Presentation(pptx_path)
    prs.slides[slide_index].notes_slide.notes_text_frame.text = notes
    prs.save(output_path)
```

---

### 8. Conversion

#### PPTX → Plain text
```python
from pptx import Presentation

def pptx_to_text(pptx_path: str, output_path: str) -> None:
    prs = Presentation(pptx_path)
    lines = []
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"--- Slide {i} ---")
        for shape in slide.shapes:
            if shape.has_text_frame:
                lines.append(shape.text_frame.text)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
```

#### PPTX → PDF or images (requires LibreOffice)
```bash
# Convert to PDF
libreoffice --headless --convert-to pdf deck.pptx

# Convert to PNG images (one per slide)
libreoffice --headless --convert-to png deck.pptx
```

#### PPTX → Markdown outline
```python
from pptx import Presentation

def pptx_to_markdown(pptx_path: str, output_path: str) -> None:
    prs = Presentation(pptx_path)
    lines = []
    for i, slide in enumerate(prs.slides, 1):
        title = slide.shapes.title.text if slide.shapes.title else f"Slide {i}"
        lines.append(f"## {title}")
        for shape in slide.shapes:
            if shape.has_text_frame and shape != slide.shapes.title:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        indent = "  " * para.level
                        lines.append(f"{indent}- {text}")
        lines.append("")
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
```

---

## Error Handling

```python
from pptx import Presentation
from pptx.exc import PackageNotFoundError

try:
    prs = Presentation("file.pptx")
except PackageNotFoundError:
    print("File not found or not a valid .pptx file.")
except Exception as e:
    print(f"Could not open presentation: {e}")
    # For .ppt: libreoffice --headless --convert-to pptx file.ppt
```

**Common issues:**
- `.ppt` (legacy) — not supported; convert via LibreOffice first
- Placeholder index varies by layout — inspect `slide.placeholders` to find the right one
- Custom fonts — may not render correctly on systems without those fonts installed

---

## Wrap Up

```
Operation: Create Presentation
Output:     presentation.pptx
Slides:     8
Slides with notes: 5
Images inserted: 2
```
