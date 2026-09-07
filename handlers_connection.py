"""Connection management for Canto Connector."""
from __future__ import annotations
import uuid
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from canto_client import CantoClient

async def resolve_client(ctx, connection_id: str = "") -> CantoClient:
    connections = await ctx.store.get("connections", [])
    if not connections:
        raise ValueError("No Canto connections configured. Use connect_canto first.")
    conn = None
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                conn = c
                break
        if not conn:
            raise ValueError(f"Connection {connection_id} not found.")
    else:
        conn = connections[0]
    return CantoClient(auth_token=conn["auth_token"], base_url=conn.get("base_url", ""))

@chat.function(
    "connect_canto",
    "Connect Canto account via credentials.",
    action_type="write",
    chain_callable=True,
    event="canto-connector.connect_canto",
    effects=["create:connection"],
    data_model=ConnectionRecord
)
async def connect_canto(ctx, params: ConnectParams) -> ActionResult:
    """Connect Canto DAM account."""
    client = CantoClient(auth_token=params.auth_token, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to authenticate with Canto: {res.get('error')}")

    connections = await ctx.store.get("connections", [])
    masked = params.auth_token[:6] + "..." if len(params.auth_token) > 6 else "***"
    record = {
        "id": f"conn_{uuid.uuid4().hex[:8]}",
        "label": params.label or "Primary Canto",
        "auth_token": params.auth_token,
        "masked_key": masked,
        "base_url": params.base_url,
        "is_active": True
    }
    for c in connections:
        c["is_active"] = False
    connections.append(record)
    await ctx.store.set("connections", connections)
    return ActionResult.success(
        {"id": record["id"], "label": record["label"], "masked_key": record["masked_key"], "base_url": record["base_url"], "is_active": True},
        summary=f"Connected Canto account '{record['label']}'."
    )

@chat.function(
    "list_connections",
    "List configured Canto connections.",
    action_type="read",
    chain_callable=True,
    event="canto-connector.list_connections",
    effects=["read:connections"],
    data_model=ConnectionList
)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """List configured connections."""
    conns = await ctx.store.get("connections", [])
    items = [
        ConnectionRecord(
            id=c["id"],
            label=c.get("label", ""),
            masked_key=c.get("masked_key", "***"),
            base_url=c.get("base_url", ""),
            is_active=c.get("is_active", False)
        )
        for c in conns
    ]
    return ActionResult.success({"connections": [i.model_dump() for i in items], "total": len(items)}, summary="Connections listed.")

@chat.function(
    "disconnect_canto",
    "Disconnect Canto account and delete stored credentials.",
    action_type="destructive",
    chain_callable=True,
    event="canto-connector.disconnect_canto",
    effects=["delete:connection"],
    data_model=DeleteResult
)
async def disconnect_canto(ctx, params: ConnectionIdParams) -> ActionResult:
    """Disconnect account."""
    connections = await ctx.store.get("connections", [])
    if not connections:
        return ActionResult.error("No active connections to disconnect.")

    target_id = params.connection_id
    if not target_id:
        target_id = connections[0]["id"]

    new_conns = [c for c in connections if c.get("id") != target_id]
    if len(new_conns) == len(connections):
        return ActionResult.error(f"Connection {target_id} not found.")

    if new_conns and not any(c.get("is_active") for c in new_conns):
        new_conns[0]["is_active"] = True

    await ctx.store.set("connections", new_conns)
    return ActionResult.success({"success": True, "message": f"Disconnected connection {target_id}."}, summary=f"Disconnected Canto connection.")
