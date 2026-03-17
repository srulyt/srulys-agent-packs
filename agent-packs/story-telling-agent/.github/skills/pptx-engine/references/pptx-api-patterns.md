# PPTX API Patterns — Advanced Reference

Detailed code patterns for backgrounds, accent shapes, metrics, tables, charts, images, and advanced formatting with python-pptx.

## Slide Background Manipulation

### Solid Background Fill
```python
def set_slide_bg(slide, color):
    """Set a solid background color on a slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

# Usage: dark slides
set_slide_bg(slide, RGBColor(0x0F, 0x1B, 0x2D))  # Navy
# Usage: light slides
set_slide_bg(slide, RGBColor(0xF4, 0xF5, 0xF7))  # Off-white
```

### Gradient Simulation (Layered Bands)
python-pptx doesn't support true gradients. Simulate with horizontal color bands:

```python
def add_gradient_bg(slide, color_top_rgb, color_bottom_rgb, bands=6):
    """Simulate a vertical gradient using horizontal color bands.
    color_top_rgb / color_bottom_rgb: tuples of (r, g, b) ints 0-255.
    Call BEFORE adding text shapes so bands render behind content.
    """
    band_height = int(Inches(7.5) / bands)
    for i in range(bands):
        ratio = i / (bands - 1) if bands > 1 else 0
        r = int(color_top_rgb[0] * (1 - ratio) + color_bottom_rgb[0] * ratio)
        g = int(color_top_rgb[1] * (1 - ratio) + color_bottom_rgb[1] * ratio)
        b = int(color_top_rgb[2] * (1 - ratio) + color_bottom_rgb[2] * ratio)
        band = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), band_height * i, Inches(13.333), band_height + Emu(1)
        )
        band.fill.solid()
        band.fill.fore_color.rgb = RGBColor(r, g, b)
        band.line.fill.background()

# Usage: add_gradient_bg(slide, (15, 27, 45), (25, 50, 80))
```

### Two-Tone Split Background
```python
def add_split_bg(slide, top_color, bottom_color, split_ratio=0.4):
    """Two-tone horizontal split background."""
    top_height = int(Inches(7.5) * split_ratio)
    top_rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), top_height
    )
    top_rect.fill.solid()
    top_rect.fill.fore_color.rgb = top_color
    top_rect.line.fill.background()
    bottom_rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), top_height,
        Inches(13.333), Inches(7.5) - top_height
    )
    bottom_rect.fill.solid()
    bottom_rect.fill.fore_color.rgb = bottom_color
    bottom_rect.line.fill.background()
```

## Accent Shape Creation Patterns

### Full-Width Top Accent Bar
```python
def add_top_accent_bar(slide, color=None):
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), Inches(13.333), Inches(0.06)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = color or RGBColor(0x3B, 0x82, 0xF6)
    bar.line.fill.background()
    return bar
```

### Left Accent Stripe
```python
def add_left_accent_stripe(slide, color=None, width=Inches(0.45)):
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), width, Inches(7.5)
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = color or RGBColor(0x0F, 0x1B, 0x2D)
    stripe.line.fill.background()
    return stripe
```

### Title Underline Separator
```python
def add_title_underline(slide, left, top, width, color=None):
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.035)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = color or RGBColor(0x3B, 0x82, 0xF6)
    line.line.fill.background()
    return line
```

### Large Number Callout
```python
def add_number_callout(slide, number, left, top, color=None):
    tx = slide.shapes.add_textbox(left, top, Inches(2.5), Inches(1.5))
    p = tx.text_frame.paragraphs[0]
    p.text = str(number)
    p.font.size = Pt(72)
    p.font.bold = True
    p.font.name = "Calibri Light"
    p.font.color.rgb = color or RGBColor(0xF5, 0x9E, 0x0B)  # Gold
    return tx
```

## Modern Typography Application

```python
# Light weight for large display text (titles, hero slides)
p.font.name = "Calibri Light"
p.font.size = Pt(54)
p.font.bold = False  # Light weight is elegant at large sizes

# Bold weight for content titles
p.font.name = "Calibri"
p.font.size = Pt(40)
p.font.bold = True

# Regular weight for body text
p.font.name = "Calibri"
p.font.size = Pt(22)
p.font.bold = False

# White text on dark backgrounds
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# Navy text on light backgrounds
p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

# Teal for subtitles and attributions
p.font.color.rgb = RGBColor(0x06, 0xB6, 0xD4)
```

## Per-Slide-Type Code Patterns

