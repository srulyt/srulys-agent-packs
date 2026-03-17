#!/usr/bin/env python3
"""
generate_deck.py — Reference script for professional PowerPoint deck generation.

This is a TEMPLATE script used by the deck-builder agent as a starting point.
The agent customizes this script per deck — embedding the specific slide content,
adjusting layouts, and adding charts/tables as needed.

Design: Dark/light rhythm with accent shapes, large typography, blank layouts only.

Usage:
    python generate_deck.py [--template path/to/template.pptx] [--output path/to/output.pptx]

Dependencies:
    pip install python-pptx
"""

import sys
import os
import argparse

# --- Dependency check ---
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("python-pptx not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE


# --- Design Constants (Professional Dark/Light Theme) ---

# Primary palette
NAVY = RGBColor(0x0F, 0x1B, 0x2D)           # Deep navy — dark slide backgrounds
ACCENT_BLUE = RGBColor(0x3B, 0x82, 0xF6)    # Vivid blue — accent bars, emphasis
ACCENT_TEAL = RGBColor(0x06, 0xB6, 0xD4)    # Teal — secondary accent, subtitles
WARM_GOLD = RGBColor(0xF5, 0x9E, 0x0B)      # Gold — key metrics, callout numbers

# Neutral palette
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE = RGBColor(0xF4, 0xF5, 0xF7)      # Light background for content slides
LIGHT_GRAY = RGBColor(0xE2, 0xE4, 0xE8)     # Borders, dividers, metric labels
TEXT_DARK = RGBColor(0x1A, 0x1A, 0x2E)       # Body text on light backgrounds
TEXT_MID = RGBColor(0x6B, 0x70, 0x80)        # Captions, secondary text
TEXT_LIGHT = RGBColor(0xA0, 0xA4, 0xB0)      # Fine print on light backgrounds

# Typography scale
TITLE_SIZE_HERO = Pt(54)    # Title slide headline
TITLE_SIZE_SECTION = Pt(48) # Section headers
TITLE_SIZE = Pt(40)         # Content slide titles
SUBTITLE_SIZE = Pt(24)      # Subtitles, taglines
BODY_SIZE = Pt(22)          # Bullet points
BODY_SMALL = Pt(18)         # Secondary body text
CAPTION_SIZE = Pt(14)       # Source attributions, fine print

# Fonts
FONT_TITLE = "Calibri Light"  # Light weight for large display text
FONT_BODY = "Calibri"         # Regular weight for readability

# Layout
MARGIN = Inches(0.75)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)
CONTENT_WIDTH = Inches(11.833)


# --- Presentation Setup ---

def create_presentation(template_path=None):
    """Create a Presentation — from template or with default professional styling."""
    if template_path and os.path.exists(template_path):
        try:
            prs = Presentation(template_path)
            print(f"Loaded template: {template_path}")
            return prs, True
        except Exception as e:
            print(f"Warning: Template failed to load ({e}). Using default mode.")

    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    return prs, False


# --- Helper Functions ---

def set_notes(slide, notes_text):
    """Add speaker notes to a slide."""
    if notes_text:
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text


def set_slide_bg(slide, color):
    """Set a solid background color on a slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_top_accent_bar(slide, color=None):
    """Full-width colored bar at top of slide."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.06)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = color or ACCENT_BLUE
    bar.line.fill.background()
    return bar


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


def add_title_underline(slide, left, top, width, color=None):
    """Thin accent line below a title for separation."""
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, Inches(0.035)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = color or ACCENT_BLUE
    line.line.fill.background()
    return line


# --- Slide Functions (all use blank layout for full control) ---

