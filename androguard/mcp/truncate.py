"""Paging and text size caps for LLM-sized MCP responses."""

from __future__ import annotations

import os
from typing import Any, Sequence, TypeVar

T = TypeVar("T")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def default_list_limit() -> int:
    return _env_int("ANDROGUARD_MCP_MAX_LIST_ITEMS", 200)


def default_text_chars() -> int:
    return _env_int("ANDROGUARD_MCP_MAX_TEXT_CHARS", 32_000)


def default_findrefs_limit() -> int:
    return _env_int("ANDROGUARD_MCP_MAX_FINDREFS", 100)


def default_vulns_limit() -> int:
    return _env_int("ANDROGUARD_MCP_MAX_VULNS", 100)


def page_items(
    items: Sequence[T],
    *,
    offset: int = 0,
    limit: int | None = None,
) -> dict[str, Any]:
    if offset < 0:
        offset = 0
    if limit is None:
        limit = default_list_limit()
    if limit < 0:
        limit = 0
    total = len(items)
    chunk = list(items[offset : offset + limit])
    truncated = offset + len(chunk) < total
    out: dict[str, Any] = {
        "items": chunk,
        "total": total,
        "offset": offset,
        "limit": limit,
        "truncated": truncated,
    }
    if truncated:
        out["next_offset"] = offset + len(chunk)
        out["hint"] = f"call again with offset={out['next_offset']}"
    return out


def truncate_text(
    text: str,
    *,
    max_chars: int | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if max_chars is None:
        max_chars = default_text_chars()
    if max_chars < 0:
        max_chars = 0
    truncated = len(text) > max_chars
    body = text[:max_chars] if truncated else text
    out: dict[str, Any] = {
        "source": body,
        "chars": len(text),
        "returned_chars": len(body),
        "truncated": truncated,
    }
    if meta:
        out.update(meta)
    if truncated:
        out["hint"] = (
            "source truncated; raise max_chars or use decompile_package "
            "to write files under workspace/output"
        )
    return out


def jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(x) for x in obj]
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)
