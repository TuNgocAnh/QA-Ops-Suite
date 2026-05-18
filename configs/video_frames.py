"""
Video frame extractor for /log-bug - extract key frames from bug recording videos.

Extracts smart key frames from short bug recording videos (max 2 minutes),
optimized for minimal frames that capture the bug context.

Usage:
  python configs/video_frames.py <video_path>                     (Windows)
  python3 configs/video_frames.py <video_path>                    (macOS / Linux)
  python configs/video_frames.py <video_path> --max-frames 8
  python configs/video_frames.py <video_path> --width 1440        (default 1280, pass 0 to disable resize)
  python configs/video_frames.py <video_path> --output-dir /tmp/frames

Programmatic:
  from configs.video_frames import extract_frames
  result = extract_frames("/path/to/bug.mp4")
  # result = {"frames": ["/tmp/.../frame_001.jpg", ...], "duration": 45.2, "fps": 30, ...}

Requirements:
  - ffmpeg + ffprobe installed (macOS: brew install ffmpeg, Windows: download from ffmpeg.org)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

MAX_DURATION_SECONDS = 120  # 2 minutes
DEFAULT_MAX_FRAMES = 10
MIN_FRAMES = 3
FRAME_QUALITY = 2  # ffmpeg jpeg quality (2=high, 5=medium, 10=low)
DEFAULT_WIDTH = 1280  # resize frames to this width (keep aspect ratio). None = no resize


def _check_ffmpeg():
    """Check ffmpeg and ffprobe are available."""
    for cmd in ("ffmpeg", "ffprobe"):
        if not shutil.which(cmd):
            print(f"Error: {cmd} not found. Install: brew install ffmpeg (macOS) or download from ffmpeg.org (Windows)")
            sys.exit(1)


def _get_video_info(video_path):
    """Get video metadata using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    video_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
        None
    )
    if not video_stream:
        raise RuntimeError("No video stream found in file")

    duration = float(data["format"].get("duration", 0))
    fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
    fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    return {
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "codec": video_stream.get("codec_name", "unknown"),
    }


def _calculate_frame_timestamps(duration, max_frames=DEFAULT_MAX_FRAMES):
    """Calculate optimal frame timestamps based on video duration.

    Strategy:
    - First frame at 0.5s (initial state)
    - Last frame at duration - 0.5s (final state / bug result)
    - Middle frames evenly distributed
    - For very short videos (<5s): just first, middle, last
    - For short videos (5-30s): every 3-5 seconds
    - For medium videos (30-120s): every 8-15 seconds
    """
    if duration <= 0:
        return [0]

    # Clamp to safe boundaries
    start = min(0.5, duration * 0.1)
    end = max(duration - 0.5, duration * 0.9)

    if duration <= 3:
        # Very short: just 2 frames (start + end)
        return [start, end]

    if duration <= 5:
        # Short: start, middle, end
        return [start, duration / 2, end]

    if duration <= 30:
        # Short video: frame every ~3-5 seconds
        interval = max(3, duration / max_frames)
    elif duration <= 60:
        # Medium: frame every ~8 seconds
        interval = max(5, duration / max_frames)
    else:
        # Longer (up to 2 min): frame every ~12-15 seconds
        interval = max(8, duration / max_frames)

    timestamps = [start]
    current = start + interval
    while current < end - (interval * 0.3):
        timestamps.append(round(current, 2))
        current += interval

    # Always include the end frame
    if timestamps[-1] < end - 1:
        timestamps.append(round(end, 2))

    # Enforce max frames limit
    if len(timestamps) > max_frames:
        # Keep first and last, evenly sample the middle
        step = (len(timestamps) - 1) / (max_frames - 1)
        indices = [round(i * step) for i in range(max_frames)]
        timestamps = [timestamps[i] for i in indices]

    # Enforce min frames (pad if needed)
    if len(timestamps) < MIN_FRAMES and duration > 3:
        mid = duration / 2
        if mid not in timestamps:
            timestamps.append(round(mid, 2))
            timestamps.sort()

    return timestamps


def _format_timestamp(seconds):
    """Format seconds to HH:MM:SS.mmm for display."""
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(int(mins), 60)
    return f"{hours:02d}:{int(mins):02d}:{secs:06.3f}"


