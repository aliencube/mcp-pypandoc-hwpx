"""Azure Blob Storage helper for uploading and streaming converted files."""

from __future__ import annotations

import logging
import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient

logger = logging.getLogger("pypandoc-hwpx")

_DEFAULT_CONTAINER = "hwpx"


class BlobStore:
    """Thin wrapper around Azure Blob Storage for upload / download."""

    def __init__(
        self,
        account_url: str,
        container_name: str = _DEFAULT_CONTAINER,
    ) -> None:
        credential = DefaultAzureCredential()
        self._service = BlobServiceClient(account_url, credential=credential)
        self._container: ContainerClient = self._service.get_container_client(
            container_name,
        )
        self._ensure_container()

    # ------------------------------------------------------------------
    def _ensure_container(self) -> None:
        """Create the container if it does not already exist."""
        try:
            self._container.create_container()
            logger.info("Created blob container: %s", self._container.container_name)
        except Exception:
            # Container already exists — safe to ignore.
            pass

    # ------------------------------------------------------------------
    def upload(self, blob_name: str, file_path: str) -> None:
        """Upload a local file to the container, overwriting if it exists."""
        with open(file_path, "rb") as fh:
            self._container.upload_blob(blob_name, fh, overwrite=True)
        logger.info("Uploaded %s -> %s", file_path, blob_name)

    # ------------------------------------------------------------------
    def download_stream(self, blob_name: str):
        """Return a ``StorageStreamDownloader`` for *blob_name*."""
        return self._container.download_blob(blob_name)

    # ------------------------------------------------------------------
    def exists(self, blob_name: str) -> bool:
        """Check whether *blob_name* exists in the container."""
        blob = self._container.get_blob_client(blob_name)
        return blob.exists()


def create_blob_store_from_env() -> BlobStore | None:
    """Create a ``BlobStore`` from environment variables.

    Returns ``None`` when the required ``AZURE_STORAGE_ACCOUNT_URL``
    variable is not set (i.e. blob storage is not configured).
    """
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    if not account_url:
        return None
    container = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", _DEFAULT_CONTAINER)
    return BlobStore(account_url, container)
