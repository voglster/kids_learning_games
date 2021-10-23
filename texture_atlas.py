import json
from collections import defaultdict
from pathlib import Path

import pygame


def atlas_region_to_rect(region: dict):
    x = region["x"]
    y = region["y"]
    width = region["width"]
    height = region["height"]
    return pygame.Rect((x, y, width, height))


def load_image_from_surface(location, surface):
    rect = atlas_region_to_rect(location)
    image = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
    image.blit(surface, (0, 0), rect)
    return image


def parse_name_from_filepath(param):
    return Path(param).stem


def build_images(surface, regions):
    return {name: load_image_from_surface(region, surface) for name, region in regions}


def build_sprite_dict(image_names):
    sprites = defaultdict(list)
    for image_name in image_names:
        if "-" in image_name:
            sprite_name, number = image_name.split("-")
            sprites[sprite_name].append(image_name)
    for group in sprites.values():
        group.sort()
    return dict(sprites)


def parse_regions(atlas_json):
    for region in atlas_json["regions"].values():
        name = parse_name_from_filepath(region["filepath"])
        yield name, region


class TextureAtlas:
    def __init__(self, name="atlas"):
        self.name = name
        sheet = pygame.image.load(self._image_path).convert_alpha()
        self.images = build_images(sheet, parse_regions(self._load_json()))
        self.sprites = build_sprite_dict(self.images.keys())

    @property
    def _image_path(self):
        return f"./assets/{self.name}.png"

    @property
    def _json_path(self):
        return f"./assets/{self.name}.json"

    def _load_json(self):
        with open(self._json_path) as f:
            return json.load(f)

    def image(self, name):
        return self.images[name]

    def sprite(self, name):
        return self.sprites[name]
