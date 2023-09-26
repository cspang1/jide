from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QLineF
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import (
    QLabel,
    QSizePolicy,
)
from source import Source

class Color(QLabel):
    """Representation of a single color in the color palette

    :param index:   Numerical index of the color in a color table
    :type index:    int
    :param source:  Source subject of the color, either sprite or tile
    :type source:   Source
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    color_selected = pyqtSignal(int, QColor, Qt.MouseButton)
    edit = pyqtSignal(int, QColor)

    def __init__(self, index, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.index = index
        self.selected = False
        self.setPixmap(QPixmap(75, 75))
        self.fill(QColor(211, 211, 211))
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    def paintEvent(self, event):
        """Color paint event to draw grid and transaprency indications

        :param event:   Paint event
        :type event:    QPaintEvent
        """
        super().paintEvent(event)
        painter = QPainter(self)
        if self.index == 0 and self.source is Source.SPRITE:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(QLineF(0, 0, 72, 72))
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(pen)
            painter.drawRect(2, 2, 70, 70)
        else:
            pen = QPen(Qt.black)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(0, 0, 74, 74)

    def fill(self, color):
        """Fills color

        :param color:   Color to be filled with
        :type color:    QColor
        """
        self.color = color
        self.pixmap().fill(self.color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        """Handles double clicking on a given color to open the color picker

        :param event:   Source event
        :type event:    QMouseEvent
        """
        if (
            self.index != 0 or self.source is Source.TILE
        ) and event.buttons() == Qt.LeftButton:
            self.edit.emit(self.index, self.color)

    def mousePressEvent(self, event):
        """Handles clicking on a given color to select that color

        :param event:   Source event
        :type event:    QMouseEvent
        """
        if event.button() in [Qt.LeftButton, Qt.RightButton]:
            self.color_selected.emit(self.index, self.color, event.button())

    def deselect(self):
        """Handles deselecting a color
        """
        self.selected = False
        self.update()

    def select(self):
        """Handles selecting a color
        """
        self.selected = True
        self.update()
