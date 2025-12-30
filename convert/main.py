import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Transform spritesheet JSON.")
    parser.add_argument("-s", "--source", required=True, help="Source JSON file.")
    parser.add_argument(
        "-d", "--destination", required=True, help="Destination JSON file."
    )
    args = parser.parse_args()

    with open(args.source) as f:
        source = json.load(f)

    result = {
        "animations": {},
    }

    for n, d in source["frames"].items():
        animation = n.split(" ")[0]

        quad = {
            "x": d["frame"]["x"],
            "y": d["frame"]["y"],
            "w": d["frame"]["w"],
            "h": d["frame"]["h"],
        }

        offset = {
            "x": d["spriteSourceSize"]["x"],
            "y": d["spriteSourceSize"]["y"],
        }

        frame = {"duration": 200, "offset": offset, "quad": quad}
        result["animations"].setdefault(animation, {"frames": []})["frames"].append(
            frame
        )

    with open(args.destination, "w") as f:
        json.dump(result, f, indent=2)

    path = args.destination.rsplit(".", 1)[0] + ".lua"
    with open(path, "w") as f:
        f.write("return {\n}\n")


if __name__ == "__main__":
    main()
