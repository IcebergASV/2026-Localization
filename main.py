from __future__ import annotations

import math
import pygame

from typing import Sequence, Tuple
from pygame import Color
from Localization.static_map import StaticMap, create_static_map, map_dynamic_to_static

Pose2D = tuple[float, float, float]

SCREEN_WIDTH = 1020
SCREEN_HEIGHT = 760
WORLD_ORIGIN = (30, 30)
WORLD_CELL_SIZE = 20
LOCAL_ORIGIN = (720, 120)
LOCAL_CELL_SIZE = 28
RECORD_ORIGIN = (30, 430)
RECORD_CELL_SIZE = 22

WORLD_WIDTH = 31
WORLD_HEIGHT = 21
WORLD_RESOLUTION = 1.0
LOCAL_SIZE = 11
LOCAL_RESOLUTION = 1.0
RECORD_WIDTH = 21
RECORD_HEIGHT = 15
RECORD_RESOLUTION = 1.0

WORLD_LAYOUT = [
    "...............................",
    "...####.................####...",
    "...#..#..................#..#..",
    "...#..#............##....#..#..",
    "...#..#............##....#..#..",
    "...####..................####..",
    "...............................",
    "....#######.........#######....",
    "....#.....#.........#.....#....",
    "....#..#..#..###..#..#..#..#....",
    "....#.....#..#.#...#.....#..#...",
    "....#######..###....#######....",
    "...............................",
    "..#####...............#####....",
    "..#...#...............#...#....",
    "..#...#.......###.....#...#....",
    "..#...#.......###.....#...#....",
    "..#####.......###.....#####....",
    "...............................",
    "...............................",
    "...............................",
]

VEHICLE_COLOR = Color("red")
WORLD_OCCUPIED = Color("#2f3d53")
WORLD_FREE = Color("#e8f1ff")
LOCAL_OCCUPIED = Color("#ff8c00")
LOCAL_FREE = Color("#ffffff")
RECORD_UNKNOWN = Color("#999999")
RECORD_OCCUPIED = Color("#2f3d53")
RECORD_FREE = Color("#ddeeff")
GRID_COLOR = Color("#bbbbbb")
TEXT_COLOR = Color("#222222")


def create_world_map() -> StaticMap:
    world_map = create_static_map(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        resolution=WORLD_RESOLUTION,
        fill_value=0.0,
        dtype=float,
    )
    for row, line in enumerate(WORLD_LAYOUT):
        for col, char in enumerate(line):
            if char == "#":
                world_map.data[row, col] = 1.0
    return world_map


def extract_dynamic_from_world(
    world_map: StaticMap,
    vehicle_pose: Pose2D,
    local_size: int,
    local_resolution: float,
) -> list[list[float]]:
    dynamic = [[0.0 for _ in range(local_size)] for _ in range(local_size)]
    center_row = (local_size - 1) / 2.0
    center_col = (local_size - 1) / 2.0
    vehicle_x, vehicle_y, heading = vehicle_pose
    cos_h = math.cos(heading)
    sin_h = math.sin(heading)

    for r in range(local_size):
        for c in range(local_size):
            local_x = (c - center_col) * local_resolution
            local_y = (center_row - r) * local_resolution
            world_x = cos_h * local_x - sin_h * local_y + vehicle_x
            world_y = sin_h * local_x + cos_h * local_y + vehicle_y
            world_row, world_col = world_map.world_to_indices(world_x, world_y)
            if world_map.inside(world_row, world_col):
                dynamic[r][c] = float(world_map.data[world_row, world_col])
    return dynamic


