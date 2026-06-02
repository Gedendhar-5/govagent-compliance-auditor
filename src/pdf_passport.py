"""
GovAgent — PDF Compliance Passport Generator
===============================================
Generates a professional, branded PDF audit report from the passport
dict produced by the Chief Compliance Officer node.

Uses fpdf2 for PDF generation — no external dependencies beyond what's
already in requirements.txt.

Usage::

    from src.pdf_passport import generate_passport_pdf
    pdf_bytes = generate_passport_pdf(passport_dict)
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from fpdf import FPDF


# ---------------------------------------------------------------------------
# Colour palette (RGB tuples)
# ---------------------------------------------------------------------------

_INDIGO       = (99, 102, 241)
_PURPLE       = (168, 85, 247)
_PINK         = (236, 72, 153)
_GREEN        = (34, 197, 94)
_YELLOW       = (234, 179, 8)
_RED          = (239, 68, 68)
_DARK_BG      = (15, 23, 42)
_CARD_BG      = (30, 41, 59)
_TEXT_PRIMARY  = (226, 232, 240)
_TEXT_MUTED    = (148, 163, 184)
_WHITE        = (255, 255, 255)


def _score_color(score: float) -> tuple[int, int, int]:
    """Return a colour tuple based on the score range."""
    if score >= 80:
        return _GREEN
    elif score >= 60:
        return _YELLOW
    else:
        return _RED


def _safe_str(value: Any) -> str:
    """Convert any value to a safe string for PDF rendering."""
    if value is None:
        return "N/A"
    return str(value)


class _PassportPDF(FPDF):
    """Custom FPDF subclass with GovAgent branding."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        """Page header — thin gradient bar."""
        if self.page_no() > 1:
            # Top accent bar
            self.set_fill_color(*_INDIGO)
            self.rect(0, 0, 210, 3, "F")
            # Page header text
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*_TEXT_MUTED)
            self.set_y(6)
            self.cell(0, 5, "GovAgent - AI Compliance Passport", align="L")
            self.ln(10)

    def footer(self):
        """Page footer with page number."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*_TEXT_MUTED)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _section_title(self, title: str):
        """Render a section title with accent line."""
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*_INDIGO)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        # Accent underline
        self.set_draw_color(*_INDIGO)
        self.set_line_width(0.5)
        x = self.get_x()
        y = self.get_y()
        self.line(x, y, x + 50, y)
        self.ln(6)

    def _body_text(self, text: str):
        """Render body text in standard style."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def _key_value(self, key: str, value: str):
        """Render a key-value pair."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(50, 6, f"{key}:", new_x="END")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")


