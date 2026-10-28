#!/usr/bin/env python3
"""
SettleSense AAT PowerPoint Presentation (.pptx) Generator.
Creates a professional, faculty-ready, editable 22-slide technical presentation
matching the official B. M. S. College of Engineering LLM AAT Template.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PPTX = PROJECT_ROOT / "report" / "SettleSense_AAT_Presentation.pptx"
FIGURES_DIR = PROJECT_ROOT / "report" / "figures"

# Institutional Palette matching template
C_BLACK = RGBColor(0, 0, 0)
C_DARK_TEXT = RGBColor(15, 23, 42)       # Charcoal (#0F172A)
C_BMS_RED = RGBColor(192, 0, 0)          # BMS Red (#C00000)
C_NAVY_BLUE = RGBColor(30, 58, 138)      # Course Blue (#1E3A8A)
C_SLATE_GRAY = RGBColor(71, 85, 105)     # Subtitle Gray (#475569)
C_MUTED = RGBColor(100, 116, 139)        # Muted (#64748B)
C_LIGHT_CARD = RGBColor(248, 250, 252)   # Card Fill (#F8FAFC)
C_BORDER = RGBColor(226, 232, 240)       # Card Border (#E2E8F0)
C_GREEN = RGBColor(22, 163, 74)          # Accent Green (#16A34A)
C_LIGHT_GREEN = RGBColor(240, 253, 244)  # Light Green Fill (#F0FDF4)
C_WHITE = RGBColor(255, 255, 255)

FONT_SERIF = "Times New Roman"


def add_slide_header(slide, category_text, title_text):
    """Adds standard clean header to technical content slides."""
    # Category Tracker (Subtle Red / Slate)
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.3))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_SERIF
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = C_BMS_RED

    # Slide Title (Navy Blue, Serif)
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.733), Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_SERIF
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY_BLUE

    # Thin Divider Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BORDER
    line.line.color.rgb = C_BORDER


def add_card(slide, left, top, width, height, fill_color=C_LIGHT_CARD, border_color=C_BORDER):
    """Adds a rounded rectangle container card."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


def add_footer(slide, current_slide, total_slides=22):
    """Adds subtle academic running footer."""
    box = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.3))
    tf = box.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"BMSCE Department of Machine Learning | Course 24AM7PCLLM: NLP for LLM | Slide {current_slide} of {total_slides}"
    p.font.name = FONT_SERIF
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_MUTED


