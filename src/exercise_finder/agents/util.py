# mypy: ignore-errors
"""Shared utilities for agents."""
from __future__ import annotations

import base64
from pathlib import Path


def guess_mime_type(path: Path) -> str:
    """
    Guess the MIME type of an image file based on its extension.
    
    Args:
        path: Path to the image file
        
    Returns:
        MIME type string (e.g., "image/png")
        
    Example:
        >>> guess_mime_type(Path("photo.jpg"))
        'image/jpeg'
        >>> guess_mime_type(Path("diagram.png"))
        'image/png'
    """
    suffix = path.suffix.lower()
    if suffix in {".png"}:
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix in {".webp"}:
        return "image/webp"
    return "application/octet-stream"


def _format_data_url(base64_data: str, mime_type: str) -> str:
    """Format base64 data and MIME type into a data URL."""
    return f"data:{mime_type};base64,{base64_data}"


def image_path_to_data_url(path: Path) -> str:
    """
    Convert an image file to a base64-encoded data URL.
    
    Args:
        path: Path to the image file
        
    Returns:
        Data URL string (e.g., "data:image/png;base64,iVBORw0KG...")
    """
    mime = guess_mime_type(path)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return _format_data_url(data, mime)


def base64_to_data_url(image_base64: str, mime_type: str = "image/png") -> str:
    """
    Convert a base64-encoded image to a data URL.
    
    Args:
        image_base64: Base64-encoded image string
        mime_type: MIME type of the image (default: "image/png")
        
    Returns:
        Data URL string (e.g., "data:image/png;base64,...")
    """
    return _format_data_url(image_base64, mime_type)

