from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QWidget,
)
# from source import Source
from ui.color_preview_ui import Ui_color_preview

class ColorPreview(QWidget, Ui_color_preview):
    """Color preview widget showing primary and secondary color selections

    :param source:  Subject source of preview, either sprite or tile
    :type source:   Source
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    switch = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # self.source = source
        self.primary_color = QColor(211, 211, 211, 255)
        self.secondary_color = QColor(211, 211, 211, 255)
        self.primary_index = 0
        self.secondary_index = 0
        self.has_transparency = True

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        rect_pen = QPen(Qt.black)
        trans_pen = QPen(Qt.red)
        rect_pen.setWidth(3)
        trans_pen.setWidth(3)
        rect_pen.setJoinStyle(Qt.MiterJoin)
        trans_pen.setCapStyle(Qt.RoundCap)
        sec_brush = QBrush(self.secondary_color)
        prim_brush = QBrush(self.primary_color)
        painter.setPen(rect_pen)
        painter.setBrush(sec_brush)
        painter.drawRect(27, 27, 61, 61)
        if self.secondary_index == 0 and self.has_transparency:
            painter.setPen(trans_pen)
            painter.drawLine(30, 30, 61 + 25, 61 + 25)
        painter.setPen(rect_pen)
        painter.setBrush(prim_brush)
        painter.drawRect(1, 1, 61, 61)
        if self.primary_index == 0 and self.has_transparency:
            painter.setPen(trans_pen)
            painter.drawLine(4, 4, 61 - 1, 61 - 1)

    @pyqtSlot(QColor, int)
    def set_primary_color(self, color, index):
        self.primary_color = color
        self.primary_index = index
        if self.secondary_index == self.primary_index:
            self.set_secondary_color(self.primary_color, self.primary_index)
        self.update()

    @pyqtSlot(QColor, int)
    def set_secondary_color(self, color, index):
        self.secondary_color = color
        self.secondary_index = index
        self.update()

    def get_secondary_index(self):
        return self.secondary_index

    def set_transparency(self, has_transparency):
        self.has_transparency = has_transparency
        self.update()
