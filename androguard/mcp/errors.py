"""Structured errors for MCP tools."""

from __future__ import annotations

from typing import Any


class McpToolError(Exception):
    """Raised inside tools; converted to a JSON error payload."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        hint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint

    def to_dict(self) -> dict[str, Any]:
        err: dict[str, Any] = {
            "ok": False,
            "error": {
                "code": self.code,
                "message": self.message,
            },
        }
        if self.hint:
            err["error"]["hint"] = self.hint
        return err


def error_payload(
    code: str,
    message: str,
    *,
    hint: str | None = None,
) -> dict[str, Any]:
    return McpToolError(code, message, hint=hint).to_dict()
