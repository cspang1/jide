from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorpicker import *

class Color(QLabel):
    color_changed = pyqtSignal(int, QColor)
    pen_changed = pyqtSignal(int)
    color_selected = pyqtSignal(int)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.selected = False
        self.setPixmap(QPixmap(100, 100))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if self.index == 0:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(QLineF(0,0,100,100))
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(10)
        else:
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
        self.color_selected.emit(self.index)
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def select(self):
        self.selected = True
        self.update()

class ColorPalette(QWidget):
    palette_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(16)]
        positions = [(row,col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, self.palette):
            swatch.fill(QColor(211, 211, 211))
            swatch.color_changed.connect(self.sendColorUpdate)
            swatch.color_selected.connect(self.selectColor)
            self.grid.addWidget(swatch, *position)
        self.enabled = False

    def setup(self, data):
        self.data = data
        self.data.spr_col_updated.connect(self.setPalette)
        self.palette[0].select()

    pyqtSlot(int, QColor)
    def sendColorUpdate(self, index, color):
        self.data.setSprCol(self.current_palette, index, color)

    pyqtSlot(str)
    def setPalette(self, palette):
        self.current_palette = palette
        widgets = (self.grid.itemAt(index) for index in range(self.grid.count()))
        for color, widget in zip(self.data.sprite_color_palettes[self.current_palette], widgets):
            widget.widget().fill(color)
        self.grid.itemAt(0).widget().fill(QColor(0,0,0))
        self.palette_updated.emit(self.current_palette)

    pyqtSlot(int)
    def selectColor(self, index):
        for idx in range(self.grid.count()):
            if idx != index:
                self.grid.itemAt(idx).widget().deselect()

class ColorPaletteDock(QDockWidget):
    palette_updated = pyqtSignal(str)

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFloating(False)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.docked_widget = QWidget(self)
        self.setWidget(self.docked_widget)
        self.docked_widget.setLayout(QVBoxLayout())
        self.docked_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.color_palette = ColorPalette()
        self.color_palette_list = QComboBox()
        self.color_palette_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.palette_picker = QHBoxLayout()
        self.palette_label = QLabel("Palette:")
        self.palette_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.palette_picker.addWidget(self.palette_label)
        self.palette_picker.addWidget(self.color_palette_list)
        self.docked_widget.layout().addLayout(self.palette_picker)
        self.docked_widget.layout().addWidget(self.color_palette)
        self.color_palette_list.setEnabled(False)
        self.color_palette.setEnabled(False)
        self.color_palette.palette_updated.connect(self.verifyCurrentPalette)

    def setup(self, data):
        self.color_palette.setup(data)
        self.color_palette_list.currentIndexChanged.connect(self.setColorPalette)
        self.color_palette_list.setEnabled(True)
        self.color_palette.setEnabled(True)
        for name, palette in data.sprite_color_palettes.items():
            self.color_palette_list.addItem(name)

    pyqtSlot(str)
    def verifyCurrentPalette(self, name):
        self.color_palette_list.setCurrentIndex(self.color_palette_list.findText(name))
        self.palette_updated.emit(name)

    def setColorPalette(self, index):
        self.color_palette.setPalette(self.color_palette_list.currentText())

    def closeEvent(self, event):
        event.ignore()