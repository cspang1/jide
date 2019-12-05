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
    clicked = pyqtSignal(int, QColor)

    def __init__(self, index, parent=None):
        QLabel.__init__(self, parent)
        self.index = index
        self.setPixmap(QPixmap(25, 25))

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)

class ColorPicker(QDialog):
    def __init__(self):
        super().__init__()
    
        actions = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel)

        actions.accepted.connect(self.accept)
        actions.rejected.connect(self.reject)
        #actions.applied.connect(self.apply)

        color_palette = ColorPalette()
        positions = [(row,col) for row in range(16) for col in range(16)]
        colors = [(red, green, blue) for red in range(8) for green in range(8) for blue in range(4)]
        color_palette.addSwatches(colors, positions)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(color_palette)
        mainLayout.addWidget(actions)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Select Color")

class ColorPalette(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(256)]
        self.enabled = False

    def addSwatches(self, colors, positions):
        for position, color, swatch in zip(positions,colors, self.palette):
            swatch.fill(QColor(*upsample(*color)))
            self.grid.addWidget(swatch, *position)