import sys
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget

class TestView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setEnabled(True)
