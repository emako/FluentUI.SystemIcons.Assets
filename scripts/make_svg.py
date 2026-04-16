#!/usr/bin/env python3
"""
make_svg.py

Organize existing Fluent System Icon SVG assets into style-based output folders.

This script reads source SVGs from:
    fluentui-system-icons/assets/**/SVG/*.svg

And classifies them into:
    FluentSystemIcons-Filled
    FluentSystemIcons-Light
    FluentSystemIcons-Regular
    FluentSystemIcons-Resizable
    FluentSystemIcons-Color

Usage
-----
    python make_svg.py [options]

Options
-------
    --assets-dir PATH           Root assets directory containing grouped icon folders
                                (default: <script_dir>/fluentui-system-icons/assets)
    --output-dir PATH           Root output directory
                                (default: <script_dir>/assets/svg)
    --clean                     Remove existing output style folders before writing

Output layout
-------------
    assets/svg/
        FluentSystemIcons-Filled/
            ic_fluent_add_16_filled.svg
            ...
        FluentSystemIcons-Light/
            ic_fluent_access_time_24_light.svg
            ...
        FluentSystemIcons-Regular/
            ...
        FluentSystemIcons-Resizable/
            ic_fluent_text_direction_horizontal_ltr.svg
            ic_fluent_text_direction_horizontal_rtl.svg
            ...
        FluentSystemIcons-Color/
            ic_fluent_approvals_app_32_color.svg
            ...
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

STYLE_FOLDER_MAP: dict[str, str] = {
    "filled": "FluentSystemIcons-Filled",
    "light": "FluentSystemIcons-Light",
    "regular": "FluentSystemIcons-Regular",
    "color": "FluentSystemIcons-Color",
}

ALL_OUTPUT_FOLDERS = [
    "FluentSystemIcons-Filled",
    "FluentSystemIcons-Light",
    "FluentSystemIcons-Regular",
    "FluentSystemIcons-Resizable",
    "FluentSystemIcons-Color",
]


def classify_svg(svg_name: str) -> str | None:
    """Return output style folder from an icon file name."""
    match = re.search(r"_([a-z]+)\.svg$", svg_name)
    if not match:
        return None
    style = match.group(1)
    return STYLE_FOLDER_MAP.get(style)


def gather_source_svgs(assets_dir: Path) -> list[Path]:
    """Return all source SVG files from nested assets/<Icon Name>/SVG folders."""
    candidates = sorted(assets_dir.glob("*/SVG/*.svg"))
    filtered: list[Path] = []
    for path in candidates:
        icon_group = path.parent.parent.name
        if icon_group.endswith(" Temp LTR") or icon_group.endswith(" Temp RTL"):
            continue
        filtered.append(path)
    return filtered


def prepare_output_dirs(output_dir: Path, clean: bool) -> dict[str, Path]:
    """Create all output category folders and optionally clean existing content."""
    out_dirs: dict[str, Path] = {}
    for folder in ALL_OUTPUT_FOLDERS:
        full = output_dir / folder
        if clean and full.exists():
            shutil.rmtree(full)
        full.mkdir(parents=True, exist_ok=True)
        out_dirs[folder] = full
    return out_dirs


def organize_svgs(assets_dir: Path, output_dir: Path, clean: bool) -> None:
    """Copy source SVG files into style-based output folders."""
    svg_files = gather_source_svgs(assets_dir)
    if not svg_files:
        sys.exit(f"No SVG files found under: {assets_dir}")

    out_dirs = prepare_output_dirs(output_dir, clean)
    copied_counts = {folder: 0 for folder in ALL_OUTPUT_FOLDERS}
    skipped_unknown: list[Path] = []

    # Flat names mirror the PNG layout: one folder per style bucket.
    seen_dest_names: dict[Path, Path] = {}

    for src in svg_files:
        folder_name = classify_svg(src.name)
        if folder_name is None:
            skipped_unknown.append(src)
            continue

        dest = out_dirs[folder_name] / src.name
        previous_src = seen_dest_names.get(dest)
        if previous_src is not None and previous_src != src:
            print(
                f"  [DUPLICATE] {dest.name} from both '{previous_src}' and '{src}'. "
                "Keeping the latest copy."
            )

        shutil.copy2(src, dest)
        seen_dest_names[dest] = src
        copied_counts[folder_name] += 1

    print(f"Source dir  : {assets_dir}")
    print(f"Output dir  : {output_dir}")
    print(f"Total source: {len(svg_files)}")
    print(f"Unknown     : {len(skipped_unknown)}")

    for folder in ALL_OUTPUT_FOLDERS:
        print(f"  {folder}: {copied_counts[folder]} file(s)")

    if skipped_unknown:
        print("\nFirst unknown SVG names:")
        for path in skipped_unknown[:10]:
            print(f"  - {path.name}")

    print("\nDone.")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description=(
            "Organize existing Fluent System Icon SVG assets into style folders."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=repo_root / "fluentui-system-icons" / "assets",
        metavar="PATH",
        help="Directory containing icon group folders with SVG files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "assets" / "svg",
        metavar="PATH",
        help="Root output directory; one sub-folder is created per style category",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing style folders in output-dir before writing",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    assets_dir: Path = args.assets_dir
    output_dir: Path = args.output_dir
    clean: bool = args.clean

    if not assets_dir.is_dir():
        sys.exit(f"Assets directory not found: {assets_dir}")

    organize_svgs(assets_dir, output_dir, clean)


if __name__ == "__main__":
    main()
