from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorpicker import *

class Color(QLabel):
    color_changed = pyqtSignal(int, QColor)
    pen_changed = pyqtSignal(int)

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
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, 99, 99)

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        if self.index != 0:
            picker = ColorPicker(self.color)
            if picker.exec():
                self.color = picker.getColor()
                self.color_changed.emit(self.index, self.color)

    def mousePressEvent(self, event):
        self.pen_changed.emit(self.index)

class ColorPalette(QWidget):
    color_changed = pyqtSignal(str, int, QColor)
    palette_updated = pyqtSignal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(16)]
        positions = [(row,col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, self.palette):
            swatch.fill(QColor(0,0,0))
            self.grid.addWidget(swatch, *position)
        for swatch in self.palette:
            swatch.color_changed.connect(self.sendColorUpdate)
        self.color_changed.connect(self.data.setSprCol)
        self.data.spr_col_updated.connect(self.setPalette)
        self.enabled = False

    pyqtSlot(int, QColor)
    def sendColorUpdate(self, index, color):
        self.color_changed.emit(self.current_palette, index, color)

    pyqtSlot(str)
    def setPalette(self, palette):
        self.current_palette = palette
        widgets = (self.grid.itemAt(index) for index in range(self.grid.count()))
        for color, widget in zip(self.data.sprite_color_palettes[self.current_palette], widgets):
            widget.widget().fill(color)
        self.grid.itemAt(0).widget().fill(QColor(0,0,0))
        self.palette_updated.emit(self.current_palette)