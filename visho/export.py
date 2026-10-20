"""Writing the CSV and the HTML map (html + css + js + data)."""

import csv
import json
import shutil
from importlib import resources
from pathlib import Path

FIELDNAMES = ["name", "latitude", "longitude", "has_gps", "picture", "thumbnail"]
WEB_FILES = ["index.html", "style.css", "app.js"]


def write_csv(locations: list[dict], output_directory: Path) -> Path:
    csv_path = output_directory / "locations.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(locations)
    return csv_path


def write_html(locations: list[dict], output_directory: Path) -> Path:
    """Copy the static web files and write the photo data as locations.js."""
    web = resources.files("visho") / "web"
    for name in WEB_FILES:
        with resources.as_file(web / name) as source:
            shutil.copyfile(source, output_directory / name)

    data = json.dumps(locations, ensure_ascii=False, separators=(",", ":"))
    (output_directory / "locations.js").write_text(
        f"const locations = {data};\n", encoding="utf-8"
    )
    return output_directory / "index.html"