def add_title_slide(prs, title, subtitle, notes=""):
    """Hero title slide — dark navy background, large white text, accent bar."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)

    # Top accent bar
    add_top_accent_bar(slide, ACCENT_BLUE)

    # Title — large, white, light weight
    tx_title = slide.shapes.add_textbox(
        Inches(1.2), Inches(2.2), Inches(10.9), Inches(1.8)
    )
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE_HERO
    p.font.bold = False
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE

    # Subtitle
    tx_sub = slide.shapes.add_textbox(
        Inches(1.2), Inches(4.2), Inches(10.9), Inches(0.8)
    )
    tf_sub = tx_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitle
    p_sub.font.size = SUBTITLE_SIZE
    p_sub.font.name = FONT_BODY
    p_sub.font.color.rgb = ACCENT_TEAL

    set_notes(slide, notes)
    return slide


def add_section_header(prs, title, subtitle="", notes=""):
    """Section divider — dark navy background, centered white text, accent line."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)

    # Centered accent line above title
    add_title_underline(slide, Inches(5.5), Inches(2.5), Inches(2.3), ACCENT_TEAL)

    # Section title
    tx_title = slide.shapes.add_textbox(
        Inches(1.5), Inches(2.8), Inches(10.3), Inches(1.5)
    )
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE_SECTION
    p.font.bold = False
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        tx_sub = slide.shapes.add_textbox(
            Inches(2.5), Inches(4.3), Inches(8.3), Inches(0.8)
        )
        p_sub = tx_sub.text_frame.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.size = SUBTITLE_SIZE
        p_sub.font.name = FONT_BODY
        p_sub.font.color.rgb = ACCENT_TEAL
        p_sub.alignment = PP_ALIGN.CENTER

    set_notes(slide, notes)
    return slide


def add_content_slide(prs, title, bullets, notes=""):
    """Content slide — off-white bg, navy left stripe, clean title."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, OFF_WHITE)

    # Left accent stripe
    add_left_accent_stripe(slide, NAVY, Inches(0.45))

    # Title
    tx_title = slide.shapes.add_textbox(
        Inches(1.1), Inches(0.5), Inches(11.5), Inches(1.0)
    )
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = NAVY

    # Bullets — whitespace separates title from body, not accent lines
    tx_body = slide.shapes.add_textbox(
        Inches(1.1), Inches(1.8), Inches(11.0), Inches(5.0)
    )
    tf_body = tx_body.text_frame
    tf_body.word_wrap = True

    for i, bullet in enumerate(bullets):
        p = tf_body.paragraphs[0] if i == 0 else tf_body.add_paragraph()
        p.text = f"\u25b8  {bullet}"
        p.font.size = BODY_SIZE
        p.font.name = FONT_BODY
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(16)

    set_notes(slide, notes)
    return slide


def add_comparison_slide(prs, title, left_header, left_points, right_header, right_points, notes=""):
    """Two-column comparison — off-white bg, navy stripe, colored column headers."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, OFF_WHITE)

    # Left accent stripe
    add_left_accent_stripe(slide, NAVY, Inches(0.45))
    add_top_accent_bar(slide, ACCENT_BLUE)

    # Title
    tx_title = slide.shapes.add_textbox(
        Inches(1.1), Inches(0.5), Inches(11.5), Inches(0.8)
    )
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.font.name = FONT_BODY

    col_width = Inches(5.3)
    col_top = Inches(1.8)

    for col_idx, (header, points) in enumerate(
        [(left_header, left_points), (right_header, right_points)]
    ):
        col_left = Inches(1.1) if col_idx == 0 else Inches(7.0)

        # Column header
        tx_h = slide.shapes.add_textbox(col_left, col_top, col_width, Inches(0.5))
        p_h = tx_h.text_frame.paragraphs[0]
        p_h.text = header
        p_h.font.size = Pt(24)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE if col_idx == 1 else NAVY
        p_h.font.name = FONT_BODY

        # Column body
        tx_b = slide.shapes.add_textbox(col_left, Inches(2.5), col_width, Inches(4.5))
        tf_b = tx_b.text_frame
        tf_b.word_wrap = True
        for i, point in enumerate(points):
            p_b = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
            p_b.text = f"\u25b8  {point}"
            p_b.font.size = Pt(20)
            p_b.font.name = FONT_BODY
            p_b.font.color.rgb = TEXT_DARK
            p_b.space_after = Pt(12)

    set_notes(slide, notes)
    return slide


