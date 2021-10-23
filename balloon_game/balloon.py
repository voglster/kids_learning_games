from math import cos, radians, sin
from random import randint


class Balloon:
    def __init__(self, position, angle, speed, rect, world, kind=0):
        self.position = position
        angle = radians(angle)
        self.vector = (cos(angle) * speed, sin(angle) * speed)
        self.kind = kind
        self.float = (0, -0.01 * randint(1, 5))
        self.rect = rect
        self.world = world

    def update(self):
        self.vector = tuple(sum(x) for x in zip(self.vector, self.float))
        self.position = tuple(sum(x) for x in zip(self.position, self.vector))
        if self.position[0] < 0 and self.vector[0] < 0:
            self.vector = self.vector[0] * -1, self.vector[1]

        if (
            self.position[0] + self.rect.right > self.world.size.right
            and self.vector[0] > 0
        ):
            self.vector = self.vector[0] * -1, self.vector[1]

    def contains(self, spot):
        x, y = spot
        x = x - self.position[0]
        y = y - self.position[1]
        x_in_bounds = 0 <= x <= self.rect.right
        y_in_bounds = 0 <= y <= self.rect.bottom
        return x_in_bounds and y_in_bounds
