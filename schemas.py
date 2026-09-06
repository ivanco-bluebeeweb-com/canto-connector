"""Pydantic schemas for Canto Connector (C33. Digital Asset Management)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameters model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Primary Canto.")
    auth_token: str = Field(description="Canto App ID and App Secret or OAuth Bearer token.")
    base_url: str = Field(default="https://oauth.canto.com/api/v1", description="Canto API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class AssetRecord(BaseModel):
    id: str
    name: str
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = 0
    thumbnail_url: Optional[str] = None
    created_at: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

class AssetList(BaseModel):
    assets: list[AssetRecord]
    total: int

class ListAssetsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    limit: int = Field(default=20, ge=1, le=100, description="Max assets to return.")
    query: Optional[str] = Field(default=None, description="Search keyword or tag filter.")

class GetAssetParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    asset_id: str = Field(description="Unique asset identifier.")

class CollectionRecord(BaseModel):
    id: str
    name: str
    asset_count: int = 0
    raw: Dict[str, Any] = Field(default_factory=dict)

class CollectionList(BaseModel):
    collections: list[CollectionRecord]
    total: int

class ListCollectionsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class DamHealthRecord(BaseModel):
    status: str
    connection_ok: bool
    total_assets_sampled: int
    asset_types_distribution: Dict[str, int] = Field(default_factory=dict)
    summary: str
