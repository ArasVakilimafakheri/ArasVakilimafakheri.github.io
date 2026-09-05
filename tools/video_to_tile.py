"""
Turn a video into looping media for a portfolio tile.

Writes an MP4 and, unless told otherwise, a GIF of the same cut so the two can
be compared. That comparison is usually decisive: GIF is limited to 256 colours
per frame, which bands badly on fire, smoke and gradients, and it stores frames
without real compression, so footage routinely lands at 10-25x the size of the
equivalent MP4. An autoplaying muted MP4 looks identical on a web page at a
fraction of the bandwidth. GIF's one advantage is being a plain image that needs
no markup changes -- so the script produces both and lets the sizes argue.

ffmpeg comes from the imageio-ffmpeg package, so nothing needs to be installed
system-wide or added to PATH.

Usage:
    # a cut, both formats
    py tools/video_to_tile.py hotfire.mp4 --start 0:12 --end 0:16 --name rocket-liquids --aspect 4:5

    # the whole video, MP4 only (a 30s GIF would be enormous)
    py tools/video_to_tile.py intro.mp4 --name itt-cannon --aspect 4:5 --mp4-only

Timestamps accept seconds (12.5), M:SS (1:05), or H:MM:SS (0:01:05.5). Omit
--start/--end to use the whole video.
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


def crop_filter(aspect, anchor="center"):
    """
    Crop to an aspect ratio, e.g. '4:5' for the portrait grid tiles.

    Anchor matters more than it sounds. Cropping a 16:9 frame to 4:5 throws away
    more than half the width, so a subject sitting off to one side -- an engine
    at the right edge with its plume trailing left, say -- disappears entirely
    under the default centre crop.
    """
    if not aspect:
        return ""
    try:
        w, h = (float(n) for n in aspect.split(":"))
    except ValueError:
        raise SystemExit(f"Could not read aspect ratio: {aspect!r} (expected e.g. 4:5)")

    cw = f"min(iw,ih*{w}/{h})"
    ch = f"min(ih,iw*{h}/{w})"

    if anchor == "left":
        x = "0"
    elif anchor == "right":
        x = f"iw-{cw}"
    elif anchor == "center":
        x = f"(iw-{cw})/2"
    else:
        try:
            x = str(int(anchor))  # explicit pixel offset
        except ValueError:
            raise SystemExit(f"--anchor must be left, center, right, or a pixel offset (got {anchor!r})")

    # Each expression is quoted because they contain commas, which ffmpeg would
    # otherwise read as the separator between one filter and the next.
    return f"crop='{cw}':'{ch}':'{x}':'(ih-{ch})/2',"


def main():
    p = argparse.ArgumentParser(description="Extract a looping GIF and MP4 from a video clip.")
    p.add_argument("video", help="Source video file")
    p.add_argument("--start", default=None, help="Clip start, e.g. 0:12 or 12.5 (default: the beginning)")
    p.add_argument("--end", default=None, help="Clip end, e.g. 0:16 (default: the end)")
    p.add_argument("--name", required=True, help="Output basename, e.g. rocket-liquids")
    p.add_argument("--out", default="images", help="Destination folder (default: images)")
    p.add_argument("--width", type=int, default=800, help="Output width in px (default 800)")
    p.add_argument("--fps", type=int, default=12, help="GIF frame rate (default 12)")
    p.add_argument("--mp4-fps", type=int, default=None,
                   help="MP4 frame rate (default: keep the source rate). Dropping to "
                        "~20 is a cheap size win on long clips")
    p.add_argument("--aspect", default=None,
                   help="Crop to this ratio, e.g. 4:5 for a grid tile")
    p.add_argument("--anchor", default="center",
                   help="Where the crop sits horizontally: left, center, right, "
                        "or a pixel offset (default center)")
    p.add_argument("--crf", type=int, default=23,
                   help="MP4 quality, lower is better: 18 near-lossless, 23 default, "
                        "30+ for long clips shown small (default 23)")
    p.add_argument("--gif-only", action="store_true", help="Skip the MP4")
    p.add_argument("--mp4-only", action="store_true", help="Skip the GIF")
    args = p.parse_args()

    if args.gif_only and args.mp4_only:
        sys.exit("--gif-only and --mp4-only contradict each other")
    if not os.path.isfile(args.video):
        sys.exit(f"No such file: {args.video}")

    # Seeking before -i is fast; -t keeps the duration unambiguous. With neither
    # bound given, the whole video is used.
    if args.start is None and args.end is None:
        cut = ["-i", args.video]
        duration = None
    else:
        start = parse_time(args.start) if args.start else 0.0
        if args.end is None:
            sys.exit("--start needs a matching --end")
        duration = parse_time(args.end) - start
        if duration <= 0:
            sys.exit("--end must come after --start")
        cut = ["-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", args.video]

    if not args.mp4_only and duration is not None and duration > 15:
        print(f"Note: {duration:.1f}s is a lot of GIF; consider --mp4-only.\n")

    os.makedirs(args.out, exist_ok=True)
    crop = crop_filter(args.aspect, args.anchor)
    scale = f"scale={args.width}:-2:flags=lanczos"

    results = []

    if not args.mp4_only:
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
        results.append(("GIF", gif_path))

    if not args.gif_only:
        mp4_path = os.path.join(args.out, args.name + ".mp4")
        print("Writing MP4...")
        rate = f"fps={args.mp4_fps}," if args.mp4_fps else ""
        run([FFMPEG, "-y", *cut,
             "-vf", f"{crop}{rate}{scale}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(args.crf),
             "-movflags", "+faststart",
             "-an",  # no audio: browsers only autoplay silent video
             mp4_path], "MP4 encoding")
        results.append(("MP4", mp4_path))

    print()
    for label, path in results:
        kb = os.path.getsize(path) // 1024
        print(f"  {label:4}  {os.path.basename(path):32}  {kb:>6} KB")

    if len(results) == 2:
        gif_bytes = os.path.getsize(results[0][1])
        mp4_bytes = os.path.getsize(results[1][1])
        if mp4_bytes:
            print(f"\n  The GIF is {gif_bytes / mp4_bytes:.1f}x the size of the MP4.")


if __name__ == "__main__":
    main()
