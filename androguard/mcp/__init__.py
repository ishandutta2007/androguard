"""Androguard MCP server for LLM hosts (optional ``androguard[mcp]``)."""

from __future__ import annotations

__all__ = ["create_server", "main"]


def __getattr__(name: str):
    if name in ("create_server", "main"):
        from androguard.mcp.server import create_server, main

        return {"create_server": create_server, "main": main}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
