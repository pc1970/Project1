---
name: xlsx
description: >
  Excel spreadsheet skill for Claude Code. Handles reading, writing, editing,
  formula evaluation, chart creation, multi-sheet operations, and conversion
  for .xlsx, .xls, and .csv files.
  TRIGGER when: user references a .xlsx, .xls, or spreadsheet file; asks to
  read/create/edit Excel; extract data; work with formulas or charts; or
  convert spreadsheet data.
---

# XLSX Skill — Excel Spreadsheet Processing

Read, write, edit, and convert Excel spreadsheets (.xlsx, .xls, .csv).

## Prerequisites

```bash
pip install openpyxl xlrd xlwt pandas
```

Check before installing:
```bash
python3 -c "import openpyxl, pandas; print('ok')" 2>/dev/null || pip install openpyxl xlrd pandas
```

- **openpyxl** — read/write `.xlsx` (primary)
- **xlrd** — read legacy `.xls` files (Excel 97-2003)
- **pandas** — data analysis, CSV/Excel conversion, aggregation
- **xlwt** — write legacy `.xls` (rarely needed)

## Workflow

Make a todo list for all tasks and work through them one at a time.

---

### 1. Identify the Operation

| User intent | Operation |
|---|---|
| "read", "extract", "what's in this sheet" | Read Data |
| "create", "generate a spreadsheet" | Create Workbook |
| "edit", "update", "change values" | Edit Data |
| "sum", "average", "formula" | Formulas |
| "chart", "graph", "visualize" | Charts |
| "multiple sheets", "another tab" | Multi-sheet |
| "convert", "export to CSV/JSON" | Conversion |

---

### 2. Read Data

#### Read with openpyxl
```python
from openpyxl import load_workbook

def read_sheet(xlsx_path: str, sheet_name: str | None = None) -> list[list]:
    """Read all rows from a sheet. sheet_name=None uses the active sheet."""
    wb = load_workbook(xlsx_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active
    return [[cell.value for cell in row] for row in ws.iter_rows()]

def list_sheets(xlsx_path: str) -> list[str]:
    wb = load_workbook(xlsx_path, read_only=True)
    names = wb.sheetnames
    wb.close()
    return names

rows = read_sheet("data.xlsx")
for row in rows:
    print(row)
```

#### Read with pandas (best for analysis)
```python
import pandas as pd

def read_excel_df(xlsx_path: str, sheet_name: str | int = 0) -> pd.DataFrame:
    """Read sheet into a DataFrame."""
    return pd.read_excel(xlsx_path, sheet_name=sheet_name)

def summarize(xlsx_path: str) -> None:
    df = read_excel_df(xlsx_path)
    print(df.head())
    print(df.describe())
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

summarize("data.xlsx")
```

#### Read legacy .xls
```python
import xlrd

def read_xls(xls_path: str, sheet_index: int = 0) -> list[list]:
    wb = xlrd.open_workbook(xls_path)
    ws = wb.sheet_by_index(sheet_index)
    return [ws.row_values(r) for r in range(ws.nrows)]
```

---

