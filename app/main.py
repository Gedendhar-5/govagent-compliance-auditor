"""
GovAgent — Streamlit Dashboard (Phase 1)
==========================================
Minimal UI to launch compliance audits, view real-time graph progress,
and inspect the generated AI Compliance Passport.

Usage::

    streamlit run app/main.py
"""

from __future__ import annotations

import json
import os
import sys
import time

# Ensure the project root (parent of app/) is on sys.path so that
# `from src.graph import ...` works regardless of working directory.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# ── Auto-rebuild FAISS index on first launch ──────────────────────────────
from pathlib import Path
_faiss_index_path = Path(_PROJECT_ROOT) / "data" / "faiss_index" / "regulations.index"
if not _faiss_index_path.exists():
    with st.spinner("Initializing regulatory database (building FAISS index) ..."):
        try:
            from src.mcp.vector_store import build_index
            build_index()
            st.success("Regulatory database initialized successfully!")
            time.sleep(1)
        except Exception as e:
            st.error(f"Failed to initialize regulatory database: {e}")

if "audit_history" not in st.session_state:
    st.session_state.audit_history = []

if "selected_audit" not in st.session_state:
    st.session_state.selected_audit = None

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="GovAgent — AI Compliance Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium dark theme
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* ── Import Google Font ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global overrides ───────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Glassmorphism card ──────────────────────────────────────── */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* ── Score gauge ─────────────────────────────────────────────── */
    .score-container {
        text-align: center;
        padding: 32px 0;
    }
    .score-value {
        font-size: 72px;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .score-label {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Certification badge ─────────────────────────────────────── */
    .cert-badge {
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        padding: 12px 24px;
        border-radius: 12px;
        margin: 16px auto;
        max-width: 500px;
    }
    .cert-pass {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #22c55e;
    }
    .cert-conditional {
        background: rgba(234, 179, 8, 0.15);
        border: 1px solid rgba(234, 179, 8, 0.3);
        color: #eab308;
    }
    .cert-fail {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }

    /* ── Node progress pill ──────────────────────────────────────── */
    .node-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 500;
        margin: 4px;
    }
    .node-done {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.25);
    }
    .node-running {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.25);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ── Metric card ─────────────────────────────────────────────── */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-label {
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }

    /* ── Sidebar styling ─────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(12px);
    }

    /* ── Header gradient ─────────────────────────────────────────── */
    .header-gradient {
        background: linear-gradient(135deg, #1e1b4b, #312e81, #4c1d95);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        text-align: center;
    }
    .header-gradient h1 {
        color: white;
        font-size: 36px;
        font-weight: 700;
        margin: 0;
    }
    .header-gradient p {
        color: #c4b5fd;
        font-size: 16px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="header-gradient">
    <h1>🛡️ GovAgent</h1>
    <p>Multi-Agent AI Safety & Legal Compliance Auditor</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — Audit configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Audit Configuration")
    st.markdown("---")

    target_name = st.text_input(
        "Target Model Name",
        value="Acme-ChatBot-v2",
        help="The name of the LLM application under audit.",
    )

    target_description = st.text_area(
        "Target Model Description",
        value=(
            "A customer-service chatbot deployed on an e-commerce platform. "
            "Handles order enquiries, returns, and general FAQs."
        ),
        height=120,
        help="A short description or system prompt of the target model.",
    )

    st.markdown("---")
    st.markdown("### 📊 Score Weights")
    w_legal   = st.slider("Legal", 0, 100, 30, key="w_legal")
    w_redteam = st.slider("Red-Team", 0, 100, 25, key="w_redteam")
    w_privacy = st.slider("Privacy", 0, 100, 25, key="w_privacy")
    w_bias    = st.slider("Bias", 0, 100, 20, key="w_bias")

    st.markdown("---")
    run_audit = st.button("🚀 Run Compliance Audit", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### 📜 Session Audit History")
    if st.session_state.audit_history:
        for idx, hist in enumerate(st.session_state.audit_history):
            score = hist["overall_score"]
            color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            if st.button(f"{color} {hist['target_model_name']} ({score})", key=f"hist_{hist['audit_id']}_{idx}"):
                st.session_state.selected_audit = hist["result"]
                st.rerun()
    else:
        st.caption("No past audits in this session.")

    st.markdown("---")
    st.caption("GovAgent v1.0.0 — Production")

# ---------------------------------------------------------------------------
# Main area — Audit execution & results
# ---------------------------------------------------------------------------

if run_audit:
    # Prepare input state
    sample_input = {
        "target_model_name": target_name,
        "target_model_description": target_description,
        "jailbreak_attempts": [],
        "errors": [],
    }

    # Import graph lazily to keep startup fast
    from src.graph import compiled_graph

    # ── Progress display ──────────────────────────────────────────
    progress_placeholder = st.empty()
    status_text = st.empty()

    node_names = [
        "init_audit", "legal_auditor", "red_team",
        "privacy_sentinel", "bias_analyzer", "chief_compliance",
    ]
    node_labels = {
        "init_audit":       "🏁 Init Audit",
        "legal_auditor":    "📜 Legal Auditor",
        "red_team":         "🔥 Red-Team",
        "privacy_sentinel": "🔒 Privacy Sentinel",
        "bias_analyzer":    "⚖️ Bias Analyzer",
        "chief_compliance": "⚖️ Chief Compliance",
    }
    completed_nodes: list[str] = []

    def _render_progress(completed: list[str], current: str | None = None) -> str:
        pills = []
        for n in node_names:
            label = node_labels.get(n, n)
            if n in completed:
                pills.append(f'<span class="node-pill node-done">✓ {label}</span>')
            elif n == current:
                pills.append(f'<span class="node-pill node-running">⟳ {label}</span>')
            else:
                pills.append(f'<span class="node-pill" style="opacity:0.3">{label}</span>')
        return '<div style="text-align:center;padding:16px 0;">' + " ".join(pills) + "</div>"

    # ── Stream execution ──────────────────────────────────────────
    result = dict(sample_input)
    with st.spinner("Running compliance audit …"):
        for step_output in compiled_graph.stream(sample_input):
            for node_name, node_output in step_output.items():
                # Merge updates into the result state mimicking the graph's reducers
                for key, val in node_output.items():
                    if key in ["jailbreak_attempts", "errors"]:
                        if key not in result or not result[key]:
                            result[key] = []
                        result[key] = list(result[key]) + list(val)
                    else:
                        result[key] = val

                progress_placeholder.markdown(
                    _render_progress(completed_nodes, node_name),
                    unsafe_allow_html=True,
                )
                time.sleep(0.5)  # Visual pacing for demo
                completed_nodes.append(node_name)

        # Final state of progress
        progress_placeholder.markdown(
            _render_progress(completed_nodes),
            unsafe_allow_html=True,
        )

    status_text.success("Audit completed successfully!")

    # Save to session history
    st.session_state.audit_history.insert(0, {
        "audit_id": result.get("audit_id", "N/A"),
        "target_model_name": target_name,
        "overall_score": result.get("overall_score", 0),
        "timestamp": result.get("passport", {}).get("timestamp", ""),
        "result": result
    })
    st.session_state.audit_history = st.session_state.audit_history[:5]
    st.session_state.selected_audit = result

elif st.session_state.selected_audit is not None:
    result = st.session_state.selected_audit
else:
    result = None

if result is not None:

    # ── Score gauge ───────────────────────────────────────────────
    overall = result.get("overall_score", 0)
    passport = result.get("passport", {})
    decision = passport.get("certification_decision", "N/A")

    st.markdown("---")

    col_score, col_decision = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="glass-card score-container">
            <div class="score-value">{overall}</div>
            <div class="score-label">Overall Compliance Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col_decision:
        # Pick CSS class
        if overall >= 90:
            badge_class = "cert-pass"
        elif overall >= 75:
            badge_class = "cert-conditional"
        else:
            badge_class = "cert-fail"

        st.markdown(f"""
        <div class="glass-card" style="display:flex;align-items:center;justify-content:center;height:100%;">
            <div>
                <div class="cert-badge {badge_class}">{decision}</div>
                <div style="text-align:center;color:#94a3b8;font-size:13px;margin-top:12px;">
                    Audit ID: {result.get('audit_id', 'N/A')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Breakdown metrics ─────────────────────────────────────────
    st.markdown("### 📊 Score Breakdown")

    breakdown = passport.get("breakdown", {})
    bc1, bc2, bc3, bc4 = st.columns(4)

    def _metric_card(col, label: str, score: float, icon: str, detail: str):
        with col:
            color = "#22c55e" if score >= 80 else "#eab308" if score >= 60 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
                <div class="metric-value" style="color:{color}">{score}</div>
                <div class="metric-label">{label}</div>
                <div style="color:#64748b;font-size:11px;margin-top:8px;">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    legal_b   = breakdown.get("legal", {})
    redteam_b = breakdown.get("red_team", {})
    privacy_b = breakdown.get("privacy", {})
    bias_b    = breakdown.get("bias", {})

    _metric_card(bc1, "Legal",   legal_b.get("score", 0),   "📜",
                 f"{legal_b.get('issues_count', 0)} issues found")
    _metric_card(bc2, "Red-Team", redteam_b.get("score", 0), "🔥",
                 f"{redteam_b.get('jailbreaks', 0)}/{redteam_b.get('attacks', 0)} jailbreaks")
    _metric_card(bc3, "Privacy",  privacy_b.get("score", 0), "🔒",
                 f"{privacy_b.get('pii_count', 0)} PII, {privacy_b.get('secrets_count', 0)} secrets")
    _metric_card(bc4, "Bias",     bias_b.get("score", 0),    "⚖️",
                 f"Toxicity: {bias_b.get('toxicity', 'N/A')}")

    # ── Detailed findings tabs ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Detailed Findings")

    tab_legal, tab_redteam, tab_privacy, tab_bias, tab_passport = st.tabs([
        "📜 Legal", "🔥 Red-Team", "🔒 Privacy", "⚖️ Bias", "📄 Passport"
    ])

    # ── Helper for severity badges ────────────────────────────────
    def _severity_badge(level: str) -> str:
        colors = {
            "critical": ("#dc2626", "#fecaca"), "high": ("#ea580c", "#fed7aa"),
            "medium": ("#ca8a04", "#fef9c3"), "low": ("#16a34a", "#bbf7d0"),
            "none": ("#64748b", "#e2e8f0"),
        }
        bg, fg = colors.get(level.lower(), colors["none"])
        return (f'<span style="background:{bg}22;color:{bg};border:1px solid {bg}44;'
                f'padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;">'
                f'{level.upper()}</span>')

    # ──────────────────────────────────────────────────────────────
    # TAB: Legal
    # ──────────────────────────────────────────────────────────────
    with tab_legal:
        lf = result.get("legal_findings", {})
        risk = lf.get("risk_classification", "unknown")
        risk_colors = {"high": "#ef4444", "unacceptable": "#dc2626",
                       "limited": "#eab308", "low": "#22c55e", "unknown": "#94a3b8"}
        rc = risk_colors.get(risk, "#94a3b8")

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:18px;font-weight:600;color:#e2e8f0;">📜 Legal Compliance Analysis</span>
                <span style="background:{rc}22;color:{rc};border:1px solid {rc}44;
                      padding:4px 14px;border-radius:999px;font-size:13px;font-weight:600;">
                    Risk: {risk.upper()}
                </span>
            </div>
            <p style="color:#94a3b8;font-size:14px;">{lf.get('summary', 'No summary available.')}</p>
        </div>
        """, unsafe_allow_html=True)

        lc1, lc2 = st.columns(2)
        with lc1:
            st.markdown("#### ⚠️ Issues Found")
            for i, issue in enumerate(lf.get("issues", []), 1):
                st.markdown(f"**{i}.** {issue}")
            if not lf.get("issues"):
                st.success("No issues found.")
        with lc2:
            st.markdown("#### ✅ Recommendations")
            for i, rec in enumerate(lf.get("recommendations", []), 1):
                st.markdown(f"**{i}.** {rec}")

        if lf.get("regulation_coverage"):
            st.markdown("#### 📋 Regulations Reviewed")
            for reg in lf["regulation_coverage"]:
                st.markdown(f"- {reg}")

        # Show retrieved FAISS clauses (Phase 3 RAG)
        retrieved = lf.get("retrieved_clauses", [])
        if retrieved:
            clauses_used = lf.get("retrieved_clauses_used", len(retrieved))
            st.markdown(f"#### 🔍 Retrieved Regulation Clauses ({clauses_used} used in analysis)")
            for clause in retrieved:
                relevance = clause.get("relevance", 0)
                rel_pct = f"{relevance * 100:.0f}%" if isinstance(relevance, (int, float)) else "N/A"
                rel_color = "#22c55e" if relevance > 0.5 else "#eab308" if relevance > 0.3 else "#94a3b8"
                st.markdown(f"""
                <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
                     border-radius:8px;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:600;color:#818cf8;">{clause.get('regulation', '')} {clause.get('article', '')}</span>
                        <span style="color:#94a3b8;margin-left:8px;">{clause.get('title', '')}</span>
                    </div>
                    <span style="color:{rel_color};font-size:12px;font-weight:600;">{rel_pct} match</span>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("🔧 Raw JSON (for developers)"):
            st.json(lf)

    # ──────────────────────────────────────────────────────────────
    # TAB: Red-Team
    # ──────────────────────────────────────────────────────────────
    with tab_redteam:
        rf = result.get("red_team_findings", {})
        attacks = rf.get("attacks_attempted", 0)
        jailbreaks = rf.get("jailbreaks_succeeded", 0)
        blocked = attacks - jailbreaks

        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:600;color:#e2e8f0;margin-bottom:12px;">
                🔥 Red-Team Security Assessment
            </div>
            <p style="color:#94a3b8;font-size:14px;">{rf.get('summary', 'No summary available.')}</p>
        </div>
        """, unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.metric("Attacks Attempted", attacks)
        with rc2:
            st.metric("Blocked", f"🟢 {blocked}")
        with rc3:
            st.metric("Jailbreaks", f"{'🔴' if jailbreaks > 0 else '🟢'} {jailbreaks}")

        st.markdown("#### 🎯 Attack Cycle Log")
        for attempt in result.get("jailbreak_attempts", []):
            cycle = attempt.get("cycle", "?")
            success = attempt.get("success", False)
            severity = attempt.get("severity", "none")
            icon = "🔴" if success else "🟢"
            attempt_status = "JAILBREAK SUCCEEDED" if success else "ATTACK BLOCKED"

            with st.expander(f"{icon} Cycle {cycle} — {attempt_status}"):
                st.markdown(f"**Severity:** {_severity_badge(severity)}", unsafe_allow_html=True)
                st.markdown("**Attack Prompt:**")
                st.code(attempt.get("prompt", ""), language=None)
                st.markdown("**Target Response:**")
                st.info(attempt.get("response", ""))
                if attempt.get("reasoning"):
                    st.markdown(f"**Evaluation:** {attempt['reasoning']}")

        with st.expander("🔧 Raw JSON (for developers)"):
            st.json(rf)

    # ──────────────────────────────────────────────────────────────
    # TAB: Privacy
    # ──────────────────────────────────────────────────────────────
    with tab_privacy:
        pf = result.get("privacy_findings", {})
        risk_level = pf.get("risk_level", "unknown")

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:18px;font-weight:600;color:#e2e8f0;">🔒 Privacy & Data Protection Scan</span>
                {_severity_badge(risk_level)}
            </div>
            <p style="color:#94a3b8;font-size:14px;">{pf.get('summary', 'No summary available.')}</p>
        </div>
        """, unsafe_allow_html=True)

        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("#### 🔍 PII Detected")
            pii_items = pf.get("pii_detected", [])
            if pii_items:
                for item in pii_items:
                    pii_type = item.get("type", "unknown").replace("_", " ").title()
                    value = item.get("value", "N/A")
                    ctx = item.get("context", "")
                    st.markdown(f"""
                    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                         border-radius:8px;padding:12px;margin-bottom:8px;">
                        <div style="font-weight:600;color:#ef4444;font-size:13px;">{pii_type}</div>
                        <div style="color:#e2e8f0;font-size:13px;margin-top:4px;">
                            <code>{value}</code>
                        </div>
                        <div style="color:#64748b;font-size:11px;margin-top:4px;">...{ctx}...</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No PII detected.")

        with pc2:
            st.markdown("#### 🔑 Secrets Detected")
            secret_items = pf.get("secrets_detected", [])
            if secret_items:
                for item in secret_items:
                    sec_type = item.get("type", "unknown").replace("_", " ").title()
                    value = item.get("value", "N/A")
                    st.markdown(f"""
                    <div style="background:rgba(234,179,8,0.08);border:1px solid rgba(234,179,8,0.2);
                         border-radius:8px;padding:12px;margin-bottom:8px;">
                        <div style="font-weight:600;color:#eab308;font-size:13px;">{sec_type}</div>
                        <div style="color:#e2e8f0;font-size:13px;margin-top:4px;">
                            <code>{value}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No secrets detected.")

        if pf.get("recommendations"):
            st.markdown("#### ✅ Recommendations")
            for i, rec in enumerate(pf["recommendations"], 1):
                st.markdown(f"**{i}.** {rec}")

        with st.expander("🔧 Raw JSON (for developers)"):
            st.json(pf)

    # ──────────────────────────────────────────────────────────────
    # TAB: Bias
    # ──────────────────────────────────────────────────────────────
    with tab_bias:
        bf = result.get("bias_findings", {})

        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:18px;font-weight:600;color:#e2e8f0;margin-bottom:12px;">
                ⚖️ Bias & Fairness Evaluation
            </div>
            <p style="color:#94a3b8;font-size:14px;">{bf.get('summary', 'No summary available.')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Toxicity & Fairness gauges
        bc1, bc2 = st.columns(2)
        tox = bf.get("toxicity_score", 0.5)
        fair = bf.get("fairness_score", 0.5)
        tox_color = "#22c55e" if tox < 0.3 else "#eab308" if tox < 0.6 else "#ef4444"
        fair_color = "#22c55e" if fair > 0.7 else "#eab308" if fair > 0.4 else "#ef4444"

        with bc1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Toxicity Score</div>
                <div class="metric-value" style="color:{tox_color}">{tox:.2f}</div>
                <div style="color:#64748b;font-size:11px;margin-top:4px;">0 = Safe · 1 = Toxic</div>
            </div>
            """, unsafe_allow_html=True)
        with bc2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Fairness Score</div>
                <div class="metric-value" style="color:{fair_color}">{fair:.2f}</div>
                <div style="color:#64748b;font-size:11px;margin-top:4px;">0 = Unfair · 1 = Fair</div>
            </div>
            """, unsafe_allow_html=True)

        # Demographic parity
        demo = bf.get("demographic_parity", {})
        if demo:
            st.markdown("#### 📊 Demographic Parity Scores")
            demo_cols = st.columns(len(demo))
            for col, (dim, score) in zip(demo_cols, demo.items()):
                d_color = "#22c55e" if score > 0.8 else "#eab308" if score > 0.6 else "#ef4444"
                with col:
                    st.markdown(f"""
                    <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.03);
                         border-radius:8px;border:1px solid rgba(255,255,255,0.06);">
                        <div style="font-size:24px;font-weight:700;color:{d_color};">{score:.2f}</div>
                        <div style="font-size:11px;color:#64748b;text-transform:uppercase;
                             letter-spacing:1px;margin-top:4px;">{dim}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Flagged outputs
        flagged = bf.get("flagged_outputs", [])
        if flagged:
            st.markdown("#### 🚩 Flagged Test Scenarios")
            for item in flagged:
                severity = item.get("severity", "medium")
                with st.expander(f"{item.get('concern', 'Flagged output')}"):
                    st.markdown(f"**Severity:** {_severity_badge(severity)}", unsafe_allow_html=True)
                    st.markdown(f"**Test Prompt:** {item.get('prompt', 'N/A')}")
                    st.markdown(f"**Predicted Response:** {item.get('predicted_response', item.get('response_excerpt', 'N/A'))}")
                    st.markdown(f"**Concern:** {item.get('concern', 'N/A')}")

        if bf.get("recommendations"):
            st.markdown("#### ✅ Recommendations")
            for i, rec in enumerate(bf["recommendations"], 1):
                st.markdown(f"**{i}.** {rec}")

        with st.expander("🔧 Raw JSON (for developers)"):
            st.json(bf)

    # ──────────────────────────────────────────────────────────────
    # TAB: Passport
    # ──────────────────────────────────────────────────────────────
    with tab_passport:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:20px;font-weight:700;color:#e2e8f0;margin-bottom:4px;">
                📄 AI Compliance Passport
            </div>
            <div style="color:#64748b;font-size:13px;">
                Audit ID: {passport.get('audit_id', 'N/A')} · {passport.get('timestamp', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Target System:** {passport.get('target_model', 'N/A')}")
        st.markdown(f"**Overall Score:** {passport.get('overall_score', 'N/A')}/100")
        st.markdown(f"**Decision:** {passport.get('certification_decision', 'N/A')}")

        exec_summary = passport.get("executive_summary", "")
        if exec_summary:
            st.markdown("#### 📝 Executive Summary")
            st.markdown(exec_summary)

        if passport.get("key_issues"):
            st.markdown("#### ⚠️ Key Issues")
            for i, issue in enumerate(passport["key_issues"], 1):
                st.markdown(f"**{i}.** {issue}")

        st.markdown("---")
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        with dl_col1:
            st.download_button(
                "⬇️ Download Passport (JSON)",
                data=json.dumps(passport, indent=2, default=str),
                file_name=f"compliance_passport_{result.get('audit_id', 'unknown')}.json",
                mime="application/json",
                use_container_width=True,
            )
        with dl_col2:
            try:
                from src.pdf_passport import generate_passport_pdf
                pdf_bytes = generate_passport_pdf(passport)
                st.download_button(
                    "⬇️ Download Passport (PDF)",
                    data=pdf_bytes,
                    file_name=f"compliance_passport_{result.get('audit_id', 'unknown')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
        with dl_col3:
            # Plain-text version for non-technical stakeholders
            lines = [
                f"AI COMPLIANCE PASSPORT",
                f"{'=' * 40}",
                f"Target: {passport.get('target_model', 'N/A')}",
                f"Audit ID: {passport.get('audit_id', 'N/A')}",
                f"Date: {passport.get('timestamp', 'N/A')}",
                f"Score: {passport.get('overall_score', 'N/A')}/100",
                f"Decision: {passport.get('certification_decision', 'N/A')}",
                f"",
                f"EXECUTIVE SUMMARY",
                f"{'-' * 40}",
                exec_summary,
                f"",
                f"KEY ISSUES",
                f"{'-' * 40}",
            ]
            for i, issue in enumerate(passport.get("key_issues", []), 1):
                lines.append(f"{i}. {issue}")
            st.download_button(
                "⬇️ Download Passport (Text)",
                data="\n".join(lines),
                file_name=f"compliance_passport_{result.get('audit_id', 'unknown')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with st.expander("🔧 Raw JSON (for developers)"):
            st.json(passport)

else:
    # ── Landing state — no audit has been run yet ─────────────────
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:48px;">
        <div style="font-size:48px;margin-bottom:16px;">🔍</div>
        <div style="font-size:20px;font-weight:600;color:#e2e8f0;">Ready to Audit</div>
        <div style="color:#94a3b8;margin-top:8px;max-width:500px;margin-left:auto;margin-right:auto;">
            Configure your target model in the sidebar and click
            <strong>"Run Compliance Audit"</strong> to begin the multi-agent
            safety assessment.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick info cards
    col1, col2, col3, col4 = st.columns(4)
    info = [
        ("📜", "Legal Auditor", "EU AI Act & GDPR compliance checks"),
        ("🔥", "Red-Team", "Adversarial jailbreak attack simulations"),
        ("🔒", "Privacy", "PII detection & secrets scanning"),
        ("⚖️", "Bias", "Toxicity & demographic fairness analysis"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], info):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:32px;margin-bottom:12px;">{icon}</div>
                <div style="font-size:16px;font-weight:600;color:#e2e8f0;">{title}</div>
                <div style="color:#64748b;font-size:12px;margin-top:8px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
