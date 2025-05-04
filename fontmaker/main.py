import argparse
import json
import re
import os

import freetype
from PIL import Image, ImageDraw, ImageFont

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True)
    parser.add_argument("-f", "--font", required=True)
    parser.add_argument("-s", "--size", type=int, required=True)
    arguments = parser.parse_args()

    face = freetype.Face(arguments.font)
    face.set_char_size(arguments.size * 64)
    glyphs = []
    charcode, gindex = face.get_first_char()
    while gindex != 0:
        ch = chr(charcode)
        if ch.encode("utf-8", errors="ignore"):
            glyphs.append(ch)
        charcode, gindex = face.get_next_char(charcode, gindex)

    font = ImageFont.truetype(arguments.font, arguments.size)
    ascent, descent = font.getmetrics()
    cell_height = ascent + descent
    cell_width = max(font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in glyphs)

    sheet_width = len(glyphs) * (cell_width + 1) + 1
    sheet = Image.new("RGBA", (sheet_width, cell_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    draw.line([(0, 0), (0, cell_height)], fill=(255, 0, 255, 255), width=1)

    x = 1
    for ch in glyphs:
        bbox = font.getbbox(ch)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        offset_x = (cell_width - w) // 2 - bbox[0]
        offset_y = (cell_height - h) // 2 - bbox[1]

        glyph_img = Image.new("1", (cell_width, cell_height), 0)
        glyph_draw = ImageDraw.Draw(glyph_img)
        glyph_draw.text((offset_x, offset_y), ch, font=font, fill=1)

        mask = glyph_img.convert("L")
        rgba_glyph = Image.new("RGBA", (cell_width, cell_height), (255,255,255,0))
        rgba_glyph.putalpha(mask)
        sheet.alpha_composite(rgba_glyph, dest=(x, 0))

        x += cell_width
        draw.line([(x, 0), (x, cell_height)], fill=(255, 0, 255, 255), width=1)
        x += 1

    name = re.sub(r"[^a-z0-9]", "", os.path.splitext(os.path.basename(arguments.font).lower())[0])
    blob_dir = os.path.join(arguments.directory, "blobs")
    font_dir = os.path.join(arguments.directory, "fonts")

    os.makedirs(blob_dir, exist_ok=True)
    os.makedirs(font_dir, exist_ok=True)

    image_path = os.path.join(blob_dir, f"{name}.png")
    json_path = os.path.join(font_dir, f"{name}.json")

    sheet.save(image_path)

    with open(json_path, "w") as f:
        json.dump(
            {
                "glyphs": "".join(glyphs),
                "spritesheet": f"blobs/{name}.png",
                "spacing": 0,
                "leading": 0,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

if __name__ == "__main__":
    main()