def add_bullet_item(text_frame, title_prefix, text_content, font_size=Pt(11), space_after=Pt(8)):
    """Helper to add bold lead-in bullet item with serif typography."""
    p_item = text_frame.add_paragraph()
    r1 = p_item.add_run()
    r1.text = title_prefix
    r1.bold = True
    r1.font.name = FONT_SERIF
    r1.font.size = font_size
    r1.font.color.rgb = C_DARK_TEXT

    r2 = p_item.add_run()
    r2.text = text_content
    r2.font.name = FONT_SERIF
    r2.font.size = font_size
    r2.font.color.rgb = C_DARK_TEXT
    p_item.space_after = space_after
    return p_item


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: COVER SLIDE (Exact BMSCE Template Layout)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)

    # 1. Institutional Logo
    logo_path = FIGURES_DIR / "bms_logo.jpg"
    if logo_path.exists():
        s1.shapes.add_picture(str(logo_path), Inches(6.066), Inches(0.35), width=Inches(1.2))

    # 2. Institutional Heading Text
    head_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.333), Inches(1.7))
    tf_h = head_box.text_frame
    tf_h.word_wrap = True
    tf_h.margin_left = tf_h.margin_right = tf_h.margin_top = tf_h.margin_bottom = 0

    p1 = tf_h.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    p1.text = "B.M.S. COLLEGE OF ENGINEERING"
    p1.font.name = FONT_SERIF
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = C_BLACK

    p2 = tf_h.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "(Autonomous Institute, Affiliated to VTU, Belagavi)"
    p2.font.name = FONT_SERIF
    p2.font.size = Pt(13)
    p2.font.italic = True
    p2.font.color.rgb = C_BLACK

    p3 = tf_h.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = "DEPARTMENT OF MACHINE LEARNING"
    p3.font.name = FONT_SERIF
    p3.font.size = Pt(19)
    p3.font.bold = True
    p3.font.color.rgb = C_BMS_RED

    p4 = tf_h.add_paragraph()
    p4.alignment = PP_ALIGN.CENTER
    p4.text = "(UG Program: B.E. in Artificial Intelligence and Machine Learning)"
    p4.font.name = FONT_SERIF
    p4.font.size = Pt(12.5)
    p4.font.color.rgb = C_BMS_RED

    # 3. Course Details
    course_box = s1.shapes.add_textbox(Inches(1.0), Inches(3.25), Inches(11.333), Inches(0.9))
    tf_c = course_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0

    p_c1 = tf_c.paragraphs[0]
    p_c1.alignment = PP_ALIGN.CENTER
    p_c1.text = "Course : Natural Language Processing for LLM"
    p_c1.font.name = FONT_SERIF
    p_c1.font.size = Pt(17)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_NAVY_BLUE

    p_c2 = tf_c.add_paragraph()
    p_c2.alignment = PP_ALIGN.CENTER
    p_c2.text = "Course Code: 24AM7PCLLM"
    p_c2.font.name = FONT_SERIF
    p_c2.font.size = Pt(17)
    p_c2.font.bold = True
    p_c2.font.color.rgb = C_NAVY_BLUE

    # 4. TOPIC
    topic_box = s1.shapes.add_textbox(Inches(1.0), Inches(4.15), Inches(11.333), Inches(1.3))
    tf_top = topic_box.text_frame
    tf_top.word_wrap = True
    tf_top.margin_left = tf_top.margin_right = tf_top.margin_top = tf_top.margin_bottom = 0

    p_t1 = tf_top.paragraphs[0]
    p_t1.alignment = PP_ALIGN.CENTER
    p_t1.text = "TOPIC"
    p_t1.font.name = FONT_SERIF
    p_t1.font.size = Pt(21)
    p_t1.font.bold = True
    p_t1.font.color.rgb = C_BMS_RED

    p_t2 = tf_top.add_paragraph()
    p_t2.alignment = PP_ALIGN.CENTER
    p_t2.text = "SettleSense: An Offline LLM-Based Securities Settlement Exception Investigation Copilot"
    p_t2.font.name = FONT_SERIF
    p_t2.font.size = Pt(14)
    p_t2.font.bold = True
    p_t2.font.color.rgb = C_NAVY_BLUE

    p_t3 = tf_top.add_paragraph()
    p_t3.alignment = PP_ALIGN.CENTER
    p_t3.text = "Alternative Assessment Tool (AAT)"
    p_t3.font.name = FONT_SERIF
    p_t3.font.size = Pt(13)
    p_t3.font.color.rgb = RGBColor(75, 44, 130)

    # 5. Bottom Left Presenters
    pres_box = s1.shapes.add_textbox(Inches(0.8), Inches(5.65), Inches(5.0), Inches(1.5))
    tf_p = pres_box.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0

    p_p1 = tf_p.paragraphs[0]
    p_p1.text = "Presented By,"
    p_p1.font.name = FONT_SERIF
    p_p1.font.size = Pt(12)
    p_p1.font.bold = True
    p_p1.font.color.rgb = C_BLACK

    p_p2 = tf_p.add_paragraph()
    p_p2.text = "Student Name & USN : [Student 1 Name & USN]"
    p_p2.font.name = FONT_SERIF
    p_p2.font.size = Pt(10.5)
    p_p2.font.color.rgb = C_BLACK

    p_p3 = tf_p.add_paragraph()
    p_p3.text = "Student Name & USN : [Student 2 Name & USN]"
    p_p3.font.name = FONT_SERIF
    p_p3.font.size = Pt(10.5)
    p_p3.font.color.rgb = C_BLACK

    p_p4 = tf_p.add_paragraph()
    p_p4.text = "Semester & Section: 7B"
    p_p4.font.name = FONT_SERIF
    p_p4.font.size = Pt(10.5)
    p_p4.font.color.rgb = C_BLACK

    p_p5 = tf_p.add_paragraph()
    p_p5.text = "Date: October 2026"
    p_p5.font.name = FONT_SERIF
    p_p5.font.size = Pt(10.5)
    p_p5.font.color.rgb = C_BLACK

    # 6. Bottom Right Faculty
    fac_box = s1.shapes.add_textbox(Inches(8.5), Inches(5.65), Inches(4.0), Inches(1.5))
    tf_f = fac_box.text_frame
    tf_f.word_wrap = True
    tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = tf_f.margin_bottom = 0

    p_f1 = tf_f.paragraphs[0]
    p_f1.text = "Faculty In-Charge:"
    p_f1.font.name = FONT_SERIF
    p_f1.font.size = Pt(11)
    p_f1.font.color.rgb = C_BLACK

    p_f2 = tf_f.add_paragraph()
    p_f2.text = "Dr. Monika Puttaramaiah"
    p_f2.font.name = FONT_SERIF
    p_f2.font.size = Pt(12.5)
    p_f2.font.bold = True
    p_f2.font.color.rgb = C_BLACK

    p_f3 = tf_f.add_paragraph()
    p_f3.text = "Associate Professor\nDepartment of Machine Learning\nBMS College of Engineering"
    p_f3.font.name = FONT_SERIF
    p_f3.font.size = Pt(10.5)
    p_f3.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 2: AGENDA (Exact BMSCE Template Layout)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)

    # Title: Agenda (Red, centered, serif)
    ag_title = s2.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.333), Inches(0.8))
    tf_at = ag_title.text_frame
    tf_at.word_wrap = True
    p_at = tf_at.paragraphs[0]
    p_at.alignment = PP_ALIGN.CENTER
    p_at.text = "Agenda"
    p_at.font.name = FONT_SERIF
    p_at.font.size = Pt(36)
    p_at.font.color.rgb = C_BMS_RED

    # Two column styled cards for the 10 points
    agenda_items_col1 = [
        "1. Introduction",
        "2. Selected NLP Topic Overview",
        "3. Real-Time Application / API Identified",
        "4. NLP Model / Architecture Study",
        "5. Dataset and Preprocessing"
    ]
    agenda_items_col2 = [
        "6. Implementation Methodology",
        "7. Results and Evaluation",
        "8. Discussion",
        "9. Conclusion",
        "10. References"
    ]

    add_card(s2, 1.8, 1.7, 4.6, 4.6)
    box_c1 = s2.shapes.add_textbox(Inches(2.1), Inches(1.9), Inches(4.0), Inches(4.2))
    tf_c1 = box_c1.text_frame
    tf_c1.word_wrap = True
    for i, item in enumerate(agenda_items_col1):
        p = tf_c1.paragraphs[0] if i == 0 else tf_c1.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = FONT_SERIF
        p.font.size = Pt(17)
        p.font.color.rgb = C_DARK_TEXT
        p.space_after = Pt(22)

    add_card(s2, 6.9, 1.7, 4.6, 4.6)
    box_c2 = s2.shapes.add_textbox(Inches(7.2), Inches(1.9), Inches(4.0), Inches(4.2))
    tf_c2 = box_c2.text_frame
    tf_c2.word_wrap = True
    for i, item in enumerate(agenda_items_col2):
        p = tf_c2.paragraphs[0] if i == 0 else tf_c2.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = FONT_SERIF
        p.font.size = Pt(17)
        p.font.color.rgb = C_DARK_TEXT
        p.space_after = Pt(22)

    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: 1. INTRODUCTION — OPERATIONAL CONTEXT & THE SETTLEMENT PROBLEM
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "1. Introduction", "Securities Settlement Exceptions in Institutional Capital Markets")

    # 3 Horizontal Cards
    cards_s3 = [
        ("Post-Trade Settlement DvP",
         "Securities settlement represents the irrevocable Delivery-versus-Payment (DvP) transfer of ownership against cash between institutional counterparties at Central Securities Depositories (CSDs like DTCC, Euroclear, Clearstream).\n\nWhen trade details, instructions, or inventory diverge, transactions fail to settle on contractual dates."),
        ("Accelerated T+1 & CSDR Mandates",
         "Under accelerated T+1 settlement cycles and European CSDR discipline regimes, fails incur immediate monetary penalties, mandatory buy-ins, and collateral strain.\n\nOperations desks must triage, investigate, and remediate settlement exceptions within narrow intraday cutoffs."),
        ("The Unstructured Narrative Bottleneck",
         "Exception feeds arrive as unstructured, cryptic text narratives (SWIFT MT548 status codes, custodian telemetry, depot remarks).\n\nManual investigation across complex Standard Operating Procedures (SOPs) is slow, repetitive, and error-prone during high-volume market events.")
    ]
    for i, (head, body) in enumerate(cards_s3):
        x = 0.8 + i * 4.0
        add_card(s3, x, 1.6, 3.733, 5.1)
        tb = s3.shapes.add_textbox(Inches(x + 0.25), Inches(1.85), Inches(3.233), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = FONT_SERIF
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY_BLUE
        p_h.space_after = Pt(14)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_SERIF
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = C_DARK_TEXT
        p_b.line_spacing = 1.25

    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: 1. INTRODUCTION — STUDY OBJECTIVES & ARCHITECTURAL SCOPE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "1. Introduction", "SettleSense Project Scope & Core Technical Objectives")

    # Left Column: Objectives
    add_card(s4, 0.8, 1.6, 5.7, 5.1)
    tb_obj = s4.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_obj = tb_obj.text_frame
    tf_obj.word_wrap = True
    p = tf_obj.paragraphs[0]
    p.text = "Key Research & Technical Objectives"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    objectives = [
        ("Synthetic Dataset Synthesis:", "240 records across 48 scenario families and 6 failure classes with zero template leakage."),
        ("Fast Triage Classifier (1.2 ms):", "Class-balanced TF-IDF + Logistic Regression baseline for instant screening."),
        ("Dual-Mode Procedure Retrieval:", "Lexical TF-IDF vs. Dense 768-dim Semantic Search (ChromaDB + Nomic Embed)."),
        ("Local Offline RAG Integration:", "Local Qwen3:4B via Ollama with strict Pydantic JSON schema output enforcement."),
        ("Safety & Uncertainty Guardrails:", "Mandatory human review flags triggered on low confidence (<0.60) or ambiguity.")
    ]
    for b_title, b_desc in objectives:
        add_bullet_item(tf_obj, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right Column: Scope & Operational Boundaries
    add_card(s4, 6.833, 1.6, 5.7, 5.1)
    tb_scp = s4.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_scp = tb_scp.text_frame
    tf_scp.word_wrap = True
    p_s = tf_scp.paragraphs[0]
    p_s.text = "Operational Scope & Boundary Principles"
    p_s.font.name = FONT_SERIF
    p_s.font.size = Pt(15)
    p_s.font.bold = True
    p_s.font.color.rgb = C_NAVY_BLUE
    p_s.space_after = Pt(10)

    scope_points = [
        ("100% Offline & Data Sovereign:", "Zero public cloud APIs; all weights and vectors execute locally, ensuring compliance with banking privacy regulations."),
        ("Advisory Decision Support:", "Outputs represent investigative hypotheses and verification checklists; human analysts retain final settlement authorization."),
        ("Evidence-Grounded Citations:", "Every recommended remediation check must map directly to an authorized standard operating procedure (SOP)."),
        ("Honest Evaluation Denominators:", "Explicitly distinguishes population-wide retrieval evaluations (N=210) from generative pilot studies (N=6).")
    ]
    for b_title, b_desc in scope_points:
        add_bullet_item(tf_scp, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: 2. SELECTED NLP TOPIC OVERVIEW — HYBRID TECHNICAL PARADIGM
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "2. Selected NLP Topic Overview", "Hybrid NLP Paradigm: Integrating Classification, Retrieval & RAG")

    pillars = [
        ("1. Multi-Class Classification", "Supervised Statistical Triage",
         "Assigns narratives into 6 canonical failure classes:\n• SSI_MISMATCH\n• TRADE_DETAIL_MISMATCH\n• SECURITIES_SHORTFALL\n• CASH_SHORTFALL\n• COUNTERPARTY_UNCONFIRMED\n• SETTLEMENT_TIMING\n\nExecutes in 1.2 ms to establish priority queues."),
        ("2. Dense Semantic Search", "Non-Parametric Knowledge Retrieval",
         "Encodes operational SOPs into 768-dimensional dense vectors via nomic-embed-text.\n\nOvercomes keyword mismatch by capturing semantic equivalence across depositories (Hit@3: 97.62% vs 92.38% lexical)."),
        ("3. Retrieval-Augmented Generation", "Grounded Generative Reasoning",
         "Contextualizes local Qwen3:4B on top-3 retrieved procedural passages.\n\nDecouples parametric language generation from knowledge storage, constraining the LLM to verified operational facts."),
        ("4. Structured JSON Decoding", "Deterministic Output Validation",
         "Enforces strict Pydantic schemas (case summary, root causes, checks, missing info).\n\nEliminates free-form hallucination drift and cross-references citations against known SOP whitelists.")
    ]
    for i, (title, sub, body) in enumerate(pillars):
        x = 0.8 + i * 2.983
        add_card(s5, x, 1.6, 2.783, 5.1)
        tb = s5.shapes.add_textbox(Inches(x + 0.2), Inches(1.8), Inches(2.383), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_SERIF
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_BLUE

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_SERIF
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_BMS_RED
        p2.space_after = Pt(10)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = FONT_SERIF
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = C_DARK_TEXT
        p3.line_spacing = 1.2

    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: 2. SELECTED NLP TOPIC OVERVIEW — USE CASES & DOMAIN CHALLENGES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "2. Selected NLP Topic Overview", "Financial Operations Use Cases & Domain-Specific NLP Challenges")

    # Left: Use Cases
    add_card(s6, 0.8, 1.6, 5.7, 5.1)
    tb_u = s6.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_u = tb_u.text_frame
    tf_u.word_wrap = True
    p = tf_u.paragraphs[0]
    p.text = "Institutional Financial Operations Use Cases"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    use_cases = [
        ("High-Volume Intraday Queue Triage:", "Operations desks processing thousands of alerts use instant classification to isolate high-risk settlement fails before CSD cutoffs."),
        ("Depository Realignment & Cross-CSD Routing:", "Surfaces exact procedures for inter-CSD transfers between Clearstream Frankfurt, Euroclear Bank, and DTCC."),
        ("Standardized Audit Note Generation:", "Synthesizes structured notes separating observed facts from working hypotheses, expediting communication between trading desks and custodians."),
        ("CSDR Penalty & Buy-In Mitigation:", "Rapid identification of missing counterparty settlement parameters enables re-instruction prior to daily fine cutoffs.")
    ]
    for b_title, b_desc in use_cases:
        add_bullet_item(tf_u, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right: Domain Challenges
    add_card(s6, 6.833, 1.6, 5.7, 5.1)
    tb_c = s6.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = "Financial NLP Complexities & Challenges"
    p_c.font.name = FONT_SERIF
    p_c.font.size = Pt(15)
    p_c.font.bold = True
    p_c.font.color.rgb = C_NAVY_BLUE
    p_c.space_after = Pt(10)

    challenges = [
        ("Entity Overlap Across Disparate Classes:", "Identical bank BICs, ISINs, and depot account references appear across SSI mismatches and physical shortfalls, requiring relational understanding."),
        ("Extreme Cost of Procedural Hallucination:", "Fabricating an unverified settlement procedure or incorrect clearing instruction can misdirect funds or incur punitive fines."),
        ("Latency Asymmetry (1.2 ms vs 6.98 s):", "Linear classifiers evaluate in milliseconds, while LLMs require seconds, demanding a decoupled dual-engine architecture."),
        ("Out-of-Distribution Ambiguity:", "Truncated or conflicting narratives must not be assigned false certainty; systems must detect epistemic doubt and escalate.")
    ]
    for b_title, b_desc in challenges:
        add_bullet_item(tf_c, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: 3. REAL-TIME APPLICATION / API — SETTLESENSE & LOCAL OLLAMA RUNTIME
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, "3. Real-Time Application / API Identified", "SettleSense Copilot & Local Ollama Runtime Integration")

    # Left Card: SettleSense Application
    add_card(s7, 0.8, 1.6, 5.7, 5.1)
    tb_app = s7.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_app = tb_app.text_frame
    tf_app.word_wrap = True
    p = tf_app.paragraphs[0]
    p.text = "SettleSense Analyst Copilot (Streamlit)"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    app_features = [
        ("Multi-Tab Operations Dashboard:", "Tab 1 (Interactive Investigation), Tab 2 (Procedure Knowledge Base), Tab 3 (Benchmarks & Metrics)."),
        ("Dual-Engine Analysis View:", "Renders instant classifier probability distribution alongside the grounded RAG report and latency stats."),
        ("Knowledge Base Browser:", "Full-text explorer for 14 operational procedure documents with search metadata tags."),
        ("Audit & Validation Inspector:", "Displays citation validation badges, automated evidence pass rates, and raw JSON telemetry."),
        ("WCAG AA Accessibility:", "Enforces >10:1 contrast ratios for mandatory human review alerts across light and dark themes.")
    ]
    for b_title, b_desc in app_features:
        add_bullet_item(tf_app, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right Card: Local Ollama Runtime API
    add_card(s7, 6.833, 1.6, 5.7, 5.1)
    tb_api = s7.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_api = tb_api.text_frame
    tf_api.word_wrap = True
    p_a = tf_api.paragraphs[0]
    p_a.text = "Local Ollama Model Execution API"
    p_a.font.name = FONT_SERIF
    p_a.font.size = Pt(15)
    p_a.font.bold = True
    p_a.font.color.rgb = C_NAVY_BLUE
    p_a.space_after = Pt(10)

    api_specs = [
        ("Local REST Endpoint:", "Communicates via http://localhost:11434 with zero outbound internet network traffic."),
        ("Dense Embedding Service:", "Serves nomic-embed-text generating 768-dimensional normalized document vectors in 18.5 ms."),
        ("Quantized LLM Engine:", "Executes qwen3:4b (4-bit quantization, 16GB RAM compatible) generating structured JSON in ~6.75 s."),
        ("Thinking Token Suppression:", "Passes think=False and uses regex sanitizers to eliminate chain-of-thought tokens from JSON payloads."),
        ("Clean Resource Reclamation:", "Hard 120s timeout terminates HTTP sessions to prevent orphaned background threads.")
    ]
    for b_title, b_desc in api_specs:
        add_bullet_item(tf_api, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: 3. REAL-TIME APPLICATION / API — CASE WALKTHROUGH
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, "3. Real-Time Application / API Identified", "Empirical Ticket Walkthrough: Case SS-0006 (SSI Mismatch)")

    # Left: Case Input
    add_card(s8, 0.8, 1.6, 5.7, 5.1)
    tb_in = s8.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_in = tb_in.text_frame
    tf_in.word_wrap = True
    p = tf_in.paragraphs[0]
    p.text = "Incoming Settlement Exception Parameters"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    in_items = [
        ("Case Identifier:", "SS-0006 (Scenario Family: FAM_SSI_02)"),
        ("Trade Instrument:", "EQUITY_CASH_BUY | ISIN: US0378331005"),
        ("CSD Status Code:", "PENDING_SETTLEMENT / DEP_ACC_MISMATCH"),
        ("Raw Exception Narrative:", "\"Counterparty instructed safekeeping account 88219 at Euroclear Bank, whereas internal trade confirmation specifies depository account 10492. Custodian clearing telemetry indicates instruction mismatch on account reference.\""),
        ("Approach A Classifier Prior:", "SSI_MISMATCH (Confidence: 89.4% | Latency: 1.2 ms)"),
        ("ChromaDB Retrieved SOPs:", "PROC_01 (SSI Verification), PROC_02 (Safekeeping Account Resolution), PROC_03 (Custodian Clearing Ref)")
    ]
    for b_title, b_desc in in_items:
        add_bullet_item(tf_in, f"• {b_title} ", b_desc, Pt(10.5), Pt(6))

    # Right: Validated Output
    add_card(s8, 6.833, 1.6, 5.7, 5.1)
    tb_out = s8.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_out = tb_out.text_frame
    tf_out.word_wrap = True
    p_o = tf_out.paragraphs[0]
    p_o.text = "Validated RAG Investigation Output (Approach D)"
    p_o.font.name = FONT_SERIF
    p_o.font.size = Pt(15)
    p_o.font.bold = True
    p_o.font.color.rgb = C_NAVY_BLUE
    p_o.space_after = Pt(10)

    out_items = [
        ("Candidate Category:", "SSI_MISMATCH (Confidence: HIGH | Latency: 6.39 s)"),
        ("Supporting Evidence (Facts):", "• Counterparty instructed safekeeping account 88219 at Euroclear Bank\n• Internal trade confirmation specifies account 10492\n• Custodian telemetry confirms reference mismatch"),
        ("Possible Root Causes:", "• Counterparty applied superseded Standing Settlement Instructions\n• Trade capture defaulted to wrong depository sub-account"),
        ("Recommended Checks:", "• Cross-reference Omgeo/Alert SSI master record\n• Verify Euroclear 10492 vs 88219 signing mandate\n• Request counterparty re-instruction"),
        ("Missing Information:", "• Validated current SSI documentation from counterparty operations"),
        ("Citations & Safety Flags:", "Cited: PROC_01, PROC_02, PROC_03 (Validity: 100%)\nrequires_human_review: False (Standard Review)")
    ]
    for b_title, b_desc in out_items:
        add_bullet_item(tf_out, f"• {b_title} ", b_desc, Pt(10.5), Pt(6))

    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: 4. NLP MODEL / ARCHITECTURE STUDY — END-TO-END DESIGN
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, "4. NLP Model / Architecture Study", "End-to-End System Architecture & Information Flow")

    # Embed Architecture Figure (High-res, large)
    arch_path = FIGURES_DIR / "architecture.png"
    if arch_path.exists():
        s9.shapes.add_picture(str(arch_path), Inches(0.8), Inches(1.5), width=Inches(11.733))

    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: 4. NLP MODEL / ARCHITECTURE STUDY — MATHEMATICAL FORMULATION
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, "4. NLP Model / Architecture Study", "Mathematical Formulation: Feature Spaces, Loss Functions & IR Metrics")

    # 4 Cards for Formulas
    math_cards = [
        ("1. Sublinear TF-IDF Vectorization",
         "Dampens term frequency burstiness while penalizing non-discriminative corpus terms:\n\n"
         "TF-IDF(t, d) = (1 + ln TF(t, d)) × ln((1 + |D|) / (1 + |{d : t ∈ d}|) + 1)\n\n"
         "Extracts up to 5,000 unigram/bigram features over normalized narrative strings."),
        ("2. Cosine Metric & ChromaDB Distance",
         "Normalized inner product measuring scale-invariant orientation in embedding space:\n\n"
         "sim(q, d) = (q · d) / (||q||₂ ||d||₂)\n"
         "D_cosine(q, d) = 1 - sim(q, d)\n\n"
         "Operates over 768-dimensional L2-normalized continuous dense vectors."),
        ("3. Regularized Multi-Class Softmax",
         "Softmax probability with class-balancing weights α_k and L2 regularization C:\n\n"
         "P(Y = k | x) = exp(w_kᵀ x + b_k) / ∑ exp(w_jᵀ x + b_j)\n"
         "L(W) = -∑ α_k y_{i,k} ln P_k + (1 / 2C) ∑ ||w_k||₂²\n\n"
         "Balances optimization across all 6 canonical operational failure classes."),
        ("4. Rank-Aware Information Retrieval",
         "Evaluates retrieval quality across 210 labelled operational cases:\n\n"
         "Hit@K = (1/|Q|) ∑ I(|D̂_K ∩ R_q| > 0)\n"
         "Recall@K = (1/|Q|) ∑ (|D̂_K ∩ R_q| / |R_q|)\n"
         "MRR = (1/|Q|) ∑ (1 / rank₁)\n\n"
         "Dense semantic retrieval achieves Hit@3: 97.62% and MRR: 0.8905.")
    ]
    for i, (head, body) in enumerate(math_cards):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 6.0
        y = 1.6 + row * 2.65
        add_card(s10, x, y, 5.733, 2.45)
        tb = s10.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.2), Inches(5.233), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = FONT_SERIF
        p_h.font.size = Pt(13.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY_BLUE
        p_h.space_after = Pt(6)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_SERIF
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = C_DARK_TEXT
        p_b.line_spacing = 1.2

    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: 5. DATASET & PREPROCESSING — SYNTHETIC DATASET & DISTRIBUTION
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(s11, "5. Dataset and Preprocessing", "240-Case Synthetic Settlement Exception Dataset Architecture")

    # Left: Embed Class Distribution Chart
    dist_path = FIGURES_DIR / "class_distribution.png"
    if dist_path.exists():
        s11.shapes.add_picture(str(dist_path), Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Right: Dataset Details
    add_card(s11, 7.3, 1.6, 5.233, 5.1)
    tb_ds = s11.shapes.add_textbox(Inches(7.55), Inches(1.85), Inches(4.733), Inches(4.6))
    tf_ds = tb_ds.text_frame
    tf_ds.word_wrap = True
    p = tf_ds.paragraphs[0]
    p.text = "Dataset Composition & Schema Design"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    ds_items = [
        ("Total Population Size:", "240 structured settlement exception records across 48 scenario families (5 variations per family)."),
        ("6 Informative Supervised Classes (N=210):", "Exactly 35 cases per canonical class:\n• SSI_MISMATCH (35)\n• TRADE_DETAIL_MISMATCH (35)\n• SECURITIES_SHORTFALL (35)\n• CASH_SHORTFALL (35)\n• COUNTERPARTY_UNCONFIRMED (35)\n• SETTLEMENT_TIMING (35)"),
        ("1 Out-of-Distribution Ambiguous Class (N=30):", "30 records labelled UNDETERMINED. Fragmentary or contradictory tickets used exclusively for uncertainty guardrails."),
        ("Metadata Attributes Preserved:", "case_id, scenario_family_id, trade_type, expected_category, transaction_status, exception_code, relevant_procedure_ids.")
    ]
    for b_title, b_desc in ds_items:
        add_bullet_item(tf_ds, f"• {b_title} ", b_desc, Pt(10.5), Pt(6))

    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: 5. DATASET & PREPROCESSING — LEAKAGE PREVENTION & SPLITTING
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_header(s12, "5. Dataset and Preprocessing", "Leakage Prevention via GroupShuffleSplit & Domain Tokenization")

    # Left: Group-Aware Split
    add_card(s12, 0.8, 1.6, 5.7, 5.1)
    tb_sp = s12.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_sp = tb_sp.text_frame
    tf_sp.word_wrap = True
    p = tf_sp.paragraphs[0]
    p.text = "Group-Aware Split Strategy"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    split_items = [
        ("Group Partitioning Algorithm:", "GroupShuffleSplit(n_splits=1, test_size=0.26, random_state=42) grouped on scenario_family_id."),
        ("Training Partition:", "155 cases across 31 distinct scenario families (exactly 5 variations each, 73.8% of informative data)."),
        ("Held-out Test Partition:", "55 cases across 11 distinct scenario families (exactly 5 variations each, 26.2% of informative data)."),
        ("Zero Cross-Template Leakage:", "Train Families ∩ Test Families = ∅. Eliminates synthetic template memorization, yielding genuine generalization benchmarks."),
        ("Strict Vocabulary Isolation:", "TF-IDF vocabulary is fit solely on the 155 training cases; test cases are vectorized using frozen parameters.")
    ]
    for b_title, b_desc in split_items:
        add_bullet_item(tf_sp, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right: Preprocessing
    add_card(s12, 6.833, 1.6, 5.7, 5.1)
    tb_pr = s12.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_pr = tb_pr.text_frame
    tf_pr.word_wrap = True
    p_p = tf_pr.paragraphs[0]
    p_p.text = "Domain-Specific NLP Preprocessing"
    p_p.font.name = FONT_SERIF
    p_p.font.size = Pt(15)
    p_p.font.bold = True
    p_p.font.color.rgb = C_NAVY_BLUE
    p_p.space_after = Pt(10)

    prep_items = [
        ("Financial Identifier Preservation:", "Custom regex tokenization preserves composite tokens including 12-char ISINs (XS434618074), SWIFT BICs, and trade tickets."),
        ("Selective Stop Word Retention:", "Preserves critical financial prepositions (against, before, after, under, between) that alter settlement obligations."),
        ("No Destructive Stemming:", "Avoids stemmers/lemmatizers that conflate settlement states (e.g. settling vs. settled represent fundamentally different lifecycle stages)."),
        ("Passage Chunking & Metadata:", "14 SOPs chunked into 42 coherent passages retaining section types (trigger_indicators, verification_steps, missing_info).")
    ]
    for b_title, b_desc in prep_items:
        add_bullet_item(tf_pr, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s12, 12)

    # =========================================================================
    # SLIDE 13: 6. IMPLEMENTATION METHODOLOGY — LOCAL STACK & DUAL ENGINES
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_header(s13, "6. Implementation Methodology", "Modular Implementation: Dual-Engine Triage & Grounded Generation")

    pillars_s13 = [
        ("Engine 1: Supervised Classifier", "Approach A (TF-IDF + Logistic Regression)",
         "• Features: 5,000 max unigram/bigram features with sublinear TF scaling.\n• Model: Multi-class Logistic Regression (L2 penalty, C=1.0, class_weight='balanced').\n• Execution Speed: 1.2 ms.\n• Purpose: Real-time high-throughput screening establishing a candidate prior for every ticket."),
        ("Engine 2: Dense Semantic Search", "Vector Retrieval (ChromaDB + Nomic)",
         "• Embedder: nomic-embed-text (768 dimensions, L2-normalized vectors).\n• Storage: Persistent local ChromaDB collection.\n• Top-K: Retrieves top-3 deduplicated procedure passages in 18.5 ms.\n• Purpose: Contextual procedural grounding across operational depositories."),
        ("Engine 3: Grounded RAG Pipeline", "Generative Reasoning (Ollama + Qwen3)",
         "• Model: qwen3:4b (4-bit quantization, think=False, temperature=0.0).\n• Prompting: Assembles ticket facts + top-3 retrieved passages + strict Pydantic JSON schema.\n• Execution Speed: ~6.75 s.\n• Purpose: In-depth investigative synthesis, root causes, and verification steps.")
    ]
    for i, (title, sub, body) in enumerate(pillars_s13):
        x = 0.8 + i * 4.0
        add_card(s13, x, 1.6, 3.733, 5.1)
        tb = s13.shapes.add_textbox(Inches(x + 0.25), Inches(1.8), Inches(3.233), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_SERIF
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_BLUE

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_SERIF
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_BMS_RED
        p2.space_after = Pt(10)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = FONT_SERIF
        p3.font.size = Pt(11)
        p3.font.color.rgb = C_DARK_TEXT
        p3.line_spacing = 1.25

    add_footer(s13, 13)

    # =========================================================================
    # SLIDE 14: 6. IMPLEMENTATION METHODOLOGY — VALIDATION & SAFETY GUARDRAILS
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_header(s14, "6. Implementation Methodology", "Deterministic Output Validation & Multi-Tier Safety Guardrails")

    # Left: Output Validation
    add_card(s14, 0.8, 1.6, 5.7, 5.1)
    tb_val = s14.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_val = tb_val.text_frame
    tf_val.word_wrap = True
    p = tf_val.paragraphs[0]
    p.text = "Pydantic Schema Validation Engine"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    val_points = [
        ("Structural JSON Enforcement:", "Validates all fields against SettlementInvestigationReport; rejects non-conforming responses."),
        ("Citation Whitelisting:", "Cross-references cited procedure IDs against knowledge base whitelist (PROC_01 to PROC_14). Any phantom citation drops validity score."),
        ("Automated Evidence Heuristic Verification:", "Verifies that supporting evidence statements contain verbatim financial entities (ISINs, accounts, BICs) extracted from ticket narrative."),
        ("Thinking Token Sanitization:", "Regex parser strips internal reasoning chains (<think>...</think>) prior to JSON extraction.")
    ]
    for b_title, b_desc in val_points:
        add_bullet_item(tf_val, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right: Safety Guardrails
    add_card(s14, 6.833, 1.6, 5.7, 5.1)
    tb_grd = s14.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_grd = tb_grd.text_frame
    tf_grd.word_wrap = True
    p_g = tf_grd.paragraphs[0]
    p_g.text = "Operational Uncertainty & Escalation Guardrails"
    p_g.font.name = FONT_SERIF
    p_g.font.size = Pt(15)
    p_g.font.bold = True
    p_g.font.color.rgb = C_NAVY_BLUE
    p_g.space_after = Pt(10)

    grd_points = [
        ("Classifier Confidence Threshold:", "If Approach A confidence falls below 0.60, the ticket is flagged as uncertain, avoiding false certainty on borderline cases."),
        ("Mandatory Human Escalation Flag:", "If LLM returns UNDETERMINED or enumerates missing information, requires_human_review = True is asserted."),
        ("WCAG AA / AAA Accessibility Compliance:", "Streamlit alerts render explicit text colors (#7F1D1D on pale red; #064E3B on pale green) achieving >10:1 contrast in dark mode."),
        ("Strict Separation of Audit Levels:", "Explicitly distinguishes automated algorithmic heuristic checks (100% pass) from human subject-matter expert audit (Pending SME Review).")
    ]
    for b_title, b_desc in grd_points:
        add_bullet_item(tf_grd, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s14, 14)

    # =========================================================================
    # SLIDE 15: 7. RESULTS AND EVALUATION — MASTER BENCHMARK & RETRIEVAL COMPARISON
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_slide_header(s15, "7. Results and Evaluation", "Multi-Approach Benchmark Results & Retrieval Performance")

    # Table of Master Reconciled Metrics
    tbl_shape = s15.shapes.add_table(6, 6, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.8))
    t = tbl_shape.table
    col_w = [2.4, 1.8, 1.8, 2.0, 1.8, 1.933]
    for i, w in enumerate(col_w):
        t.columns[i].width = Inches(w)

    headers = ["Approach", "Sample Size (N)", "Accuracy / Hit@3", "Recall@3 / F1", "Mean Latency", "Citation Validity"]
    for j, h in enumerate(headers):
        cell = t.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_BLUE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            r.font.name = FONT_SERIF
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = C_WHITE

    bench_rows = [
        ("Approach A: Classifier", "N=55 Held-out Cases", "94.55% (52/55)", "Macro-F1: 0.9281", "1.2 ms", "N/A (Classifier)"),
        ("Approach B: Lexical IR", "N=210 Labelled Cases", "92.38% (Hit@3)", "Recall@3: 68.81%", "2.8 ms", "N/A (IR Only)"),
        ("Dense Semantic IR", "N=210 Labelled Cases", "97.62% (Hit@3)", "Recall@3: 72.86%", "18.5 ms", "N/A (IR Only)"),
        ("Approach C: Prompt-Only", "N=6 Pilot Cases", "83.33% (5/6)", "Macro-F1: 0.8333", "6.12 s", "N/A (Ungrounded)"),
        ("Approach D: Semantic RAG", "Retrieval N=210, LLM N=6", "97.62% Hit@3 / 83.33% Acc", "Recall@3: 72.86% / F1: 0.8333", "6.98 s", "100.0% (18/18 Valid)")
    ]
    for r_idx, r_data in enumerate(bench_rows, start=1):
        bg = C_LIGHT_CARD if r_idx % 2 == 1 else C_WHITE
        for c_idx, val in enumerate(r_data):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.name = FONT_SERIF
                r.font.size = Pt(9)
                r.font.color.rgb = C_DARK_TEXT

    # Embed Retrieval Figure below table
    ret_path = FIGURES_DIR / "retrieval_hit3_comparison.png"
    if ret_path.exists():
        s15.shapes.add_picture(str(ret_path), Inches(3.666), Inches(3.55), width=Inches(6.0))

    add_footer(s15, 15)

    # =========================================================================
    # SLIDE 16: 7. RESULTS AND EVALUATION — CONFUSION MATRIX & LATENCY PROFILES
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_slide_header(s16, "7. Results and Evaluation", "Classifier Confusion Matrix & Component Latency Profiles")

    # Left: Confusion Matrix
    cm_path = FIGURES_DIR / "confusion_matrix.png"
    if cm_path.exists():
        s16.shapes.add_picture(str(cm_path), Inches(0.8), Inches(1.6), width=Inches(5.7))

    # Right: Latency Profile
    lat_path = FIGURES_DIR / "response_latency_comparison.png"
    if lat_path.exists():
        s16.shapes.add_picture(str(lat_path), Inches(6.833), Inches(1.6), width=Inches(5.7))

    add_footer(s16, 16)

    # =========================================================================
    # SLIDE 17: 7. RESULTS AND EVALUATION — ERROR CASE STUDY & UNCERTAINTY
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_slide_header(s17, "7. Results and Evaluation", "RAG Error Diagnostic (Case SS-0096) & Uncertainty Guardrail Results")

    # Left: Error Case Study
    add_card(s17, 0.8, 1.6, 5.7, 5.1)
    tb_err = s17.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_err = tb_err.text_frame
    tf_err.word_wrap = True
    p = tf_err.paragraphs[0]
    p.text = "In-Depth Diagnostic: RAG Case SS-0096 Error"
    p.font.name = FONT_SERIF
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BMS_RED
    p.space_after = Pt(8)

    err_points = [
        ("Ground Truth Category:", "SECURITIES_SHORTFALL (Repo Closing ticket)"),
        ("RAG Predicted Category:", "SSI_MISMATCH (Incorrect diagnosis)"),
        ("Observed Narrative:", "\"Inventory location fragmentation... Counterparty awaiting delivery at Clearstream Frankfurt (CBF), but our inventory is located at an alternate European depository. Inter-CSD realignment required.\""),
        ("Retrieval Behavior:", "Successfully retrieved PROC_05 (Shortfall) and PROC_06 (Realignment), plus PROC_03 (SSI Verification)."),
        ("Root Cause of Error:", "Qwen3:4B fixated on 'depository mismatch' phrasing rather than physical inventory location, misclassifying ticket as instruction error."),
        ("Critical Heuristic Insight:", "Automated evidence validator awarded 100% because entities matched, proving algorithmic heuristics cannot substitute human SME review!")
    ]
    for b_title, b_desc in err_points:
        add_bullet_item(tf_err, f"• {b_title} ", b_desc, Pt(10), Pt(4))

    # Right: Uncertainty Figure
    unc_path = FIGURES_DIR / "uncertainty_handling.png"
    if unc_path.exists():
        s17.shapes.add_picture(str(unc_path), Inches(6.833), Inches(1.6), width=Inches(5.7))

    add_footer(s17, 17)

    # =========================================================================
    # SLIDE 18: 8. DISCUSSION — STRENGTHS, WEAKNESSES & IMPLEMENTATION HURDLES
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_slide_header(s18, "8. Discussion", "Architectural Insights, Strengths & Implementation Challenges")

    # Left: Strengths & Weaknesses
    add_card(s18, 0.8, 1.6, 5.7, 5.1)
    tb_sw = s18.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_sw = tb_sw.text_frame
    tf_sw.word_wrap = True
    p = tf_sw.paragraphs[0]
    p.text = "Architectural Strengths & Trade-offs"
    p.font.name = FONT_SERIF
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_BLUE
    p.space_after = Pt(10)

    sw_points = [
        ("100% Data Sovereignty:", "Local execution guarantees zero data leakage, conforming with strict institutional banking secrecy mandates."),
        ("Dual-Engine Synergies:", "Sub-2ms classification handles high-speed queue triage; RAG synthesis provides deep investigation for complex tickets."),
        ("Quantized Model Reasoning Limitations:", "4-bit quantized 4B models exhibit subtle boundary confusion on complex multi-depot narratives (e.g. SS-0096)."),
        ("Throughput Constraints:", "Generative inference (~6.75 s) limits full RAG to asynchronous analyst copilot workflows rather than microsecond wire routing.")
    ]
    for b_title, b_desc in sw_points:
        add_bullet_item(tf_sw, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    # Right: Challenges Resolved
    add_card(s18, 6.833, 1.6, 5.7, 5.1)
    tb_ch = s18.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_ch = tb_ch.text_frame
    tf_ch.word_wrap = True
    p_c = tf_ch.paragraphs[0]
    p_c.text = "Engineering Hurdles Diagnosed & Resolved"
    p_c.font.name = FONT_SERIF
    p_c.font.size = Pt(15)
    p_c.font.bold = True
    p_c.font.color.rgb = C_NAVY_BLUE
    p_c.space_after = Pt(10)

    ch_points = [
        ("Qwen Thinking Token Pollution:", "Suppressed internal chain-of-thought tokens (<think>) via think=False and regex filters to ensure 100% JSON parsing reliability."),
        ("Orphaned Background Inference Threads:", "Re-engineered client timeout handlers with session termination, eliminating 100% CPU lockups on long queries."),
        ("Template Leakage Elimination:", "Replaced naive random splits with GroupShuffleSplit on scenario families, replacing inflated 100% accuracy with realistic 94.55%."),
        ("UI Dark-Theme Contrast Inversion:", "Replaced unstyled alert banners with WCAG AAA compliant CSS rules (>10:1 contrast) ensuring legibility across themes.")
    ]
    for b_title, b_desc in ch_points:
        add_bullet_item(tf_ch, f"• {b_title} ", b_desc, Pt(11), Pt(8))

    add_footer(s18, 18)

    # =========================================================================
    # SLIDE 19: 9. CONCLUSION — SUMMARY OF CONTRIBUTIONS & KEY LEARNINGS
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    add_slide_header(s19, "9. Conclusion", "Summary of Technical Contributions & Key Learnings")

    cards_s19 = [
        ("1. Classical NLP Retains Immense Value", "Efficiency & Reliability",
         "Supervised linear models over normalized TF-IDF representations deliver 94.55% accuracy in 1.2 ms, outperforming LLMs by three orders of magnitude in speed for closed-world triage."),
        ("2. Semantic Embeddings Bridge Domain Lexicons", "Vocabulary Generalization",
         "Dense 768-dim embeddings achieve 97.62% Hit@3 and 0.8905 MRR, decisively outperforming lexical keyword search (+5.24%) across complex depository synonyms."),
        ("3. Structured Outputs Require Hard Guardrails", "Mitigating Hallucination",
         "Local LLMs reliably follow complex Pydantic JSON schemas (100% valid parsing), but automated heuristic checks must be paired with human oversight on nuanced domain boundaries."),
        ("4. Local-First AI is Feasible for Capital Markets", "Complete Data Sovereignty",
         "Demonstrates that an enterprise-grade post-trade investigation copilot can execute entirely on standard workstation hardware without cloud API dependencies.")
    ]
    for i, (title, sub, body) in enumerate(cards_s19):
        x = 0.8 + i * 2.983
        add_card(s19, x, 1.6, 2.783, 5.1)
        tb = s19.shapes.add_textbox(Inches(x + 0.2), Inches(1.8), Inches(2.383), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_SERIF
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_BLUE

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_SERIF
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_BMS_RED
        p2.space_after = Pt(10)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = FONT_SERIF
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = C_DARK_TEXT
        p3.line_spacing = 1.25

    add_footer(s19, 19)

    # =========================================================================
    # SLIDE 20: 9. CONCLUSION — FUTURE WORK & PRODUCTION ROADMAP
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    add_slide_header(s20, "9. Conclusion", "Production Roadmap & Future Research Extensions")

    future_cards = [
        ("1. Scaled LLM Benchmark", "Expanded Evaluation Split",
         "Scale generative benchmarking from the 6-case pilot to the complete 55 held-out test split using batch local inference queues to quantify statistical variance."),
        ("2. Domain Fine-Tuned Embeddings", "Contrastive Representation Learning",
         "Fine-tune nomic-embed-text on historical SWIFT MT548 status archives via triplet loss to further separate overlapping account and depository entities."),
        ("3. Multi-Agent Cross-Depot Realignment", "Autonomous Tool Calling",
         "Equip the copilot with tool-calling capabilities to query local inventory databases and draft formatted SWIFT MT542/MT543 realignment instructions."),
        ("4. Active Learning & Analyst Feedback", "Continuous SOP Optimization",
         "Incorporate human analyst feedback and accepted note corrections to dynamically update vector procedure weights and improve few-shot exemplars.")
    ]
    for i, (title, sub, body) in enumerate(future_cards):
        x = 0.8 + i * 2.983
        add_card(s20, x, 1.6, 2.783, 5.1)
        tb = s20.shapes.add_textbox(Inches(x + 0.2), Inches(1.8), Inches(2.383), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_SERIF
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_BLUE

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_SERIF
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_BMS_RED
        p2.space_after = Pt(10)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = FONT_SERIF
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = C_DARK_TEXT
        p3.line_spacing = 1.25

    add_footer(s20, 20)

    # =========================================================================
    # SLIDE 21: 10. REFERENCES — VERIFIED ACADEMIC & TECHNICAL CITATIONS
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    add_slide_header(s21, "10. References", "Verified Academic and Industry Standards Bibliography")

    # Left Column Citations
    add_card(s21, 0.8, 1.6, 5.7, 5.1)
    tb_r1 = s21.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    p1 = tf_r1.paragraphs[0]
    p1.text = "Academic Foundations [1] – [5]"
    p1.font.name = FONT_SERIF
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = C_NAVY_BLUE
    p1.space_after = Pt(8)

    refs_c1 = [
        ("[1] Jurafsky & Martin (2024)", "Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition (3rd ed. draft, Stanford University)."),
        ("[2] Manning, Raghavan & Schütze (2008)", "Introduction to Information Retrieval (Cambridge University Press)."),
        ("[3] Lewis et al. (NeurIPS 2020)", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Advances in Neural Information Processing Systems, vol. 33)."),
        ("[4] Pedregosa et al. (JMLR 2011)", "Scikit-learn: Machine Learning in Python (Journal of Machine Learning Research, vol. 12)."),
        ("[5] Nussbaum et al. (arXiv 2024)", "Nomic Embed: Training a Reproducible Long Context Text Embedder (arXiv:2402.01613).")
    ]
    for tag, desc in refs_c1:
        add_bullet_item(tf_r1, f"{tag}: ", desc, Pt(9.5), Pt(6))

    # Right Column Citations
    add_card(s21, 6.833, 1.6, 5.7, 5.1)
    tb_r2 = s21.shapes.add_textbox(Inches(7.083), Inches(1.85), Inches(5.2), Inches(4.6))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    p2 = tf_r2.paragraphs[0]
    p2.text = "Models & Market Standards [6] – [10]"
    p2.font.name = FONT_SERIF
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = C_NAVY_BLUE
    p2.space_after = Pt(8)

    refs_c2 = [
        ("[6] Qwen Team (2024)", "Qwen2.5: A Party of Foundation and Instruction-Tuned Language Models (Alibaba Cloud Technical Report)."),
        ("[7] Chroma Core Team (2024)", "Chroma: The Open-Source AI Application Database (Official Documentation)."),
        ("[8] Ollama Project (2024)", "Ollama: Get Up and Running with Large Language Models Locally (Official Documentation)."),
        ("[9] ICMA Operations Working Group (2023)", "CSDR Settlement Discipline: Cash Penalties and Buy-in Rules Best Practices (Zurich, Switzerland)."),
        ("[10] SWIFT Standards (2024)", "ISO 15022 & ISO 20022 Securities Settlement and Reconciliation Message Definition Report (MT548/sese.024, La Hulpe, Belgium).")
    ]
    for tag, desc in refs_c2:
        add_bullet_item(tf_r2, f"{tag}: ", desc, Pt(9.5), Pt(6))

    add_footer(s21, 21)

    # =========================================================================
    # SLIDE 22: CLOSING SLIDE (Exact BMSCE Template Layout)
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)

    # Center text box for "Thank you !"
    thank_box = s22.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.0))
    tf_th = thank_box.text_frame
    tf_th.word_wrap = True

    p_th = tf_th.paragraphs[0]
    p_th.alignment = PP_ALIGN.CENTER
    p_th.text = "Thank you !"
    p_th.font.name = FONT_SERIF
    p_th.font.size = Pt(54)
    p_th.font.bold = True
    p_th.font.color.rgb = C_BLACK

    p_qa = tf_th.add_paragraph()
    p_qa.alignment = PP_ALIGN.CENTER
    p_qa.text = "Questions & Discussion"
    p_qa.font.name = FONT_SERIF
    p_qa.font.size = Pt(22)
    p_qa.font.bold = True
    p_qa.font.color.rgb = C_NAVY_BLUE
    p_qa.space_before = Pt(20)

    p_foot = tf_th.add_paragraph()
    p_foot.alignment = PP_ALIGN.CENTER
    p_foot.text = "B. M. S. College of Engineering | Department of Machine Learning\nCourse: Natural Language Processing for LLM (24AM7PCLLM)"
    p_foot.font.name = FONT_SERIF
    p_foot.font.size = Pt(13)
    p_foot.font.color.rgb = C_SLATE_GRAY
    p_foot.space_before = Pt(24)

    # Save presentation
    OUTPUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PPTX))
    print(f"Presentation successfully saved to: {OUTPUT_PPTX}")
    print(f"Total slides generated: {len(prs.slides)}")


if __name__ == "__main__":
    build_presentation()