def extract_frames(video_path, max_frames=DEFAULT_MAX_FRAMES, output_dir=None, width=DEFAULT_WIDTH):
    """Extract key frames from a video file.

    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to extract (default 10)
        output_dir: Directory to save frames (default: temp dir)
        width: Resize frames to this pixel width, keep aspect ratio (default 1280).
               Pass None or 0 to disable resize (use original resolution).

    Returns:
        dict with keys:
            frames: list of frame file paths (jpg)
            duration: video duration in seconds
            fps: video fps
            width, height: video resolution (ORIGINAL, not output)
            output_width: actual width of extracted frames (after resize)
            timestamps: list of timestamps (seconds) for each frame
            output_dir: directory containing frames
    """
    _check_ffmpeg()

    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Get video info
    info = _get_video_info(video_path)

    # Validate duration
    if info["duration"] > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Video is {info['duration']:.0f}s (max {MAX_DURATION_SECONDS}s / {MAX_DURATION_SECONDS // 60} minutes). "
            f"Please trim the video or provide a shorter recording."
        )

    if info["duration"] <= 0:
        raise ValueError("Video has no duration or is corrupted")

    # Calculate timestamps
    timestamps = _calculate_frame_timestamps(info["duration"], max_frames)

    # Create output directory
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="qa-ops-suite-frames-")
    else:
        os.makedirs(output_dir, exist_ok=True)

    # Determine target output width (resize). 0/None => keep original.
    try:
        target_width = int(width) if width else 0
    except (TypeError, ValueError):
        target_width = 0
    # Don't upscale: if original is already smaller than target, skip resize.
    if target_width and info["width"] and target_width >= info["width"]:
        target_width = 0
    output_width = target_width if target_width else info["width"]

    # Extract frames at calculated timestamps
    frames = []
    for i, ts in enumerate(timestamps, 1):
        output_path = os.path.join(output_dir, f"frame_{i:03d}.jpg")
        cmd = [
            "ffmpeg", "-v", "quiet",
            "-ss", str(ts),
            "-i", video_path,
            "-frames:v", "1",
        ]
        if target_width:
            # scale=W:-2 keeps aspect ratio + ensures even height (libx264 requirement)
            cmd += ["-vf", f"scale={target_width}:-2"]
        cmd += [
            "-q:v", str(FRAME_QUALITY),
            "-y",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(output_path):
            frames.append(output_path)
        else:
            print(f"Warning: Failed to extract frame at {_format_timestamp(ts)}", file=sys.stderr)

    if not frames:
        raise RuntimeError("Failed to extract any frames from video")

    return {
        "frames": frames,
        "duration": info["duration"],
        "fps": info["fps"],
        "width": info["width"],
        "height": info["height"],
        "output_width": output_width,
        "codec": info["codec"],
        "timestamps": timestamps[:len(frames)],
        "output_dir": output_dir,
        "video_path": video_path,
    }


def print_summary(result):
    """Print human-readable summary of extraction result."""
    dur = result["duration"]
    mins, secs = divmod(dur, 60)
    print(f"Video: {os.path.basename(result['video_path'])}")
    print(f"Duration: {int(mins)}m {secs:.1f}s | Resolution: {result['width']}x{result['height']} | FPS: {result['fps']:.0f}")
    out_w = result.get("output_width") or result["width"]
    if out_w != result["width"]:
        print(f"Frames resized to width {out_w}px (original {result['width']}px)")
    print(f"Extracted {len(result['frames'])} frames:")
    for i, (frame, ts) in enumerate(zip(result["frames"], result["timestamps"]), 1):
        print(f"  [{i}] {_format_timestamp(ts)} => {frame}")
    print(f"Output dir: {result['output_dir']}")


# =============================================================
# CLI
# =============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract key frames from bug recording videos")
    parser.add_argument("video_path", help="Path to video file")
    parser.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES, help=f"Max frames to extract (default {DEFAULT_MAX_FRAMES})")
    parser.add_argument("--output-dir", help="Output directory for frames (default: temp dir)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"Resize frame to this pixel width, keep aspect ratio (default {DEFAULT_WIDTH}). Pass 0 to disable resize.")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        result = extract_frames(args.video_path, args.max_frames, args.output_dir, args.width)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_summary(result)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
