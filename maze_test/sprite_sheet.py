import json

import pygame


def load_image_from_sheet(location, base_sheet, size=32):
    x = location["x"]
    y = location["y"]
    rect = pygame.Rect((x, y, size, size))
    image = pygame.Surface(rect.size).convert_alpha()
    image.blit(base_sheet, (0, 0), rect)
    return image


class SpriteSheet:
    def __init__(self, filename="spritesheet"):
        """Load the sheet."""
        try:
            sheet = pygame.image.load(f"./assets/images/{filename}.png").convert_alpha()
            with open(f"./assets/images/{filename}.json") as f:
                data = json.load(f)
            self.images = {
                name: load_image_from_sheet(location, sheet)
                for name, location in data["images"].items()
            }

            self.sprites = {
                name: [self.load_image(name) for name in image_names]
                for name, image_names in data["sprites"].items()
            }

        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def load_image(self, name):
        return self.images[name]

    def load_sprite(self, name):
        return self.sprites[name]
