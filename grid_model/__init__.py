from enum import Enum

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

    def paint(self, x, y):
        if self.grid[y][x] == 0:
            self.cells_painted += 1
        self.grid[y][x] += 1

        if self.stopping_condition == StoppingCondition.ALL_FILLED and self.cells_painted == self.total_cells:
            return StoppingCondition.ALL_FILLED
        elif self.stopping_condition == StoppingCondition.SECOND_DROP and self.grid[y][x] == 2:
            return StoppingCondition.SECOND_DROP
        return None