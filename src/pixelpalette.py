import math
from PyQt5.QtCore import Qt, QSize, QLineF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QDockWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QToolButton,
    QScrollArea,
    QSizePolicy,
    QToolTip,
)
from source import Source


class Overlay(QLabel):
    """Pixel palette overlay used to draw gridlines and selection box

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    tiles_selected = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.height = 0
        self.selected = (0, 0, 0)
        self.setMouseTracking(True)
        self.orig_x = self.orig_y = 0
        self.orig_index = 0
        self.last_x = self.last_y = 0

    def setDims(self, height):
        """Set height in sprites/tiles of pixel palette

        :param height: Number of rows in pixel palette
        :type height: int
        """
        self.height = height
        self.setFixedSize(16 * 25, self.height * 25)

    def selectSubjects(self, root, width, height):
        """Select rectangular region of sprites/tiles

        :param root: Index of root selected element
        :type root: int
        :param width: Width of selection from root
        :type width: int
        :param height: Height of selection from root
        :type height: int
        """
        self.selected = (root, width, height)
        self.update()

    def paintEvent(self, event):
        """Paint event for the overlay

        :param event: QPaintEvent event
        :type event: QPaintEvent
        """
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, 16 * 25 - 1, self.height * 25 - 1)
        lines = []
        for longitude in range(16):
            line = QLineF(longitude * 25, 0, longitude * 25, self.height * 25)
            lines.append(line)
        for latitude in range(self.height):
            line = QLineF(0, latitude * 25, 16 * 25, latitude * 25)
            lines.append(line)
        painter.drawLines(lines)
        s_root, s_width, s_height = self.selected
        x = s_root % 16
        y = math.floor(s_root / 16)
        pen.setColor(Qt.red)
        pen.setWidth(3)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(x * 25, y * 25, s_width * 25, s_height * 25)

    def getCoords(self, event):
        """Get bounded coordinates of a mouse event

        :param event: Source event
        :type event: QMouseEvent
        :return: Bounded horizontal and vertical coordinate of mouse event
        :rtype: tuple(int, int)
        """
        x = min(max(0, math.floor(event.localPos().x() / 25)), 16)
        y = min(max(0, math.floor(event.localPos().y() / 25)), self.height)
        return x, y

    def clamp(self, value, lower=0, upper=16):
        """Clamp a coordinate to bounded dimensions

        :param value: Value to clamp
        :type value: int
        :param lower: Lower bound of clamp, defaults to 0
        :type lower: int, optional
        :param upper: Upper bound of clamp, defaults to 16
        :type upper: int, optional
        :return: Clamped coordinate
        :rtype: int
        """
        return min(max(lower, value), upper)

    def mousePressEvent(self, event):
        """Event to handle mouse clicks on overlay

        :param event: Source event
        :type event: QMouseEvent
        """
        if event.buttons() == Qt.LeftButton:
            self.orig_x, self.orig_y = (
                math.floor(event.pos().x() / 25),
                math.floor(event.pos().y() / 25),
            )
            self.orig_index = self.orig_x + self.orig_y * 16
            self.last_x, self.last_y = (self.orig_x, self.orig_y)
            if event.modifiers() != Qt.ControlModifier:
                self.tiles_selected.emit(self.orig_index, -1, -1)

    def mouseMoveEvent(self, event):
        """Event to handle mouse movement after clicking on overlay

        :param event: Source event
        :type event: QMouseEvent
        """
        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            x, y = (
                self.clamp(math.ceil(event.pos().x() / 25)),
                self.clamp(math.ceil(event.pos().y() / 25), upper=self.height),
            )
            if (x, y) != (self.last_x, self.last_y):
                width = x - self.orig_x if x > self.orig_x else -1
                height = y - self.orig_y if y > self.orig_y else -1
                self.tiles_selected.emit(self.orig_index, width, height)
            self.last_x, self.last_y = (
                self.clamp(math.floor(event.pos().x() / 25)),
                self.clamp(math.floor(self.pos().y() / 25), upper=self.height),
            )
        else:
            x, y = self.getCoords(event)
            QToolTip.showText(event.globalPos(), hex(x + y * 16))


class Tile(QLabel):
    def __init__(self, index, parent=None):
        """Tile representing rendered version of single tile/sprite

        :param index: Index of element in centralized GameData data
        :type index: intr
        :param parent: Parent widget, defaults to None
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.color_palette = [0] * 16
        self.data = [[0] * 8] * 8
        self.index = index

    def setData(self, data):
        """Set pixel data of tile

        :param data: Pixel data list
        :type data: list(int)
        """
        self.data = bytes([pix for sub in data for pix in sub])

    def setColors(self, palette):
        """Set color palette of tile

        :param palette: List of colors representing color palette
        :type palette: list(QColor)
        """
        self.color_palette = palette

    def update(self):
        """Update the tile QImage
        """
        image = QImage(self.data, 8, 8, QImage.Format_Indexed8).scaled(25, 25)
        image.setColorTable([color.rgba() for color in self.color_palette])
        self.setPixmap(QPixmap.fromImage(image))


