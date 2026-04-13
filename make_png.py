#!/usr/bin/env python3
"""
make_png.py

Convert all TTF icon fonts in the fonts/ directory to individual PNG images.
Each glyph in the font is rendered using its corresponding JSON name-to-codepoint
mapping (e.g. FluentSystemIcons-Filled.json).

Usage
-----
    python make_png.py [options]

Options
-------
    --size INT                  Fallback PNG canvas size in pixels if icon name
                                does not contain a numeric size token
                                (default: 16)
    --color {black,white,both}  Icon colour (default: both)
    --fonts-dir PATH            Directory that contains the TTF files
                                (default: <script_dir>/fluentui-system-icons/fonts)
    --output-dir PATH           Root output directory
                                (default: <script_dir>/assets/png)

Output layout
-------------
    assets/png/
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
import re
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


def infer_canvas_size_from_icon_name(icon_name: str) -> int | None:
    """Infer icon size from name, e.g. ic_fluent_access_time_24_filled -> 24."""
    match = re.search(r"_(\d+)(?:_[^_]+)?$", icon_name)
    if not match:
        return None
    return int(match.group(1))


# ---------------------------------------------------------------------------
# Per-font conversion
# ---------------------------------------------------------------------------


def convert_font(
    ttf_path: Path,
    output_root: Path,
    fallback_canvas_px: int,
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

    font_cache: dict[int, ImageFont.FreeTypeFont] = {}
    total = 0
    used_sizes: set[int] = set()
    fallback_count = 0

    for icon_name, codepoint in icon_map.items():
        inferred_size = infer_canvas_size_from_icon_name(icon_name)
        if inferred_size is None:
            icon_canvas_px = fallback_canvas_px
            fallback_count += 1
            print(
                f"  [FALLBACK] {font_stem}: icon '{icon_name}' has no size token; "
                f"using {fallback_canvas_px}px"
            )
        else:
            icon_canvas_px = inferred_size
        used_sizes.add(icon_canvas_px)

        if icon_canvas_px not in font_cache:
            font_cache[icon_canvas_px] = _load_font_at_size(ttf_path, icon_canvas_px)

        font = font_cache[icon_canvas_px]
        for color in colors:
            img = render_glyph(font, codepoint, icon_canvas_px, color)
            # Naming: <icon_name>_<canvas_px>_<color>.png
            # Example: ic_fluent_add_16_filled_16_black.png
            filename = f"{icon_name}_{icon_canvas_px}_{color}.png"
            img.save(font_out_dir / filename, format="PNG")
            total += 1

    size_list = ", ".join(str(px) for px in sorted(used_sizes))
    print(
        f"  {font_stem}: {total} PNG(s), sizes [{size_list}], "
        f"fallback used {fallback_count} time(s) -> {font_out_dir}"
    )


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
        default=16,
        metavar="INT",
        help="Fallback output PNG canvas size in pixels when icon name has no size token",
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
        default=script_dir / "assets" / "png",
        metavar="PATH",
        help="Root output directory; one sub-folder is created per TTF",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    fonts_dir: Path = args.fonts_dir
    output_dir: Path = args.output_dir
    fallback_canvas_px: int = args.size
    colors: list[str] = ["black", "white"] if args.color == "both" else [args.color]

    if not fonts_dir.is_dir():
        sys.exit(f"Fonts directory not found: {fonts_dir}")

    ttf_files = sorted(fonts_dir.glob("*.ttf"))
    if not ttf_files:
        sys.exit(f"No TTF files found in {fonts_dir}")

    print(
        f"Canvas size : auto by icon name (fallback {fallback_canvas_px}px)\n"
        f"Colours     : {', '.join(colors)}\n"
        f"Fonts dir   : {fonts_dir}\n"
        f"Output dir  : {output_dir}\n"
        f"TTF files   : {len(ttf_files)}\n"
    )

    for ttf_path in ttf_files:
        print(f"Processing {ttf_path.name} ...")
        convert_font(ttf_path, output_dir, fallback_canvas_px, colors)

    print("\nDone.")


if __name__ == "__main__":
    main()
