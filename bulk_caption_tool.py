#!/usr/bin/env python3
"""Standalone folder caption generator for Tail Tagger models.

Uses the existing project venv/dependencies and classifier stack to run inference
across a folder and write comma-separated `.txt` captions per image.
"""

import argparse
import os
import sys

from config_manager import ConfigManager
from classifier_manager import ClassifierManager
from file_operations import FileOperations


def parse_args():
    parser = argparse.ArgumentParser(description="Generate captions for all images in a folder using Tail Tagger models.")
    parser.add_argument("folder", help="Folder containing images")
    parser.add_argument("--model", default=None, help="Model ID to use (e.g. JTP-3, JTP_PILOT2). Defaults to config active model.")
    parser.add_argument("--threshold", type=float, default=None, help="Score threshold (default from config: classifier_threshold)")
    parser.add_argument("--overwrite-mode", choices=["auto", "base", "ext"], default="auto",
                        help="Caption path mode: auto=prefer existing image.ext.txt else image.txt, base=image.txt, ext=image.ext.txt")
    return parser.parse_args()


def resolve_txt_path(image_path: str, mode: str) -> str:
    base_txt = os.path.splitext(image_path)[0] + ".txt"
    ext_txt = image_path + ".txt"
    if mode == "base":
        return base_txt
    if mode == "ext":
        return ext_txt
    return ext_txt if os.path.exists(ext_txt) else base_txt


def main():
    args = parse_args()
    folder = os.path.normpath(args.folder)
    if not os.path.isdir(folder):
        print(f"ERROR: folder not found: {folder}")
        return 1

    cfg = ConfigManager()
    threshold = args.threshold if args.threshold is not None else cfg.get_config_value("classifier_threshold")
    if threshold is None:
        threshold = 0.30
    threshold = max(0.01, min(float(threshold), 0.95))

    classifier = ClassifierManager(config_manager=cfg, use_gpu=True)
    if args.model:
        classifier.set_active_model(args.model)

    active_model = classifier.get_active_model_id()
    if not active_model:
        print("ERROR: no active model available.")
        return 1

    print(f"Using model: {active_model}")
    print(f"Threshold: {threshold:.2f}")

    files = FileOperations().get_sorted_image_files(folder)
    if not files:
        print("No images found.")
        return 0

    updated = 0
    errors = 0
    for i, image_path in enumerate(files, start=1):
        rel = os.path.basename(image_path)
        print(f"[{i}/{len(files)}] {rel}")
        try:
            results = classifier.analyze_image_sync(image_path, threshold=threshold)
            tags = [tag for tag, _score in results if _score >= threshold]
            spaced_tags = [FileOperations.convert_underscores_to_spaces(t) for t in tags]

            txt_path = resolve_txt_path(image_path, args.overwrite_mode)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(", ".join(spaced_tags))
            updated += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"Done. Updated: {updated}, Errors: {errors}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
