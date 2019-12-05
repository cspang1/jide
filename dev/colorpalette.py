from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorpicker import *

class Color(QLabel):
    def __init__(self, index, parent=None):
        QLabel.__init__(self, parent)
        self.index = index
        self.setPixmap(QPixmap(100, 100))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if self.index == 0:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(QLineF(0,0,100,100))
        pen = QPen(Qt.black)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, 100, 100)

    def fill(self, color):
        self.pixmap().fill(color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        if self.index != 0:
            picker = ColorPicker()
            picker.exec()

    def mousePressEvent(self, event):
        print("Set pen color to {}".format(self.index))

class ColorPalette(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.setLayout(self.grid)
        palette = [Color(n) for n in range(16)]
        positions = [(row,col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, palette):
            swatch.fill(QColor(0,0,0))
            self.grid.addWidget(swatch, *position)
        self.enabled = False

    def setPalette(self, palette):
        widgets = (self.grid.itemAt(index) for index in range(self.grid.count()))
        for color, widget in zip(self.data.sprite_color_palettes[palette], widgets):
            widget.widget().fill(color)
        self.grid.itemAt(0).widget().fill(QColor(0,0,0))