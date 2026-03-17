---
name: pptx-engine
description: "Technical foundation for programmatic PowerPoint generation using python-pptx. Covers API patterns, template mode vs default mode, slide layout strategy, styling, charts, tables, and error handling. Keywords: python-pptx, PowerPoint, pptx, slide, layout, chart, table, shape, font, generate."
---

# PPTX Engine

Technical reference for generating professional PowerPoint decks programmatically using the `python-pptx` library.

## When to Use This Skill

Load this skill when:
- Generating a Python script to create a .pptx file
- Working with python-pptx API for slides, shapes, charts, or tables
- Choosing between template mode and default mode
- Applying consistent styling programmatically
- Troubleshooting pptx generation errors

## Quick Start

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Create presentation (default mode)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Add a slide
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)
slide.shapes.title.text = "Action-Oriented Headline"

# Save
prs.save('output.pptx')
```

## Core API Patterns

### Presentation Object
```python
# Default mode — blank presentation
prs = Presentation()

# Template mode — load existing .pptx
prs = Presentation('template.pptx')

# Set widescreen 16:9
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
```

### Slide Layouts
The default presentation provides these built-in layouts:

| Index | Layout Name | Use For |
|-------|------------|---------|
| 0 | Title Slide | Opening slide |
| 1 | Title and Content | Most content slides |
| 2 | Section Header | Section dividers |
| 3 | Two Content | Side-by-side comparison |
| 4 | Comparison | Labeled comparison |
| 5 | Title Only | Charts, custom content |
| 6 | Blank | Fully custom slides |

```python
# List available layouts
for i, layout in enumerate(prs.slide_layouts):
    print(f"{i}: {layout.name}")

# Add a slide with specific layout
slide = prs.slides.add_slide(prs.slide_layouts[1])
```

### Text Formatting

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor

# Access text frame
tf = slide.shapes.title.text_frame
tf.clear()

# Add paragraph with formatting
p = tf.paragraphs[0]
p.text = "Headline Text"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)
p.font.name = "Calibri"

# Add additional paragraphs
p2 = tf.add_paragraph()
p2.text = "Body text"
p2.font.size = Pt(18)
p2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
```

### Adding Shapes with Position and Size

```python
from pptx.util import Inches

# Add a text box at specific position
left = Inches(0.75)
top = Inches(1.5)
width = Inches(11.833)
height = Inches(5.0)

txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame
tf.word_wrap = True
```

### Bullet Points

```python
# Add bullets to a text frame
tf = txBox.text_frame
tf.clear()

for i, bullet_text in enumerate(bullets):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = bullet_text
    p.font.size = Pt(18)
    p.font.name = "Calibri"
    p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p.level = 0
    p.space_after = Pt(12)
```

### Speaker Notes

```python
# Add speaker notes to a slide
notes_slide = slide.notes_slide
notes_tf = notes_slide.notes_text_frame
notes_tf.text = "Speaker notes for this slide. Emphasize the key metric."
```

## Template Mode vs. Default Mode

### Template Mode

When the user provides a .pptx file as a design template:

```python
prs = Presentation('user_template.pptx')

# Discover available layouts
for i, layout in enumerate(prs.slide_layouts):
    placeholders = [(ph.placeholder_format.idx, ph.name) for ph in layout.placeholders]
    print(f"Layout {i}: {layout.name} — Placeholders: {placeholders}")

# Use template's layouts and inherit all styling
slide = prs.slides.add_slide(prs.slide_layouts[0])

# Fill placeholders (they inherit template styling)
for shape in slide.placeholders:
    if shape.placeholder_format.idx == 0:  # Title
        shape.text = "My Title"
    elif shape.placeholder_format.idx == 1:  # Subtitle/Body
        shape.text = "My content"
```

**Key rules for template mode:**
- Use the template's placeholders — don't create shapes from scratch on templated layouts
- Inherit ALL styling — fonts, colors, backgrounds, logos
- If a needed layout doesn't exist in the template, use the closest match + add manual shapes

### Default Mode

