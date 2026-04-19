"""PDF → Markdown via Marker (datalab-to/marker); models loaded lazily once per process."""

from __future__ import annotations

import logging
import os
import tempfile
import threading
from typing import Any

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_converter: Any = None


def _get_pdf_converter() -> Any:
    global _converter
    with _lock:
        if _converter is None:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict

            device = os.environ.get("MARKER_DEVICE") or None
            kwargs: dict[str, Any] = {}
            if device:
                kwargs["device"] = device
            logger.info(
                "Initializing Marker PdfConverter (first run downloads/loads models; device=%s)",
                device or "default",
            )
            _converter = PdfConverter(
                artifact_dict=create_model_dict(**kwargs),
                config={},
            )
        return _converter


def extract_pdf_markdown(data: bytes) -> str:
    """Write bytes to a temp ``.pdf``, run Marker, return markdown body."""
    if not data:
        raise ValueError("Empty PDF")

    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.write(fd, data)
        os.close(fd)
        rendered = _get_pdf_converter()(path)
        return rendered.markdown.strip()
    except Exception as e:
        logger.exception("Marker PDF conversion failed")
        raise ValueError(f"PDF extraction failed: {e}") from e
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
