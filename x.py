import sys
import os
import argparse
import random
import numpy as np
from PIL import Image

def generate_sheets(image_path: str, target_width: int = 150):
    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        sys.exit(1)

    # Base name for output naming
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    out_a = f"{base_name}_sheet_a.png"
    out_b = f"{base_name}_sheet_b.png"
    out_sim = f"{base_name}_preview.png"

    # 1. Load image and convert to greyscale
    img = Image.open(image_path).convert("L")

    # Resize preserving aspect ratio
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Convert to pure black (0) and white (1)
    bw_arr = np.array(img)
    binary = np.where(bw_arr < 128, 0, 1)

    h, w = binary.shape
    out_h, out_w = h * 2, w * 2

    sheet_a = np.zeros((out_h, out_w), dtype=np.uint8)
    sheet_b = np.zeros((out_h, out_w), dtype=np.uint8)

    # Permutations of balanced 2x2 blocks (2 white, 2 black)
    patterns = [
        np.array([[255, 0], [0, 255]], dtype=np.uint8),
        np.array([[0, 255], [255, 0]], dtype=np.uint8),
        np.array([[255, 255], [0, 0]], dtype=np.uint8),
        np.array([[0, 0], [255, 255]], dtype=np.uint8),
        np.array([[255, 0], [255, 0]], dtype=np.uint8),
        np.array([[0, 255], [0, 255]], dtype=np.uint8),
    ]

    for y in range(h):
        for x in range(w):
            base_pattern = random.choice(patterns)
            y2, x2 = y * 2, x * 2

            if binary[y, x] == 1:
                # White pixel: Identical patterns (translucent overlap)
                sheet_a[y2:y2+2, x2:x2+2] = base_pattern
                sheet_b[y2:y2+2, x2:x2+2] = base_pattern
            else:
                # Black pixel: Inverted patterns (blocks 100% of light)
                inverted_pattern = 255 - base_pattern
                sheet_a[y2:y2+2, x2:x2+2] = base_pattern
                sheet_b[y2:y2+2, x2:x2+2] = inverted_pattern

    # Scale up blocks using nearest-neighbour so printer output is crisp
    scale_factor = 6
    final_size = (out_w * scale_factor, out_h * scale_factor)

    img_a = Image.fromarray(sheet_a).resize(final_size, Image.Resampling.NEAREST)
    img_b = Image.fromarray(sheet_b).resize(final_size, Image.Resampling.NEAREST)

    # Simulated overlap (light passes only where both are white)
    simulated = np.minimum(sheet_a, sheet_b)
    img_sim = Image.fromarray(simulated).resize(final_size, Image.Resampling.NEAREST)

    img_a.save(out_a)
    img_b.save(out_b)
    img_sim.save(out_sim)

    print(f"Created:\n - {out_a}\n - {out_b}\n - {out_sim}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split an image into two visual cryptography printable sheets."
    )
    parser.add_argument("image_path", type=str, help="Path to the image to split")
    parser.add_argument(
        "--width",
        type=int,
        default=150,
        help="Target grid width in logical pixels (default: 150)",
    )
    args = parser.parse_args()

    generate_sheets(args.image_path, target_width=args.width)