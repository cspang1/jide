from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Tile(QLabel):
    tile_selected = pyqtSignal(str)
 
    def __init__(self, name, tile, pixels, parent=None):
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.original = tile
        self.setPixmap(QPixmap.fromImage(self.original))
        self.name = name
        self.selected = False
        self.pixels = pixels

    def setColors(self, palette):
        self.original.setColorTable([color.rgba() for color in palette])
        self.setPixmap(QPixmap.fromImage(self.original))

    def mouseDoubleClickEvent(self, event):
        self.select()

    def select(self):
        self.tile_selected.emit(self.name)
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def enterEvent(self, event):
        QToolTip.showText(event.globalPos(), self.name)

    def leaveEvent(self, event):
        QToolTip.hideText()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, 24, 24)

class PixelPalette(QFrame):
    subject_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop)
        self.setLayout(self.grid)
        self.enabled = False

    def setup(self, data):
        self.data = data
        row = col = 0
        for name,sprite in self.data.sprite_pixel_palettes.items():
            sprite = QImage(bytes([pix for sub in sprite for pix in sub]), 8, 8, QImage.Format_Indexed8)
            color_palette = list(self.data.sprite_color_palettes.values())[0]
            sprite = sprite.scaled(25, 25)
            tile = Tile(name, sprite, self)
            tile.setColors(color_palette)
            tile.tile_selected.connect(self.selectTile)
            self.grid.addWidget(tile, row, col)
            if row == col == 0:
                tile.select()
            col = col + 1 if col < 15 else 0
            row = row + 1 if col == 0 else row
        self.setEnabled(True)

    pyqtSlot(str)
    def selectTile(self, name):
        self.subject_selected.emit(name)
        widgets = (self.grid.itemAt(index).widget() for index in range(self.grid.count()))
        for widget in widgets:
            if(widget.name != name):
                widget.deselect()

    pyqtSlot(str)
    def setColorPalette(self, palette):
        self.current_palette = palette
        widgets = (self.grid.itemAt(index).widget() for index in range(self.grid.count()))
        for widget in widgets:
            widget.setColors(self.data.sprite_color_palettes[palette])

class PixelPaletteDock(QDockWidget):
    palette_updated = pyqtSignal(str)

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFloating(False)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFixedWidth(self.scroll_area.verticalScrollBar().sizeHint().width() + 403)
        self.scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.pixel_palette = PixelPalette()
        self.palette_updated.connect(self.pixel_palette.setColorPalette)
        self.scroll_area.setWidget(self.pixel_palette)
        self.setWidget(self.scroll_area)

    def setup(self, data):
        self.pixel_palette.setup(data)

    def closeEvent(self, event):
        event.ignore()