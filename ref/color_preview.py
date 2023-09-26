from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QWidget,
)
# from source import Source
from color_preview_ui import Ui_color_preview

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
        # if self.source is Source.SPRITE:
        if True:
            if self.secondary_index == 0:
                painter.setPen(trans_pen)
                painter.drawLine(30, 30, 61 + 25, 61 + 25)
        painter.setPen(rect_pen)
        painter.setBrush(prim_brush)
        painter.drawRect(1, 1, 61, 61)
        # if self.source is Source.SPRITE:
        if True:
            if self.primary_index == 0:
                painter.setPen(trans_pen)
                painter.drawLine(4, 4, 61 - 1, 61 - 1)

    # def setPrimaryColor(self, color):
    #     """Sets the primary color of the preview

    #     :param color:   Color to be set as the primary
    #     :type color:    QColor
    #     """
    #     self.primary_color = color
    #     self.update()

    # def setPrimaryIndex(self, index):
    #     """Sets the index of the chosen primary color of the preview

    #     :param index:   Index to be set as the primary
    #     :type index:    int
    #     """
    #     self.primary_index = index
    #     self.update()

    # def setSecondaryColor(self, color):
    #     """Sets the secondary color of the preview

    #     :param color:   Color to be set as the secondary
    #     :type color:    QColor
    #     """
    #     self.secondary_color = color
    #     self.update()

    # def setSecondaryIndex(self, index):
    #     """Sets the index of the chosen secondary color of the preview

    #     :param index:   Index to be set as the secondary
    #     :type index:    int
    #     """
    #     self.secondary_index = index
    #     self.update()

    # @pyqtSlot(bool)
    # def setColorSwitchEnabled(self, enabled):
    #     """Sets the switch color action/button to be enabled/disabled

    #     :param enabled: Whether color switch is to be enabled or disabled
    #     :type enabled:  bool
    #     """
    #     self.switch_color.setEnabled(enabled)
    #     self.switch_button.setIcon(self.switch_icon)
