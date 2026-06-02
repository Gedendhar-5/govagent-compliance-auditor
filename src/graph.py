"""
GovAgent — LangGraph Workflow Definition
==========================================
Builds, compiles, and exports the compliance-audit ``StateGraph``.

Graph topology
--------------
::

    START → init_audit
               │
        ┌──────┼──────────┬──────────────┐
        ▼      ▼          ▼              ▼
     legal  red_team  privacy_sentinel  bias_analyzer   ← fan-out
        └──────┼──────────┴──────────────┘
               ▼
        chief_compliance                                ← fan-in
               │
              END

Fan-out is achieved by routing ``init_audit`` to all four specialist nodes
simultaneously.  Fan-in is achieved by having every specialist edge converge
on ``chief_compliance``.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents.bias_analyzer import bias_analyzer_node
from src.agents.compliance_officer import chief_compliance_node, init_audit_node
from src.agents.legal_auditor import legal_auditor_node
from src.agents.privacy_sentinel import privacy_sentinel_node
from src.agents.red_teamer import red_team_node
from src.state import AuditState

# ---------------------------------------------------------------------------
# Node names (constants for readability & refactoring safety)
# ---------------------------------------------------------------------------

INIT_AUDIT         = "init_audit"
LEGAL_AUDITOR      = "legal_auditor"
RED_TEAM           = "red_team"
PRIVACY_SENTINEL   = "privacy_sentinel"
BIAS_ANALYZER      = "bias_analyzer"
CHIEF_COMPLIANCE   = "chief_compliance"


def build_graph() -> StateGraph:
    """Construct (but do not compile) the GovAgent compliance graph.

    Returns
    -------
    StateGraph
        An uncompiled ``StateGraph[AuditState]`` ready for ``.compile()``.
    """
    graph = StateGraph(AuditState)

    # ── Register nodes ─────────────────────────────────────────────────
    graph.add_node(INIT_AUDIT,       init_audit_node)
    graph.add_node(LEGAL_AUDITOR,    legal_auditor_node)
    graph.add_node(RED_TEAM,         red_team_node)
    graph.add_node(PRIVACY_SENTINEL, privacy_sentinel_node)
    graph.add_node(BIAS_ANALYZER,    bias_analyzer_node)
    graph.add_node(CHIEF_COMPLIANCE, chief_compliance_node)

    # ── Entry edge ─────────────────────────────────────────────────────
    graph.add_edge(START, INIT_AUDIT)

    # ── Fan-out: init_audit → all four specialists simultaneously ──────
    graph.add_conditional_edges(
        INIT_AUDIT,
        # Router function: always dispatch to ALL specialists
        lambda _state: [LEGAL_AUDITOR, RED_TEAM, PRIVACY_SENTINEL, BIAS_ANALYZER],
        # Mapping (identity — node names match the router return values)
        {
            LEGAL_AUDITOR:    LEGAL_AUDITOR,
            RED_TEAM:         RED_TEAM,
            PRIVACY_SENTINEL: PRIVACY_SENTINEL,
            BIAS_ANALYZER:    BIAS_ANALYZER,
        },
    )

    # ── Fan-in: every specialist → chief_compliance ────────────────────
    graph.add_edge(LEGAL_AUDITOR,    CHIEF_COMPLIANCE)
    graph.add_edge(RED_TEAM,         CHIEF_COMPLIANCE)
    graph.add_edge(PRIVACY_SENTINEL, CHIEF_COMPLIANCE)
    graph.add_edge(BIAS_ANALYZER,    CHIEF_COMPLIANCE)

    # ── Exit edge ──────────────────────────────────────────────────────
    graph.add_edge(CHIEF_COMPLIANCE, END)

    return graph


# ---------------------------------------------------------------------------
# Pre-compiled graph — importable by other modules
# ---------------------------------------------------------------------------

compiled_graph = build_graph().compile()
