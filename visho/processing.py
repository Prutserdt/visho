"""Processing all photos in parallel into location records."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from visho.config import MAX_WORKERS, MIN_WORKERS
from visho.gps import get_gps
from visho.thumbnails import create_thumbnail


def process_photo(image_path: Path, thumbnail_directory: Path) -> dict:
    thumbnail_path = create_thumbnail(image_path, thumbnail_directory)
    gps = get_gps(image_path)
    latitude, longitude = gps if gps else (None, None)
    return {
        "name": image_path.name,
        "latitude": latitude,
        "longitude": longitude,
        "has_gps": gps is not None,
        "picture": image_path.resolve().as_uri(),
        "thumbnail": thumbnail_path.resolve().as_uri(),
    }


def build_locations(photos: list[Path], thumbnail_directory: Path) -> list[dict]:
    if not photos:
        return []
    worker_count = min(MAX_WORKERS, max(MIN_WORKERS, (os.cpu_count() or 4) * 2))
    locations = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = executor.map(
            lambda photo: process_photo(photo, thumbnail_directory), photos
        )
        for number, location in enumerate(results, start=1):
            print(f"Processing {number}/{len(photos)}: {location['name']}")
            locations.append(location)
    return locations
