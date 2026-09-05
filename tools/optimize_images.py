"""
Prepare raw camera photos for the portfolio site.

Photos straight off a phone or DSLR are 4-12 MB each. A page with nine of those
takes many seconds to load and bloats the git repo permanently, since git keeps
every version of a binary file forever. This script resizes and compresses them
to web dimensions, and strips EXIF metadata along the way -- phone photos embed
GPS coordinates of where they were taken, which should not go on a public site.

Usage:
    py tools/optimize_images.py images/raw                  # -> images/
    py tools/optimize_images.py images/raw --max-width 1200 # smaller, for grid tiles
    py tools/optimize_images.py images/raw --out images/    # explicit destination

PNG inputs stay PNG (better for CAD screenshots and MATLAB plots, which have
flat colour and hard edges). Everything else is written as JPEG.
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is not installed. Run:  py -m pip install pillow")

# iPhone photos are .HEIC, which Pillow cannot read on its own.
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIC = True
except ImportError:
    HEIC = False

SOURCE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic", ".heif"}


def slugify(name):
    """'Hot Fire Test 3.JPG' -> 'hot-fire-test-3'"""
    stem = os.path.splitext(name)[0].lower()
    cleaned = [c if c.isalnum() else "-" for c in stem]
    slug = "".join(cleaned)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "image"


def optimize(src_path, out_dir, max_width, quality):
    name = os.path.basename(src_path)
    ext = os.path.splitext(name)[1].lower()

    if ext in {".heic", ".heif"} and not HEIC:
        return None, f"{name}: HEIC support missing. Run:  py -m pip install pillow-heif"

    try:
        img = Image.open(src_path)
    except Exception as exc:
        return None, f"{name}: could not open ({exc})"

    # Cameras record orientation as metadata rather than rotating the pixels.
    # Apply it now, because stripping EXIF below would otherwise leave the
    # image sideways.
    img = ImageOps.exif_transpose(img)

    before = os.path.getsize(src_path)
    if img.width > max_width:
        height = round(img.height * max_width / img.width)
        img = img.resize((max_width, height), Image.LANCZOS)

    keep_png = ext == ".png"
    out_ext = ".png" if keep_png else ".jpg"
    out_path = os.path.join(out_dir, slugify(name) + out_ext)

    # Pasting the pixels into a brand new image leaves EXIF (and its GPS tags)
    # behind, since none of that metadata follows the pixel data across.
    mode = img.mode if keep_png else "RGB"
    clean = Image.new(mode, img.size)
    clean.paste(img.convert(mode))

    if keep_png:
        clean.save(out_path, "PNG", optimize=True)
    else:
        clean.save(out_path, "JPEG", quality=quality, optimize=True, progressive=True)

    after = os.path.getsize(out_path)
    saved = 100 - (after * 100 // max(before, 1))
    return (
        f"{name}  ->  {os.path.basename(out_path)}"
        f"   {before // 1024} KB -> {after // 1024} KB  ({saved}% smaller)",
        None,
    )


def main():
    parser = argparse.ArgumentParser(description="Resize, compress and de-EXIF photos for the web.")
    parser.add_argument("source", help="Folder holding the raw photos")
    parser.add_argument("--out", default="images", help="Destination folder (default: images)")
    parser.add_argument("--max-width", type=int, default=1800,
                        help="Longest edge in pixels (default 1800; use ~1200 for grid tiles)")
    parser.add_argument("--quality", type=int, default=82,
                        help="JPEG quality 1-95 (default 82)")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        sys.exit(f"No such folder: {args.source}")
    os.makedirs(args.out, exist_ok=True)

    files = sorted(
        f for f in os.listdir(args.source)
        if os.path.splitext(f)[1].lower() in SOURCE_TYPES
    )
    if not files:
        sys.exit(f"No images found in {args.source}")

    problems = []
    done = 0
    for f in files:
        line, problem = optimize(os.path.join(args.source, f), args.out,
                                 args.max_width, args.quality)
        if problem:
            problems.append(problem)
        else:
            print(line)
            done += 1

    print(f"\n{done} image(s) written to {args.out}/")
    if problems:
        print("\nSkipped:")
        for p in problems:
            print("  " + p)


if __name__ == "__main__":
    main()
