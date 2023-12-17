import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import flet
from flet import Page
from flet.matplotlib_chart import MatplotlibChart

matplotlib.use("svg")

class ScatterChart(flet.UserControl):
    def __init__(self, N=45, **kwargs):
        super().__init__(**kwargs)
        self.N = N
        self.fig, self.ax = plt.subplots()

    def build(self):
        x, y = np.random.rand(2, self.N)
        c = np.random.randint(1, 5, size=self.N)
        s = np.random.randint(10, 220, size=self.N)

        scatter = self.ax.scatter(x, y, c=c, s=s)

        # Produce a legend with the unique colors from the scatter
        legend1 = self.ax.legend(*scatter.legend_elements(), loc="lower left", title="Classes")
        self.ax.add_artist(legend1)

        # Produce a legend with a cross section of sizes from the scatter
        handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)
        legend2 = self.ax.legend(handles, labels, loc="upper right", title="Sizes")

        # Add the MatplotlibChart to the UserControl
        return MatplotlibChart(self.fig, expand=True)
