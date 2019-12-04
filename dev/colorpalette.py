from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

SWATCH_SIZE = 25

def upsample(red, green, blue):
    red = round((red/7)*255)
    green = round((green/7)*255)
    blue = round((blue/3)*255)
    return (red, green, blue)

class Color(QLabel):
    color = QColor()
    clicked = pyqtSignal(QColor)

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.setPixmap(QPixmap(SWATCH_SIZE,SWATCH_SIZE))

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)

    def mousePressEvent(self, event):
        self.clicked.emit(self.color)

class ColorPalette(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(SWATCH_SIZE*16, SWATCH_SIZE*16)
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)
        self.setLayout(grid)
        self.swatches = [Color() for n in range(256)]

        positions = [(row,col) for row in range(16) for col in range(16)]
        colors = [(red, green, blue) for red in range(8) for green in range(8) for blue in range(4)]

        for position, color, swatch in zip(positions,colors, self.swatches):
            swatch.fill(QColor(*upsample(*color)))
            grid.addWidget(swatch, *position)
