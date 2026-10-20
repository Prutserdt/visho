"""Reading GPS coordinates from EXIF data."""

from pathlib import Path

from PIL import ExifTags, Image


def as_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value.numerator / value.denominator


def gps_to_decimal(values, reference: str):
    if not values or len(values) != 3:
        return None
    result = (
        as_float(values[0])
        + as_float(values[1]) / 60
        + as_float(values[2]) / 3600
    )
    if reference.upper() in {"S", "W"}:
        result = -result
    return result


def get_gps(image_path: Path):
    """Return (latitude, longitude) in decimal degrees, or None."""
    try:
        with Image.open(image_path) as image:
            exif = image.getexif()
            if not exif:
                return None
            gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
            latitude = gps.get(2)
            latitude_ref = gps.get(1)
            longitude = gps.get(4)
            longitude_ref = gps.get(3)
            if not all((latitude, latitude_ref, longitude, longitude_ref)):
                return None
            if isinstance(latitude_ref, bytes):
                latitude_ref = latitude_ref.decode("ascii")
            if isinstance(longitude_ref, bytes):
                longitude_ref = longitude_ref.decode("ascii")
            latitude = gps_to_decimal(latitude, latitude_ref)
            longitude = gps_to_decimal(longitude, longitude_ref)
            if latitude is None or longitude is None:
                return None
            return latitude, longitude
    except Exception as error:
        print(f"Could not read EXIF from {image_path.name}: {error}")
        return None
