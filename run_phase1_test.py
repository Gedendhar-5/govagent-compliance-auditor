#!/usr/bin/env python3
"""
GovAgent — End-to-End Test Runner (Phase 2)
=============================================
Invokes the compiled LangGraph compliance pipeline with real LLM-powered
agents (Groq), prints each node's output, and asserts correctness.

Usage::

    python run_phase1_test.py

"""

from __future__ import annotations

import io
import json
import os
import sys
import textwrap

# Force UTF-8 on Windows so emoji and special chars render correctly
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _divider(title: str) -> None:
    """Print a section divider."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main() -> None:
    _divider("GovAgent -- Phase 2 Test Runner (LLM-Powered)")

    # ------------------------------------------------------------------
    # 1. Import the compiled graph
    # ------------------------------------------------------------------
    print("\n  Importing compiled graph ...")
    try:
        from src.graph import compiled_graph
    except Exception as exc:
        print(f"  FAIL: Could not import graph: {exc}")
        sys.exit(1)
    print("  OK: Graph imported successfully.\n")

    # ------------------------------------------------------------------
    # 2. Prepare sample input
    # ------------------------------------------------------------------
    sample_input = {
        "target_model_name": "Acme-ChatBot-v2",
        "target_model_description": (
            "A customer-service chatbot deployed on an e-commerce platform. "
            "Handles order enquiries, returns, and general FAQs. "
            "Uses GPT-4 as the backbone with a custom system prompt."
        ),
        "jailbreak_attempts": [],
        "errors": [],
    }

    _divider("Sample Input")
    print(json.dumps(sample_input, indent=2))

    # ------------------------------------------------------------------
    # 3. Run the graph (stream mode to show progress)
    # ------------------------------------------------------------------
    _divider("Running Compliance Audit (LLM-Powered)")
    print("  This may take 30-60 seconds as agents query Groq API...\n")

    for step_output in compiled_graph.stream(sample_input):
        for node_name, node_state in step_output.items():
            print(f"  [DONE] Node: {node_name}")
            if isinstance(node_state, dict):
                # Show the score if available
                for key, value in node_state.items():
                    if key.endswith("_findings") and isinstance(value, dict):
                        score = value.get("score", "N/A")
                        agent = value.get("agent", key)
                        status = value.get("status", "unknown")
                        print(f"         -> {agent}: score={score}, status={status}")
                    elif key == "status":
                        print(f"         -> status: {value}")
                    elif key == "audit_id":
                        print(f"         -> audit_id: {value}")
                    elif key == "overall_score":
                        print(f"         -> overall_score: {value}")

    # ------------------------------------------------------------------
    # 4. Get full merged state
    # ------------------------------------------------------------------
    _divider("Full Audit Results")
    print("  Re-invoking graph for final merged state...\n")

    full_result = compiled_graph.invoke(sample_input)

    # Print key results
    print(f"  Status:         {full_result.get('status')}")
    print(f"  Audit ID:       {full_result.get('audit_id')}")
    print(f"  Overall Score:  {full_result.get('overall_score')}")

    passport = full_result.get("passport", {})
    print(f"  Certification:  {passport.get('certification_decision', 'N/A')}")

    # Print breakdown
    breakdown = passport.get("breakdown", {})
    if breakdown:
        print("\n  Score Breakdown:")
        for dim, info in breakdown.items():
            print(f"    {dim:12s}: {info.get('score', 'N/A')}/100 ({info.get('weight', '')})")

    # Print executive summary
    exec_summary = passport.get("executive_summary", "")
    if exec_summary:
        print(f"\n  Executive Summary:")
        for line in textwrap.wrap(exec_summary, width=70):
            print(f"    {line}")

    # Print jailbreak attempts
    attempts = full_result.get("jailbreak_attempts", [])
    if attempts:
        print(f"\n  Jailbreak Attempts ({len(attempts)}):")
        for a in attempts:
            status = "SUCCESS" if a.get("success") else "BLOCKED"
            print(f"    Cycle {a.get('cycle', '?')}: [{status}] {a.get('prompt', '')[:70]}...")

    # ------------------------------------------------------------------
    # 5. Assertions
    # ------------------------------------------------------------------
    _divider("Assertions")

    passed = 0
    failed = 0

    def _assert(label: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            print(f"  PASS: {label}")
            passed += 1
        else:
            print(f"  FAIL: {label}")
            failed += 1

    _assert(
        "status == 'completed'",
        full_result.get("status") == "completed",
    )
    _assert(
        "overall_score is a float in [0, 100]",
        isinstance(full_result.get("overall_score"), (int, float))
        and 0 <= full_result["overall_score"] <= 100,
    )
    _assert(
        "passport is non-empty dict",
        isinstance(full_result.get("passport"), dict)
        and len(full_result["passport"]) > 0,
    )
    _assert(
        "passport contains certification_decision",
        "certification_decision" in full_result.get("passport", {}),
    )
    _assert(
        "passport contains executive_summary",
        bool(full_result.get("passport", {}).get("executive_summary")),
    )
    _assert(
        "audit_id is set",
        bool(full_result.get("audit_id")),
    )
    _assert(
        "legal_findings present with score",
        isinstance(full_result.get("legal_findings"), dict)
        and "score" in full_result.get("legal_findings", {}),
    )
    _assert(
        "red_team_findings present with score",
        isinstance(full_result.get("red_team_findings"), dict)
        and "score" in full_result.get("red_team_findings", {}),
    )
    _assert(
        "privacy_findings present with pii_detected",
        isinstance(full_result.get("privacy_findings"), dict)
        and "pii_detected" in full_result.get("privacy_findings", {}),
    )
    _assert(
        "bias_findings present with toxicity_score",
        isinstance(full_result.get("bias_findings"), dict)
        and "toxicity_score" in full_result.get("bias_findings", {}),
    )
    _assert(
        "jailbreak_attempts has >= 1 entry",
        isinstance(full_result.get("jailbreak_attempts"), list)
        and len(full_result["jailbreak_attempts"]) >= 1,
    )
    _assert(
        "sample_outputs were generated",
        isinstance(full_result.get("sample_outputs"), list)
        and len(full_result["sample_outputs"]) > 0,
    )

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    _divider("Summary")
    total = passed + failed
    print(f"\n  {passed}/{total} assertions passed.")
    if failed == 0:
        print("\n  Phase 2 test PASSED -- all agents working with Groq LLM!\n")
        sys.exit(0)
    else:
        print(f"\n  Phase 2 test FAILED -- {failed} assertion(s) broken.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
