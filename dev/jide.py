from PyQt5 import QtWidgets
from canvas import GraphicsView

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JIDE")
        self.setCentralWidget(GraphicsView(self))
        self.setStyleSheet("background-color: #494949;")