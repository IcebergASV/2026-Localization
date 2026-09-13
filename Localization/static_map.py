from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as np


Pose2D = tuple[float, float, float]


def _center_indices(shape: tuple[int, int]) -> tuple[float, float]:
    height, width = shape
    return (height - 1) / 2.0, (width - 1) / 2.0


def _to_ndarray(array: Sequence[Sequence[float]]) -> np.ndarray:
    return np.asarray(array, dtype=float)


@dataclass
class StaticMap:
    width: int
    height: int
    resolution: float = 1.0
    fill_value: float = 0.0
    dtype: type = float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive integers")
        if self.resolution <= 0:
            raise ValueError("resolution must be positive")

        self.data = np.full((self.height, self.width), self.fill_value, dtype=self.dtype)
        self.center_row, self.center_col = _center_indices((self.height, self.width))

    def reset(self, fill_value: Optional[float] = None) -> None:
        value = self.fill_value if fill_value is None else fill_value
        self.data.fill(value)

    def indices_to_world(self, row: int, col: int) -> tuple[float, float]:
        x = (col - self.center_col) * self.resolution
        y = (self.center_row - row) * self.resolution
        return x, y

    def world_to_indices(self, x: float, y: float) -> tuple[int, int]:
        col = int(round(x / self.resolution + self.center_col))
        row = int(round(self.center_row - y / self.resolution))
        return row, col

    def inside(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def update_from_dynamic(
        self,
        dynamic_map: Sequence[Sequence[float]],
        vehicle_pose: Pose2D,
        dynamic_resolution: Optional[float] = None,
        merge_fn: Optional[Callable[[float, float], float]] = None,
    ) -> None:
        dynamic = _to_ndarray(dynamic_map)
        if dynamic.ndim != 2:
            raise ValueError("dynamic_map must be a 2D array")

        resolution = self.resolution if dynamic_resolution is None else dynamic_resolution
        if resolution <= 0:
            raise ValueError("dynamic_resolution must be positive")

        dynamic_height, dynamic_width = dynamic.shape
        dynamic_center_row, dynamic_center_col = _center_indices(dynamic.shape)
        vehicle_x, vehicle_y, heading = vehicle_pose

        cos_heading = np.cos(heading)
        sin_heading = np.sin(heading)

        for dynamic_row in range(dynamic_height):
            for dynamic_col in range(dynamic_width):
                local_x = (dynamic_col - dynamic_center_col) * resolution
                local_y = (dynamic_center_row - dynamic_row) * resolution

                world_x = cos_heading * local_x - sin_heading * local_y + vehicle_x
                world_y = sin_heading * local_x + cos_heading * local_y + vehicle_y

                static_row, static_col = self.world_to_indices(world_x, world_y)
                if not self.inside(static_row, static_col):
                    continue

                value = float(dynamic[dynamic_row, dynamic_col])
                if merge_fn is None:
                    self.data[static_row, static_col] = value
                else:
                    self.data[static_row, static_col] = merge_fn(self.data[static_row, static_col], value)

    def visible_region(self) -> tuple[float, float, float, float]:
        half_w = self.width * self.resolution / 2.0
        half_h = self.height * self.resolution / 2.0
        return (-half_w, -half_h, half_w, half_h)


def create_static_map(
    width: int,
    height: int,
    resolution: float = 1.0,
    fill_value: float = 0.0,
    dtype: type = float,
) -> StaticMap:
    return StaticMap(width=width, height=height, resolution=resolution, fill_value=fill_value, dtype=dtype)


def map_dynamic_to_static(
    static_map: StaticMap,
    dynamic_map: Sequence[Sequence[float]],
    vehicle_pose: Pose2D,
    dynamic_resolution: Optional[float] = None,
    merge_fn: Optional[Callable[[float, float], float]] = None,
) -> StaticMap:
    static_map.update_from_dynamic(dynamic_map, vehicle_pose, dynamic_resolution, merge_fn)
    return static_map


__all__ = [
    "Pose2D",
    "StaticMap",
    "create_static_map",
    "map_dynamic_to_static",
]
