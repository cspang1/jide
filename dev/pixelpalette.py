from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from sources import Sources
import math

class Overlay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.height = 0
        self.selected = (0, 0, 0)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def setDims(self, height):
        self.height = height
        self.setFixedSize(16*25, self.height*25)

    def selectTiles(self, root, width, height):
        self.selected = (root, width, height)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0,0,16*25-1,self.height*25-1)
        lines = []
        for longitude in range(16):
            line = QLineF(longitude*25, 0, longitude*25, self.height*25)
            lines.append(line)
        for latitude in range(self.height):
            line = QLineF(0, latitude*25, 16*25, latitude*25)
            lines.append(line)
        painter.drawLines(lines)
        s_root, s_width, s_height = self.selected
        x = s_root % 16
        y = math.floor(s_root / 16)
        pen.setColor(Qt.red)
        pen.setWidth(3)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(x*25, y*25, s_width*25, s_height*25)

class Tile(QLabel):
    tile_selected = pyqtSignal(str, int)
 
    def __init__(self, name, data, index, parent=None):
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.original = data
        self.setPixmap(QPixmap.fromImage(self.original.scaled(25, 25)))
        self.name = name
        self.index = index

    def getData(self):
        return self.original

    def updatePixmap(self, col, row, value):
        self.original.setPixel(col, row, value)
        self.setPixmap(QPixmap.fromImage(self.original.scaled(25, 25)))

    def setColors(self, palette):
        self.original.setColorTable([color.rgba() for color in palette])
        self.setPixmap(QPixmap.fromImage(self.original.scaled(25, 25)))

    def mousePressEvent(self, event):
        self.tile_selected.emit(self.name, self.index)

    def enterEvent(self, event):
        QToolTip.showText(event.globalPos(), "{0}: {1}".format(hex(self.index), self.name))

    def leaveEvent(self, event):
        QToolTip.hideText()

class PixelPalette(QFrame):
    subject_selected = pyqtSignal(int, int, int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.contents = {}
        self.overlay = None
        self.selected = None
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop)
        self.setLayout(self.grid)
        self.enabled = False
        self.width = 4 # DEMO
        self.height = 4 # DEMO

    def setup(self, data):
        self.data = data
        self.data.spr_pix_updated.connect(self.updatePixel)
        row = col = index = 0
        for name,sprite in self.data.sprite_pixel_palettes.items():
            sprite = QImage(bytes([pix for sub in sprite for pix in sub]), 8, 8, QImage.Format_Indexed8)
            color_palette = list(self.data.sprite_color_palettes.values())[0]
            tile = Tile(name, sprite, index, self)
            tile.setColors(color_palette)
            tile.tile_selected.connect(self.selectTiles)
            self.contents[name] = tile
            self.grid.addWidget(self.contents[name], row, col)
            col = col + 1 if col < 15 else 0
            row = row + 1 if col == 0 else row
            index += 1
        self.setEnabled(True)
        self.overlay = Overlay(self)
        self.overlay.setDims(math.floor(self.contents.__len__()/16))
        self.selectTiles(next(iter(self.contents)))

    pyqtSlot(str, int, int)
    def updatePixel(self, name, row, col):
        if name != self.selected:
            self.selectTiles(name)
        data = self.data.getSprite(name) if self.source == Sources.SPRITE else self.data.getTile(name)
        self.contents[name].updatePixmap(col, row, data[row][col])

    pyqtSlot(str)
    def selectTiles(self, name):
        self.selected = name
        index = list(self.contents.keys()).index(name)
        data = list(self.data.getSprites()) if self.source == Sources.SPRITE else list(self.data.getTiles())
        num_rows = math.floor(data.__len__() / 16)
        initial_row = math.floor(index/16)
        if math.floor((index + self.width - 1) / 16) > initial_row:
            index = math.floor(index/16) * 16 + 16 - self.width
        if initial_row + self.height > num_rows:
            index -= 16 * (initial_row + self.height - num_rows)
        self.subject_selected.emit(index, self.width, self.height)
        self.overlay.selectTiles(index, self.width, self.height)

    pyqtSlot(str)
    def setColorPalette(self, palette):
        self.current_palette = palette
        widgets = (self.grid.itemAt(index).widget() for index in range(self.grid.count()))
        for widget in widgets:
            widget.setColors(self.data.sprite_color_palettes[palette])

class PixelPaletteDock(QDockWidget):
    palette_updated = pyqtSignal(str)

    def __init__(self, source, parent=None):
        title = "Sprite " if source == Sources.SPRITE else "Tile "
        super().__init__(title + "Palettes", parent)
        self.source = source
        self.setFloating(False)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFixedWidth(self.scroll_area.verticalScrollBar().sizeHint().width() + 403)
        self.scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.pixel_palette = PixelPalette(source)
        self.palette_updated.connect(self.pixel_palette.setColorPalette)
        self.scroll_area.setWidget(self.pixel_palette)
        self.setWidget(self.scroll_area)

    def setup(self, data):
        self.pixel_palette.setup(data)

    def closeEvent(self, event):
        event.ignore()