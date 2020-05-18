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

    def selectSubjects(self, root, width, height):
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
    tile_selected = pyqtSignal(int)
 
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.color_palette = [0]*16
        self.data = [[0]*8]*8
        self.index = index

    def getIndex(self):
        return self.index

    def setData(self, data):
        self.data = bytes([pix for sub in data for pix in sub])

    def setColors(self, palette):
        self.color_palette = palette

    def update(self):
        image = QImage(self.data, 8, 8, QImage.Format_Indexed8).scaled(25, 25)
        image.setColorTable([color.rgba() for color in self.color_palette])
        self.setPixmap(QPixmap.fromImage(image))

    def mousePressEvent(self, event):
        self.tile_selected.emit(self.index)

    def enterEvent(self, event):
        QToolTip.showText(event.globalPos(), hex(self.index))

    def leaveEvent(self, event):
        QToolTip.hideText()

class PixelPalette(QFrame):
    subject_selected = pyqtSignal(int, int, int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.contents = []
        self.overlay = None
        self.selected = None
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop)
        self.setLayout(self.grid)
        self.enabled = False
        self.loc_cache = {}
        self.selected = 0
        self.top_left = (0,0)
        self.bottom_right = (0,0)
        self.select_width = 1
        self.select_height = 1

    def setup(self, data):
        self.data = data
        row = col = index = 0
        for index, sprite in enumerate(self.data.getSprites()):
            color_palette = list(self.data.getSprColPals())[0]
            tile = Tile(index, self)
            tile.setColors(color_palette)
            tile.setData(sprite)
            tile.update()
            tile.tile_selected.connect(self.selectSubjects)
            self.contents.append(tile)
            self.grid.addWidget(self.contents[index], row, col)
            col = col + 1 if col < 15 else 0
            row = row + 1 if col == 0 else row
            index += 1
        self.setEnabled(True)
        self.overlay = Overlay()
        self.overlay.setDims(math.floor(self.contents.__len__()/16))
        self.grid.addWidget(self.overlay, 0, 0, -1, -1)
        self.genLocCache(math.floor(self.contents.__len__()/16))
        self.data.spr_batch_updated.connect(self.updateSubjects)
        self.selectSubjects(self.contents[0].getIndex())

    pyqtSlot(int)
    def selectSubjects(self, index):
        self.selected = index
        data = self.data.getSprites() if self.source == Sources.SPRITE else self.data.getTiles()
        num_rows = math.floor(data.__len__() / 16)
        initial_row = math.floor(self.selected/16)
        if math.floor((self.selected + self.select_width - 1) / 16) > initial_row:
            self.selected = math.floor(self.selected/16) * 16 + 16 - self.select_width
        if initial_row + self.select_height > num_rows:
            self.selected -= 16 * (initial_row + self.select_height - num_rows)
        self.top_left = self.genCoords(self.selected)
        self.bottom_right = self.genCoords(self.selected + 16 * self.select_height + self.select_width)
        self.overlay.selectSubjects(self.selected, self.select_width, self.select_height)
        self.subject_selected.emit(self.selected, self.select_width, self.select_height)

    pyqtSlot(set)
    def updateSubjects(self, subjects):
        lowest = self.contents[-1]
        for subject in subjects:
            tile = self.contents[subject]
            tile.setData(self.data.getSprite(subject))
            tile.update()
            lowest = subject if tile.index < self.contents[lowest].index else lowest
            if not self.inSelection(self.contents[lowest].index):
                self.selectSubjects(lowest)
            else:
                self.subject_selected.emit(self.selected, self.select_width, self.select_height)

    pyqtSlot(str)
    def setColorPalette(self, palette):
        self.current_palette = palette
        for subject in self.contents:
            subject.setColors(self.data.sprite_color_palettes[self.current_palette])
            subject.update()

    def inSelection(self, index):
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        x, y = self.loc_cache[index]
        return x1 <= x <= x2-1 and y1 <= y <= y2-1

    # NEEDS TO BE CALLED AGAIN WHENEVER # OF SPRITES/TILES CHANGES!
    def genLocCache(self, height):
        for loc in range(height*16):
            self.loc_cache[loc] = self.genCoords(loc)

    def genCoords(self, index):
        return (index % 16, math.floor(index/16))

    def changeSelectionSize(self, width, height):
        self.select_width = width
        self.select_height = height
        self.selectSubjects(self.selected)

class Contents(QWidget):
    def __init__(self, source, palette, parent=None):
        super().__init__(parent)
        self.palette = palette
        control_layout = QHBoxLayout()
        w_label = QLabel("Width:")
        self.width = QSpinBox()
        self.width.setMaximum(16)
        self.width.setMinimum(1)
        h_label = QLabel("Height:")
        self.height = QSpinBox()
        self.height.setMaximum(8) # HARDCODED FOR DEMO
        self.height.setMinimum(1)
        self.width.valueChanged.connect(self.widthChanged)
        self.height.valueChanged.connect(self.heightChanged)
        control_layout.addWidget(w_label)
        control_layout.addWidget(self.width)
        control_layout.addWidget(h_label)
        control_layout.addWidget(self.height)
        scroll_area = QScrollArea(self)
        self.setFixedWidth(scroll_area.verticalScrollBar().sizeHint().width() + 420)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(self.palette)
        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    @pyqtSlot(int)
    def widthChanged(self, width):
        self.palette.changeSelectionSize(width, self.height.value())

    @pyqtSlot(int)
    def heightChanged(self, height):
        self.palette.changeSelectionSize(self.width.value(), height)

class PixelPaletteDock(QDockWidget):
    palette_updated = pyqtSignal(str)

    def __init__(self, source, parent=None):
        title = "Sprite " if source == Sources.SPRITE else "Tile "
        super().__init__(title + "Palettes", parent)
        self.setFloating(False)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.pixel_palette = PixelPalette(source)
        self.contents = Contents(source, self.pixel_palette)
        self.palette_updated.connect(self.pixel_palette.setColorPalette)
        self.setWidget(self.contents)

    def setup(self, data):
        self.pixel_palette.setup(data)

    def closeEvent(self, event):
        event.ignore()