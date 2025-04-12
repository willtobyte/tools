import argparse
import json
import os

import freetype
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--font",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        required=True,
    )
    arguments = parser.parse_args()

    face = freetype.Face(arguments.font)
    face.set_char_size(arguments.size * 64)
    glyphs = [chr(cp) for cp in range(32, 128) if face.get_char_index(cp)]

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
        draw.text((x + offset_x, offset_y), ch, font=font, fill=(255, 255, 255, 255))
        x += cell_width
        draw.line([(x, 0), (x, cell_height)], fill=(255, 0, 255, 255), width=1)
        x += 1

    name = os.path.splitext(os.path.basename(arguments.font))[0]
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
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