### 3. Create a Workbook

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_workbook(output_path: str, headers: list[str], data: list[list]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    # Header row with styling
    header_fill = PatternFill("solid", fgColor="1F497D")
    header_font = Font(bold=True, color="FFFFFF")
    border = Border(
        bottom=Side(style="medium"),
        right=Side(style="thin"),
    )

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border
        ws.column_dimensions[get_column_letter(col)].width = max(len(header) + 4, 12)

    # Data rows with alternating row colors
    light_fill = PatternFill("solid", fgColor="EBF0F8")
    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if row_idx % 2 == 0:
                cell.fill = light_fill

    # Freeze header row
    ws.freeze_panes = "A2"

    # Auto-filter
    ws.auto_filter.ref = ws.dimensions

    wb.save(output_path)

create_workbook("report.xlsx",
    headers=["Name", "Department", "Score", "Grade"],
    data=[
        ["Alice", "Engineering", 95, "A"],
        ["Bob", "Marketing", 82, "B"],
        ["Carol", "Engineering", 91, "A-"],
    ])
```

---

### 4. Edit Data

```python
from openpyxl import load_workbook

def update_cell(xlsx_path: str, output_path: str, sheet: str, row: int, col: int, value) -> None:
    """Update a single cell (1-indexed row and col)."""
    wb = load_workbook(xlsx_path)
    wb[sheet].cell(row=row, column=col, value=value)
    wb.save(output_path)

def find_and_replace(xlsx_path: str, output_path: str, old_value, new_value) -> int:
    """Replace all occurrences of old_value with new_value. Returns count."""
    wb = load_workbook(xlsx_path)
    count = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value == old_value:
                    cell.value = new_value
                    count += 1
    wb.save(output_path)
    return count

def append_rows(xlsx_path: str, output_path: str, sheet_name: str, new_rows: list[list]) -> None:
    """Append rows to the end of a sheet."""
    wb = load_workbook(xlsx_path)
    ws = wb[sheet_name]
    for row in new_rows:
        ws.append(row)
    wb.save(output_path)
```

---

### 5. Formulas

```python
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter

def add_summary_row(xlsx_path: str, output_path: str, sheet_name: str, numeric_cols: list[int]) -> None:
    """Add a SUM/AVERAGE row at the bottom of numeric columns (1-indexed)."""
    wb = load_workbook(xlsx_path)
    ws = wb[sheet_name]
    last_row = ws.max_row
    data_start = 2  # assume row 1 is headers

    summary_row = last_row + 2
    ws.cell(row=summary_row, column=1, value="Summary")

    for col in numeric_cols:
        col_letter = get_column_letter(col)
        ws.cell(row=summary_row, column=col,
                value=f"=SUM({col_letter}{data_start}:{col_letter}{last_row})")
        ws.cell(row=summary_row + 1, column=col,
                value=f"=AVERAGE({col_letter}{data_start}:{col_letter}{last_row})")

    wb.save(output_path)

# Common formula patterns:
# =SUM(A2:A100)
# =AVERAGE(B2:B100)
# =COUNTIF(C2:C100,">=90")
# =VLOOKUP(A2,Sheet2!A:B,2,FALSE)
# =IF(D2>=90,"A",IF(D2>=80,"B","C"))
# =TEXT(A2,"YYYY-MM-DD")
```

---

### 6. Charts

```python
from openpyxl import load_workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

def add_bar_chart(xlsx_path: str, output_path: str, sheet_name: str,
                  title: str, data_col: int, labels_col: int, anchor: str = "E2") -> None:
    """Add a bar chart to the sheet."""
    wb = load_workbook(xlsx_path)
    ws = wb[sheet_name]

    chart = BarChart()
    chart.type = "col"
    chart.title = title
    chart.y_axis.title = "Value"
    chart.x_axis.title = "Category"

    data_ref = Reference(ws, min_col=data_col, min_row=1, max_row=ws.max_row)
    cats_ref = Reference(ws, min_col=labels_col, min_row=2, max_row=ws.max_row)

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.shape = 4
    ws.add_chart(chart, anchor)

    wb.save(output_path)

# Chart types available: BarChart, LineChart, PieChart, ScatterChart, AreaChart
```

---

### 7. Multi-Sheet Operations

```python
from openpyxl import load_workbook, Workbook

def split_by_column(xlsx_path: str, output_path: str, split_col: int) -> None:
    """Split a sheet into multiple sheets based on unique values in split_col."""
    wb = load_workbook(xlsx_path)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    rows_by_key: dict = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        key = str(row[split_col - 1])
        rows_by_key.setdefault(key, []).append(row)

    new_wb = Workbook()
    new_wb.remove(new_wb.active)

    for key, rows in rows_by_key.items():
        new_ws = new_wb.create_sheet(title=key[:31])  # sheet names max 31 chars
        new_ws.append(headers)
        for row in rows:
            new_ws.append(list(row))

    new_wb.save(output_path)

def merge_sheets(input_paths: list[str], output_path: str) -> None:
    """Merge first sheet of each workbook into a single sheet."""
    import pandas as pd
    dfs = [pd.read_excel(p) for p in input_paths]
    pd.concat(dfs, ignore_index=True).to_excel(output_path, index=False)
```

---

### 8. Conversion

#### XLSX → CSV
```python
import pandas as pd

def xlsx_to_csv(xlsx_path: str, output_path: str, sheet_name: str | int = 0) -> None:
    pd.read_excel(xlsx_path, sheet_name=sheet_name).to_csv(output_path, index=False)
```

#### CSV → XLSX
```python
import pandas as pd

def csv_to_xlsx(csv_path: str, output_path: str) -> None:
    pd.read_csv(csv_path).to_excel(output_path, index=False)
```

#### XLSX → JSON
```python
import pandas as pd, json

def xlsx_to_json(xlsx_path: str, output_path: str) -> None:
    df = pd.read_excel(xlsx_path)
    with open(output_path, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2, default=str)
```

#### XLSX → Markdown table
```python
import pandas as pd

def xlsx_to_markdown(xlsx_path: str) -> str:
    return pd.read_excel(xlsx_path).to_markdown(index=False)
```

---

## Error Handling

```python
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

try:
    wb = load_workbook("file.xlsx")
except InvalidFileException:
    print("Not a valid .xlsx file. If it's .xls, use xlrd instead.")
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Could not open workbook: {e}")
```

**Common issues:**
- `.xls` passed to `openpyxl` — use `xlrd` to read it or convert with LibreOffice first
- `data_only=True` required to read computed formula results instead of formula strings
- Very large files — use `load_workbook(path, read_only=True)` for memory efficiency
- Merged cells — access via `ws.merged_cells`; reading merged cells returns `None` for non-top-left cells

---

## Wrap Up

```
Operation: Create Workbook
Output:     report.xlsx
Sheets:     1 (Data)
Rows:       203 (including header)
Columns:    6
Charts:     1 (Bar — Score by Department)
```
