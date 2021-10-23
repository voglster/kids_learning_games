from math import cos, radians, sin
from random import randint

import pygame

FPS = 30
gravity = (0, 0.3)


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
        if x < 0 or y < 0:
            return False
        if x > self.rect.right or y > self.rect.bottom:
            return False
        return True


class Particle:
    def __init__(self, position, angle, speed, decay=5, color=None):
        self.position = position
        self.original_color = color or (255, 255, 255)
        self.age = 0
        angle = radians(angle)
        self.vector = (cos(angle) * speed, sin(angle) * speed)
        self.decay = decay
        self.size = randint(1, 7)

    @property
    def draw_position(self):
        return tuple(int(x) for x in self.position)

    @property
    def color(self):
        return tuple(max(0, self.original_color[i] - self.age) for i in range(3))

    def update(self):
        self.vector = tuple(sum(x) for x in zip(self.vector, gravity))
        self.position = (
            self.position[0] + self.vector[0],
            self.position[1] + self.vector[1],
        )
        self.age += self.decay

    @property
    def dead(self):
        return self.color == (0, 0, 0)


class Player:
    def __init__(self):
        self.score = 0


class HudView:
    def __init__(self, player: Player, surface, font):
        self.hud = player
        self.surface = surface
        self.font = font

    def draw(self):
        pass


class World:
    def __init__(self, size, balloon_rect):
        self.size = size
        self.points = []
        self.balloons = []
        self.balloon_rect = balloon_rect

    def spawn(self, position):
        color = tuple(randint(100, 255) for _ in range(3))
        count = randint(5, 50)
        rounds = randint(1, 5)
        initial = randint(0, 360)
        for i in range(count):
            angle = initial + ((360 / count * rounds) * i)
            self.points.append(
                Particle(position, angle, randint(2, 12), randint(2, 7), color=color)
            )

    def spawn_balloon(self):
        self.balloons.append(
            Balloon(
                (
                    randint(0, self.size.right - self.balloon_rect.right),
                    self.size.bottom,
                ),
                randint(-30, 30),
                randint(0, 4),
                self.balloon_rect,
                self,
                kind=randint(0, 2),
            )
        )

    def update(self):
        for balloon in tuple(self.balloons):
            balloon.update()
            if balloon.position[1] + self.balloon_rect.bottom < 0:
                self.balloons.remove(balloon)
        for point in tuple(self.points):
            point.update()
            if point.dead:
                self.points.remove(point)


class App:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 150)
        for j in [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]:
            j.init()

        pygame.font.init()
        pygame.event.set_grab(True)
        self.font = pygame.font.SysFont("Comic Sans MS", 30)
        self._running = True
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Simulation")
        self.balloons = [
            pygame.image.load(f"./assets/images/balloon{i}.png").convert_alpha()
            for i in range(3)
        ]
        self.balloon_box = self.balloons[0].get_rect()

        self.pops = [
            pygame.mixer.Sound(f"assets/sounds/pop{x}.ogg") for x in range(1, 4)
        ]
        self.clock = pygame.time.Clock()
        self.world = World(pygame.display.get_surface().get_rect(), self.balloon_box)
        self.shooting = False

        # self.ease = QuadEaseInOut(start=0, end=300, duration=2 * FPS)
        self.time = 0

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                self._running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            spot = event.pos
            for balloon in reversed(self.world.balloons):
                if balloon.contains(spot):
                    self.world.balloons.remove(balloon)
                    self.world.spawn(spot)
                    self.world.spawn(spot)
                    self.world.spawn(spot)
                    self.world.spawn(spot)
                    self.world.spawn(spot)
                    self.world.spawn(spot)
                    self.pops[randint(0, 2)].play()
                    break

    def on_render(self):
        self.display.fill([1, 1, 1])
        self.time += 1
        for balloon in self.world.balloons:
            balloon: Balloon
            self.display.blit(self.balloons[balloon.kind], balloon.position)

        for point in self.world.points:
            pygame.draw.circle(
                self.display, point.color, point.draw_position, point.size
            )

        if self.shooting:
            pos = pygame.mouse.get_pos()
            self.world.spawn(pos)

        if len(self.world.balloons) < 10:
            self.world.spawn_balloon()

        pygame.display.flip()
        self.clock.tick(FPS)
        self.world.update()

    def on_execute(self):
        while self._running:
            pygame.event.pump()
            for event in pygame.event.get():
                self.on_event(event)
            x, y = pygame.mouse.get_pos()
            r = pygame.display.get_surface().get_rect()
            if not r.collidepoint(x, y):
                if x < 0:
                    x = 0
                if x > r.right:
                    x = r.right
                if y < 0:
                    y = 0
                if y > r.bottom:
                    y = r.bottom
                pygame.mouse.set_pos(x, y)
            self.on_render()
        pygame.quit()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