class PixelPalette(QFrame):
    """Palette of sprite/tiles to be used to select canvas editing area

    :param source: Source subject of the palette, either tile or sprite
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    subject_selected = pyqtSignal(int, int, int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.data = None
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
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)
        self.select_width = 1
        self.select_height = 1

    def setup(self, data):
        """Sets up the data source for the palette and generates the palette

        :param data: Data source of palette
        :type data: GameData
        """
        self.data = data
        self.selected = 0
        self.current_palette = list(self.data.getColPals(self.source))[0]
        self.genPalette()
        self.data.pix_batch_updated.connect(self.updateSubjects)

    @pyqtSlot()
    def genPalette(self):
        """Generates the palette based on the data source
        """
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)
        self.contents.clear()
        row = col = index = 0
        for index, element in enumerate(self.data.getPixelPalettes(self.source)):
            tile = Tile(index, self)
            tile.setColors(self.current_palette)
            tile.setData(element)
            tile.update()
            self.contents.append(tile)
            self.grid.addWidget(self.contents[index], row, col)
            col = col + 1 if col < 15 else 0
            row = row + 1 if col == 0 else row
        self.overlay = Overlay()
        self.overlay.tiles_selected.connect(self.selectSubjects)
        self.overlay.setDims(math.floor(self.contents.__len__() / 16))
        self.grid.addWidget(self.overlay, 0, 0, -1, -1)
        self.genLocCache(math.floor(self.contents.__len__() / 16))
        self.selectSubjects(index=self.selected)

    pyqtSlot(int, int, int)

    def selectSubjects(self, index=None, width=-1, height=-1):
        """Selects a rectangular region of tiles in the palette. None and negative index/width/height values result in internal values being used.

        :param index: Root index of selection, defaults to None
        :type index: int, optional
        :param width: Width of selection from index, defaults to -1
        :type width: int, optional
        :param height: Height of selection from index, defaults to -1
        :type height: int, optional
        """
        self.select_width = width if width > 0 else self.select_width
        self.select_height = height if height > 0 else self.select_height
        self.selected = index if index is not None else self.selected
        data = self.data.getPixelPalettes(self.source)
        num_rows = math.floor(data.__len__() / 16)
        initial_row = math.floor(self.selected / 16)
        if math.floor((self.selected + self.select_width - 1) / 16) > initial_row:
            self.selected = math.floor(self.selected / 16) * 16 + 16 - self.select_width
        if initial_row + self.select_height > num_rows:
            temp_index = self.selected - 16 * (
                initial_row + self.select_height - num_rows
            )
            if temp_index < 0:
                self.select_height -= 1
            else:
                self.selected = temp_index
        self.top_left = self.genCoords(self.selected)
        self.bottom_right = self.genCoords(
            self.selected + 16 * self.select_height + self.select_width
        )
        self.overlay.selectSubjects(
            self.selected, self.select_width, self.select_height
        )
        self.subject_selected.emit(self.selected, self.select_width, self.select_height)

    pyqtSlot(Source, set)

    def updateSubjects(self, source, subjects):
        """Updates the palette's tiles with data from the centralized GameData

        :param source: Source subject of update, either sprite or tile
        :type source: Source
        :param subjects: A set of subject indexes which need to be updated
        :type subjects: set(int)
        """
        if source is not self.source:
            return
        lowest = len(self.contents) - 1
        for subject in subjects:
            tile = self.contents[subject]
            tile.setData(self.data.getElement(subject, self.source))
            tile.update()
            lowest = subject if tile.index < lowest else lowest
            if not self.inSelection(lowest):
                self.selectSubjects(lowest)
            else:
                self.subject_selected.emit(
                    self.selected, self.select_width, self.select_height
                )

    pyqtSlot(str)

    def setColorPalette(self, palette):
        """Set the color palette to be used by the sprites/tiles

        :param palette: Name of the color palette
        :type palette: str
        """
        if self.data is not None:
            self.current_palette = self.data.getColPal(palette, self.source)
            for subject in self.contents:
                subject.setColors(self.current_palette)
                subject.update()

    def inSelection(self, index):
        """Determine if an index is inside the rectangular selection area

        :param index: Target index
        :type index: int
        :return: Whether the target index is inside the selection
        :rtype: bool
        """
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        x, y = self.loc_cache[index]
        return x1 <= x <= x2 - 1 and y1 <= y <= y2 - 1

    @pyqtSlot(int)
    def genLocCache(self, height):
        """Generates a cache of 2D locations for indexes

        :param height: Height of the pixel palette in tiles/sprites
        :type height: int
        """
        self.loc_cache.clear()
        for loc in range(height * 16):
            self.loc_cache[loc] = self.genCoords(loc)

    def genCoords(self, index):
        """Generates the 2D coordinates for a given element index

        :param index: Index of the element
        :type index: int
        :return: (x,y) coordinates of the element
        :rtype: tuple(int, int)
        """
        return (index % 16, math.floor(index / 16))


class Contents(QWidget):
    """Visual contents of the pixel palette

    :param source: Subject source of the contents, either sprite or tile
    :type source: Source
    :param palette: Palette to render in contents
    :type palette: PixelPalette
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    height_changed = pyqtSignal()

    def __init__(self, source, palette, parent=None):
        super().__init__(parent)
        self.source = source
        self.palette = palette
        self.height = 0

        row_ctrl_layout = QHBoxLayout()
        self.add_row = QToolButton(self)
        self.add_row.clicked.connect(self.addPalRow)
        self.add_row.setToolTip("Add new row")
        self.add_row.setEnabled(False)
        add_icon = QIcon()
        add_icon.addPixmap(QPixmap(":/icons/add_row.png"))
        self.add_row.setIcon(add_icon)
        self.add_row.setIconSize(QSize(24, 24))
        self.rem_row = QToolButton(self)
        self.rem_row.clicked.connect(self.remPalRow)
        self.rem_row.setToolTip("Remove last row")
        self.rem_row.setEnabled(False)
        remove_icon = QIcon()
        remove_icon.addPixmap(QPixmap(":/icons/remove_row.png"))
        self.rem_row.setIconSize(QSize(24, 24))
        self.rem_row.setIcon(remove_icon)
        row_ctrl_layout.addWidget(self.add_row)
        row_ctrl_layout.addWidget(self.rem_row)
        row_ctrl_layout.addStretch()

        scroll_area = QScrollArea(self)
        self.setFixedWidth(scroll_area.verticalScrollBar().sizeHint().width() + 420)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(self.palette)
        main_layout = QVBoxLayout()
        main_layout.addLayout(row_ctrl_layout)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def setup(self, data):
        """Sets up the data source for the contents and set dimensions

        :param data: Data source of contents
        :type data: GameData
        """
        self.data = data
        self.data.row_count_updated.connect(self.palRowCntChanged)
        self.height = math.floor(self.data.getPixelPalettes(self.source).__len__() / 16)
        if self.height <= 1:
            self.rem_row.setEnabled(False)
        self.add_row.setEnabled(True)
        self.rem_row.setEnabled(True)

    @pyqtSlot()
    def addPalRow(self):
        """Appends a row to the content palette
        """
        self.data.addPixRow(self.source)

    @pyqtSlot()
    def remPalRow(self):
        """Removes the last rom from the content palette
        """
        if self.height > 1:
            self.data.remPixRow(self.source)

    @pyqtSlot(Source, int)
    def palRowCntChanged(self, source, num_rows):
        """Limits changes to the palette row count by enabling/disable UI elements

        :param source: [description]
        :type source: [type]
        :param num_rows: [description]
        :type num_rows: [type]
        """
        if source is not self.source:
            return
        self.height = num_rows
        self.height_changed.emit()
        if self.height <= 1:
            self.rem_row.setEnabled(False)
        else:
            self.rem_row.setEnabled(True)


class PixelPaletteDock(QDockWidget):
    """Dock containing the pixel palette

    :param source: Subject source of the dock, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    palette_updated = pyqtSignal(str)

    def __init__(self, source, parent=None):
        title = "Sprite " if source == Source.SPRITE else "Tile "
        super().__init__(title + "Palettes", parent)
        self.setFloating(False)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        )
        self.pixel_palette = PixelPalette(source)
        self.contents = Contents(source, self.pixel_palette)
        self.palette_updated.connect(self.pixel_palette.setColorPalette)
        self.setWidget(self.contents)

    def setup(self, data):
        """Sets up the data source for the dock

        :param data: Data source of dock
        :type data: GameData
        """
        self.pixel_palette.setup(data)
        self.contents.setup(data)
        self.contents.height_changed.connect(self.pixel_palette.genPalette)

    def closeEvent(self, event):
        """Handles the close event of the dock by disable it

        :param event: Close event
        :type event: QCloseEvent
        """
        event.ignore()
