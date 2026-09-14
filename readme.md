# Visual Cryptography Optical Overlay (2-out-of-2 Secret Sharing)

This tool implements a 2-out-of-2 visual cryptography secret sharing scheme. It takes any input image (such as a silhouette or high-contrast graphic), binarizes it, and splits it into two distinct printable image sheets (`sheet_a.png` and `sheet_b.png`).

Individually, each sheet looks like random modular noise or a dense QR-style dot pattern and reveals zero information about the original image. However, when both sheets are printed on standard paper or transparent film and **overlapped directly over a torch, lamp, or phone flashlight**, the secret silhouette magically appears.

---

## How It Works

1. **Sub-pixel Expansion ($2 \times 2$ blocks):**
   - Each pixel of the source image expands into a $2 \times 2$ sub-pixel block on Sheet A and Sheet B.
   - Every block contains exactly 2 black and 2 white sub-pixels (50% local optical density on each individual sheet).
2. **Optical OR Logic (Transmissivity):**
   - **White pixel in secret:** Both Sheet A and Sheet B receive the **exact same** $2 \times 2$ pattern. When aligned, the transparent sub-pixels match up and let light pass through (50% transmission).
   - **Black pixel in secret:** Sheet B receives the **inverted complement** of Sheet A's pattern. When overlapped, all 4 sub-pixels are blocked (0% transmission), producing an opaque black silhouette.

---

## Installation

Ensure you have Python 3.8+ installed. Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

---

## Usage

Run `x.py` by providing the path to your source image:

```bash
python x.py pikachu.png
```

### Optional Arguments

- `--width`: Logical module width for resolution adjustment (default: `150`).

```bash
python x.py pikachu.png --width 180
```

### Generated Outputs

When executed, the script creates three files:
- `<filename>_sheet_a.png` — First printable encrypted sheet.
- `<filename>_sheet_b.png` — Second printable encrypted sheet.
- `<filename>_preview.png` — A digital simulation of the physical optical overlap.

---

## Physical Printing & Demonstration Tips

1. **Paper Selection:** 
   - Standard 70–80 gsm copy paper works great when illuminated from behind with a phone flashlight or torch.
   - For maximum clarity and high-contrast projection, print onto transparent overhead projector (OHP) / acetate film.
2. **Alignment:**
   - Both pages are generated with identical outer dimensions.
   - Align the physical borders of the papers carefully while holding them in front of your light source until the hidden figure snaps into focus.