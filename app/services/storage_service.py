"""Local filesystem storage service."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings


class StorageService:
    def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        raise NotImplementedError

    def get_bytes(self, key: str) -> bytes:
        raise NotImplementedError

    def get_local_path(self, key: str) -> Path | None:
        return None


class LocalStorageService(StorageService):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get_bytes(self, key: str) -> bytes:
        path = self._path(key)
        return path.read_bytes()

    def get_local_path(self, key: str) -> Path | None:
        path = self._path(key)
        return path if path.exists() else None


def get_storage_service() -> StorageService:
    return LocalStorageService(settings.UPLOAD_DIR)
