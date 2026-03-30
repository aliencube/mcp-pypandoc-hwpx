import argparse
import logging
import os
import tempfile
import uuid
from urllib.parse import quote, unquote, urlparse

import httpx
import pypandoc_hwpx
from mcp.server.fastmcp import FastMCP
from pypandoc_hwpx.PandocToHwpx import PandocToHwpx
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from src.blob import BlobStore, create_blob_store_from_env

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("pypandoc-hwpx")

# ---------------------------------------------------------------------------
# Resolve the reference HWPX file bundled with pypandoc-hwpx.
# ---------------------------------------------------------------------------
_BLANK_HWPX = os.path.join(os.path.dirname(pypandoc_hwpx.__file__), "blank.hwpx")

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP("pypandoc-hwpx")

# ---------------------------------------------------------------------------
# Blob storage & server base URL (initialised lazily in main())
# ---------------------------------------------------------------------------
_blob_store: BlobStore | None = None
_base_url: str | None = None


def _resolve_reference(reference_hwpx: str | None = None) -> str:
    """Return the path to the reference HWPX file to use for conversion."""
    if reference_hwpx and os.path.isfile(reference_hwpx):
        logger.debug("Using custom reference HWPX: %s", reference_hwpx)
        return reference_hwpx
    if os.path.isfile(_BLANK_HWPX):
        logger.debug("Using bundled reference HWPX: %s", _BLANK_HWPX)
        return _BLANK_HWPX
    logger.error("No reference HWPX file found")
    raise FileNotFoundError(
        "No reference HWPX file found.  Pass an explicit path via "
        "'reference_hwpx' or ensure pypandoc-hwpx is installed correctly."
    )


def _convert(input_path: str, output_path: str, reference_hwpx: str | None = None) -> str:
    """Run the conversion and return the absolute output path."""
    ref = _resolve_reference(reference_hwpx)
    logger.info("Converting %s -> %s (ref=%s)", input_path, output_path, ref)
    PandocToHwpx.convert_to_hwpx(input_path, output_path, ref)
    result = os.path.abspath(output_path)
    logger.info("Conversion complete: %s", result)
    return result


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def _is_url(path: str) -> bool:
    """Return ``True`` if *path* looks like an HTTP(S) URL."""
    return path.startswith("http://") or path.startswith("https://")


def _filename_from_url(url: str) -> str:
    """Extract the filename component from a URL."""
    parsed = urlparse(url)
    name = os.path.basename(unquote(parsed.path))
    return name if name else "download"


def _download_to_temp(url: str, dest_path: str) -> None:
    """Download *url* and save it to *dest_path*."""
    logger.info("Downloading %s", url)
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest_path, "wb") as fh:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    fh.write(chunk)
    logger.info("Downloaded %s -> %s", url, dest_path)


def _make_blob_name(original_filename: str) -> str:
    """Generate a unique blob name preserving the ``.hwpx`` extension."""
    stem = os.path.splitext(original_filename)[0]
    unique = uuid.uuid4().hex[:8]
    return f"{stem}-{unique}.hwpx"