def draw_map_grid(
    screen: pygame.Surface,
    origin: tuple[int, int],
    grid: Sequence[Sequence[float]],
    cell_size: int,
    occupied_color: Color,
    free_color: Color,
    unknown_color: Color | None = None,
) -> None:
    ox, oy = origin
    height = len(grid)
    width = len(grid[0])
    for row in range(height):
        for col in range(width):
            value = grid[row][col]
            if unknown_color is not None and value == 0.5:
                color = unknown_color
            else:
                color = occupied_color if value else free_color
            rect = pygame.Rect(ox + col * cell_size, oy + row * cell_size, cell_size, cell_size)
            screen.fill(color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_world_map(screen: pygame.Surface, world_map: StaticMap, vehicle_pose: Pose2D) -> None:
    draw_map_grid(screen, WORLD_ORIGIN, world_map.data, WORLD_CELL_SIZE, WORLD_OCCUPIED, WORLD_FREE)
    vehicle_x, vehicle_y, heading = vehicle_pose
    vehicle_row, vehicle_col = world_map.world_to_indices(vehicle_x, vehicle_y)
    if world_map.inside(vehicle_row, vehicle_col):
        center_x = WORLD_ORIGIN[0] + vehicle_col * WORLD_CELL_SIZE + WORLD_CELL_SIZE / 2
        center_y = WORLD_ORIGIN[1] + vehicle_row * WORLD_CELL_SIZE + WORLD_CELL_SIZE / 2
        pygame.draw.circle(screen, VEHICLE_COLOR, (int(center_x), int(center_y)), 8)
        arrow_len = WORLD_CELL_SIZE * 2
        end_x = center_x + math.cos(heading) * arrow_len
        end_y = center_y - math.sin(heading) * arrow_len
        pygame.draw.line(screen, VEHICLE_COLOR, (center_x, center_y), (end_x, end_y), 3)
    label = pygame.font.SysFont(None, 24).render("World Map (Truth)", True, TEXT_COLOR)
    screen.blit(label, (WORLD_ORIGIN[0], WORLD_ORIGIN[1] - 26))


def draw_dynamic_map(screen: pygame.Surface, dynamic_map: Sequence[Sequence[float]]) -> None:
    draw_map_grid(screen, LOCAL_ORIGIN, dynamic_map, LOCAL_CELL_SIZE, LOCAL_OCCUPIED, LOCAL_FREE)
    center = LOCAL_ORIGIN[0] + (LOCAL_SIZE - 1) / 2 * LOCAL_CELL_SIZE, LOCAL_ORIGIN[1] + (LOCAL_SIZE - 1) / 2 * LOCAL_CELL_SIZE
    pygame.draw.circle(screen, VEHICLE_COLOR, (int(center[0]), int(center[1])), 10)
    pygame.draw.circle(screen, Color("black"), (int(center[0]), int(center[1])), 4)
    label = pygame.font.SysFont(None, 24).render("Dynamic Local View", True, TEXT_COLOR)
    screen.blit(label, (LOCAL_ORIGIN[0], LOCAL_ORIGIN[1] - 26))


def draw_recorded_map(screen: pygame.Surface, recorded_map: StaticMap) -> None:
    draw_map_grid(screen, RECORD_ORIGIN, recorded_map.data, RECORD_CELL_SIZE, RECORD_OCCUPIED, RECORD_FREE, RECORD_UNKNOWN)
    label = pygame.font.SysFont(None, 24).render("Recorded Static Map", True, TEXT_COLOR)
    screen.blit(label, (RECORD_ORIGIN[0], RECORD_ORIGIN[1] - 26))


def draw_info(screen: pygame.Surface, vehicle_pose: Pose2D) -> None:
    font = pygame.font.SysFont(None, 22)
    vehicle_x, vehicle_y, heading = vehicle_pose
    lines = [
        f"Vehicle pose: x={vehicle_x:.1f}, y={vehicle_y:.1f}, heading={heading:.2f} rad",
        "Arrow keys: move vehicle",
        "Q/E: rotate left/right",
        "R: reset position",
        "Space: clear recorded map",
    ]
    for index, line in enumerate(lines):
        text = font.render(line, True, TEXT_COLOR)
        screen.blit(text, (720, 30 + index * 24))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Static Map Observation Recorder")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    world_map = create_world_map()
    recorded_map = create_static_map(
        width=RECORD_WIDTH,
        height=RECORD_HEIGHT,
        resolution=RECORD_RESOLUTION,
        fill_value=0.5,
        dtype=float,
    )

    vehicle_pose: Pose2D = (0.0, 0.0, 0.0)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                x, y, heading = vehicle_pose
                if event.key == pygame.K_LEFT:
                    x -= 0.5
                elif event.key == pygame.K_RIGHT:
                    x += 0.5
                elif event.key == pygame.K_UP:
                    y += 0.5
                elif event.key == pygame.K_DOWN:
                    y -= 0.5
                elif event.key == pygame.K_q:
                    heading += 0.2
                elif event.key == pygame.K_e:
                    heading -= 0.2
                elif event.key == pygame.K_r:
                    x, y, heading = 0.0, 0.0, 0.0
                elif event.key == pygame.K_SPACE:
                    recorded_map.reset()
                vehicle_pose = (x, y, heading)

        dynamic_map = extract_dynamic_from_world(world_map, vehicle_pose, LOCAL_SIZE, LOCAL_RESOLUTION)
        recorded_map.reset()
        map_dynamic_to_static(recorded_map, dynamic_map, vehicle_pose, dynamic_resolution=LOCAL_RESOLUTION)

        screen.fill(Color("#f0f4ff"))
        draw_world_map(screen, world_map, vehicle_pose)
        draw_dynamic_map(screen, dynamic_map)
        draw_recorded_map(screen, recorded_map)
        draw_info(screen, vehicle_pose)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
