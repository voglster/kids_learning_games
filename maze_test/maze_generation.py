from random import choice
from typing import Set, Tuple


def in_range(value, max, min_value=0):
    return min_value <= value < max


def is_in_maze(cell, x_size, y_size):
    x, y = cell
    return in_range(x, x_size) and in_range(y, y_size)


def neighbor_cells(cell):
    x, y = cell
    north_cell = x, y + 1
    east_cell = x + 1, y
    south_cell = x, y - 1
    west_cell = x - 1, y
    return north_cell, east_cell, south_cell, west_cell


def filter_to_only_in_maze(cells, x_size, y_size):
    return [cell for cell in cells if is_in_maze(cell, x_size, y_size)]


def filter_to_not_visited(cells, visited: Set[Tuple[int, int]]):
    return [cell for cell in cells if cell not in visited]


def get_neighbors_in_maze(start, x_size, y_size):
    cells = neighbor_cells(start)
    return filter_to_only_in_maze(cells, x_size, y_size)


def make(x_size=10, y_size=10, start=(0, 1)):
    visited_cells = set()
    visited_cells.add(start)
    stack = [start]
    removed_walls = []
    while stack:
        current_cell = stack.pop()
        all_neighbors = neighbor_cells(current_cell)
        only_in_maze = filter_to_only_in_maze(all_neighbors, x_size, y_size)
        only_not_visited = filter_to_not_visited(only_in_maze, visited_cells)
        if only_not_visited:
            stack.append(current_cell)
            next_cell = choice(only_not_visited)
            removed_walls.append((current_cell, next_cell))
            visited_cells.add(next_cell)
            stack.append(next_cell)
    return removed_walls


def filled_array(x, y, value=1):
    ret = []
    for y_i in range(y):
        ret.append([value] * x)
    return ret


def expand(x_size, y_size, removed_walls):
    maze = filled_array(x_size * 2 + 1, y_size * 2 + 1)
    for removed_wall in removed_walls:
        (o_x, o_y), (d_x, d_y) = removed_wall
        maze[1 + o_x * 2][1 + o_y * 2] = 0
        maze[1 + d_x * 2][1 + d_y * 2] = 0
        x, y = o_x + d_x, o_y + d_y
        maze[1 + x][1 + y] = 0
    return maze