When no template is provided, build professional styling from scratch:

```python
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Professional defaults — Dark/Light theme
NAVY = RGBColor(0x0F, 0x1B, 0x2D)           # Dark slide backgrounds
ACCENT_BLUE = RGBColor(0x3B, 0x82, 0xF6)    # Accent bars, emphasis
ACCENT_TEAL = RGBColor(0x06, 0xB6, 0xD4)    # Secondary accent, subtitles
WARM_GOLD = RGBColor(0xF5, 0x9E, 0x0B)      # Key metrics, callout numbers
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE = RGBColor(0xF4, 0xF5, 0xF7)      # Light slide backgrounds
TEXT_DARK = RGBColor(0x1A, 0x1A, 0x2E)       # Body text on light backgrounds
TEXT_MID = RGBColor(0x6B, 0x70, 0x80)        # Captions
LIGHT_GRAY = RGBColor(0xE2, 0xE4, 0xE8)     # Dividers, metric labels

# Typography
TITLE_SIZE_HERO = Pt(54)    # Title slide headline
TITLE_SIZE_SECTION = Pt(48) # Section headers
TITLE_SIZE = Pt(40)         # Content slide titles
SUBTITLE_SIZE = Pt(24)      # Subtitles
BODY_SIZE = Pt(22)          # Bullets
BODY_SMALL = Pt(18)         # Secondary text
CAPTION_SIZE = Pt(14)       # Fine print

FONT_TITLE = "Calibri Light"  # Light weight for large display text
FONT_BODY = "Calibri"         # Regular weight for readability
MARGIN = Inches(0.75)
```

## Background and Visual Elements

Every slide should have at least one non-text visual element. These helpers form the backbone of the design system:

### Slide Background Fill
```python
def set_slide_bg(slide, color):
    """Set a solid background color on a slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color
```

### Accent Bar (Top)
```python
def add_top_accent_bar(slide, color=None):
    """Full-width colored bar at top of slide (0.06" tall)."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.06)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = color or ACCENT_BLUE
    bar.line.fill.background()
    return bar
```

### Left Accent Stripe
```python
def add_left_accent_stripe(slide, color=None, width=Inches(0.45)):
    """Vertical color stripe on left edge — visual anchor."""
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), width, SLIDE_HEIGHT
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = color or NAVY
    stripe.line.fill.background()
    return stripe
```

### Title Underline
```python
def add_title_underline(slide, left, top, width, color=None):
    """Thin accent line below a title for visual separation."""
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, Inches(0.035)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = color or ACCENT_BLUE
    line.line.fill.background()
    return line
```

## Slide Type Implementation Patterns

**Important**: Always use `prs.slide_layouts[6]` (Blank) and build all elements manually. Default placeholder layouts (0, 1, 2) produce generic-looking output. Blank layouts give full control over positioning, backgrounds, and accent elements.

**Layout variety is critical**: Use DIFFERENT builder functions for different slide content. Do not reuse the same function for every content slide. The patterns below give you a diverse toolkit.

### Title Slide (Dark Background)
```python
def add_title_slide(prs, title, subtitle, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank — full control
    set_slide_bg(slide, NAVY)
    add_top_accent_bar(slide, ACCENT_BLUE)

    tx_title = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(1.8))
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE_HERO  # 54pt
    p.font.bold = False
    p.font.name = FONT_TITLE       # Calibri Light
    p.font.color.rgb = WHITE

    tx_sub = slide.shapes.add_textbox(Inches(1.2), Inches(4.2), Inches(10.9), Inches(0.8))
    p_sub = tx_sub.text_frame.paragraphs[0]
    p_sub.text = subtitle
    p_sub.font.size = SUBTITLE_SIZE
    p_sub.font.name = FONT_BODY
    p_sub.font.color.rgb = ACCENT_TEAL

    set_notes(slide, notes)
    return slide
```

