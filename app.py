"""Extension declaration, capabilities, health check for Canto Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    
    "canto-connector",
    version="0.1.0",
    display_name="Canto",
    icon="icon.svg",
    capabilities=["canto:manage"],
    description="Official Imperal connector for Canto (C30. Email Marketing & Newsletter). Manage operations securely."
)

app = ext
chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("canto_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Canto connection(s) configured." if count else "Not connected yet."
    }