def add_quote_slide(prs, quote_text, attribution, notes=""):
    """Quote slide — dark bg, large italic quote, teal attribution."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)

    # Large decorative quotation mark
    tx_mark = slide.shapes.add_textbox(
        Inches(1.0), Inches(1.2), Inches(2.0), Inches(2.0)
    )
    p_mark = tx_mark.text_frame.paragraphs[0]
    p_mark.text = "\u201C"
    p_mark.font.size = Pt(120)
    p_mark.font.name = FONT_TITLE
    p_mark.font.color.rgb = ACCENT_BLUE

    # Quote text
    tx_quote = slide.shapes.add_textbox(
        Inches(1.5), Inches(2.5), Inches(10.3), Inches(2.8)
    )
    tf = tx_quote.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = quote_text
    p.font.size = Pt(32)
    p.font.italic = True
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.LEFT

    # Attribution
    p2 = tf.add_paragraph()
    p2.text = f"\u2014 {attribution}"
    p2.font.size = Pt(18)
    p2.font.name = FONT_BODY
    p2.font.color.rgb = ACCENT_TEAL
    p2.space_before = Pt(24)

    set_notes(slide, notes)
    return slide


def add_metric_slide(prs, title, metrics, notes=""):
    """Big-number metrics slide — dark bg, gold numbers, white labels.

    metrics: list of tuples (value, label) — max 3
    Example: [("40%", "Churn Reduction"), ("$2.3M", "Pipeline Growth")]
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)
    add_top_accent_bar(slide, ACCENT_BLUE)

    # Title
    tx_title = slide.shapes.add_textbox(
        Inches(1.2), Inches(0.5), Inches(10.9), Inches(1.0)
    )
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = WHITE

    # Metrics — evenly spaced columns
    num_metrics = min(len(metrics), 3)
    if num_metrics == 0:
        set_notes(slide, notes)
        return slide

    col_width = Inches(10.9 / num_metrics)

    for i, (value, label) in enumerate(metrics[:3]):
        col_left = Inches(1.2) + col_width * i

        # Big number
        tx_val = slide.shapes.add_textbox(
            col_left, Inches(2.8), col_width, Inches(1.8)
        )
        p_val = tx_val.text_frame.paragraphs[0]
        p_val.text = value
        p_val.font.size = Pt(72)
        p_val.font.bold = True
        p_val.font.name = FONT_TITLE
        p_val.font.color.rgb = WARM_GOLD
        p_val.alignment = PP_ALIGN.CENTER

        # Label
        tx_lbl = slide.shapes.add_textbox(
            col_left, Inches(4.6), col_width, Inches(0.8)
        )
        p_lbl = tx_lbl.text_frame.paragraphs[0]
        p_lbl.text = label
        p_lbl.font.size = Pt(20)
        p_lbl.font.name = FONT_BODY
        p_lbl.font.color.rgb = LIGHT_GRAY
        p_lbl.alignment = PP_ALIGN.CENTER

    set_notes(slide, notes)
    return slide


def add_big_statement(prs, headline, subtitle="", notes="", bg_color=None):
    """Big statement slide — headline only, maximum impact, no bullets or accents.

    Use at narrative turning points, key insights, provocative claims.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, bg_color or NAVY)
    # No accent bars, no stripes — maximum restraint

    tx = slide.shapes.add_textbox(
        Inches(1.5), Inches(2.0), Inches(10.3), Inches(2.5)
    )
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = headline
    p.font.size = Pt(56)
    p.font.bold = False
    p.font.name = FONT_TITLE
    p.font.color.rgb = WHITE

    if subtitle:
        tx_sub = slide.shapes.add_textbox(
            Inches(1.5), Inches(4.8), Inches(10.3), Inches(0.8)
        )
        p_sub = tx_sub.text_frame.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.size = BODY_SMALL
        p_sub.font.name = FONT_BODY
        p_sub.font.color.rgb = ACCENT_TEAL

    set_notes(slide, notes)
    return slide


def add_split_slide(prs, title, context, points, notes=""):
    """Split layout — headline + context on left, supporting points on right.

    Use for: context + evidence, claim + proof, headline + detail.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, OFF_WHITE)
    add_left_accent_stripe(slide, NAVY, Inches(0.45))

    # Left column: headline + context
    tx_title = slide.shapes.add_textbox(
        Inches(1.1), Inches(0.8), Inches(5.0), Inches(1.5)
    )
    tf = tx_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = NAVY

    if context:
        tx_ctx = slide.shapes.add_textbox(
            Inches(1.1), Inches(2.5), Inches(5.0), Inches(3.5)
        )
        tf_ctx = tx_ctx.text_frame
        tf_ctx.word_wrap = True
        p_ctx = tf_ctx.paragraphs[0]
        p_ctx.text = context
        p_ctx.font.size = BODY_SIZE
        p_ctx.font.name = FONT_BODY
        p_ctx.font.color.rgb = TEXT_MID

    # Right column: supporting points
    tx_right = slide.shapes.add_textbox(
        Inches(6.8), Inches(0.8), Inches(5.8), Inches(5.5)
    )
    tf_r = tx_right.text_frame
    tf_r.word_wrap = True
    for i, pt in enumerate(points[:4]):
        p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        p.text = f"\u25b8  {pt}"
        p.font.size = Pt(20)
        p.font.name = FONT_BODY
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(16)

    set_notes(slide, notes)
    return slide


