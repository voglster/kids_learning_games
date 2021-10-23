from itertools import combinations
from random import choice, sample

import pygame
from pygame.locals import *

from maze_test.maze_generation import (expand, filter_to_only_in_maze, make,
                                       neighbor_cells)
from maze_test.sprite_sheet import SpriteSheet


class Player:
    def __init__(self, position=(1, 1)):
        self.x, self.y = position
        self.history = []

    def move_right(self):
        self.history.append(self.position)
        self.x += 1

    def move_left(self):
        self.history.append(self.position)
        self.x -= 1

    def move_up(self):
        self.history.append(self.position)
        self.y -= 1

    def move_down(self):
        self.history.append(self.position)
        self.y += 1

    def backup(self):
        if self.history:
            self.x, self.y = self.history.pop()

    def reset(self, position=(1, 1)):
        self.__init__(position)

    @property
    def position(self):
        return self.x, self.y


class Goal:
    def __init__(self, position=(1, 1)):
        self.x, self.y = position

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, value):
        self.x, self.y = value


def calc_distance_sq(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = x1 - x2
    dy = y1 - y2
    return dx ** 2 + dy ** 2


class Maze:
    def __init__(self, x_size=10, y_size=10):
        removed_walls = make(x_size, y_size)
        self.maze = expand(x_size, y_size, removed_walls)
        points = []
        for y, row in enumerate(self.maze):
            for x, value in enumerate(row):
                if self.on_wall((x, y)):
                    continue
                all_neighbors = neighbor_cells((x, y))
                only_in_maze = filter_to_only_in_maze(
                    all_neighbors, x_size * 2 + 1, y_size * 2 + 1
                )
                if sum(1 for cell in only_in_maze if not self.on_wall(cell)) == 1:
                    points.append((x, y))
        _, self.start, end = choice(
            sorted(
                (
                    (calc_distance_sq(start, end), start, end)
                    for start, end in combinations(points, 2)
                ),
                key=lambda x: x[0],
                reverse=True,
            )[:3]
        )
        points.remove(self.start)
        points.remove(end)
        self.goals = [end]
        if len(points) >= 2:
            self.goals.extend(sample(points, 2))

    def on_wall(self, cell):
        x, y = cell
        return bool(self.maze[y][x])


class ReversingSprite(pygame.sprite.Sprite):
    def __init__(self, images):
        super(ReversingSprite, self).__init__()
        self.counter = 0
        # adding all the images to sprite array
        self.images = images
        self.reverse = False

        # index value to get the image from the array
        # initially it is 0
        self.index = 0

        # now the image that we will display will be the index from the image array
        self.image = self.images[self.index]

    def update(self):
        if self.counter < 2:
            self.counter += 1
            return
        self.counter = 0
        # when the update method is called, we will increment the index
        if not self.reverse:
            self.index += 1
        else:
            self.index -= 1

        # if the index is larger than the total images
        if self.index >= len(self.images):
            self.reverse = True
            self.index = len(self.images) - 2

        if self.index < 0:
            self.reverse = False
            self.index = 0

        # finally we will update the image that will be displayed
        self.image = self.images[self.index]


class App:
    def __init__(self):
        self.size = 20

        self.windowWidth = 32 * (self.size * 2 + 1)
        self.windowHeight = 32 * (self.size * 2 + 1)

        self.maze = Maze(self.size, self.size)
        self.player = Player(self.maze.start)
        self.goals = [Goal(x) for x in self.maze.goals]
        pygame.init()
        pygame.key.set_repeat(200, 150)
        for j in [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]:
            j.init()

        self.display = pygame.display.set_mode(
            (self.windowWidth, self.windowHeight), pygame.RESIZABLE
        )
        pygame.display.set_caption("Maze Game")
        self.fake_screen = self.display.copy()
        self.display = pygame.display.set_mode((1000, 1000), pygame.RESIZABLE)
        self._running = True
        ss = SpriteSheet()
        self.coin_sprite = ReversingSprite(ss.load_sprite("coin"))

        self.block_surf = ss.load_image("block")
        self.block_size = self.block_surf.get_size()
        self.player_surf = ss.load_image("player")
        self.goal_surf = ss.load_image("coin-01")
        self.dot_surf = ss.load_image("dot")
        self.complete = pygame.mixer.Sound("sounds/ding.ogg")
        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_UP:
                self.player.move_up()
            if event.key == K_RIGHT:
                self.player.move_right()
            if event.key == K_DOWN:
                self.player.move_down()
            if event.key == K_LEFT:
                self.player.move_left()
            if event.key == K_BACKSPACE:
                self.player.backup()
            if event.key == K_RETURN:
                self.maze = Maze(self.size, self.size)
                self.goals = [Goal(x) for x in self.maze.goals]
                self.player.reset(self.maze.start)
            if event.key in [K_ESCAPE, K_q]:
                pygame.quit()

        elif event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if (x and not y) or (not x and y):
                if x < 0:
                    self.player.move_left()
                elif x > 0:
                    self.player.move_right()
                elif y > 0:
                    self.player.move_up()
                elif y < 0:
                    self.player.move_down()

        if self.maze.on_wall(self.player.position):
            self.player.backup()
        for goal in list(self.goals):
            if self.player.position == goal.position:
                self.complete.play()
                self.goals.remove(goal)
            if not self.goals:
                self.maze = Maze(self.size, self.size)
                self.goals = [Goal(x) for x in self.maze.goals]
                self.player.reset(self.maze.start)

    def draw_player(self):
        for position in self.player.history[-10:]:
            x, y = position
            self.fake_screen.blit(
                self.dot_surf,
                (x * self.block_size[0], y * self.block_size[1]),
            )

        self.fake_screen.blit(
            self.player_surf,
            (self.player.x * self.block_size[0], self.player.y * self.block_size[1]),
        )

    def draw_goals(self):
        for goal in self.goals:
            self.fake_screen.blit(
                self.coin_sprite.image,
                (goal.x * self.block_size[0], goal.y * self.block_size[1]),
            )

    def draw_maze(self):
        x_scale, y_scale = self.block_size
        for y_index, row in enumerate(self.maze.maze):
            for x_index, value in enumerate(row):
                if value:
                    self.fake_screen.blit(
                        self.block_surf, (x_index * x_scale, y_index * y_scale)
                    )

    def on_render(self):
        self.fake_screen.fill((1, 1, 1))
        self.draw_maze()
        self.draw_goals()
        self.draw_player()
        self.display.blit(
            pygame.transform.scale(self.fake_screen, self.display.get_rect().size),
            (0, 0),
        )
        pygame.display.flip()
        self.coin_sprite.update()
        self.clock.tick(30)

    def on_execute(self):
        while self._running:
            pygame.event.pump()
            for event in pygame.event.get():
                self.on_event(event)
            self.on_render()
        pygame.quit()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
