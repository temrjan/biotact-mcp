"""MCP server for Biotact knowledge base.

Exposes three tools: biotact_search, biotact_stats, biotact_get_transcript.
Reads BIOTACT_API_KEY from environment. Runs via stdio (Claude Code / Desktop).
"""

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

API_URL = "https://core.biotact.uz/api/v1/knowledge"
TIMEOUT = 30.0

mcp = FastMCP("Biotact Knowledge Base")


def _api_key() -> str:
    key = os.environ.get("BIOTACT_API_KEY", "")
    if not key:
        raise RuntimeError("BIOTACT_API_KEY environment variable is not set")
    return key


def _headers() -> dict[str, str]:
    return {"X-API-Key": _api_key()}


def _fmt_results(data: dict[str, Any]) -> str:
    """Format search results into readable text."""
    results = data.get("results", [])
    if not results:
        return f"No results found for query: {data.get('query', '')}"

    lines: list[str] = [f"Query: {data.get('query', '')}", f"Found: {len(results)} results\n"]
    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})
        lines.append(f"[{i}] score={r.get('score', 0):.3f}")
        lines.append(f"    source: {r.get('source', '')} | year: {meta.get('year', '?')}")
        lines.append(f"    url: {meta.get('source_url', '')}")
        lines.append(f"    nutrients: {meta.get('nutrients', [])} | specialty: {meta.get('specialty', '')}")
        lines.append(f"    age_group: {meta.get('age_group', [])} | has_full_text: {meta.get('has_full_text', False)}")
        lines.append(f"    content: {r.get('content', '')[:300]}...")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def biotact_search(
    query: str,
    source: str = "",
    limit: int = 5,
    threshold: float = 0.0,
) -> str:
    """Search the Biotact knowledge base.

    Args:
        query: Search query in any language (Russian queries auto-translated for Dr. Berg).
        source: Filter by collection. One of: biotact, dr_berg, nutrition, medical, files.
                Leave empty to search all collections.
        limit: Number of results (1-50). Defaults to 5.
        threshold: Minimum similarity score (0.0-1.0). Defaults to 0.0.

    Returns:
        Formatted search results with scores, metadata, and content snippets.
    """
    params: dict[str, str | int | float] = {"q": query, "limit": limit}
    if source:
        params["source"] = source
    if threshold > 0.0:
        params["threshold"] = threshold

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{API_URL}/search", params=params, headers=_headers())
            resp.raise_for_status()
            return _fmt_results(resp.json())
    except httpx.TimeoutException:
        return "Error: request timed out (>30s). The server may be overloaded."
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def biotact_stats() -> str:
    """Get statistics for all Biotact knowledge base collections.

    Returns:
        Table with collection names and document counts.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{API_URL}/stats", headers=_headers())
            resp.raise_for_status()
            data = resp.json()

        collections = data.get("collections", {})
        total = data.get("total_points", 0)

        lines = ["Biotact Knowledge Base — Collections", "=" * 40]
        for name, count in collections.items():
            lines.append(f"  {name:<20} {count:>6} vectors")
        lines.append("-" * 40)
        lines.append(f"  {'TOTAL':<20} {total:>6} vectors")

        return "\n".join(lines)
    except httpx.TimeoutException:
        return "Error: request timed out (>30s)."
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def biotact_get_transcript(video_id: str) -> str:
    """Get full transcript of a Dr. Berg YouTube video.

    Args:
        video_id: YouTube video ID (e.g. 'dQw4w9WgXcQ' from youtube.com/watch?v=dQw4w9WgXcQ).

    Returns:
        Full transcript text, or an error message if not found.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{API_URL}/transcript/{video_id}", headers=_headers())
            resp.raise_for_status()
            data = resp.json()
            return data.get("transcript", str(data))
    except httpx.TimeoutException:
        return "Error: request timed out (>30s)."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Transcript not found for video_id: {video_id}"
        return f"Error {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run()
