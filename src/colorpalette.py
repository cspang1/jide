from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QLineF
from PyQt5.QtGui import QColor, QIcon, QPixmap, QKeySequence, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QDockWidget,
    QVBoxLayout,
    QSizePolicy,
    QGridLayout,
    QAction,
    QToolButton,
    QHBoxLayout,
    QComboBox,
    qApp,
    QUndoStack,
    QInputDialog,
    QLineEdit,
    QMessageBox,
)
from .colorpicker import ColorPicker, upsample, downsample, normalize
from . import resources
from .source import Source


class ColorPreview(QWidget):
    """Color preview widget showing primary and secondary color selections

    :param source: Subject source of preview, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    switch = pyqtSignal()

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.setFixedSize(95, 95)
        self.primary_color = QColor(211, 211, 211, 255)
        self.secondary_color = QColor(211, 211, 211, 255)
        self.primary_index = 0
        self.secondary_index = 0
        self.switch_icon = QIcon()
        self.switch_icon.addPixmap(QPixmap(":/icons/switch_color.png"))
        self.switch_color = QAction(self)
        self.switch_color.setShortcut("X")
        self.switch_color.triggered.connect(self.switch)
        self.switch_button = QToolButton(self)
        self.switch_color.setToolTip("Switch colors (X)")
        self.switch_button.setDefaultAction(self.switch_color)
        self.setColorSwitchEnabled(True)
        self.switch_button.move(-1, 63)
        self.switch_button.resize(28, 28)
        self.switch_button.setIcon(self.switch_icon)

    def paintEvent(self, event):
        """Preview paint event to draw regular and transparent color selections

        :param event: Paint event
        :type event: QPaintEvent
        """
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
        if self.source is Source.SPRITE:
            if self.secondary_index == 0:
                painter.setPen(trans_pen)
                painter.drawLine(30, 30, 61 + 25, 61 + 25)
        painter.setPen(rect_pen)
        painter.setBrush(prim_brush)
        painter.drawRect(1, 1, 61, 61)
        if self.source is Source.SPRITE:
            if self.primary_index == 0:
                painter.setPen(trans_pen)
                painter.drawLine(4, 4, 61 - 1, 61 - 1)

    def setPrimaryColor(self, color):
        """Sets the primary color of the preview

        :param color: Color to be set as the primary
        :type color: QColor
        """
        self.primary_color = color
        self.update()

    def setPrimaryIndex(self, index):
        """Sets the index of the chosen primary color of the preview

        :param index: Index to be set as the primary
        :type index: int
        """
        self.primary_index = index
        self.update()

    def setSecondaryColor(self, color):
        """Sets the secondary color of the preview

        :param color: Color to be set as the secondary
        :type color: QColor
        """
        self.secondary_color = color
        self.update()

    def setSecondaryIndex(self, index):
        """Sets the index of the chosen secondary color of the preview

        :param index: Index to be set as the secondary
        :type index: int
        """
        self.secondary_index = index
        self.update()

    @pyqtSlot(bool)
    def setColorSwitchEnabled(self, enabled):
        """Sets the switch color aciton/button to be enabled/disabled

        :param enabled: Whether color switch is to be enabled or disabled
        :type enabled: bool
        """
        self.switch_color.setEnabled(enabled)
        self.switch_button.setIcon(self.switch_icon)


class Color(QLabel):
    """Representation of a single color in the color palette

    :param index: Numerical index of the color in a color table
    :type index: int
    :param source: Source subject of the color, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
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

    def paintEvent(self, event):
        """Color paint event to draw grid and transaprency indications

        :param event: Paint event
        :type event: QPaintEvent
        """
        super().paintEvent(event)
        painter = QPainter(self)
        if self.index == 0 and self.source is Source.SPRITE:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(QLineF(0, 0, 75, 75))
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(10)
        else:
            pen = QPen(Qt.black)
            pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, 74, 74)

    def fill(self, color):
        """Fills color

        :param color: Color to be filled with
        :type color: QColor
        """
        self.color = color
        self.pixmap().fill(self.color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        """Handles double clicking on a given color to open the color picker

        :param event: Source event
        :type event: QMouseEvent
        """
        if (
            self.index != 0 or self.source is Source.TILE
        ) and event.buttons() == Qt.LeftButton:
            self.edit.emit(self.index, self.color)

    def mousePressEvent(self, event):
        """Handles clicking on a given color to select that color

        :param event: Source event
        :type event: QMouseEvent
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


class ColorPalette(QWidget):
    """Represents a palette of colors

    :param source: Subject source of the palette, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    palette_updated = pyqtSignal(str)
    color_selected = pyqtSignal(int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.picker = ColorPicker(self)
        self.color_preview = ColorPreview(self.source, self)
        self.color_preview.switch.connect(self.switchColors)
        self.palette = [Color(n, self.source, self) for n in range(16)]
        positions = [(row, col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, self.palette):
            swatch.color_selected.connect(self.selectColor)
            swatch.edit.connect(self.openPicker)
            self.grid.addWidget(swatch, *position)
        self.enabled = False
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.grid)
        self.main_layout.addWidget(self.color_preview)
        self.main_layout.setContentsMargins(0, 0, 5, 0)
        self.main_layout.setSpacing(19)
        self.setLayout(self.main_layout)

    def setup(self, data):
        """Sets up the data source for the palette and initial selection

        :param data: Data source of palette
        :type data: GameData
        """
        self.data = data
        self.data.col_pal_updated.connect(self.setPalette)
        self.palette[0].select()

    @pyqtSlot(int, QColor)
    def openPicker(self, index, orig_color):
        """Handles opening the color picker after double-clicking on a color

        :param index: Index of the color selected
        :type index: int
        :param orig_color: Original color of the selection color
        :type orig_color: QColor
        """
        self.picker.setColor(orig_color)
        self.picker.preview_color.connect(
            lambda orig_color: self.previewColor(index, orig_color)
        )
        if self.picker.exec():
            new_color = self.picker.getColor()
            self.sendColorUpdate(index, new_color, orig_color)
        else:
            self.previewColor(index, orig_color)
        self.picker.preview_color.disconnect()

    @pyqtSlot(int, QColor)
    def sendColorUpdate(self, index, new_color, orig_color=None):
        """Sends color update to centralized GameData data

        :param index: Index of changed color in palette
        :type index: int
        :param new_color: Color to be changed to
        :type new_color: QColor
        :param orig_color: Original color, defaults to None
        :type orig_color: QColor, optional
        """
        self.data.setColor(
            self.current_palette, index, new_color, self.source, orig_color
        )

    @pyqtSlot(QColor)
    def previewColor(self, index, color):
        """Triggers preview of color throughout application when interacting with color picker

        :param index: Index of the color being changed
        :type index: int
        :param color: Color to be previewed
        :type color: QColor
        """
        self.data.previewColor(self.current_palette, index, color, self.source)

    @pyqtSlot(Source, str)
    def setPalette(self, source, palette):
        """Sets the overall color palette colors

        :param source: Subject source of color palette, either sprite or tile
        :type source: Source
        :param palette: Name of the color palette to be set to
        :type palette: str
        """
        if source is not self.source:
            return
        self.current_palette = palette
        widgets = [self.grid.itemAt(index) for index in range(self.grid.count())]
        for color, widget in zip(
            self.data.getColPal(self.current_palette, self.source), widgets
        ):
            widget.widget().fill(color)
            index = widgets.index(widget)
            if index == self.color_preview.primary_index:
                self.color_preview.setPrimaryColor(
                    color
                    if (index != 0 or self.source is Source.TILE)
                    else QColor(Qt.magenta)
                )
            if index == self.color_preview.secondary_index:
                self.color_preview.setSecondaryColor(
                    color
                    if (index != 0 or self.source is Source.TILE)
                    else QColor(Qt.magenta)
                )
        if self.source is Source.SPRITE:
            self.grid.itemAt(0).widget().fill(QColor(Qt.magenta))
        self.palette_updated.emit(self.current_palette)

    @pyqtSlot()
    def switchColors(self):
        """Switches the active color between the primary and secondary colors
        """
        pindex = self.color_preview.primary_index
        pcolor = self.color_preview.primary_color
        sindex = self.color_preview.secondary_index
        scolor = self.color_preview.secondary_color
        self.selectColor(sindex, scolor, Qt.LeftButton)
        self.selectColor(pindex, pcolor, Qt.RightButton)

    @pyqtSlot(int, QColor, Qt.MouseButton)
    def selectColor(self, index, color, button):
        """Selects a primary or secondary color from the palette

        :param index: Index of the chosen color
        :type index: int
        :param color: Color chosen
        :type color: QColor
        :param button: Which mouse button was used to select the primary or secondary color
        :type button: Qt.MouseButton
        """
        if button == Qt.LeftButton:
            self.color_preview.setPrimaryColor(color)
            self.color_preview.setPrimaryIndex(index)
            for idx in range(self.grid.count()):
                if idx != index:
                    self.grid.itemAt(idx).widget().deselect()
                else:
                    self.grid.itemAt(idx).widget().select()
            self.color_selected.emit(index)
        elif button == Qt.RightButton:
            self.color_preview.setSecondaryColor(color)
            self.color_preview.setSecondaryIndex(index)


class ColorPaletteDock(QDockWidget):
    """Dock containing the color palette and preview area

    :param source: Subject source for the dock and its contents, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    palette_updated = pyqtSignal(str)

    def __init__(self, source, parent=None):
        super().__init__("Color Palettes", parent)
        self.source = source
        self.setFloating(False)
        self.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        )
        self.docked_widget = QWidget(self)
        self.setWidget(self.docked_widget)
        self.docked_widget.setLayout(QVBoxLayout())
        self.docked_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.color_palette = ColorPalette(self.source, self)
        self.color_palette_list = QComboBox()
        self.color_palette_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.palette_picker = QHBoxLayout()
        self.palette_label = QLabel("Palette:")
        self.palette_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.palette_picker.addWidget(self.palette_label)
        self.palette_picker.addWidget(self.color_palette_list)
        self.add_palette = QToolButton(self)
        self.add_palette.mousePressEvent = self.addPaletteReq
        self.add_palette.setToolTip("Add new palette")
        add_icon = QIcon()
        add_icon.addPixmap(QPixmap(":/icons/add.png"))
        self.add_palette.setIcon(add_icon)
        self.add_palette.setEnabled(False)
        self.remove_palette = QToolButton(self)
        self.remove_palette.mousePressEvent = self.removePaletteReq
        self.remove_palette.setToolTip("Remove current palette")
        remove_icon = QIcon()
        remove_icon.addPixmap(QPixmap(":/icons/remove.png"))
        self.remove_palette.setIcon(remove_icon)
        self.remove_palette.setEnabled(False)
        self.rename_palette = QToolButton(self)
        self.rename_palette.mousePressEvent = self.renamePaletteReq
        self.rename_palette.setToolTip("Rename current palette")
        rename_icon = QIcon()
        rename_icon.addPixmap(QPixmap(":/icons/rename.png"))
        self.rename_palette.setIcon(rename_icon)
        self.rename_palette.setEnabled(False)
        self.palette_picker.addWidget(self.add_palette)
        self.palette_picker.addWidget(self.remove_palette)
        self.palette_picker.addWidget(self.rename_palette)
        self.docked_widget.layout().addLayout(self.palette_picker)
        self.docked_widget.layout().addWidget(self.color_palette)
        self.color_palette_list.setEnabled(False)
        self.color_palette.setEnabled(False)
        self.color_palette.palette_updated.connect(self.verifyCurrentPalette)

    def setup(self, data):
        """Sets up the data source for the dock's contents and enables UI elements

        :param data: Data source of dock
        :type data: GameData
        """
        self.data = data
        self.data.col_pal_renamed.connect(self.renamePalette)
        self.data.col_pal_added.connect(self.addPalette)
        self.data.col_pal_removed.connect(self.removePalette)
        self.color_palette.setup(self.data)
        self.color_palette_list.currentIndexChanged.connect(self.setColorPalette)
        self.color_palette_list.setEnabled(True)
        self.color_palette.setEnabled(True)
        self.add_palette.setEnabled(True)
        self.remove_palette.setEnabled(True)
        self.rename_palette.setEnabled(True)
        for name in self.data.getColPalNames(self.source):
            self.color_palette_list.addItem(name)

    def addPaletteReq(self, event=None):
        """Sends command to GameData source to add a color palette

        :param event: Mouse click event which triggered the request, defaults to None
        :type event: QMouseEvent, optional
        """
        name, accepted = QInputDialog.getText(
            self, "Add", "Palette name:", QLineEdit.Normal, "New palette"
        )
        if accepted:
            self.data.addColPal(name, self.source)

    def removePaletteReq(self, event=None):
        """Sends command to GameData source to remove a color palette

        :param event: Mouse click event which triggered the request, defaults to None
        :type event: QMouseEvent, optional
        """
        if self.color_palette_list.count() == 1:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "There must be at least one sprite and tile color palette in the project",
            ).exec()
        else:
            name = self.color_palette_list.currentText()
            self.data.remColPal(name, self.source)

    def renamePaletteReq(self, event=None):
        """Sends command to GameData source to rename a color palette

        :param event: Mouse click event which triggered the request, defaults to None
        :type event: QMouseEvent, optional
        """
        cur_name = self.color_palette_list.currentText()
        new_name, accepted = QInputDialog.getText(
            self, "Rename", "Palette name:", QLineEdit.Normal, cur_name
        )
        if accepted:
            self.data.setColPalName(cur_name, new_name, self.source)

    @pyqtSlot(Source, str, int)
    def addPalette(self, source, name, index):
        """Adds a new color palette

        :param source: Subject source of the addition, either sprite or tile
        :type source: Source
        :param name: Name of the added color palette
        :type name: str
        :param index: Index in color palette list to insert the new palette
        :type index: int
        """
        if source is not self.source:
            return
        if name != None:
            self.color_palette_list.insertItem(index, name)
            self.color_palette_list.setCurrentIndex(index)
            self.color_palette.current_palette = name
        else:
            QMessageBox(
                QMessageBox.Critical, "Error", "Palette with that name already exists"
            ).exec()
            self.addPaletteReq()

    @pyqtSlot(Source, str)
    def removePalette(self, source, name):
        """Removes a color palette

        :param source: Subject source of the removal, either sprite or tile
        :type source: Source
        :param name: Name of the removed color palette
        :type name: str
        """
        if source is not self.source:
            return
        if name != None:
            index = self.color_palette_list.findText(name)
            self.color_palette_list.removeItem(index)
            name = self.color_palette_list.currentText()
            self.color_palette.current_palette = name
        else:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to remove palette {}".format(name),
            ).exec()

    @pyqtSlot(Source, str, str)
    def renamePalette(self, source, cur_name, new_name):
        """Renames a color palette

        :param source: Subject source of the removal, either sprite or tile
        :type source: Source
        :param cur_name: Current name of the target color palette
        :type cur_name: str
        :param new_name: New name of the target color palette
        :type new_name: str
        """
        if source is not self.source:
            return
        if cur_name != new_name:
            self.color_palette_list.setItemText(
                self.color_palette_list.findText(cur_name), new_name
            )
            self.color_palette_list.setCurrentIndex(
                self.color_palette_list.findText(new_name)
            )
            self.color_palette.current_palette = new_name
        else:
            QMessageBox(
                QMessageBox.Critical, "Error", "Palette with that name already exists"
            ).exec()
            self.renamePaletteReq()

    @pyqtSlot(str)
    def verifyCurrentPalette(self, name):
        """Ensures that the current color palette in the selection list is accurate

        :param name: Name of the selected color palette
        :type name: str
        """
        self.color_palette_list.setCurrentIndex(self.color_palette_list.findText(name))
        self.palette_updated.emit(name)

    def setColorPalette(self):
        """Sets the active color palette to the one chosen in the selection list
        """
        self.color_palette.setPalette(
            self.source, self.color_palette_list.currentText()
        )

    def closeEvent(self, event):
        """Intercepts the dock close event to prevent its closure

        :param event: Source event
        :type event: QEvent
        """
        event.ignore()
