"""Command-line entry point."""

import argparse
import shlex
from pathlib import Path

from visho.browser import open_in_browser
from visho.config import DEFAULT_DIRECTORY, OUTPUT_DIRNAME, THUMBNAIL_DIRNAME
from visho.config import (
    DEFAULT_DIRECTORY,
    THUMBNAIL_DIRNAME,
    cache_directory_for,
)


#from visho.browser import open_in_browser
from visho.config import DEFAULT_DIRECTORY, OUTPUT_DIRNAME, THUMBNAIL_DIRNAME
from visho.export import write_csv, write_html
from visho.photos import find_photos
from visho.processing import build_locations


def resolve_directory_path(current_directory: Path, value: str) -> Path:
    """Resolve a path relative to the current directory."""
    path = Path(value).expanduser()

    if not path.is_absolute():
        path = current_directory / path

    return path.resolve()


def print_directory(directory: Path) -> None:
    """Print the contents of a directory."""
    try:
        entries = sorted(directory.iterdir(), key=lambda path: (not path.is_dir(), path.name.lower()))
    except OSError as error:
        print(f"Unable to list directory: {error}")
        return

    print(f"\nContents of {directory}:")

    if not entries:
        print("  Directory is empty.")
        return

    for entry in entries:
        suffix = "/" if entry.is_dir() else ""
        print(f"  {entry.name}{suffix}")


def choose_directory() -> Path:
    """Interactively choose the directory containing the photos."""
    directory = DEFAULT_DIRECTORY.expanduser().resolve()

    print("#######################")
    print("## VISHO application ##")
    print("#######################")

    while True:
        print(f"\nCurrent directory:  {directory}")
        print(
            "Command options:\n"
            "y  = pick this directory\n"
            "cd = change directory\n"
            "h  = help\n"
            "e  = exit"
        )

        try:
            answer = input("\nvisho> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit

        if not answer:
            continue

        try:
            parts = shlex.split(answer)
        except ValueError as error:
            print(f"Invalid command: {error}")
            continue

        command = parts[0].lower()
        values = parts[1:]

        if command in {"use", "select", "y", "yes"}:
            if directory.is_dir():
                return directory

            print(f"Not a directory: {directory}")
            continue

        if command in {"quit", "q", "exit", "e"}:
            raise SystemExit

        if command in {"help", "h", "?"}:
            print(
                "\nCommands:\n"
                "  y, yes, select       Select the current directory\n"
                "  cd PATH              Change directory\n"
                "  ls [PATH]            List a directory\n"
                "  pwd                  Show the current directory\n"
                "  up                   Go to the parent directory\n"
                "  h, help, ?           Show this help\n"
                "  e, q, quit, exit     Exit the application\n"
            )
            continue

        if command == "pwd":
            print(directory)
            continue

        if command == "up":
            directory = directory.parent
            continue

        if command == "ls":
            if len(values) > 1:
                print("Usage: ls [PATH]")
                continue

            target = directory

            if values:
                target = resolve_directory_path(directory, values[0])

            if target.is_dir():
                print_directory(target)
            else:
                print(f"Not a directory: {target}")

            continue

        if command == "cd":
            if len(values) != 1:
                print("Usage: cd PATH")
                continue

            target = resolve_directory_path(directory, values[0])

            if target.is_dir():
                directory = target
            else:
                print(f"Not a directory: {target}")

            continue

        print(f"Unknown command: {command}. Type 'h' for help.")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="visho",
        description="Build an interactive map of geotagged JPEG photos.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        help="photo directory (asks interactively if omitted)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="do not open the map in the browser afterwards",
    )
    return parser.parse_args()


def main() -> None:
    """Run the application."""
    arguments = parse_arguments()

    if arguments.directory:
        directory = arguments.directory.expanduser().resolve()

        if not directory.is_dir():
            raise SystemExit(f"Not a directory: {directory}")
    else:
        directory = choose_directory()


    #output_directory = directory / OUTPUT_DIRNAME
    output_directory = cache_directory_for(directory)
    thumbnail_directory = output_directory / THUMBNAIL_DIRNAME

    output_directory.mkdir(parents=True, exist_ok=True)

    photos = find_photos(directory)
    print(f"\nFound {len(photos)} valid JPEG files.")

    locations = build_locations(photos, thumbnail_directory)
    csv_path = write_csv(locations, output_directory)
    html_path = write_html(locations, output_directory)

    geotagged_count = sum(location["has_gps"] for location in locations)

    print()
    print(f"Valid JPEG files found: {len(photos)}")
    print(f"Photos with GPS: {geotagged_count}")
    print(f"Photos without GPS: {len(photos) - geotagged_count}")
    print(f"CSV written to: {csv_path}")
    print(f"Map written to: {html_path}")
    print(f"Thumbnails written to: {thumbnail_directory}")

    if not arguments.no_browser:
        open_in_browser(html_path)


if __name__ == "__main__":
    main()
