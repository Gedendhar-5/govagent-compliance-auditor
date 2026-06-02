"""
GovAgent — MCP Client Tools
==============================
Provides helper functions that agents can call to interact with the
regulatory compliance database.  In Phase 3 this calls the FAISS vector
store directly; in production it would connect to the MCP server.

Usage::

    from src.mcp.tools import query_compliance_db
    clauses = query_compliance_db("automated decision making")
"""

from __future__ import annotations

from typing import Any

from src.mcp.vector_store import query_regulations


def query_compliance_db(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Query the compliance regulation database.

    Performs semantic search over EU AI Act and GDPR clauses using
    the FAISS vector store.

    Parameters
    ----------
    query : str
        Natural language query about AI regulations.
    top_k : int
        Number of results to return.

    Returns
    -------
    list[dict]
        Top-K matching regulation clauses, each containing:
        ``id``, ``regulation``, ``article``, ``title``, ``text``,
        and ``similarity_score``.
    """
    return query_regulations(query, top_k=top_k)


def format_clauses_for_prompt(clauses: list[dict[str, Any]]) -> str:
    """Format retrieved regulation clauses as text for LLM prompt injection.

    Parameters
    ----------
    clauses : list[dict]
        Regulation clauses from ``query_compliance_db()``.

    Returns
    -------
    str
        Formatted text block ready to be inserted into an LLM prompt.
    """
    if not clauses:
        return "No relevant regulations found."

    lines = ["The following regulation clauses are relevant to this audit:\n"]
    for i, c in enumerate(clauses, 1):
        lines.append(
            f"--- Clause {i} ---\n"
            f"Regulation: {c['regulation']}\n"
            f"Article: {c['article']}\n"
            f"Title: {c['title']}\n"
            f"Relevance: {c.get('similarity_score', 'N/A')}\n"
            f"Text: {c['text']}\n"
        )
    return "\n".join(lines)
