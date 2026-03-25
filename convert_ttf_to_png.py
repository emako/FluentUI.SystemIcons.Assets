#!/usr/bin/env python3
"""
convert_ttf_to_png.py

Convert all TTF icon fonts in the fonts/ directory to individual PNG images.
Each glyph in the font is rendered using its corresponding JSON name-to-codepoint
mapping (e.g. FluentSystemIcons-Filled.json).

Usage
-----
    python convert_ttf_to_png.py [options]

Options
-------
    --size {16,24}              Output PNG canvas size in pixels (default: 16)
    --color {black,white,both}  Icon colour (default: both)
    --fonts-dir PATH            Directory that contains the TTF files
                                (default: <script_dir>/fluentui-system-icons/fonts)
    --output-dir PATH           Root output directory
                                (default: <script_dir>/assets/images)

Output layout
-------------
    assets/images/
        FluentSystemIcons-Filled/
            ic_fluent_add_16_filled_16_black.png
            ic_fluent_add_16_filled_16_white.png
            ...
        FluentSystemIcons-Regular/
            ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required.  Install it with:\n" "    pip install Pillow")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def load_icon_map(json_path: Path) -> dict[str, int]:
    """Return {icon_name: unicode_codepoint} from a Fluent icon JSON file."""
    with open(json_path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_font_at_size(ttf_path: Path, px: int) -> ImageFont.FreeTypeFont:
    """Load a FreeType font sized so glyphs fill *px* pixels with 1 px padding."""
    # Use (px - 2) so glyphs have a 1 px margin on each side; this avoids
    # clipping on icons whose metrics touch the em-square boundary.
    font_size = max(px - 2, 1)
    return ImageFont.truetype(str(ttf_path), font_size)


def render_glyph(
    font: ImageFont.FreeTypeFont,
    codepoint: int,
    canvas_px: int,
    color: str,
) -> Image.Image:
    """Render a single icon glyph centred on a transparent RGBA canvas."""
    char = chr(codepoint)
    fg_color = (255, 255, 255, 255) if color == "white" else (0, 0, 0, 255)

    img = Image.new("RGBA", (canvas_px, canvas_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # textbbox returns (left, top, right, bottom) relative to the given anchor
    bbox = draw.textbbox((0, 0), char, font=font)
    glyph_w = bbox[2] - bbox[0]
    glyph_h = bbox[3] - bbox[1]

    x = (canvas_px - glyph_w) // 2 - bbox[0]
    y = (canvas_px - glyph_h) // 2 - bbox[1]

    draw.text((x, y), char, font=font, fill=fg_color)
    return img


# ---------------------------------------------------------------------------
# Per-font conversion
# ---------------------------------------------------------------------------


def convert_font(
    ttf_path: Path,
    output_root: Path,
    canvas_px: int,
    colors: list[str],
) -> None:
    """Convert every glyph in *ttf_path* to PNGs under *output_root*."""
    json_path = ttf_path.with_suffix(".json")
    if not json_path.exists():
        print(f"  [SKIP] No JSON mapping found for {ttf_path.name}")
        return

    icon_map = load_icon_map(json_path)
    font_stem = ttf_path.stem  # e.g. "FluentSystemIcons-Filled"
    font_out_dir = output_root / font_stem
    font_out_dir.mkdir(parents=True, exist_ok=True)

    font = _load_font_at_size(ttf_path, canvas_px)
    total = 0

    for icon_name, codepoint in icon_map.items():
        for color in colors:
            img = render_glyph(font, codepoint, canvas_px, color)
            # Naming: <icon_name>_<canvas_px>_<color>.png
            # Example: ic_fluent_add_16_filled_16_black.png
            filename = f"{icon_name}_{canvas_px}_{color}.png"
            img.save(font_out_dir / filename, format="PNG")
            total += 1

    print(f"  {font_stem}: {total} PNG(s) -> {font_out_dir}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(
        description=(
            "Render every glyph in Fluent System Icon TTF fonts as PNG images."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--size",
        type=int,
        choices=[16, 24],
        default=16,
        metavar="{16,24}",
        help="Output PNG canvas size in pixels",
    )
    parser.add_argument(
        "--color",
        choices=["black", "white", "both"],
        default="both",
        help="Icon foreground colour (transparent background)",
    )
    parser.add_argument(
        "--fonts-dir",
        type=Path,
        default=script_dir / "fluentui-system-icons" / "fonts",
        metavar="PATH",
        help="Directory containing the TTF files and their JSON mappings",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=script_dir / "assets" / "images",
        metavar="PATH",
        help="Root output directory; one sub-folder is created per TTF",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    fonts_dir: Path = args.fonts_dir
    output_dir: Path = args.output_dir
    canvas_px: int = args.size
    colors: list[str] = ["black", "white"] if args.color == "both" else [args.color]

    if not fonts_dir.is_dir():
        sys.exit(f"Fonts directory not found: {fonts_dir}")

    ttf_files = sorted(fonts_dir.glob("*.ttf"))
    if not ttf_files:
        sys.exit(f"No TTF files found in {fonts_dir}")

    print(
        f"Canvas size : {canvas_px}x{canvas_px} px\n"
        f"Colours     : {', '.join(colors)}\n"
        f"Fonts dir   : {fonts_dir}\n"
        f"Output dir  : {output_dir}\n"
        f"TTF files   : {len(ttf_files)}\n"
    )

    for ttf_path in ttf_files:
        print(f"Processing {ttf_path.name} ...")
        convert_font(ttf_path, output_dir, canvas_px, colors)

    print("\nDone.")


if __name__ == "__main__":
    main()