def generate_passport_pdf(passport: dict[str, Any], output_path: str | None = None) -> bytes:
    """Generate a professional PDF compliance passport.

    Parameters
    ----------
    passport : dict
        The passport dict from ``chief_compliance_node()``.
    output_path : str | None
        If provided, also save the PDF to this file path.

    Returns
    -------
    bytes
        The raw PDF file content.
    """
    pdf = _PassportPDF()
    pdf.alias_nb_pages()

    # ── Page 1: Cover ─────────────────────────────────────────────
    pdf.add_page()

    # Title block
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*_INDIGO)
    pdf.cell(0, 15, "GovAgent", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*_TEXT_MUTED)
    pdf.cell(0, 8, "AI Safety & Legal Compliance Auditor", align="C",
             new_x="LMARGIN", new_y="NEXT")

    # Decorative line
    pdf.ln(5)
    pdf.set_draw_color(*_INDIGO)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)

    # Document title
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 12, "AI Compliance Passport", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Audit metadata
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"Audit ID: {passport.get('audit_id', 'N/A')}", align="C",
             new_x="LMARGIN", new_y="NEXT")

    timestamp = passport.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = dt.strftime("%B %d, %Y at %H:%M UTC")
    except Exception:
        date_str = _safe_str(timestamp)
    pdf.cell(0, 7, f"Date: {date_str}", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # Target model
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, f"Target System: {passport.get('target_model', 'N/A')}",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # ── Score gauge ───────────────────────────────────────────────
    overall = passport.get("overall_score", 0)
    score_color = _score_color(overall)

    # Score circle (simulated with a filled rect + text)
    cx = 105  # center X
    cy = pdf.get_y() + 15
    r = 20

    # Outer circle
    pdf.set_fill_color(*score_color)
    pdf.set_draw_color(*score_color)
    pdf.ellipse(cx - r, cy - r, r * 2, r * 2, style="D")

    # Score text
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*score_color)
    score_text = f"{overall}"
    pdf.set_xy(cx - 15, cy - 8)
    pdf.cell(30, 16, score_text, align="C")

    pdf.set_xy(cx - 20, cy + 10)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(40, 5, "/ 100", align="C")

    pdf.set_y(cy + r + 8)

    # Certification decision
    decision = passport.get("certification_decision", "N/A")
    pdf.set_font("Helvetica", "B", 14)

    if "CERTIFIED" in decision and "NOT" not in decision and "REJECTED" not in decision:
        pdf.set_text_color(*_GREEN)
    elif "CONDITIONALLY" in decision:
        pdf.set_text_color(*_YELLOW)
    else:
        pdf.set_text_color(*_RED)

    pdf.cell(0, 10, decision, align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Page 2: Executive Summary ─────────────────────────────────
    pdf.add_page()
    pdf._section_title("Executive Summary")

    exec_summary = passport.get("executive_summary", "No executive summary available.")
    # Handle encoding — replace problematic chars
    exec_summary = exec_summary.encode("latin-1", errors="replace").decode("latin-1")
    pdf._body_text(exec_summary)

    # ── Score Breakdown Table ─────────────────────────────────────
    pdf._section_title("Score Breakdown")

    breakdown = passport.get("breakdown", {})

    # Table header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(240, 240, 245)
    pdf.set_text_color(60, 60, 60)
    col_widths = [50, 25, 25, 90]
    headers = ["Agent", "Score", "Weight", "Key Detail"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1, fill=True, align="C")
    pdf.ln()

    # Table rows
    rows = [
        ("Legal Compliance",
         breakdown.get("legal", {}).get("score", 0),
         "30%",
         f"{breakdown.get('legal', {}).get('issues_count', 0)} issues, Risk: {breakdown.get('legal', {}).get('risk_classification', 'N/A')}"),
        ("Red-Team Security",
         breakdown.get("red_team", {}).get("score", 0),
         "25%",
         f"{breakdown.get('red_team', {}).get('jailbreaks', 0)}/{breakdown.get('red_team', {}).get('attacks', 0)} jailbreaks succeeded"),
        ("Data Privacy",
         breakdown.get("privacy", {}).get("score", 0),
         "25%",
         f"{breakdown.get('privacy', {}).get('pii_count', 0)} PII, {breakdown.get('privacy', {}).get('secrets_count', 0)} secrets, Risk: {breakdown.get('privacy', {}).get('risk_level', 'N/A')}"),
        ("Bias & Fairness",
         breakdown.get("bias", {}).get("score", 0),
         "20%",
         f"Toxicity: {breakdown.get('bias', {}).get('toxicity', 'N/A')}, Fairness: {breakdown.get('bias', {}).get('fairness', 'N/A')}"),
    ]

    pdf.set_font("Helvetica", "", 10)
    for label, score, weight, detail in rows:
        sc = _score_color(score)
        # Agent name
        pdf.set_text_color(40, 40, 40)
        pdf.cell(col_widths[0], 8, label, border=1)
        # Score (coloured)
        pdf.set_text_color(*sc)
        pdf.cell(col_widths[1], 8, f"{score}", border=1, align="C")
        # Weight
        pdf.set_text_color(100, 100, 100)
        pdf.cell(col_widths[2], 8, weight, border=1, align="C")
        # Detail
        pdf.set_text_color(60, 60, 60)
        detail_safe = detail.encode("latin-1", errors="replace").decode("latin-1")
        pdf.cell(col_widths[3], 8, detail_safe, border=1)
        pdf.ln()

    # ── Key Issues ────────────────────────────────────────────────
    issues = passport.get("key_issues", [])
    if issues:
        pdf.ln(4)
        pdf._section_title("Key Issues")
        for i, issue in enumerate(issues, 1):
            issue_safe = _safe_str(issue).encode("latin-1", errors="replace").decode("latin-1")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*_RED)
            pdf.cell(8, 5, f"{i}.")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 5, issue_safe)
            pdf.ln(1)

    # ── Agent Summaries ───────────────────────────────────────────
    summaries = passport.get("agent_summaries", {})
    if summaries:
        pdf.add_page()
        pdf._section_title("Agent Summaries")

        agent_labels = {
            "legal": "Legal Compliance Agent",
            "red_team": "Red-Team Security Agent",
            "privacy": "Data Privacy Sentinel",
            "bias": "Bias & Fairness Auditor",
        }
        agent_icons = {
            "legal": "[LEGAL]",
            "red_team": "[RED-TEAM]",
            "privacy": "[PRIVACY]",
            "bias": "[BIAS]",
        }

        for key, label in agent_labels.items():
            summary = summaries.get(key, "")
            if isinstance(summary, list):
                summary = "; ".join(str(s) for s in summary)
            if not summary:
                continue

            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*_INDIGO)
            pdf.cell(0, 7, f"{agent_icons[key]} {label}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            summary_safe = _safe_str(summary).encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 5, summary_safe)
            pdf.ln(4)

    # ── Footer block ──────────────────────────────────────────────
    pdf.ln(10)
    pdf.set_draw_color(*_INDIGO)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*_TEXT_MUTED)
    pdf.cell(0, 5,
             f"Generated by GovAgent v1.0  |  Audit ID: {passport.get('audit_id', 'N/A')}  |  {date_str}",
             align="C")

    # ── Output ────────────────────────────────────────────────────
    pdf_bytes = pdf.output()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_passport = {
        "title": "AI Compliance Passport",
        "audit_id": "test-1234-5678",
        "target_model": "Acme-ChatBot-v2",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "certification_decision": "NOT CERTIFIED - Significant Issues (Remediation Required)",
        "overall_score": 66.15,
        "executive_summary": (
            "The Acme-ChatBot-v2 system has undergone a comprehensive compliance audit "
            "across four critical dimensions. The overall compliance score of 66.15/100 "
            "indicates significant issues that must be addressed before deployment."
        ),
        "breakdown": {
            "legal": {"score": 60.0, "weight": "30%", "issues_count": 3, "risk_classification": "high"},
            "red_team": {"score": 95.0, "weight": "25%", "attacks": 3, "jailbreaks": 0},
            "privacy": {"score": 32.0, "weight": "25%", "pii_count": 5, "secrets_count": 2, "risk_level": "critical"},
            "bias": {"score": 82.0, "weight": "20%", "toxicity": 0.15, "fairness": 0.78},
        },
        "key_issues": [
            "No documented risk-management system (EU AI Act Art. 9)",
            "PII detected in model outputs (5 instances)",
            "API key pattern found in generated text",
        ],
        "agent_summaries": {
            "legal": "Multiple EU AI Act and GDPR compliance gaps identified.",
            "red_team": "All 3 adversarial attacks were successfully blocked.",
            "privacy": "Critical privacy risks: 5 PII items and 2 secrets detected.",
            "bias": "Low toxicity (0.15) but fairness could be improved (0.78).",
        },
    }

    pdf_data = generate_passport_pdf(sample_passport, "test_passport.pdf")
    print(f"Generated test PDF: {len(pdf_data)} bytes")
