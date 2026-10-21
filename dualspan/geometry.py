"""Pure monitor geometry operations, independent of OS/display server."""
from dataclasses import dataclass
from typing import Sequence, Tuple

@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Rectangle dimensions must be positive")
    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)
    def intersection_area(self, other: "Rect") -> int:
        w = max(0, min(self.x + self.width, other.x + other.width) - max(self.x, other.x))
        h = max(0, min(self.y + self.height, other.y + other.height) - max(self.y, other.y))
        return w * h
    def to_dict(self):
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

@dataclass(frozen=True)
class Monitor:
    name: str
    rect: Rect

@dataclass(frozen=True)
class Window:
    id: str
    title: str
    rect: Rect

def union(a: Rect, b: Rect) -> Rect:
    x, y = min(a.x, b.x), min(a.y, b.y)
    return Rect(x, y, max(a.x + a.width, b.x + b.width) - x, max(a.y + a.height, b.y + b.height) - y)

def select_pair(monitors: Sequence[Monitor], window: Rect) -> Tuple[int, int]:
    if len(monitors) < 2:
        raise ValueError("Two connected and enabled monitors are required")
    a = max(range(len(monitors)), key=lambda i: (window.intersection_area(monitors[i].rect), -distance_sq(window.center, monitors[i].rect.center)))
    b = min((i for i in range(len(monitors)) if i != a), key=lambda i: (distance_sq(monitors[a].rect.center, monitors[i].rect.center), i))
    return a, b

def distance_sq(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

def selection(monitors: Sequence[Monitor], window: Rect, indices=None) -> Tuple[Monitor, Monitor]:
    if indices is None:
        i, j = select_pair(monitors, window)
    else:
        i, j = indices
        if i == j or min(i, j) < 0 or max(i, j) >= len(monitors):
            raise ValueError("Select two different, listed monitor numbers")
    return monitors[i], monitors[j]