def _convert_from_url(
    url: str,
    input_suffix: str,
    output_path: str | None,
    reference_hwpx: str | None,
) -> str:
    """Download a file from *url*, convert it, upload to blob, return link.

    If blob storage is not configured the converted file is saved to
    *output_path* (which must be provided in that case).
    """
    source_name = _filename_from_url(url)

    with tempfile.TemporaryDirectory() as tmp:
        # Download source file
        in_path = os.path.join(tmp, f"input{input_suffix}")
        _download_to_temp(url, in_path)

        # Determine blob / output name
        if output_path:
            blob_name = os.path.basename(output_path)
        else:
            blob_name = _make_blob_name(source_name)
        if not blob_name.endswith(".hwpx"):
            blob_name = os.path.splitext(blob_name)[0] + ".hwpx"
        out_path = os.path.join(tmp, blob_name)

        # Convert
        _convert(in_path, out_path, reference_hwpx)

        # Upload to blob storage if available
        if _blob_store is not None and _base_url is not None:
            _blob_store.upload(blob_name, out_path)
            download_url = f"{_base_url.rstrip('/')}/download/{blob_name}"
            logger.info("Upload complete — download URL: %s", download_url)
            return download_url

        # Fallback: save locally when blob storage is not configured
        if output_path is None:
            raise ValueError(
                "output_path is required when Azure Blob Storage is not configured "
                "and input_path is a URL."
            )
        dest = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(out_path, "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())
        logger.info("Saved converted file locally: %s", dest)
        return dest


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def docx_to_hwpx(
    input_path: str,
    output_path: str | None = None,
    reference_hwpx: str | None = None,
) -> str:
    """Convert a .docx file to a .hwpx file.

    Args:
        input_path: Local file path or URL to the source .docx file.
        output_path: Path where the resulting .hwpx file will be written.
                     Required for local input; optional when input_path is
                     a URL and Azure Blob Storage is configured.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file, or a download URL
        when the source was a URL and Azure Blob Storage is configured.
    """
    if _is_url(input_path):
        return _convert_from_url(input_path, ".docx", output_path, reference_hwpx)

    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if output_path is None:
        raise ValueError("output_path is required when input_path is a local file.")
    logger.info("docx_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


@mcp.tool()
def html_to_hwpx(
    input_path: str,
    output_path: str | None = None,
    reference_hwpx: str | None = None,
) -> str:
    """Convert an HTML file to a .hwpx file.

    Args:
        input_path: Local file path or URL to the source HTML file.
        output_path: Path where the resulting .hwpx file will be written.
                     Required for local input; optional when input_path is
                     a URL and Azure Blob Storage is configured.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file, or a download URL
        when the source was a URL and Azure Blob Storage is configured.
    """
    if _is_url(input_path):
        return _convert_from_url(input_path, ".html", output_path, reference_hwpx)

    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if output_path is None:
        raise ValueError("output_path is required when input_path is a local file.")
    logger.info("html_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


@mcp.tool()
def md_to_hwpx(
    input_path: str,
    output_path: str | None = None,
    reference_hwpx: str | None = None,
) -> str:
    """Convert a Markdown file to a .hwpx file.

    Args:
        input_path: Local file path or URL to the source Markdown (.md) file.
        output_path: Path where the resulting .hwpx file will be written.
                     Required for local input; optional when input_path is
                     a URL and Azure Blob Storage is configured.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file, or a download URL
        when the source was a URL and Azure Blob Storage is configured.
    """
    if _is_url(input_path):
        return _convert_from_url(input_path, ".md", output_path, reference_hwpx)

    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if output_path is None:
        raise ValueError("output_path is required when input_path is a local file.")
    logger.info("md_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


# ---------------------------------------------------------------------------
# Custom HTTP route — file download proxy
# ---------------------------------------------------------------------------

@mcp.custom_route("/download/{blob_name:path}", methods=["GET"])
async def download_blob(request: Request) -> Response:
    """Stream a converted .hwpx file from Azure Blob Storage."""
    blob_name: str = request.path_params["blob_name"]

    if _blob_store is None:
        return Response("Blob storage is not configured", status_code=503)
    if not _blob_store.exists(blob_name):
        return Response("File not found", status_code=404)

    stream = _blob_store.download_stream(blob_name)

    # RFC 5987: use filename* with UTF-8 encoding for non-ASCII names
    encoded_name = quote(blob_name)
    return StreamingResponse(
        stream.chunks(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
        },
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    global _blob_store, _base_url

    parser = argparse.ArgumentParser(description="pypandoc-hwpx MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        default=False,
        help="Run the server using Streamable HTTP transport instead of stdio",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the Streamable HTTP server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for the Streamable HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="External base URL of this server, used for download links. "
             "Falls back to BASE_URL env var, then http://localhost:<port>.",
    )
    parser.add_argument(
        "--allowed-origin",
        type=str,
        action="append",
        default=None,
        help="Allowed origin for DNS rebinding protection (can be repeated). "
             "e.g. https://example.com:*",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Initialise Azure Blob Storage (if configured via env vars)
    _blob_store = create_blob_store_from_env()
    if _blob_store is not None:
        logger.info("Azure Blob Storage configured")
    else:
        logger.info("Azure Blob Storage not configured — URL mode will save locally")

    # Resolve the server's external base URL
    container_app_hostname = os.environ.get("CONTAINER_APP_HOSTNAME")
    _base_url = (
        args.base_url
        or os.environ.get("BASE_URL")
        or (f"https://{container_app_hostname}" if container_app_hostname else None)
        or f"http://localhost:{args.port}"
    )
    logger.info("Base URL: %s", _base_url)

    if args.http:
        mcp.settings.host = args.host
        mcp.settings.port = args.port

        # Configure DNS rebinding protection for non-localhost deployments
        if args.host not in ("127.0.0.1", "localhost", "::1"):
            from mcp.server.transport_security import TransportSecuritySettings

            mcp.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
                allowed_origins=args.allowed_origin or [],
            )
            logger.info(
                "DNS rebinding protection disabled for host=%s", args.host,
            )

    transport = "streamable-http" if args.http else "stdio"
    logger.info("Starting server (transport=%s)", transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