def add_question_slide(prs, question, notes=""):
    """Question slide — centered provocative question, no accents.

    Use before major evidence sections to create anticipation.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)
    # No accent elements — clean and focused

    tx = slide.shapes.add_textbox(
        Inches(1.5), Inches(2.5), Inches(10.3), Inches(2.5)
    )
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


def add_cta_slide(prs, title, next_steps, contact="", notes=""):
    """Closing slide — dark bg, teal step numbers, white text."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    set_slide_bg(slide, NAVY)
    add_top_accent_bar(slide, ACCENT_TEAL)

    # Title
    tx_title = slide.shapes.add_textbox(
        Inches(1.2), Inches(0.5), Inches(10.9), Inches(1.0)
    )
    p = tx_title.text_frame.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.name = FONT_BODY
    p.font.color.rgb = WHITE

    # Accent line
    add_title_underline(slide, Inches(1.2), Inches(1.55), Inches(3.0), ACCENT_TEAL)

    # Next steps
    for i, (action, detail) in enumerate(next_steps):
        y_offset = Inches(2.2 + i * 1.4)

        # Step number (large, colored)
        tx_num = slide.shapes.add_textbox(
            Inches(1.2), y_offset, Inches(0.8), Inches(0.8)
        )
        p_num = tx_num.text_frame.paragraphs[0]
        p_num.text = str(i + 1)
        p_num.font.size = Pt(40)
        p_num.font.bold = True
        p_num.font.name = FONT_TITLE
        p_num.font.color.rgb = ACCENT_TEAL

        # Action text
        tx_action = slide.shapes.add_textbox(
            Inches(2.2), y_offset, Inches(7.0), Inches(0.5)
        )
        p_action = tx_action.text_frame.paragraphs[0]
        p_action.text = action
        p_action.font.size = BODY_SIZE
        p_action.font.bold = True
        p_action.font.name = FONT_BODY
        p_action.font.color.rgb = WHITE

        # Detail
        tx_detail = slide.shapes.add_textbox(
            Inches(2.2), y_offset + Inches(0.5), Inches(7.0), Inches(0.4)
        )
        p_detail = tx_detail.text_frame.paragraphs[0]
        p_detail.text = f"\u2192 {detail}"
        p_detail.font.size = BODY_SMALL
        p_detail.font.name = FONT_BODY
        p_detail.font.color.rgb = TEXT_MID

    if contact:
        tx_contact = slide.shapes.add_textbox(
            Inches(1.2), Inches(6.5), CONTENT_WIDTH, Inches(0.5)
        )
        p_c = tx_contact.text_frame.paragraphs[0]
        p_c.text = contact
        p_c.font.size = CAPTION_SIZE
        p_c.font.color.rgb = TEXT_LIGHT
        p_c.font.name = FONT_BODY

    set_notes(slide, notes)
    return slide


# ===========================================================================
# DECK CONTENT — The deck-builder agent replaces this section per deck
# ===========================================================================

