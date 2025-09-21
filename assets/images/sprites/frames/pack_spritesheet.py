#!/usr/bin/env python3
"""
pack_spritesheet.py
Builds a 4x4 sprite sheet (192x256) with 16 frames of size 48x64 (RGBA).
Usage:
  python pack_spritesheet.py --in frames_dir --out forest_mystic_192x256.png [--manifest manifest_order.txt] [--dither] [--maxcolors 32] [--pad 0]
Requirements: Pillow
"""
import argparse, os, sys
from PIL import Image

CELL_W, CELL_H = 48, 64
COLS, ROWS = 4, 4
SHEET_W, SHEET_H = CELL_W * COLS, CELL_H * ROWS

DEFAULT_ORDER = [
  # Row 1 (Down): idle, walkA, walkB, walkC
  "down_idle.png", "down_walk1.png", "down_walk2.png", "down_walk3.png",
  # Row 2 (Left)
  "left_idle.png", "left_walk1.png", "left_walk2.png", "left_walk3.png",
  # Row 3 (Right)
  "right_idle.png", "right_walk1.png", "right_walk2.png", "right_walk3.png",
  # Row 4 (Up)
  "up_idle.png", "up_walk1.png", "up_walk2.png", "up_walk3.png",
]

def read_manifest(path):
    order = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#"):
                continue
            order.append(line)
    return order

def load_and_fit(path, cell_w, cell_h, pad=0):
    """Load an RGBA frame and fit it into cell, preserving aspect.
       Will center the image inside the cell. If larger, it will downscale.
    """
    im = Image.open(path).convert("RGBA")
    # Remove any color-key backgrounds (optional step if needed)
    # None by default.
    w, h = im.size

    # enforce max size (cell - padding)
    target_w = cell_w - (pad*2)
    target_h = cell_h - (pad*2)

    scale = min(target_w/max(1,w), target_h/max(1,h))
    if scale < 1.0:
        new_w = max(1, int(w*scale))
        new_h = max(1, int(h*scale))
        im = im.resize((new_w, new_h), Image.NEAREST)

    # center it
    canvas = Image.new("RGBA", (cell_w, cell_h), (0,0,0,0))
    cx = (cell_w - im.size[0]) // 2
    cy = (cell_h - im.size[1]) // 2
    canvas.alpha_composite(im, (cx, cy))
    return canvas

def quantize_image(im, maxcolors, dither):
    # Convert to P mode with limited palette, keeping alpha
    # Split alpha, quantize RGB, then re-attach alpha for best results
    rgb = im.convert("RGB")
    dither_flag = Image.FLOYDSTEINBERG if dither else Image.NONE
    pal = rgb.quantize(colors=maxcolors, method=Image.MEDIANCUT, dither=dither_flag)
    pal_rgb = pal.convert("RGB")
    a = im.split()[-1]
    out = Image.merge("RGBA", (*pal_rgb.split(), a))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_dir", required=True, help="Directory with 16 input frames")
    ap.add_argument("--out", dest="out_path", required=True, help="Output PNG path (192x256)")
    ap.add_argument("--manifest", dest="manifest", default=None, help="Optional manifest_order.txt path")
    ap.add_argument("--dither", action="store_true", help="Enable Floyd–Steinberg dithering when quantizing")
    ap.add_argument("--maxcolors", type=int, default=32, help="Max colors for palette quantization (default 32)")
    ap.add_argument("--pad", type=int, default=0, help="Padding inside each 48x64 cell")
    args = ap.parse_args()

    order = DEFAULT_ORDER
    if args.manifest:
        order = read_manifest(args.manifest)
        if len(order) != 16:
            print(f"Manifest must list exactly 16 filenames; got {len(order)}", file=sys.stderr)
            sys.exit(2)

    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0,0,0,0))

    # place frames
    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            fname = order[idx]
            src_path = os.path.join(args.in_dir, fname)
            if not os.path.exists(src_path):
                print(f"Missing frame: {src_path}", file=sys.stderr)
                sys.exit(3)
            frame = load_and_fit(src_path, CELL_W, CELL_H, pad=args.pad)
            sheet.alpha_composite(frame, (c*CELL_W, r*CELL_H))
            idx += 1

    # optional quantize for 16-bit/SNES vibe
    if args.maxcolors and args.maxcolors > 0:
        sheet = quantize_image(sheet, args.maxcolors, args.dither)

    # save
    sheet.save(args.out_path, "PNG")
    print(f"Wrote {args.out_path} ({SHEET_W}x{SHEET_H})")

if __name__ == "__main__":
    main()
