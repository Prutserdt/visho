"""Central settings. Change defaults here instead of throughout the code."""

import hashlib
from pathlib import Path
 
DEFAULT_DIRECTORY = Path("~/Downloads").expanduser()

IMAGE_EXTENSIONS = {".jpg", ".jpeg"}

# Thumbnails
THUMBNAIL_SIZE = (180, 135)
JPEG_QUALITY = 78

# Output layout (relative to the photo directory)
#OUTPUT_DIRNAME = "locations"
#THUMBNAIL_DIRNAME = "thumbnails"
# Generated data is stored outside the photo directory.
CACHE_DIRECTORY = Path("~/.cache/visho").expanduser()
# Output layout
OUTPUT_DIRNAME = "locations"
THUMBNAIL_DIRNAME = "thumbnails"

# Parallel processing
MAX_WORKERS = 16
MIN_WORKERS = 4

def cache_directory_for(photo_directory: Path) -> Path:
    """Return the stable cache directory for a photo directory."""
    resolved_directory = photo_directory.expanduser().resolve()
    digest = hashlib.sha256(
        str(resolved_directory).encode("utf-8")
    ).hexdigest()[:16]
    return CACHE_DIRECTORY / digest / OUTPUT_DIRNAME
