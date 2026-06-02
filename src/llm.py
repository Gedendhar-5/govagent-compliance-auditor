"""
GovAgent — Centralised LLM Factory (Phase 4 — Langfuse Tracing)
=================================================================
Provides a single ``get_llm()`` function that returns a configured
Groq-backed ChatModel with optional Langfuse distributed tracing.

When ``LANGFUSE_PUBLIC_KEY`` and ``LANGFUSE_SECRET_KEY`` are set in
.env, all LLM calls are automatically traced.  When not set, tracing
is silently skipped — zero overhead.

Usage::

    from src.llm import get_llm
    llm = get_llm(trace_name="legal_auditor")
    response = llm.invoke("Hello!")
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


# ---------------------------------------------------------------------------
# Langfuse configuration
# ---------------------------------------------------------------------------

def _langfuse_configured() -> bool:
    """Check if Langfuse credentials are available."""
    return bool(
        os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )


def _get_langfuse_handler(trace_name: str = "govagent"):
    """Create a Langfuse callback handler if configured."""
    try:
        from langfuse.langchain import CallbackHandler
        return CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            trace_name=trace_name,
        )
    except ImportError:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def get_llm(temperature: float = 0.3, model: str | None = None,
            trace_name: str | None = None):
    """Return a configured ChatGroq instance with optional Langfuse tracing.

    Parameters
    ----------
    temperature : float
        Sampling temperature (0 = deterministic, 1 = creative).
    model : str | None
        Groq model name.  Defaults to ``GROQ_MODEL`` env var or
        ``llama-3.3-70b-versatile``.
    trace_name : str | None
        Name for Langfuse trace grouping (e.g. ``"legal_auditor"``).
        Only used when Langfuse is configured.

    Returns
    -------
    ChatGroq
        A ready-to-use LangChain chat model.

    Raises
    ------
    ValueError
        If ``GROQ_API_KEY`` is not set or is still the placeholder.
    """
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("your-"):
        raise ValueError(
            "GROQ_API_KEY is not set.  Please add your key to the .env file.\n"
            "Get one at: https://console.groq.com/keys"
        )

    model_name = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Build callbacks list
    callbacks = []
    if _langfuse_configured():
        handler = _get_langfuse_handler(trace_name or "govagent")
        if handler:
            callbacks.append(handler)

    return ChatGroq(
        api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=4096,
        callbacks=callbacks if callbacks else None,
    )
