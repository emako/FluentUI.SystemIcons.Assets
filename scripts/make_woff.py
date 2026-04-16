#!/usr/bin/env python3
"""
Copy Fluent UI System Icons WOFF files to target directory.
"""

import shutil
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Copy Fluent UI System Icons WOFF files to target directory"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="assets/woff",
        help="Output directory (default: assets/woff)",
    )

    args = parser.parse_args()

    # Source directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    source_dir = (
        repo_root / "fluentui-system-icons" / "fonts"
    )

    # Target directory
    # Resolve relative paths from the repo root so behavior is stable
    # even when invoked from outside the repository root.
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
    patterns = ["*.woff"]
    files_copied = 0

    for pattern in patterns:
        for source_file in source_dir.glob(pattern):
            target_file = output_dir / source_file.name
            print(f"Copying: {source_file.name}")
            try:
                shutil.copy2(source_file, target_file)
            except OSError as exc:
                print(f"Error: Failed to copy {source_file.name}: {exc}")
                return 1
            files_copied += 1

    print(f"\nSuccessfully copied {files_copied} files to {output_dir}")
    return 0


if __name__ == "__main__":
    exit(main())
