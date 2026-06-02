"""
GovAgent — AuditState Schema (Phase 2)
========================================
Defines the global shared state that flows through the LangGraph compliance
pipeline.  Every node reads from and writes to this TypedDict.

List fields use LangGraph's ``Annotated`` reducer pattern so that parallel
branches (fan-out) can **append** items without overwriting each other.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


# ---------------------------------------------------------------------------
# AuditState
# ---------------------------------------------------------------------------

class AuditState(TypedDict, total=False):
    """Shared state schema for the GovAgent compliance pipeline.

    Attributes
    ----------
    target_model_name : str
        Human-readable name of the LLM application under audit.
    target_model_description : str
        Short description or system prompt of the target model.
    audit_id : str
        Unique identifier (UUID4) assigned at the start of each audit run.
    status : str
        Current pipeline status — one of ``"pending"``, ``"running"``,
        ``"completed"``, or ``"failed"``.

    sample_outputs : list[str]
        Sample LLM outputs generated from the mock target, used by the
        Privacy Sentinel for PII / secrets scanning.

    legal_findings : dict
        Output from the Legal Auditor node.
    red_team_findings : dict
        Output from the Red-Team node.
    privacy_findings : dict
        Output from the Privacy Sentinel node.
    bias_findings : dict
        Output from the Bias Analyzer node.

    jailbreak_attempts : list[dict]
        Append-only log of each red-team attack cycle.
    overall_score : float
        Weighted compliance score computed by the Chief Compliance node.
    passport : dict
        Final "AI Compliance Passport" payload.
    errors : list[str]
        Append-only collection of errors encountered during the run.
    """

    # ── Inputs ──────────────────────────────────────────────────────────
    target_model_name: str
    target_model_description: str

    # ── Run metadata ────────────────────────────────────────────────────
    audit_id: str
    status: str

    # ── Sample outputs for Privacy Sentinel scanning ────────────────────
    sample_outputs: list[str]

    # ── Agent findings ──────────────────────────────────────────────────
    legal_findings: dict[str, Any]
    red_team_findings: dict[str, Any]
    privacy_findings: dict[str, Any]
    bias_findings: dict[str, Any]

    # ── Append-only lists (reducers) ────────────────────────────────────
    jailbreak_attempts: Annotated[list[dict[str, Any]], operator.add]
    errors: Annotated[list[str], operator.add]

    # ── Aggregated outputs ──────────────────────────────────────────────
    overall_score: float
    passport: dict[str, Any]
