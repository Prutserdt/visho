"""Creating (cached) thumbnails."""

from pathlib import Path

from PIL import Image, ImageOps

from visho.config import JPEG_QUALITY, THUMBNAIL_SIZE


def create_thumbnail(image_path: Path, thumbnail_directory: Path) -> Path:
    """Create a thumbnail; reuse it if it is newer than the original.

    Falls back to the original picture if creating the thumbnail fails.
    """
    thumbnail_directory.mkdir(parents=True, exist_ok=True)
    thumbnail_path = thumbnail_directory / f"{image_path.stem}.jpg"

    if (
        thumbnail_path.exists()
        and thumbnail_path.stat().st_mtime >= image_path.stat().st_mtime
    ):
        return thumbnail_path

    try:
        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image)
            image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(thumbnail_path, "JPEG", quality=JPEG_QUALITY)
    except Exception as error:
        print(f"Could not create thumbnail for {image_path.name}: {error}")
        return image_path

    return thumbnail_path
