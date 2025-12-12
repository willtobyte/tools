#!/usr/bin/env python3
"""
Convert Tiled Map JSON (.tmj) to Carimbo tilemap format.

Usage:
    python tmj2carimbo.py input.tmj output.json
    python tmj2carimbo.py input.tmj  # outputs to stdout
"""

import json
import sys
from pathlib import Path


def convert_tmj_to_carimbo(tmj_data: dict) -> dict:
    """Convert TMJ format to Carimbo tilemap format."""

    tile_width = tmj_data.get("tilewidth", 64)
    tile_height = tmj_data.get("tileheight", 64)

    if tile_width != tile_height:
        print(f"Warning: non-square tiles ({tile_width}x{tile_height}), using width", file=sys.stderr)

    tile_size = tile_width
    map_width = tmj_data["width"]
    map_height = tmj_data["height"]

    # Get firstgid from tilesets (default to 1)
    firstgid = 1
    if tmj_data.get("tilesets"):
        firstgid = tmj_data["tilesets"][0].get("firstgid", 1)

    layers = []

    for layer in tmj_data.get("layers", []):
        if layer.get("type") != "tilelayer":
            continue

        layer_name = layer.get("name", "unnamed")
        layer_data = layer.get("data", [])
        layer_width = layer.get("width", map_width)

        # Check if layer name contains "collider" (case insensitive)
        is_collider = "collider" in layer_name.lower()

        tiles = []
        for index, tile_id in enumerate(layer_data):
            if tile_id == 0:
                continue

            x = index % layer_width
            y = index // layer_width

            # Convert from TMJ tile ID (1-based with firstgid) to 0-based
            converted_id = tile_id - firstgid

            tiles.append({
                "x": x,
                "y": y,
                "id": converted_id
            })

        layers.append({
            "collider": is_collider,
            "name": layer_name,
            "tiles": tiles
        })

    return {
        "tile_size": tile_size,
        "width": map_width,
        "height": map_height,
        "layers": layers
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    with open(input_path, "r", encoding="utf-8") as f:
        tmj_data = json.load(f)

    result = convert_tmj_to_carimbo(tmj_data)
    output_json = json.dumps(result, indent=2)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_json)
            f.write("\n")
        print(f"Converted {input_path} -> {output_path}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
