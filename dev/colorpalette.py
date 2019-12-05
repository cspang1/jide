from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorpicker import *

class Color(QLabel):
    color = QColor()
    clicked = pyqtSignal(int, QColor)
    double_clicked = pyqtSignal(int, QColor)

    def __init__(self, index, parent=None):
        QLabel.__init__(self, parent)
        self.index = index
        self.setPixmap(QPixmap(100, 100))

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        picker = ColorPicker()
        picker.exec()

    def mousePressEvent(self, event):
        print("Set pen color to {}".format(self.index))

class ColorPalette(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(16)]
        positions = [(row,col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, self.palette):
            swatch.fill(QColor(0,0,0))
            self.grid.addWidget(swatch, *position)
        self.enabled = False

    def setPalette(self, colors):
        widgets = (self.grid.itemAt(index) for index in range(self.grid.count()))
        for color, widget in zip(colors, widgets):
            widget.widget().fill(QColor(*color))