DECK_CONTENT = {
    "title": "Presentation Title",
    "subtitle": "Audience \u2014 Date",
    "slides": [
        {
            "type": "title",
            "title": "Presentation Title",
            "subtitle": "Audience \u2014 Date",
            "notes": "Welcome the audience. Set the tone for the presentation."
        },
        {
            "type": "big_statement",
            "headline": "One bold insight that changes everything",
            "subtitle": "The hook that makes the audience lean in",
            "notes": "Pause. Let the statement land. This is the opening hook."
        },
        {
            "type": "content",
            "title": "Action-Oriented Headline Goes Here",
            "bullets": [
                "First supporting point with specific evidence",
                "Second supporting point with data",
                "Third supporting point with outcome",
            ],
            "notes": "Expand on each point verbally. Transition: move to the next section."
        },
        {
            "type": "split",
            "title": "The context that frames the argument",
            "context": "This is where you provide the narrative context that makes the supporting points meaningful.",
            "points": [
                "Evidence point one with specifics",
                "Evidence point two with data",
                "Evidence point three with outcome",
            ],
            "notes": "Left side sets up the story, right side delivers the proof."
        },
        {
            "type": "question",
            "question": "What if we could solve this\nwithout adding headcount?",
            "notes": "Pause after the question. Let the audience think. Then move to the answer."
        },
        {
            "type": "metric",
            "title": "Key Results That Speak for Themselves",
            "metrics": [
                ("40%", "Churn Reduction"),
                ("$2.3M", "Pipeline Growth"),
                ("3x", "Faster Onboarding"),
            ],
            "notes": "Let the numbers land. Pause after revealing each metric."
        },
        {
            "type": "cta",
            "title": "Clear Next Steps to Drive Action",
            "next_steps": [
                ("Approve the proposed approach", "Decision by Friday"),
                ("Kick off Phase 1 implementation", "Engineering lead \u2014 Week of March 23"),
                ("Schedule follow-up review", "All stakeholders \u2014 April 15"),
            ],
            "contact": "Questions? Reach out to team@company.com",
            "notes": "Be explicit about what you need. Make the ask clear and concrete."
        },
    ],
}


def build_deck(content, template_path=None, output_path="output.pptx"):
    """Build the complete deck from content specification."""
    prs, is_template = create_presentation(template_path)

    for slide_spec in content["slides"]:
        slide_type = slide_spec["type"]
        notes = slide_spec.get("notes", "")

        if slide_type == "title":
            add_title_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("subtitle", ""),
                notes,
            )

        elif slide_type == "section":
            add_section_header(
                prs,
                slide_spec["title"],
                slide_spec.get("subtitle", ""),
                notes,
            )

        elif slide_type == "content":
            add_content_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("bullets", []),
                notes,
            )

        elif slide_type == "comparison":
            add_comparison_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("left_header", "Before"),
                slide_spec.get("left_points", []),
                slide_spec.get("right_header", "After"),
                slide_spec.get("right_points", []),
                notes,
            )

        elif slide_type == "quote":
            add_quote_slide(
                prs,
                slide_spec["quote"],
                slide_spec.get("attribution", ""),
                notes,
            )

        elif slide_type == "metric":
            add_metric_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("metrics", []),
                notes,
            )

        elif slide_type == "big_statement":
            add_big_statement(
                prs,
                slide_spec.get("headline", slide_spec.get("title", "")),
                slide_spec.get("subtitle", ""),
                notes,
                slide_spec.get("bg_color", None),
            )

        elif slide_type == "split":
            add_split_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("context", ""),
                slide_spec.get("points", slide_spec.get("bullets", [])),
                notes,
            )

        elif slide_type == "question":
            add_question_slide(
                prs,
                slide_spec.get("question", slide_spec.get("title", "")),
                notes,
            )

        elif slide_type == "cta":
            add_cta_slide(
                prs,
                slide_spec["title"],
                slide_spec.get("next_steps", []),
                slide_spec.get("contact", ""),
                notes,
            )

        else:
            # Fallback: treat unknown types as content slides
            add_content_slide(
                prs,
                slide_spec.get("title", "Untitled"),
                slide_spec.get("bullets", []),
                notes,
            )

    # Save
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    prs.save(output_path)
    slide_count = len(prs.slides)
    print(f"SUCCESS: Generated '{output_path}' with {slide_count} slides")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate a PowerPoint deck")
    parser.add_argument(
        "--template", type=str, default=None,
        help="Path to a .pptx template file for design inheritance"
    )
    parser.add_argument(
        "--output", type=str, default="output.pptx",
        help="Output file path (default: output.pptx)"
    )
    args = parser.parse_args()

    try:
        build_deck(DECK_CONTENT, template_path=args.template, output_path=args.output)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
