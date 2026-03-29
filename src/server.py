import argparse
import logging
import os

import pypandoc_hwpx
from mcp.server.fastmcp import FastMCP
from pypandoc_hwpx.PandocToHwpx import PandocToHwpx

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
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def docx_to_hwpx(
    input_path: str,
    output_path: str,
    reference_hwpx: str | None = None,
) -> str:
    """Convert a .docx file to a .hwpx file.

    Args:
        input_path: Path to the source .docx file.
        output_path: Path where the resulting .hwpx file will be written.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file.
    """
    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    logger.info("docx_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


@mcp.tool()
def html_to_hwpx(
    input_path: str,
    output_path: str,
    reference_hwpx: str | None = None,
) -> str:
    """Convert an HTML file to a .hwpx file.

    Args:
        input_path: Path to the source HTML file.
        output_path: Path where the resulting .hwpx file will be written.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file.
    """
    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    logger.info("html_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


@mcp.tool()
def md_to_hwpx(
    input_path: str,
    output_path: str,
    reference_hwpx: str | None = None,
) -> str:
    """Convert a Markdown file to a .hwpx file.

    Args:
        input_path: Path to the source Markdown (.md) file.
        output_path: Path where the resulting .hwpx file will be written.
        reference_hwpx: Optional path to a reference .hwpx file for styles.

    Returns:
        The absolute path of the generated .hwpx file.
    """
    if not os.path.isfile(input_path):
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    logger.info("md_to_hwpx called: %s -> %s", input_path, output_path)
    return _convert(input_path, output_path, reference_hwpx)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="pypandoc-hwpx MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        default=False,
        help="Run the server using Streamable HTTP transport instead of stdio",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for the Streamable HTTP transport (default: 8000)",
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

    if args.http:
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port

    transport = "streamable-http" if args.http else "stdio"
    logger.info("Starting server (transport=%s)", transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
