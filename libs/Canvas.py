from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        super(MplCanvas, self).__init__(self.figure)

    def clear(self):
        """ Очистка всего графика и добавление чистого листа """
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)

    def saveAs(self, fname):
        self.figure.savefig(fname)