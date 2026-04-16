#!/usr/bin/env python3
"""
Copy Fluent UI System Icons WOFF2 files to target directory.
"""

import os
import shutil
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Copy Fluent UI System Icons WOFF2 files to target directory"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="assets/woff2",
        help="Output directory (default: assets/woff2)",
    )

    args = parser.parse_args()

    # Source directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    source_dir = (
        repo_root / "fluentui-system-icons" / "fonts"
    )

    # Target directory
    output_dir_arg = Path(args.output_dir)
    output_dir = output_dir_arg if output_dir_arg.is_absolute() else repo_root / output_dir_arg

    # Validate source directory exists
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return 1

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # File patterns to copy
    patterns = ["*.woff2"]
    files_copied = 0

    for pattern in patterns:
        for source_file in source_dir.glob(pattern):
            target_file = output_dir / source_file.name
            print(f"Copying: {source_file.name}")
            shutil.copy2(source_file, target_file)
            files_copied += 1

    print(f"\nSuccessfully copied {files_copied} files to {output_dir}")
    return 0


if __name__ == "__main__":
    exit(main())