### Content Slide — Headline + Bullets (Light Background)
```python
def add_content_slide(prs, title, bullets, notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, OFF_WHITE)
    add_left_accent_stripe(slide, NAVY, Inches(0.45))

    tx_title = slide.shapes.add_textbox(Inches(1.1), Inches(0.5), Inches(11.5), Inches(1.0))
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE  # 40pt
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = NAVY

    # Bullets — 22pt, max 4 items
    tx_body = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.5), Inches(4.5))
    tf = tx_body.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets[:4]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = bullet
        p.font.size = BODY_SIZE
        p.font.name = FONT_BODY
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(16)

    set_notes(slide, notes)
    return slide
```

### Big Statement Slide (Dark Background, Maximum Impact)
```python
def add_big_statement(prs, headline, subtitle="", notes="", bg_color=None):
    """Headline-only slide for key insights — NO bullets, NO accents, maximum restraint."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, bg_color or NAVY)
    # No accent bars, no stripes — just the statement

    tx = slide.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.3), Inches(2.5))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = headline
    p.font.size = Pt(56)
    p.font.bold = False
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE

    if subtitle:
        tx_sub = slide.shapes.add_textbox(Inches(1.5), Inches(4.8), Inches(10.3), Inches(0.8))
        p_sub = tx_sub.text_frame.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.size = BODY_SMALL
        p_sub.font.name = FONT_BODY
        p_sub.font.color.rgb = ACCENT_TEAL

    set_notes(slide, notes)
    return slide
```

### Split Layout Slide (Light Background, Two Halves)
```python
def add_split_slide(prs, title, context, points, notes=""):
    """Two-column layout: headline + context on left, supporting points on right."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, OFF_WHITE)
    add_left_accent_stripe(slide, NAVY, Inches(0.45))

    # Left column: headline + context
    tx_title = slide.shapes.add_textbox(Inches(1.1), Inches(0.8), Inches(5.0), Inches(1.5))
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = NAVY

    if context:
        tx_ctx = slide.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(3.0))
        p_ctx = tx_ctx.text_frame.paragraphs[0]
        p_ctx.text = context
        p_ctx.font.size = BODY_SIZE
        p_ctx.font.name = FONT_BODY
        p_ctx.font.color.rgb = TEXT_MID

    # Right column: supporting points
    tx_right = slide.shapes.add_textbox(Inches(6.8), Inches(0.8), Inches(5.8), Inches(5.5))
    tf_r = tx_right.text_frame
    tf_r.word_wrap = True
    for i, pt in enumerate(points[:4]):
        p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        p.text = pt
        p.font.size = Pt(20)
        p.font.name = FONT_BODY
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(16)

    set_notes(slide, notes)
    return slide
```

### Question Slide (Dark Background, Centered)
```python
def add_question_slide(prs, question, notes=""):
    """Provocative question to create tension before evidence sections."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, NAVY)
    # No accents — clean and focused

    tx = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(10.3), Inches(2.5))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = question
    p.font.size = Pt(50)
    p.font.bold = False
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    set_notes(slide, notes)
    return slide
```

### Section Header (Dark Background, Centered)
```python
def add_section_header(prs, title, subtitle="", notes=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, NAVY)
    # Title: 48pt, Calibri Light, white, centered
    # Subtitle: 24pt, Calibri, teal, centered
```

## Error Handling Patterns

### Dependency Check
```python
try:
    from pptx import Presentation
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
```

### Template Validation
```python
import os

def load_template(template_path):
    if template_path and os.path.exists(template_path):
        try:
            prs = Presentation(template_path)
            print(f"Template loaded: {template_path}")
            return prs
        except Exception as e:
            print(f"Warning: Template failed to load ({e}). Using default mode.")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs
```

### Safe Execution Wrapper
```python
def main():
    try:
        # ... generation code ...
        prs.save(output_path)
        slide_count = len(prs.slides)
        print(f"SUCCESS: Generated {output_path} with {slide_count} slides")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## References

For detailed code patterns:
- [PPTX API Patterns](references/pptx-api-patterns.md) — Tables, charts, images, master slides, advanced formatting
- [generate_deck.py](scripts/generate_deck.py) — Reference Python script for the full generation pipeline
