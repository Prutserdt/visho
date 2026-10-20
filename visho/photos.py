"""Finding and validating photo files."""

from pathlib import Path

from PIL import Image

from visho.config import IMAGE_EXTENSIONS


def is_valid_image(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception as error:
        print(f"Skipping invalid JPEG {path.name}: {error}")
        return False


def find_photos(directory: Path) -> list[Path]:
    photos = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            if is_valid_image(path):
                photos.append(path)
    return photos
