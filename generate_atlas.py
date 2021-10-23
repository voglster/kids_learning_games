from pathlib import Path

from image_packer import packer

input_filepaths = [f"./raw_assets/*.{x}" for x in "png jpg bmp".split()]
output_filepath = Path(f"./assets/atlas.png")
container_width = 1024

options = {
    "margin": (1, 1, 1, 1),
    "collapse_margin": False,
    "enable_auto_size": True,
    "enable_vertical_flip": True,
    "force_pow2": False,
}

packer.pack(
    input_filepaths=input_filepaths,
    output_filepath=output_filepath,
    container_width=container_width,
    options=options,
)
