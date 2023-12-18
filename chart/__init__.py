import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import flet
from flet import Page
from flet.matplotlib_chart import MatplotlibChart

matplotlib.use("svg")

class ScatterChart(flet.UserControl):
    def __init__(self, data=None, x_var='X', y_vars=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.x_var = x_var
        self.y_vars = y_vars or []
        self.fig, self.ax = plt.subplots()

    def build(self):
        if not self.data or not self.x_var or not self.y_vars:
            return flet.Text("No data or variables selected.")

        x = [item[self.x_var] for item in self.data]
        
        for y_var in self.y_vars:
            y = [item[y_var] for item in self.data]
            self.ax.scatter(x, y, label=y_var)

        self.ax.set_xlabel(self.x_var)
        self.ax.set_ylabel("Values")
        self.ax.set_title(f"{self.x_var} vs {', '.join(self.y_vars)}")
        self.ax.legend()

        # Add the MatplotlibChart to the UserControl
        return MatplotlibChart(self.fig, expand=True)