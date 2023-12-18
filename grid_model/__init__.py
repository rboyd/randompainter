from enum import Enum
from collections import Counter

class StoppingCondition(Enum):
    ALL_FILLED = 1
    SECOND_DROP = 2

class GridModel:
    def __init__(self, width, height, stopping_condition):
        self.width = width
        self.height = height
        self.stopping_condition = stopping_condition
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.cells_painted = 0
        self.total_cells = width * height
        self.total_drops = 0
        self.drops_by_color = Counter()
        self.max_drops_on_square = 0

    def paint(self, x, y, color):
        self.total_drops += 1
        self.drops_by_color[color] += 1
        self.grid[y][x] += 1

        if self.grid[y][x] > self.max_drops_on_square:
            self.max_drops_on_square = self.grid[y][x]

        if self.grid[y][x] == 1:
            self.cells_painted += 1

        if self.stopping_condition == StoppingCondition.ALL_FILLED and self.cells_painted == self.total_cells:
            return self._get_statistics()
        elif self.stopping_condition == StoppingCondition.SECOND_DROP and self.grid[y][x] == 2:
            return self._get_statistics()
        return None

    def _get_statistics(self):
        total_drops = sum(sum(row) for row in self.grid)
        average_drops = total_drops / self.total_cells
        return {
            'x': self.width,
            'y': self.height,
            'total_drops': self.total_drops,
            'drops_by_color': dict(self.drops_by_color),
            'max_drops_on_square': self.max_drops_on_square,
            'average_drops': average_drops
        }