### Key Metric / Big Number Slide (Dark Background)
```python
def add_metric_slide(prs, title, metrics, notes=""):
    """Big-number metrics slide. metrics: list of (value, label) tuples, max 3."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0x0F, 0x1B, 0x2D))
    add_top_accent_bar(slide)

    # Title: 40pt bold white
    tx_title = slide.shapes.add_textbox(Inches(1.2), Inches(0.5), Inches(10.9), Inches(1.0))
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.name = "Calibri"
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    num_metrics = min(len(metrics), 3)
    col_width = Inches(10.9 / num_metrics) if num_metrics > 0 else Inches(10.9)
    for i, (value, label) in enumerate(metrics[:3]):
        col_left = Inches(1.2) + col_width * i
        # Value: 72pt bold gold, centered
        tx_val = slide.shapes.add_textbox(col_left, Inches(2.8), col_width, Inches(1.8))
        p_val = tx_val.text_frame.paragraphs[0]
        p_val.text = value
        p_val.font.size = Pt(72)
        p_val.font.bold = True
        p_val.font.name = "Calibri Light"
        p_val.font.color.rgb = RGBColor(0xF5, 0x9E, 0x0B)
        p_val.alignment = PP_ALIGN.CENTER
        # Label: 20pt light gray, centered
        tx_lbl = slide.shapes.add_textbox(col_left, Inches(4.6), col_width, Inches(0.8))
        p_lbl = tx_lbl.text_frame.paragraphs[0]
        p_lbl.text = label
        p_lbl.font.size = Pt(20)
        p_lbl.font.name = "Calibri"
        p_lbl.font.color.rgb = RGBColor(0xE2, 0xE4, 0xE8)
        p_lbl.alignment = PP_ALIGN.CENTER

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

### Quote Slide (Dark Background, Oversized Quote Mark)
```python
def add_quote_slide(prs, quote_text, attribution, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0x0F, 0x1B, 0x2D))

    # Decorative quote mark: 120pt blue
    tx_mark = slide.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(2.0), Inches(2.0))
    p_mark = tx_mark.text_frame.paragraphs[0]
    p_mark.text = "\u201C"
    p_mark.font.size = Pt(120)
    p_mark.font.name = "Calibri Light"
    p_mark.font.color.rgb = RGBColor(0x3B, 0x82, 0xF6)

    # Quote: 32pt italic white
    tx_quote = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(10.3), Inches(2.8))
    tf = tx_quote.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = quote_text
    p.font.size = Pt(32)
    p.font.italic = True
    p.font.name = "Calibri Light"
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Attribution: 18pt teal
    p2 = tf.add_paragraph()
    p2.text = f"\u2014 {attribution}"
    p2.font.size = Pt(18)
    p2.font.name = "Calibri"
    p2.font.color.rgb = RGBColor(0x06, 0xB6, 0xD4)
    p2.space_before = Pt(24)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

### CTA / Closing Slide (Dark Background, Numbered Steps)
```python
def add_cta_slide(prs, title, next_steps, contact="", notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0x0F, 0x1B, 0x2D))
    add_top_accent_bar(slide, RGBColor(0x06, 0xB6, 0xD4))
    # Title: 40pt bold white
    # Each step: large teal number (40pt) + white action text (22pt bold) + gray detail (18pt)
    # Steps positioned vertically with 1.4" spacing
    # Contact info: 14pt light gray at bottom
```

## Table Creation

### Basic Table
```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def add_table_slide(prs, title, headers, rows, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, RGBColor(0xF4, 0xF5, 0xF7))  # Off-white
    add_left_accent_stripe(slide, RGBColor(0x0F, 0x1B, 0x2D), Inches(0.45))
    add_top_accent_bar(slide)

    # Title
    tx_title = slide.shapes.add_textbox(Inches(1.1), Inches(0.5), Inches(11.5), Inches(0.8))
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.name = "Calibri"
    p.font.color.rgb = RGBColor(0x0F, 0x1B, 0x2D)

    # Table dimensions
    num_rows = len(rows) + 1  # +1 for header
    num_cols = len(headers)
    left = Inches(1.1)
    top = Inches(1.8)
    width = Inches(11.5)
    height = Inches(0.4) * num_rows

    table = slide.shapes.add_table(num_rows, num_cols, left, top, width, height).table

    # Style header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.bold = True
            paragraph.font.size = Pt(14)
            paragraph.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            paragraph.font.name = "Calibri"
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x0F, 0x1B, 0x2D)

    # Fill data rows
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_text in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(cell_text)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(12)
                paragraph.font.name = "Calibri"
                paragraph.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

### Table Styling Tips
- Set column widths proportionally: `table.columns[0].width = Inches(3.0)`
- Alternate row shading for readability:
  ```python
  if row_idx % 2 == 0:
      cell.fill.solid()
      cell.fill.fore_color.rgb = RGBColor(0xF2, 0xF2, 0xF2)
  ```
- Minimize borders — use light gray if needed, never thick black lines

## Chart Insertion

### Bar Chart
```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

