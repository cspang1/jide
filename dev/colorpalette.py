from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ColorPalette(QWidget):

    def __init__(self):
        super().__init__()
        self.setMaximumSize(320, 320)
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)
        self.setLayout(grid)

        positions = [(row,col) for row in range(16) for col in range(16)]
        colors = [(red, green, blue) for red in range(8) for green in range(8) for blue in range(4)]

        for position, color in zip(positions,colors):
            label = QLabel()
            pixmap = QPixmap(20,20)
            pixmap.fill(QColor(*self.upsample(*color)))
            label.setPixmap(pixmap)
            grid.addWidget(label, *position)

    def upsample(self, red, green, blue):
        red = round((red/7)*255)
        green = round((green/7)*255)
        blue = round((blue/3)*255)
        return (red, green, blue)