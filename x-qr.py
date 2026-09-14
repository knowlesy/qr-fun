import sys
import os
import argparse
import random
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import qrcode
from qrcode.constants import ERROR_CORRECT_H

RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def generate_qr_matrix(url: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=1,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = np.array(qr.get_matrix(), dtype=bool)
    return matrix

def get_protected_mask(size: int, border: int = 4):
    """
    Protects the vital QR features (finder patterns, timing lines, quiet zone)
    so smartphones can reliably decode the Rickroll payload.
    """
    mask = np.zeros((size, size), dtype=bool)
    fp_size = 8  # 7x7 pattern + 1 module border
    
    # Corner finder patterns
    mask[border:border+fp_size, border:border+fp_size] = True
    mask[border:border+fp_size, size-border-fp_size:size-border] = True
    mask[size-border-fp_size:size-border, border:border+fp_size] = True

    # Timing patterns
    timing_idx = border + 6
    mask[timing_idx, :] = True
    mask[:, timing_idx] = True

    # Quiet zone border
    mask[:border, :] = True
    mask[-border:, :] = True
    mask[:, :border] = True
    mask[:, -border:] = True

    return mask

def generate_sheets(image_path: str, url: str = RICKROLL_URL):
    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    out_a = f"{base_name}_sheet_a.png"
    out_b = f"{base_name}_sheet_b.png"
    out_sim = f"{base_name}_preview.png"

    # 1. Generate base QR Code
    qr_matrix = generate_qr_matrix(url)
    qr_size = qr_matrix.shape[0]
    protected = get_protected_mask(qr_size, border=4)

    # 2. Prepare secret image preserving aspect ratio (no squishing)
    raw_img = Image.open(image_path).convert("L")
    
    # Scale proportionally so the longest edge fits inside the QR grid
    img_fitted = ImageOps.contain(raw_img, (qr_size, qr_size), method=Image.Resampling.LANCZOS)
    
    # Center on a pure white square background
    canvas_img = Image.new("L", (qr_size, qr_size), color=255)
    offset_x = (qr_size - img_fitted.width) // 2
    offset_y = (qr_size - img_fitted.height) // 2
    canvas_img.paste(img_fitted, (offset_x, offset_y))

    # Threshold to pure black (0) and white (1)
    bw_arr = np.array(canvas_img)
    secret_binary = np.where(bw_arr < 128, 0, 1)

    # 3. Build Visual Cryptography 2x2 Sub-pixel Grid
    out_size = qr_size * 2
    sheet_a = np.zeros((out_size, out_size), dtype=np.uint8)
    sheet_b = np.zeros((out_size, out_size), dtype=np.uint8)

    patterns = [
        np.array([[255, 0], [0, 255]], dtype=np.uint8),
        np.array([[0, 255], [255, 0]], dtype=np.uint8),
        np.array([[255, 255], [0, 0]], dtype=np.uint8),
        np.array([[0, 0], [255, 255]], dtype=np.uint8),
        np.array([[255, 0], [255, 0]], dtype=np.uint8),
        np.array([[0, 255], [0, 255]], dtype=np.uint8),
    ]

    for y in range(qr_size):
        for x in range(qr_size):
            y2, x2 = y * 2, x * 2

            if protected[y, x]:
                # Finder patterns remain solid on both sheets
                val = 0 if qr_matrix[y, x] else 255
                sheet_a[y2:y2+2, x2:x2+2] = val
                sheet_b[y2:y2+2, x2:x2+2] = val
            else:
                pat = random.choice(patterns)
                if secret_binary[y, x] == 1:
                    # Secret is white: match patterns
                    sheet_a[y2:y2+2, x2:x2+2] = pat
                    sheet_b[y2:y2+2, x2:x2+2] = pat
                else:
                    # Secret is black: complementary patterns
                    sheet_a[y2:y2+2, x2:x2+2] = pat
                    sheet_b[y2:y2+2, x2:x2+2] = 255 - pat

    # 4. Format to standard A4 Canvas (300 DPI: 2480 x 3508 px)
    def render_a4_page(matrix_data):
        canvas = Image.new("RGB", (2480, 3508), "white")
        draw = ImageDraw.Draw(canvas)

        # Scale QR block to 1800 x 1800 px (~152 mm square)
        qr_rendered = Image.fromarray(matrix_data).resize(
            (1800, 1800), Image.Resampling.NEAREST
        )
        x_pos = (2480 - 1800) // 2
        y_pos = (3508 - 1800) // 2

        canvas.paste(qr_rendered, (x_pos, y_pos))

        # Precision alignment crosshairs in margins
        coords = [
            (x_pos - 50, y_pos - 50),
            (x_pos + 1800 + 50, y_pos - 50),
            (x_pos - 50, y_pos + 1800 + 50),
            (x_pos + 1800 + 50, y_pos + 1800 + 50),
        ]
        line_len = 35
        for cx, cy in coords:
            draw.line([(cx - line_len, cy), (cx + line_len, cy)], fill="black", width=5)
            draw.line([(cx, cy - line_len), (cx, cy + line_len)], fill="black", width=5)

        return canvas

    sheet_a_img = render_a4_page(sheet_a)
    sheet_b_img = render_a4_page(sheet_b)

    # Simulated light overlay
    simulated = np.minimum(sheet_a, sheet_b)
    sim_img = render_a4_page(simulated)

    sheet_a_img.save(out_a, dpi=(300, 300))
    sheet_b_img.save(out_b, dpi=(300, 300))
    sim_img.save(out_sim, dpi=(300, 300))

    print(f"Generated:\n - {out_a}\n - {out_b}\n - {out_sim}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate proportional visual cryptography sheets."
    )
    parser.add_argument("image_path", type=str, help="Path to input silhouette image")
    parser.add_argument(
        "--url",
        type=str,
        default=RICKROLL_URL,
        help="QR redirect URL (defaults to Rickroll)",
    )
    args = parser.parse_args()

    generate_sheets(args.image_path, url=args.url)