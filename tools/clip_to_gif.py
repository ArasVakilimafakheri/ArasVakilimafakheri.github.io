"""
Cut a short clip out of a video and turn it into a looping GIF (and an MP4).

Both are produced from the same cut so they can be compared directly. That
comparison matters: GIF is limited to 256 colours per frame, which bands badly
on fire, smoke and gradients, and it stores frames without real compression, so
a few seconds of footage routinely lands at 10-20x the size of the equivalent
MP4. An autoplaying muted MP4 looks identical to a GIF on a web page and costs a
fraction of the bandwidth -- but GIF still wins on being a plain image that
works anywhere without markup changes, so the script hands over both and lets
the sizes make the argument.

ffmpeg comes from the imageio-ffmpeg package, so nothing needs to be installed
system-wide or added to PATH.

Usage:
    py tools/clip_to_gif.py hotfire.mp4 --start 0:12 --end 0:16 --name rocket-liquids
    py tools/clip_to_gif.py hotfire.mp4 --start 12.5 --end 16 --name rocket-liquids --aspect 4:5

Timestamps accept seconds (12.5), M:SS (1:05), or H:MM:SS (0:01:05.5).
"""

import argparse
import os
import subprocess
import sys

try:
    import imageio_ffmpeg
except ImportError:
    sys.exit("imageio-ffmpeg is not installed. Run:  py -m pip install imageio-ffmpeg")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def parse_time(value):
    """'1:05.5' -> 65.5 seconds. Also accepts '65.5' and '0:01:05.5'."""
    parts = str(value).strip().split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise SystemExit(f"Could not read timestamp: {value!r}")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def run(args, label):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise SystemExit(f"ffmpeg failed during {label}:\n{tail}")


def crop_filter(aspect):
    """Centre-crop to an aspect ratio, e.g. '4:5' for the portrait grid tiles."""
    if not aspect:
        return ""
    try:
        w, h = (float(n) for n in aspect.split(":"))
    except ValueError:
        raise SystemExit(f"Could not read aspect ratio: {aspect!r} (expected e.g. 4:5)")
    # Take the largest centred rectangle of this ratio that fits in the source.
    return f"crop='min(iw,ih*{w}/{h})':'min(ih,iw*{h}/{w})',"


def main():
    p = argparse.ArgumentParser(description="Extract a looping GIF and MP4 from a video clip.")
    p.add_argument("video", help="Source video file")
    p.add_argument("--start", required=True, help="Clip start, e.g. 0:12 or 12.5")
    p.add_argument("--end", required=True, help="Clip end, e.g. 0:16")
    p.add_argument("--name", required=True, help="Output basename, e.g. rocket-liquids")
    p.add_argument("--out", default="images", help="Destination folder (default: images)")
    p.add_argument("--width", type=int, default=800, help="Output width in px (default 800)")
    p.add_argument("--fps", type=int, default=12, help="GIF frame rate (default 12)")
    p.add_argument("--aspect", default=None,
                   help="Centre-crop to this ratio, e.g. 4:5 for a grid tile")
    p.add_argument("--gif-only", action="store_true", help="Skip the MP4")
    args = p.parse_args()

    if not os.path.isfile(args.video):
        sys.exit(f"No such file: {args.video}")

    start = parse_time(args.start)
    duration = parse_time(args.end) - start
    if duration <= 0:
        sys.exit("--end must come after --start")
    if duration > 15:
        print(f"Note: {duration:.1f}s is long for a looping clip; 3-6s usually reads better.\n")

    os.makedirs(args.out, exist_ok=True)
    crop = crop_filter(args.aspect)
    scale = f"scale={args.width}:-2:flags=lanczos"

    # Seeking before -i is fast; -t keeps the duration unambiguous.
    cut = ["-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", args.video]

    gif_path = os.path.join(args.out, args.name + ".gif")
    palette = os.path.join(args.out, f".{args.name}-palette.png")

    # A GIF built against a palette generated from the actual clip looks far
    # better than ffmpeg's default quantisation, which is what makes most
    # converted GIFs look muddy.
    print("Building palette...")
    run([FFMPEG, "-y", *cut,
         "-vf", f"{crop}fps={args.fps},{scale},palettegen=stats_mode=diff",
         palette], "palette generation")

    print("Writing GIF...")
    run([FFMPEG, "-y", *cut, "-i", palette,
         "-lavfi", f"{crop}fps={args.fps},{scale}[x];[x][1:v]"
                   "paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
         "-loop", "0", gif_path], "GIF encoding")
    os.remove(palette)

    results = [("GIF", gif_path)]

    if not args.gif_only:
        mp4_path = os.path.join(args.out, args.name + ".mp4")
        print("Writing MP4...")
        run([FFMPEG, "-y", *cut,
             "-vf", f"{crop}{scale}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
             "-movflags", "+faststart",
             "-an",  # no audio: browsers only autoplay silent video
             mp4_path], "MP4 encoding")
        results.append(("MP4", mp4_path))

    print()
    for label, path in results:
        kb = os.path.getsize(path) // 1024
        print(f"  {label:4}  {os.path.basename(path):32}  {kb:>6} KB")

    if len(results) == 2:
        gif_kb = os.path.getsize(results[0][1])
        mp4_kb = os.path.getsize(results[1][1])
        if mp4_kb:
            print(f"\n  The GIF is {gif_kb / mp4_kb:.1f}x the size of the MP4.")


if __name__ == "__main__":
    main()
