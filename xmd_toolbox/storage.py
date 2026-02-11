"""Storage interface for XMD ToolBox.

Placeholder module. All methods are stubs until the metadata schema and S3 layout are defined.
"""

from __future__ import annotations

from typing import Iterable, Protocol


class StorageBackend(Protocol):
    """Protocol for storage backends.

    Placeholder protocol. Methods are intentionally unimplemented.
    """

    def list_assets(self, asset_type: str) -> Iterable[str]:
        """Return asset identifiers for a given asset type.

        Placeholder stub.
        """
        raise NotImplementedError("Storage backend is not implemented yet.")

    def get_metadata(self, asset_id: str) -> dict:
        """Return metadata for a given asset.

        Placeholder stub.
        """
        raise NotImplementedError("Storage backend is not implemented yet.")

    def put_metadata(self, asset_id: str, metadata: dict) -> None:
        """Persist metadata for a given asset.

        Placeholder stub.
        """
        raise NotImplementedError("Storage backend is not implemented yet.")


class S3Storage:
    """AWS S3 storage backend.

    Placeholder class. Implementation is deferred.
    """

    def __init__(self, bucket_name: str) -> None:
        """Initialize storage with the S3 bucket name.

        Placeholder stub.
        """
        self.bucket_name = bucket_name

    def list_assets(self, asset_type: str) -> Iterable[str]:
        """Return asset identifiers for a given asset type.

        Placeholder stub.
        """
        raise NotImplementedError("S3 storage is not implemented yet.")

    def get_metadata(self, asset_id: str) -> dict:
        """Return metadata for a given asset.

        Placeholder stub.
        """
        raise NotImplementedError("S3 storage is not implemented yet.")

    def put_metadata(self, asset_id: str, metadata: dict) -> None:
        """Persist metadata for a given asset.

        Placeholder stub.
        """
        raise NotImplementedError("S3 storage is not implemented yet.")
