---
name: reftab-image-converter
description: Converts uploaded images to the correct format for RefTab thumbnails: 1080 × 1908 px portrait, logo centered on a white canvas. Use this skill whenever the user wants to prepare, convert, resize, or fix an image for RefTab, mentions "RefTab format", "thumbnail", or asks to make an image match the correct dimensions. Also trigger if the user uploads one or more images and says anything like "same as before", "do the same fix", "convert this", or "make it work in RefTab". Trigger even for single images or batches.
---

# RefTab Image Converter

Converts any uploaded image into the correct RefTab thumbnail format:
- **Output size**: 1080 × 1908 px (portrait)
- **Background**: White (#FFFFFF)
- **Logo placement**: Scaled to full width, centered vertically
- **Output format**: PNG

---

## Workflow

### 1. Identify input images
Check the uploaded files from the conversation. The user may upload one or many images. Process all of them.

### 2. Run the conversion script
Use `bash_tool` to run the Python conversion. Always install Pillow first if needed.

```bash
pip install pillow --break-system-packages -q
```

Then run the conversion (adapt paths to match the actual uploaded filenames):

```python
from PIL import Image
import os

TARGET_W, TARGET_H = 1080, 1908
BACKGROUND = (255, 255, 255)

input_paths = [
    # list all uploaded image paths here
    "/mnt/user-data/uploads/your_image.png",
]

for input_path in input_paths:
    img = Image.open(input_path)

    # Scale to full width, preserve aspect ratio
    scale = TARGET_W / img.width
    new_w = TARGET_W
    new_h = int(img.height * scale)

    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Create white canvas
    canvas = Image.new("RGB", (TARGET_W, TARGET_H), BACKGROUND)

    # Center vertically
    y_offset = (TARGET_H - new_h) // 2
    canvas.paste(img_resized, (0, y_offset))

    # Save output
    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)
    output_path = f"/mnt/user-data/outputs/{name}_reftab.png"
    canvas.save(output_path)
    print(f"Saved: {output_path} ({TARGET_W}x{TARGET_H})")
```

### 3. Handle edge cases

| Situation | Handling |
|---|---|
| Image is already portrait | Still reformat to exactly 1080×1908 — pad as needed |
| Image is square | Scale to width, pad top and bottom equally |
| Image is very tall (taller than 1908 when scaled) | Scale to fit height instead, centre horizontally |
| Image has transparency (RGBA/PNG) | Flatten onto white background before resizing: `img = Image.alpha_composite(Image.new("RGBA", img.size, "WHITE"), img.convert("RGBA")).convert("RGB")` |
| Batch of images | Loop through all, save each with `_reftab` suffix |

### 4. Present the output
Use `present_files` to share all converted images with the user.

---

## Output naming convention
`{original_filename}_reftab.png`

Examples:
- `linktek.png` → `linktek_reftab.png`
- `citect_scada.png` → `citect_scada_reftab.png`

---

## Quick reference
- Target: **1080 × 1908 px**
- Background: **white**
- Scale mode: **fit width**, then centre vertically
- Format: **PNG**
