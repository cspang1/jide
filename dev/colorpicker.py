from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def upsample(red, green, blue):
    red = round((red/7)*255)
    green = round((green/7)*255)
    blue = round((blue/3)*255)
    return (red, green, blue)

class Color(QLabel):
    color = QColor()
    clicked = pyqtSignal(QColor)

    def __init__(self, index, parent=None):
        QLabel.__init__(self, parent)
        self.index = index
        self.setPixmap(QPixmap(25, 25))

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, 24, 24)

    def mousePressEvent(self, event):
        self.clicked.emit(self.color)

class ColorPalette(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(256)]
        positions = [(row,col) for row in range(16) for col in range(16)]
        colors = [(red, green, blue) for red in range(8) for green in range(8) for blue in range(4)]
        for position, color, swatch in zip(positions,colors, self.palette):
            swatch.fill(QColor(*upsample(*color)))
            self.grid.addWidget(swatch, *position)
        self.enabled = False

class ColorPicker(QDialog):
    def __init__(self, color):
        super().__init__()

        self.color = color

        actions = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        actions.accepted.connect(self.accept)
        actions.rejected.connect(self.reject)

        color_palette = ColorPalette()
        for swatch in color_palette.palette:
            swatch.clicked.connect(self.colorChosen)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(color_palette)
        mainLayout.addWidget(actions)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Select Color")

    def getColor(self):
        return self.color

    @pyqtSlot(QColor)
    def colorChosen(self, color):
        self.color = color