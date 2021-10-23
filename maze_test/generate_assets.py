import json
import os
from collections import defaultdict
from math import ceil, floor
from pathlib import Path

from PIL import Image


def images():
    for dirpath, dnames, fnames in os.walk("./raw_assets"):
        for f in fnames:
            if f.endswith(".png"):
                yield Path(f"{dirpath}/{f}").absolute()


tile_size = 32
tiles_per_row = 4

images_per_sheet = tiles_per_row ** 2


def frames_by_sheet_number(frames):
    for index, frame in frames:
        pass


frames = []

for path in images():
    with Image.open(path) as im:
        frames.append((im.getdata(), path.stem))

sprite_sheet_width = tile_size * tiles_per_row
sprite_sheet_height = tile_size * ceil(len(frames) / tiles_per_row)

sprite_sheet = Image.new("RGBA", (sprite_sheet_width, sprite_sheet_height))

lkp = {}
for index, (current_frame, name) in enumerate(frames):
    top = tile_size * floor(index / tiles_per_row)
    left = tile_size * (index % tiles_per_row)
    bottom = top + tile_size
    right = left + tile_size

    box = (left, top, right, bottom)

    cut_frame = current_frame.crop((0, 0, tile_size, tile_size))
    sprite_sheet.paste(cut_frame, box)
    lkp[name] = {"x": box[0], "y": box[1]}


sprite_sheet.save(f"assets/images/spritesheet.png", "PNG")

sprites = defaultdict(list)

for key in lkp.keys():
    if "-" in key:
        sprite_name, _ = key.split("-")
        sprites[sprite_name].append(key)

sprites = dict(sprites)

for k, v in list(sprites.items()):
    sprites[k] = sorted(v, key=lambda y: int(y.split("-")[1]))

with open("assets/images/spritesheet.json", "w") as f:
    json.dump({"images": lkp, "sprites": sprites}, f, indent=4)
