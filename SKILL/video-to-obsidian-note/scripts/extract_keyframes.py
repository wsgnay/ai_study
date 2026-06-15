#!/usr/bin/env python3
"""Extract keyframes from a local video and optionally build a contact sheet.

Usage:
  python extract_keyframes.py video.mp4 output_dir --times 45,125,215
  python extract_keyframes.py video.mp4 output_dir --interval 30 --max-frames 40
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def _load_cv2():
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit("OpenCV is required: install/use a Python env with cv2 available.") from exc
    return cv2


def _load_pillow():
    try:
        from PIL import Image, ImageDraw  # type: ignore
    except Exception:
        return None, None
    return Image, ImageDraw


def parse_times(raw: str | None, duration: float, interval: int | None, max_frames: int) -> list[int]:
    if raw:
        return sorted({int(float(x.strip())) for x in raw.split(",") if x.strip()})
    if not interval:
        interval = 30
    times = list(range(0, max(1, int(duration)), interval))
    if len(times) > max_frames:
        step = math.ceil(len(times) / max_frames)
        times = times[::step][:max_frames]
    return times


def make_contact_sheet(image_paths: list[Path], out_path: Path) -> None:
    Image, ImageDraw = _load_pillow()
    if Image is None or ImageDraw is None:
        return

    thumbs = []
    for path in image_paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((320, 180))
        canvas = Image.new("RGB", (320, 210), "white")
        canvas.paste(image, ((320 - image.width) // 2, 0))
        ImageDraw.Draw(canvas).text((8, 185), path.name, fill=(0, 0, 0))
        thumbs.append(canvas)

    if not thumbs:
        return

    cols = 2 if len(thumbs) <= 12 else 4
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 320, rows * 210), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 320, (index // cols) * 210))
    sheet.save(out_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--times", help="Comma-separated seconds to extract.")
    parser.add_argument("--interval", type=int, default=30, help="Scan interval when --times is omitted.")
    parser.add_argument("--max-frames", type=int, default=40)
    parser.add_argument("--prefix", default="frame")
    parser.add_argument("--contact-sheet", action="store_true")
    args = parser.parse_args()

    cv2 = _load_cv2()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps if fps else 0
    times = parse_times(args.times, duration, args.interval, args.max_frames)

    written: list[Path] = []
    for index, seconds in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        out_path = args.output_dir / f"{args.prefix}-{index:02d}-{seconds:04d}s.jpg"
        if cv2.imwrite(str(out_path), frame):
            written.append(out_path)
    cap.release()

    if args.contact_sheet:
        make_contact_sheet(written, args.output_dir / f"_{args.prefix}_contact_sheet.jpg")

    print(f"duration_seconds={duration:.2f}")
    print(f"requested_frames={len(times)}")
    print(f"written_frames={len(written)}")
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
