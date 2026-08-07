#!/usr/bin/env python3
"""Build a narrated video from matching image/audio segments."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageFilter
except ImportError as exc:
    raise SystemExit("ERROR: Pillow is required to process source images.") from exc


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".aac")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.splitlines()[-30:])
        fail(f"Command failed:\n{' '.join(command)}\n{tail}")
    return result


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        fail(f"Required tool is not available: {name}")
    return path


def require_text(item: dict[str, Any], key: str, owner: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{owner}.{key} must be a non-empty string.")
    return value.strip()


def load_segments(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"Missing narration file: {path}")
    segments: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"Invalid JSONL at {path}:{line_number}: {exc}")
        if not isinstance(value, dict):
            fail(f"{path}:{line_number} must contain a JSON object.")
        segments.append(value)
    if not segments:
        fail(f"Narration file is empty: {path}")

    seen: set[str] = set()
    for index, segment in enumerate(segments, start=1):
        owner = f"segment[{index}]"
        segment_id = require_text(segment, "id", owner)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", segment_id):
            fail(f"{owner}.id contains unsupported characters: {segment_id}")
        if segment_id in seen:
            fail(f"Duplicate segment id: {segment_id}")
        seen.add(segment_id)
        order = segment.get("order")
        if isinstance(order, bool) or not isinstance(order, int) or order != index:
            fail(f"{owner}.order must be {index}.")
        require_text(segment, "narration", owner)
        require_text(segment, "audio_file", owner)
    return segments


def discover_numbered_segments(
    input_dir: Path,
    images_dir: Path,
) -> list[dict[str, Any]]:
    image_directories: list[Path] = []
    for directory in (images_dir, input_dir):
        resolved = directory.resolve()
        if resolved not in image_directories and resolved.is_dir():
            image_directories.append(resolved)

    numbered_images: dict[int, Path] = {}
    pattern = re.compile(r"^(?:section[_-]?)?(\d+)$", re.IGNORECASE)
    for directory in image_directories:
        for candidate in directory.iterdir():
            if not candidate.is_file() or candidate.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            match = pattern.fullmatch(candidate.stem)
            if not match:
                continue
            number = int(match.group(1))
            if number <= 0:
                fail(f"Image numbering must start at 1: {candidate}")
            if number in numbered_images:
                fail(
                    f"Multiple images found for sequence number {number}: "
                    f"{numbered_images[number]}, {candidate}"
                )
            numbered_images[number] = candidate.resolve()

    if not numbered_images:
        fail(
            "Missing narration_segments.jsonl and no numbered images were found. "
            "Use names such as 1.png, 2.png, or section_1.png."
        )
    numbers = sorted(numbered_images)
    expected = list(range(1, numbers[-1] + 1))
    if numbers != expected:
        fail(f"Image sequence must be continuous from 1: found {numbers}")

    return [
        {
            "id": f"section_{number}",
            "order": order,
            "narration": "Narration is supplied by the matching audio file.",
            "audio_file": f"section_{number}.mp3",
            "_discovered_without_manifest": True,
        }
        for order, number in enumerate(numbers, start=1)
    ]


def id_aliases(segment_id: str) -> list[str]:
    aliases = [segment_id]
    match = re.search(r"(\d+)$", segment_id)
    if match:
        raw_number = match.group(1)
        normalized = str(int(raw_number))
        for value in (raw_number, normalized, normalized.zfill(2), normalized.zfill(3)):
            if value not in aliases:
                aliases.append(value)
    return aliases


def resolve_named_file(
    directories: list[Path],
    aliases: list[str],
    extensions: tuple[str, ...],
    owner: str,
) -> Path | None:
    matches: list[Path] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for alias in aliases:
            for extension in extensions:
                candidate = directory / f"{alias}{extension}"
                if candidate.is_file() and candidate.resolve() not in matches:
                    matches.append(candidate.resolve())
    if not matches:
        return None
    if len(matches) > 1:
        fail(
            f"Multiple files found for {owner}: "
            + ", ".join(str(path) for path in matches)
        )
    return matches[0]


def resolve_image(input_dir: Path, images_dir: Path, segment_id: str) -> Path:
    image = resolve_named_file(
        [images_dir, input_dir],
        id_aliases(segment_id),
        IMAGE_EXTENSIONS,
        f"image {segment_id}",
    )
    if image is None:
        fail(
            f"Missing image for {segment_id}. Accepted names include "
            f"{segment_id}.png and {id_aliases(segment_id)[-1]}.png."
        )
    return image


def resolve_audio(input_dir: Path, segment: dict[str, Any]) -> Path:
    segment_id = require_text(segment, "id", "segment")
    explicit = Path(require_text(segment, "audio_file", f"segment {segment_id}")).expanduser()
    candidates: list[Path] = []
    if explicit.is_absolute():
        candidates.append(explicit)
    else:
        candidates.extend((input_dir / explicit, input_dir.parent / explicit))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    audio = resolve_named_file(
        [input_dir / "audio", input_dir],
        id_aliases(segment_id),
        AUDIO_EXTENSIONS,
        f"audio {segment_id}",
    )
    if audio is None:
        fail(f"Missing audio for {segment_id} in {input_dir}.")
    return audio


def probe_media(path: Path) -> dict[str, Any]:
    ffprobe = require_tool("ffprobe")
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"Could not parse ffprobe output for {path}: {exc}")


def media_duration(path: Path) -> float:
    payload = probe_media(path)
    try:
        duration = float(payload["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        fail(f"Could not read media duration: {path}")
    if duration <= 0:
        fail(f"Media duration must be positive: {path}")
    return duration


def inspect_image_quality(path: Path, target_width: int) -> dict[str, Any]:
    try:
        with Image.open(path) as image:
            source_width, source_height = image.size
    except OSError as exc:
        fail(f"Unreadable image file: {path}: {exc}")
    if source_width <= 0 or source_height <= 0:
        fail(f"Image dimensions must be positive: {path}")
    upscale_factor = target_width / source_width
    if upscale_factor <= 1.0:
        quality = "native_or_downscaled"
    elif upscale_factor <= 1.35:
        quality = "mild_upscale"
    elif upscale_factor <= 1.75:
        quality = "heavy_upscale"
    else:
        quality = "severe_upscale"
    return {
        "source_width": source_width,
        "source_height": source_height,
        "target_width": target_width,
        "upscale_factor": round(upscale_factor, 3),
        "quality": quality,
        "enhance": upscale_factor > 1.0,
    }


def render_float_background(
    source: Path,
    output: Path,
    *,
    width: int,
    height: int,
) -> None:
    with Image.open(source) as raw:
        image = raw.convert("RGB")
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (
            max(width, round(image.width * scale)),
            max(height, round(image.height * scale)),
        ),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    cropped = resized.crop((left, top, left + width, top + height))
    blurred = cropped.filter(
        ImageFilter.GaussianBlur(radius=max(16, round(min(width, height) * 0.025)))
    )
    softened = Image.blend(
        blurred,
        Image.new("RGB", blurred.size, (248, 248, 250)),
        0.22,
    )
    softened.save(output, quality=94)


def build_segment(
    *,
    image: Path,
    audio: Path,
    duration: float,
    output: Path,
    work_dir: Path,
    width: int,
    height: int,
    fps: int,
    motion: str,
    pre_roll: float,
    enhance_image: bool,
) -> None:
    ffmpeg = require_tool("ffmpeg")
    background_path: Path | None = None
    if motion == "float":
        background_path = work_dir / "float_background.jpg"
        render_float_background(
            image,
            background_path,
            width=width,
            height=height,
        )

    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(fps),
        "-i",
        str(image),
    ]
    if background_path is not None:
        command.extend(
            ["-loop", "1", "-framerate", str(fps), "-i", str(background_path)]
        )
    audio_input_index = 2 if background_path is not None else 1
    command.extend(["-i", str(audio)])

    visual_duration = duration + pre_roll
    scale_flags = ":flags=lanczos+accurate_rnd+full_chroma_int"
    enhancement = ",cas=strength=0.25" if enhance_image else ""
    if motion == "float":
        movement_start = pre_roll
        movement_span = max(0.1, duration)
        progress = (
            f"min(max((t-{movement_start:.6f})/{movement_span:.6f},0),1)"
        )
        foreground_width = max(2, round(width * 0.94 / 2) * 2)
        foreground_height = max(2, round(height * 0.94 / 2) * 2)
        background_width = max(2, round(width * 1.04 / 2) * 2)
        background_height = max(2, round(height * 1.04 / 2) * 2)
        filters = [
            f"[1:v]scale={background_width}:{background_height}:"
            f"flags=lanczos+accurate_rnd,"
            f"crop={width}:{height}:"
            f"x='(iw-ow)/2-4+8*({progress})':"
            f"y='(ih-oh)/2-6+12*({progress})',"
            f"fps={fps},format=rgba[float_bg]",
            f"[0:v]scale={foreground_width}:{foreground_height}:"
            f"force_original_aspect_ratio=decrease:force_divisible_by=2"
            f"{scale_flags}{enhancement},fps={fps},format=rgba[float_fg]",
            f"[float_bg][float_fg]overlay="
            f"x='(W-w)/2+6-12*({progress})':"
            f"y='(H-h)/2+10-20*({progress})':"
            f"eof_action=repeat[base]",
        ]
    elif motion == "scroll":
        scroll_start = pre_roll + duration * 0.15
        scroll_span = max(0.1, duration * 0.70)
        progress = (
            f"min(max((t-{scroll_start:.6f})/{scroll_span:.6f},0),1)"
        )
        eased = f"(({progress})*({progress})*(3-2*({progress})))"
        filters = [
            f"[0:v]scale={width}:-2{scale_flags}{enhancement},"
            f"pad={width}:max(ih\\,{height}):(ow-iw)/2:(oh-ih)/2:"
            f"color=0xF5F5F7,"
            f"crop={width}:{height}:0:'(ih-oh)*{eased}',"
            f"fps={fps},format=rgba[base]"
        ]
    else:
        filters = [
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease:"
            f"force_divisible_by=2{scale_flags}{enhancement},"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:"
            f"color=0xF5F5F7,fps={fps},format=rgba[base]"
        ]

    previous = "base"

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{previous}]",
            "-map",
            f"{audio_input_index}:a:0",
            "-t",
            f"{visual_duration:.3f}",
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run(command)


def combine_segments(
    segment_files: list[Path],
    durations: list[float],
    output: Path,
    transition_duration: float,
    fps: int,
) -> None:
    ffmpeg = require_tool("ffmpeg")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    for path in segment_files:
        command.extend(["-i", str(path)])

    filters: list[str] = []
    for index in range(len(segment_files)):
        filters.append(
            f"[{index}:v]setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
        )
        filters.append(
            f"[{index}:a]aresample=48000,asetpts=PTS-STARTPTS[a{index}]"
        )

    if len(segment_files) == 1:
        video_label = "v0"
    elif transition_duration <= 0:
        video_inputs = "".join(f"[v{index}]" for index in range(len(segment_files)))
        filters.append(
            f"{video_inputs}concat=n={len(segment_files)}:v=1:a=0[vout]"
        )
        video_label = "vout"
    else:
        previous = "v0"
        elapsed = durations[0]
        for index in range(1, len(segment_files)):
            output_label = f"vx{index}"
            offset = elapsed - transition_duration
            filters.append(
                f"[{previous}][v{index}]xfade=transition=fade:"
                f"duration={transition_duration:.3f}:offset={offset:.3f}"
                f"[{output_label}]"
            )
            previous = output_label
            elapsed += durations[index]
        video_label = previous

    audio_inputs = "".join(f"[a{index}]" for index in range(len(segment_files)))
    filters.append(
        f"{audio_inputs}concat=n={len(segment_files)}:v=0:a=1[aout]"
    )
    total_duration = sum(durations)
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{video_label}]",
            "-map",
            "[aout]",
            "-t",
            f"{total_duration:.3f}",
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run(command)


def validate_output(path: Path, width: int, height: int, expected_duration: float) -> dict[str, Any]:
    payload = probe_media(path)
    streams = payload.get("streams")
    if not isinstance(streams, list):
        fail(f"No streams found in output: {path}")
    video_streams = [
        stream for stream in streams
        if isinstance(stream, dict) and stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream for stream in streams
        if isinstance(stream, dict) and stream.get("codec_type") == "audio"
    ]
    if len(video_streams) != 1 or len(audio_streams) != 1:
        fail("Output must contain exactly one video stream and one audio stream.")
    video = video_streams[0]
    if video.get("codec_name") != "h264":
        fail("Output video codec must be H.264.")
    if audio_streams[0].get("codec_name") != "aac":
        fail("Output audio codec must be AAC.")
    if video.get("width") != width or video.get("height") != height:
        fail("Output dimensions do not match the requested canvas.")
    actual_duration = media_duration(path)
    if abs(actual_duration - expected_duration) > max(1.0, expected_duration * 0.01):
        fail("Output duration does not match the narration audio sequence.")
    return {
        "duration_seconds": round(actual_duration, 3),
        "video_codec": "h264",
        "audio_codec": "aac",
        "width": width,
        "height": height,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a portrait video from one directory containing matching "
            "narration, image, and audio files."
        )
    )
    parser.add_argument("input_dir", nargs="?")
    parser.add_argument("--topic-dir", help=argparse.SUPPRESS)
    parser.add_argument("--images-dir")
    parser.add_argument("--segments")
    parser.add_argument("--output")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1440)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--motion",
        choices=("float", "scroll", "none"),
        default="none",
    )
    parser.add_argument("--transition-duration", type=float, default=0.6)
    parser.add_argument(
        "--image-quality-policy",
        choices=("best-effort", "strict"),
        default="best-effort",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    input_value = args.input_dir or args.topic_dir
    if not input_value:
        fail("Provide the directory containing the video assets.")
    input_dir = Path(input_value).expanduser().resolve()
    if not input_dir.is_dir():
        fail(f"Input directory does not exist: {input_dir}")
    if not (input_dir / "narration_segments.jsonl").is_file():
        legacy_video_dir = input_dir / "video"
        if args.topic_dir and (legacy_video_dir / "narration_segments.jsonl").is_file():
            input_dir = legacy_video_dir

    images_dir = (
        Path(args.images_dir).expanduser().resolve()
        if args.images_dir
        else input_dir / "images"
    )
    segments_path = (
        Path(args.segments).expanduser().resolve()
        if args.segments
        else next(
            (
                candidate
                for candidate in (
                    input_dir / "narration_segments.jsonl",
                    input_dir.parent / "narration_segments.jsonl",
                )
                if candidate.is_file()
            ),
            None,
        )
    )
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_dir / "final_video.mp4"
    )
    if output.exists() and not args.overwrite:
        fail(f"Output already exists; pass --overwrite to replace it: {output}")
    if args.width < 320 or args.height < 320 or args.fps <= 0:
        fail("Canvas dimensions and FPS must be positive and practical.")
    if args.transition_duration < 0:
        fail("--transition-duration cannot be negative.")

    require_tool("ffmpeg")
    require_tool("ffprobe")
    segments = (
        load_segments(segments_path)
        if segments_path is not None
        else discover_numbered_segments(input_dir, images_dir)
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    prepared: list[dict[str, Any]] = []
    for segment in segments:
        segment_id = str(segment["id"])
        image = resolve_image(input_dir, images_dir, segment_id)
        audio = resolve_audio(input_dir, segment)
        duration = media_duration(audio)
        quality_target_width = (
            round(args.width * 0.94) if args.motion == "float" else args.width
        )
        image_quality = inspect_image_quality(image, quality_target_width)
        if (
            args.image_quality_policy == "strict"
            and float(image_quality["upscale_factor"]) > 1.5
        ):
            fail(
                f"Image {image} needs {image_quality['upscale_factor']}x enlargement. "
                "Upscale the source image first or use a smaller output canvas."
            )
        prepared.append(
            {
                "id": segment_id,
                "order": segment["order"],
                "image": image,
                "audio": audio,
                "duration": duration,
                "image_quality": image_quality,
            }
        )

    if len(prepared) > 1:
        transition_duration = min(
            args.transition_duration,
            min(float(item["duration"]) for item in prepared) * 0.25,
        )
        if transition_duration < 0.05:
            transition_duration = 0.0
    else:
        transition_duration = 0.0

    timeline_segments: list[dict[str, Any]] = []
    cursor = 0.0
    with tempfile.TemporaryDirectory(prefix="narrated-video-") as temp:
        work_root = Path(temp)
        rendered: list[Path] = []
        durations = [float(item["duration"]) for item in prepared]
        for item_index, item in enumerate(prepared):
            segment_dir = work_root / str(item["id"])
            segment_dir.mkdir()
            segment_output = segment_dir / f"{item['id']}.mp4"
            pre_roll = transition_duration if item_index else 0.0
            build_segment(
                image=item["image"],
                audio=item["audio"],
                duration=float(item["duration"]),
                output=segment_output,
                work_dir=segment_dir,
                width=args.width,
                height=args.height,
                fps=args.fps,
                motion=args.motion,
                pre_roll=pre_roll,
                enhance_image=bool(item["image_quality"]["enhance"]),
            )
            rendered.append(segment_output)

            start = cursor
            cursor += float(item["duration"])
            timeline_segments.append(
                {
                    "id": item["id"],
                    "order": item["order"],
                    "image_file": str(item["image"]),
                    "audio_file": str(item["audio"]),
                    "image_quality": item["image_quality"],
                    "start_seconds": round(start, 3),
                    "end_seconds": round(cursor, 3),
                    "duration_seconds": round(float(item["duration"]), 3),
                }
            )
        combine_segments(
            rendered,
            durations,
            output,
            transition_duration,
            args.fps,
        )

    timeline_path = input_dir / "video_timeline.json"
    timeline_path.write_text(
        json.dumps(
            {
                "version": 1,
                "input_directory": str(input_dir),
                "segments": timeline_segments,
                "transition": {
                    "style": "crossfade",
                    "duration_seconds": round(transition_duration, 3),
                },
                "total_duration_seconds": round(cursor, 3),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    validation = validate_output(output, args.width, args.height, cursor)
    report_path = input_dir / "video_build_report.json"
    report_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "segments": len(prepared),
                "canvas": f"{args.width}x{args.height}",
                "aspect_ratio": (
                    "3:4"
                    if abs(args.width / args.height - 0.75) < 0.02
                    else "16:9"
                    if abs(args.width / args.height - 16 / 9) < 0.03
                    else "custom"
                ),
                "fps": args.fps,
                "motion": args.motion,
                "motion_details": (
                    {
                        "foreground_scale": "94%",
                        "foreground_travel": "12px horizontal, 20px vertical",
                        "background_scale": "104%",
                        "background_travel": "8px horizontal, 12px vertical",
                        "direction": "counter_motion",
                    }
                    if args.motion == "float"
                    else {
                        "top_hold": "15%",
                        "vertical_scroll": "70%",
                        "bottom_hold": "15%",
                    }
                    if args.motion == "scroll"
                    else {"style": "still"}
                ),
                "transition": {
                    "style": "crossfade",
                    "duration_seconds": round(transition_duration, 3),
                },
                "image_quality_policy": args.image_quality_policy,
                "image_quality": [
                    {
                        "id": item["id"],
                        "image_file": str(item["image"]),
                        **item["image_quality"],
                    }
                    for item in prepared
                ],
                "image_quality_warnings": [
                    (
                        f"{item['id']} requires "
                        f"{item['image_quality']['upscale_factor']}x enlargement"
                    )
                    for item in prepared
                    if item["image_quality"]["quality"]
                    in {"heavy_upscale", "severe_upscale"}
                ],
                "output": str(output),
                "timeline": str(timeline_path),
                **validation,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "passed",
                "output": str(output),
                "segments": len(prepared),
                "duration_seconds": validation["duration_seconds"],
                "timeline": str(timeline_path),
                "report": str(report_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
