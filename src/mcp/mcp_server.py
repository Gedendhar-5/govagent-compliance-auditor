"""
GovAgent — Custom MCP Server for Regulatory Databases
=======================================================
Exposes a ``query_compliance_database`` tool and a ``list_regulations``
resource via the Model Context Protocol (MCP).

This server can be run standalone and connected to by MCP-compatible
clients.  For in-process usage (Phase 3), the Legal Auditor calls
``tools.query_compliance_db()`` directly.

Usage::

    python -m src.mcp.mcp_server
"""

from __future__ import annotations

import json
from typing import Any

try:
    from mcp.server import Server
    from mcp.types import TextContent, Tool
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False

from src.mcp.regulations import REGULATION_CLAUSES
from src.mcp.vector_store import query_regulations

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

if _MCP_AVAILABLE:
    server = Server("govagent-compliance-db")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Expose the query_compliance_database tool."""
        return [
            Tool(
                name="query_compliance_database",
                description=(
                    "Search the EU AI Act and GDPR regulation database using "
                    "semantic similarity. Returns the most relevant regulation "
                    "clauses for a given query."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query about AI regulations.",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5).",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool invocations."""
        if name == "query_compliance_database":
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 5)
            results = query_regulations(query, top_k=top_k)

            # Format results as readable text
            output_lines = [f"Found {len(results)} relevant regulations:\n"]
            for i, r in enumerate(results, 1):
                output_lines.append(
                    f"{i}. [{r['regulation']} {r['article']}] {r['title']} "
                    f"(relevance: {r['similarity_score']:.3f})\n"
                    f"   {r['text'][:200]}...\n"
                )

            return [TextContent(type="text", text="\n".join(output_lines))]

        raise ValueError(f"Unknown tool: {name}")


def get_all_regulations() -> list[dict[str, str]]:
    """Return the full list of indexed regulation articles.

    This serves as the ``list_regulations`` resource.

    Returns
    -------
    list[dict]
        All regulation clauses in the corpus.
    """
    return [
        {
            "id": c["id"],
            "regulation": c["regulation"],
            "article": c["article"],
            "title": c["title"],
        }
        for c in REGULATION_CLAUSES
    ]


# ---------------------------------------------------------------------------
# CLI entry point — run the MCP server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not _MCP_AVAILABLE:
        print("MCP SDK not installed.  Install with: pip install mcp")
        print("Running in standalone query mode instead.\n")

    print("GovAgent Compliance Database — MCP Server")
    print(f"  Regulations indexed: {len(REGULATION_CLAUSES)}")
    print(f"  Available tools: query_compliance_database")
    print(f"  Available resources: list_regulations\n")

    # Demo query
    print("  Demo query: 'human oversight AI systems'")
    results = query_regulations("human oversight AI systems", top_k=3)
    for r in results:
        print(f"    [{r['similarity_score']:.3f}] {r['regulation']} {r['article']}: {r['title']}")
