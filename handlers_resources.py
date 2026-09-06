"""Resource handlers for Canto Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    NoParams, ListAssetsParams, GetAssetParams, AssetRecord, AssetList,
    ListCollectionsParams, CollectionRecord, CollectionList, DamHealthRecord
)
from handlers_connection import resolve_client

@chat.function(
    "list_assets",
    "List digital assets in Canto DAM.",
    action_type="read",
    chain_callable=True,
    event="canto-connector.list_assets",
    effects=["read:assets"],
    data_model=AssetList
)
async def list_assets(params: ListAssetsParams, ctx) -> ActionResult:
    """List assets from DAM."""
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_assets = await client.list_assets(limit=params.limit, query=params.query)
        items = []
        for a in raw_assets:
            aid = str(a.get("id", a.get("key", a.get("assetId", ""))))
            name = a.get("name", a.get("filename", a.get("title", f"Asset {aid}")))
            ctype = a.get("contentType", a.get("mime_type", a.get("type", "unknown")))
            size = a.get("fileSize", a.get("size", 0))
            thumb = a.get("thumbnailUrl", a.get("preview_url", a.get("url", None)))
            created = a.get("created", a.get("created_at", a.get("creationDate", None)))
            items.append(AssetRecord(
                id=aid,
                name=name,
                content_type=ctype,
                file_size_bytes=int(size) if isinstance(size, (int, float)) else 0,
                thumbnail_url=thumb,
                created_at=str(created) if created else None,
                raw=a
            ))
        return ActionResult.ok({"assets": [i.model_dump() for i in items], "total": len(items)})
    except Exception as e:
        return ActionResult.error(f"Error listing Canto assets: {e}")

@chat.function(
    "get_asset",
    "Get details of one digital asset in Canto.",
    action_type="read",
    chain_callable=True,
    event="canto-connector.get_asset",
    effects=["read:asset"],
    data_model=AssetRecord
)
async def get_asset(params: GetAssetParams, ctx) -> ActionResult:
    """Get single asset metadata."""
    try:
        client = await resolve_client(ctx, params.connection_id)
        a = await client.get_asset(params.asset_id)
        aid = str(a.get("id", params.asset_id))
        name = a.get("name", a.get("filename", a.get("title", f"Asset {aid}")))
        ctype = a.get("contentType", a.get("mime_type", a.get("type", "unknown")))
        size = a.get("fileSize", a.get("size", 0))
        thumb = a.get("thumbnailUrl", a.get("preview_url", a.get("url", None)))
        created = a.get("created", a.get("created_at", None))
        record = AssetRecord(
            id=aid,
            name=name,
            content_type=ctype,
            file_size_bytes=int(size) if isinstance(size, (int, float)) else 0,
            thumbnail_url=thumb,
            created_at=str(created) if created else None,
            raw=a
        )
        return ActionResult.ok(record.model_dump())
    except Exception as e:
        return ActionResult.error(f"Error fetching asset {params.asset_id}: {e}")

@chat.function(
    "list_collections",
    "List albums or collections in Canto.",
    action_type="read",
    chain_callable=True,
    event="canto-connector.list_collections",
    effects=["read:collections"],
    data_model=CollectionList
)
async def list_collections(params: ListCollectionsParams, ctx) -> ActionResult:
    """List DAM collections/albums."""
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_cols = await client.list_collections()
        items = []
        for c in raw_cols:
            cid = str(c.get("id", c.get("key", "")))
            cname = c.get("name", c.get("title", f"Collection {cid}"))
            cnt = c.get("assetCount", c.get("count", c.get("mediaCount", 0)))
            items.append(CollectionRecord(
                id=cid,
                name=cname,
                asset_count=int(cnt) if isinstance(cnt, (int, float)) else 0,
                raw=c
            ))
        return ActionResult.ok({"collections": [i.model_dump() for i in items], "total": len(items)})
    except Exception as e:
        return ActionResult.error(f"Error listing collections: {e}")

@chat.function(
    "audit_dam_health",
    "Audit Canto digital asset library health and type distribution.",
    action_type="read",
    chain_callable=True,
    event="canto-connector.audit_dam_health",
    effects=["read:dam_health"],
    data_model=DamHealthRecord
)
async def audit_dam_health(params: ListAssetsParams, ctx) -> ActionResult:
    """Audit DAM health."""
    try:
        client = await resolve_client(ctx, params.connection_id)
        assets = await client.list_assets(limit=50)
        types: dict[str, int] = {}
        for a in assets:
            t = a.get("contentType", a.get("type", "other"))
            types[t] = types.get(t, 0) + 1

        rec = DamHealthRecord(
            status="healthy" if len(assets) > 0 else "empty",
            connection_ok=True,
            total_assets_sampled=len(assets),
            asset_types_distribution=types,
            summary=f"Canto library contains {len(assets)} sampled assets across {len(types)} media formats."
        )
        return ActionResult.ok(rec.model_dump(), summary=rec.summary)
    except Exception as e:
        return ActionResult.error(f"Error auditing DAM health: {e}")
