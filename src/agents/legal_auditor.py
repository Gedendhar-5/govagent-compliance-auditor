"""
GovAgent — Legal Auditor Agent (Phase 3 — RAG-Enhanced)
=========================================================
Uses Groq LLM with RCTFCE prompt framework AND retrieval-augmented
generation (RAG) via the FAISS vector store.

Before calling the LLM, this agent:
1. Queries the regulation database with the target model description
2. Retrieves the top-5 most relevant EU AI Act / GDPR clauses
3. Injects the retrieved clauses as reference material into the prompt

This grounds the analysis in actual regulation text.
"""

from __future__ import annotations

import json
import traceback
from typing import Any

from src.llm import get_llm
from src.mcp.tools import format_clauses_for_prompt, query_compliance_db

# ---------------------------------------------------------------------------
# RCTFCE Prompt Template (RAG-enhanced)
# ---------------------------------------------------------------------------

_LEGAL_PROMPT = """\
## Role
You are a **Senior Legal Compliance Auditor** specializing in AI regulation, \
with deep expertise in the EU AI Act and the General Data Protection Regulation (GDPR).

## Context
You are auditing an AI system before deployment.  The system under review is:
- **Name:** {target_model_name}
- **Description:** {target_model_description}

## Reference Material (Retrieved from Regulation Database)
The following regulation clauses have been retrieved from the compliance \
database as the most relevant to this audit.  Use these as the primary \
basis for your analysis:

{retrieved_clauses}

## Task
Perform a thorough legal compliance assessment using the retrieved regulation \
clauses above:
1. For each retrieved clause, assess whether the target AI system complies.
2. Identify specific legal compliance gaps with article citations.
3. Provide actionable recommendations referencing the specific articles.
4. Classify the overall risk level of the system.

## Format
Return your analysis as a JSON object (and nothing else) with this exact schema:
{{
    "score": <float 0-100, where 100 is fully compliant>,
    "regulation_coverage": [<list of regulation articles actually analysed>],
    "issues": [<list of specific compliance gaps, citing article numbers>],
    "recommendations": [<list of actionable steps, citing articles>],
    "risk_classification": "<low | limited | high | unacceptable>",
    "summary": "<2-3 sentence executive summary>",
    "retrieved_clauses_used": <number of retrieved clauses that were relevant>
}}

## Constraints
- Ground your analysis in the retrieved regulation text — cite article numbers.
- Score conservatively: assume worst-case if information is missing.
- Maximum 5 issues and 5 recommendations.
- Output ONLY valid JSON, no markdown code fences, no extra text.

## Example
For a medical diagnosis chatbot with retrieved clauses about Art. 6, Art. 9, Art. 22:
{{
    "score": 45.0,
    "regulation_coverage": ["EU AI Act Art. 6", "EU AI Act Art. 9", "GDPR Art. 22"],
    "issues": ["High-risk AI system under EU AI Act Art. 6(2) — requires conformity assessment"],
    "recommendations": ["Conduct conformity assessment per Art. 43 before deployment"],
    "risk_classification": "high",
    "summary": "This medical AI is classified as high-risk under Art. 6(2) and requires significant compliance work.",
    "retrieved_clauses_used": 3
}}
"""


def legal_auditor_node(state: dict[str, Any]) -> dict[str, Any]:
    """RAG-enhanced Legal Auditor node.

    1. Retrieves relevant regulation clauses from FAISS vector store
    2. Injects them into the RCTFCE prompt
    3. Calls Groq LLM for grounded legal analysis

    Parameters
    ----------
    state : dict
        Current ``AuditState`` snapshot.

    Returns
    -------
    dict
        State update containing ``legal_findings``.
    """
    target_name = state.get("target_model_name", "Unknown Model")
    target_desc = state.get("target_model_description", "No description provided.")

    # Step 1: Retrieve relevant regulation clauses (RAG)
    retrieved_clauses = []
    try:
        # Query with the target description for relevance
        retrieved_clauses = query_compliance_db(target_desc, top_k=5)
        # Also query with common compliance concerns
        extra_clauses = query_compliance_db(
            "automated decision making AI transparency human oversight data protection",
            top_k=3,
        )
        # Merge and deduplicate
        seen_ids = {c["id"] for c in retrieved_clauses}
        for c in extra_clauses:
            if c["id"] not in seen_ids:
                retrieved_clauses.append(c)
                seen_ids.add(c["id"])
    except Exception:
        pass  # Will proceed without retrieved clauses

    formatted_clauses = format_clauses_for_prompt(retrieved_clauses)

    # Step 2: Call LLM with RAG-enhanced prompt
    try:
        llm = get_llm(temperature=0.2, trace_name="legal_auditor")

        prompt = _LEGAL_PROMPT.format(
            target_model_name=target_name,
            target_model_description=target_desc,
            retrieved_clauses=formatted_clauses,
        )

        response = llm.invoke(prompt)
        raw_text = response.content.strip()

        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].strip()
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

        analysis = json.loads(raw_text)

        findings: dict[str, Any] = {
            "agent": "Legal Auditor",
            "target_model": target_name,
            "score": float(analysis.get("score", 50.0)),
            "regulation_coverage": analysis.get("regulation_coverage", []),
            "issues": analysis.get("issues", []),
            "recommendations": analysis.get("recommendations", []),
            "risk_classification": analysis.get("risk_classification", "unknown"),
            "summary": analysis.get("summary", ""),
            "retrieved_clauses": [
                {
                    "regulation": c["regulation"],
                    "article": c["article"],
                    "title": c["title"],
                    "relevance": c.get("similarity_score", 0),
                }
                for c in retrieved_clauses
            ],
            "retrieved_clauses_used": analysis.get("retrieved_clauses_used", len(retrieved_clauses)),
            "status": "completed",
        }

    except Exception as exc:
        findings = {
            "agent": "Legal Auditor",
            "target_model": target_name,
            "score": 50.0,
            "regulation_coverage": [],
            "issues": [f"Legal analysis failed: {exc}"],
            "recommendations": ["Re-run audit with valid API credentials."],
            "risk_classification": "unknown",
            "summary": f"Analysis could not be completed: {exc}",
            "retrieved_clauses": [],
            "retrieved_clauses_used": 0,
            "status": "error",
            "error_trace": traceback.format_exc(),
        }

    return {"legal_findings": findings}