def add_bar_chart_slide(prs, title, categories, series_data, notes=""):
    """
    series_data: list of tuples (series_name, [values])
    Example: [("Q3 2025", [10, 20, 30]), ("Q4 2025", [15, 25, 35])]
    """
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
    slide.shapes.title.text = title

    chart_data = CategoryChartData()
    chart_data.categories = categories
    for series_name, values in series_data:
        chart_data.add_series(series_name, values)

    left = Inches(1.0)
    top = Inches(1.8)
    width = Inches(11.0)
    height = Inches(5.0)

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        left, top, width, height, chart_data
    ).chart

    # Style the chart
    chart.has_legend = len(series_data) > 1
    if chart.has_legend:
        chart.legend.include_in_layout = False

    # Style category axis
    category_axis = chart.category_axis
    category_axis.tick_labels.font.size = Pt(12)
    category_axis.tick_labels.font.name = "Calibri"

    # Style value axis
    value_axis = chart.value_axis
    value_axis.tick_labels.font.size = Pt(12)
    value_axis.tick_labels.font.name = "Calibri"

    if notes:
        slide.notes_slide.notes_text_frame.text = notes

    return slide
```

### Line Chart
```python
def add_line_chart_slide(prs, title, categories, series_data, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title

    chart_data = CategoryChartData()
    chart_data.categories = categories
    for series_name, values in series_data:
        chart_data.add_series(series_name, values)

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(1.0), Inches(1.8), Inches(11.0), Inches(5.0),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.include_in_layout = False

    if notes:
        slide.notes_slide.notes_text_frame.text = notes

    return slide
```

### Pie Chart
```python
from pptx.chart.data import ChartData

def add_pie_chart_slide(prs, title, categories, values, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title

    chart_data = ChartData()
    chart_data.categories = categories
    chart_data.add_series("", values)

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.PIE,
        Inches(2.5), Inches(1.8), Inches(8.0), Inches(5.0),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.include_in_layout = False
    plot = chart.plots[0]
    plot.has_data_labels = True
    data_labels = plot.data_labels
    data_labels.number_format = '0%'
    data_labels.font.size = Pt(12)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes

    return slide
```

## Image Insertion

### Adding Images
```python
def add_image_slide(prs, title, image_path, caption="", notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
    slide.shapes.title.text = title

    # Center image on slide
    img_left = Inches(1.5)
    img_top = Inches(1.8)
    img_width = Inches(10.0)
    # Height auto-calculated to maintain aspect ratio
    slide.shapes.add_picture(image_path, img_left, img_top, width=img_width)

    if caption:
        txBox = slide.shapes.add_textbox(
            Inches(1.5), Inches(6.8), Inches(10.0), Inches(0.5)
        )
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = caption
        p.font.size = Pt(10)
        p.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        p.alignment = PP_ALIGN.CENTER

    if notes:
        slide.notes_slide.notes_text_frame.text = notes

    return slide
```

## Custom Shape Creation

### Colored Rectangle Background
```python
from pptx.enum.shapes import MSO_SHAPE

def add_accent_rectangle(slide, left, top, width, height, color):
    """Generic colored rectangle — use for accent bars, stripes, overlays."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()  # No border
    return shape
```

### Quote Slide with Custom Layout (Legacy — see modern version above)
```python
def add_quote_slide_light(prs, quote_text, attribution, notes=""):
    """Light-background quote variant with left accent bar."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, RGBColor(0xF4, 0xF5, 0xF7))

    # Accent bar on left
    add_accent_rectangle(
        slide,
        Inches(0.75), Inches(2.0),
        Inches(0.08), Inches(3.5),
        RGBColor(0x3B, 0x82, 0xF6)
    )

    # Quote text: 28pt italic dark
    txBox = slide.shapes.add_textbox(
        Inches(1.25), Inches(2.0), Inches(10.5), Inches(3.0)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f'"{quote_text}"'
    p.font.size = Pt(28)
    p.font.italic = True
    p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    p.font.name = "Calibri Light"

    # Attribution: 16pt teal
    p2 = tf.add_paragraph()
    p2.text = f"\u2014 {attribution}"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(0x06, 0xB6, 0xD4)
    p2.font.name = "Calibri"
    p2.space_before = Pt(18)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

## Two-Column Comparison Slide
```python
def add_comparison_slide(prs, title, left_header, left_points, right_header, right_points, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, RGBColor(0xF4, 0xF5, 0xF7))
    add_left_accent_stripe(slide, RGBColor(0x0F, 0x1B, 0x2D), Inches(0.45))
    add_top_accent_bar(slide)

    # Title: 40pt bold navy
    txTitle = slide.shapes.add_textbox(Inches(1.1), Inches(0.5), Inches(11.5), Inches(0.8))
    p = txTitle.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x0F, 0x1B, 0x2D)
    p.font.name = "Calibri"

    add_title_underline(slide, Inches(1.1), Inches(1.4), Inches(3.0))

    col_width = Inches(5.3)
    col_top = Inches(1.8)

    for col_idx, (header, points) in enumerate([(left_header, left_points), (right_header, right_points)]):
        col_left = Inches(1.1) if col_idx == 0 else Inches(7.0)

        # Column header: 24pt bold
        txH = slide.shapes.add_textbox(col_left, col_top, col_width, Inches(0.5))
        p_h = txH.text_frame.paragraphs[0]
        p_h.text = header
        p_h.font.size = Pt(24)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(0x3B, 0x82, 0xF6) if col_idx == 1 else RGBColor(0x0F, 0x1B, 0x2D)
        p_h.font.name = "Calibri"

        # Column body: 20pt with bullet marker
        txB = slide.shapes.add_textbox(col_left, Inches(2.5), col_width, Inches(4.5))
        tf_b = txB.text_frame
        tf_b.word_wrap = True
        for i, point in enumerate(points):
            p_b = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
            p_b.text = f"\u25b8  {point}"
            p_b.font.size = Pt(20)
            p_b.font.name = "Calibri"
            p_b.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
            p_b.space_after = Pt(12)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

## Closing / CTA Slide
```python
def add_cta_slide(prs, title, next_steps, contact="", notes=""):
    """Dark background, teal step numbers, white text."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0x0F, 0x1B, 0x2D))
    add_top_accent_bar(slide, RGBColor(0x06, 0xB6, 0xD4))

    # Title: 40pt bold white
    txTitle = slide.shapes.add_textbox(Inches(1.2), Inches(0.5), Inches(10.9), Inches(1.0))
    p = txTitle.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.font.name = "Calibri"

    add_title_underline(slide, Inches(1.2), Inches(1.55), Inches(3.0), RGBColor(0x06, 0xB6, 0xD4))

    # Steps with large colored numbers
    for i, (action, detail) in enumerate(next_steps):
        y_offset = Inches(2.2 + i * 1.4)
        # Step number: 40pt bold teal
        tx_num = slide.shapes.add_textbox(Inches(1.2), y_offset, Inches(0.8), Inches(0.8))
        p_num = tx_num.text_frame.paragraphs[0]
        p_num.text = str(i + 1)
        p_num.font.size = Pt(40)
        p_num.font.bold = True
        p_num.font.name = "Calibri Light"
        p_num.font.color.rgb = RGBColor(0x06, 0xB6, 0xD4)
        # Action: 22pt bold white
        tx_action = slide.shapes.add_textbox(Inches(2.2), y_offset, Inches(7.0), Inches(0.5))
        p_action = tx_action.text_frame.paragraphs[0]
        p_action.text = action
        p_action.font.size = Pt(22)
        p_action.font.bold = True
        p_action.font.name = "Calibri"
        p_action.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        # Detail: 18pt mid gray
        tx_detail = slide.shapes.add_textbox(Inches(2.2), y_offset + Inches(0.5), Inches(7.0), Inches(0.4))
        p_detail = tx_detail.text_frame.paragraphs[0]
        p_detail.text = f"\u2192 {detail}"
        p_detail.font.size = Pt(18)
        p_detail.font.name = "Calibri"
        p_detail.font.color.rgb = RGBColor(0x6B, 0x70, 0x80)

    if contact:
        tx_contact = slide.shapes.add_textbox(Inches(1.2), Inches(6.5), Inches(11.833), Inches(0.5))
        p_c = tx_contact.text_frame.paragraphs[0]
        p_c.text = contact
        p_c.font.size = Pt(14)
        p_c.font.color.rgb = RGBColor(0xA0, 0xA4, 0xB0)
        p_c.font.name = "Calibri"

    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide
```

## Speaker Notes Best Practices

```python
def set_notes(slide, notes_text):
    """Add speaker notes to any slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = notes_text
    p.font.size = Pt(12)
    p.font.name = "Calibri"
```

Every slide should have notes containing:
1. Expanded talking points (what the presenter says beyond what's on the slide)
2. Key data points to mention verbally
3. Transition cue to the next slide

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Text overflows shape | Shape too small or text too long | Set `text_frame.word_wrap = True` and size shapes generously |
| Fonts don't render | Font not available on target system | Stick to Calibri, Arial, or Segoe UI |
| Layout index error | Template has fewer layouts than expected | Enumerate layouts first, fall back gracefully |
| Chart data mismatch | Categories and values have different lengths | Validate data before adding to chart |
| Image not found | Path is relative and incorrect | Use `os.path.abspath()` for image paths |
| Empty placeholder error | Accessing placeholder that doesn't exist | Check `len(slide.placeholders)` before accessing |
