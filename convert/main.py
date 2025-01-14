import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Transform spritesheet JSON.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file.")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file.")
    args = parser.parse_args()

    with open(args.input) as f:
        source = json.load(f)

    out = {
        "spritesheet": f"blobs/{source['meta']['image']}",
        "scale": int(source["meta"]["scale"]),
        "size": {
            "width": source["meta"]["size"]["w"],
            "height": source["meta"]["size"]["h"],
        },
        "animations": {},
    }

    for n, d in source["frames"].items():
        animation = n.split(" ")[0]
        rect = {
            "x": d["frame"]["x"],
            "y": d["frame"]["y"],
            "width": d["frame"]["w"],
            "height": d["frame"]["h"],
        }
        offset = {
            "x": d["spriteSourceSize"]["x"],
            "y": d["spriteSourceSize"]["y"],
        }
        frame = {"duration": 200, "offset": offset, "rect": rect}
        out["animations"].setdefault(animation, {"frames": []})["frames"].append(frame)

    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
