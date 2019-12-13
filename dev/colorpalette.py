from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorpicker import *
import resources

class ColorPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(95, 95)
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
        if self.secondary_index == 0:
            painter.setPen(trans_pen)
            painter.drawLine(27, 27, 61+28, 61+28)
        painter.setPen(rect_pen)
        painter.setBrush(prim_brush)
        painter.drawRect(1, 1, 61, 61)
        if self.primary_index == 0:
            painter.setPen(trans_pen)
            painter.drawLine(1, 1, 61+2, 61+2)

    def setPrimaryColor(self, index, color):
        if self.primary_index == index:
            self.primary_color = color
        self.update()

    def setSecondaryColor(self, color):
        self.secondary_color = color
        self.update()

    def setPrimaryIndex(self, index):
        self.primary_index = index

    def setSecondaryIndex(self, index):
        self.secondary_index = index

class Color(QLabel):
    color_selected = pyqtSignal(int, QColor, Qt.MouseButton)
    edit = pyqtSignal(int, QColor)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.selected = False
        self.setPixmap(QPixmap(75, 75))
        self.fill(QColor(211, 211, 211))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if self.index == 0:
            pen = QPen(Qt.red)
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(QLineF(0,0,75,75))
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(10)
        else:
            pen = QPen(Qt.black)
            pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, 74, 74)

    def fill(self, color):
        self.color = color
        self.pixmap().fill(self.color)
        self.update()

    def mouseDoubleClickEvent(self, event):
        if self.index != 0 and event.buttons() == Qt.LeftButton:
            self.edit.emit(self.index, self.color)

    def mousePressEvent(self, event):
        if event.button() in [Qt.LeftButton, Qt.RightButton]:
            self.color_selected.emit(self.index, self.color, event.button())
            if event.button() == Qt.LeftButton:
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
    color_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.picker = ColorPicker(self)
        self.color_preview = ColorPreview(self)
        self.palette = [Color(n) for n in range(16)]
        positions = [(row,col) for row in range(4) for col in range(4)]
        for position, swatch in zip(positions, self.palette):
            swatch.color_selected.connect(self.selectColor)
            swatch.edit.connect(self.openPicker)
            self.grid.addWidget(swatch, *position)
        self.enabled = False
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.grid)
        self.main_layout.addWidget(self.color_preview)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def setup(self, data):
        self.data = data
        self.data.spr_col_pal_updated.connect(self.setPalette)
        self.palette[0].select()
        self.color_preview.setPrimaryIndex(0)
        self.color_preview.setSecondaryIndex(0)

    pyqtSlot(int, QColor)
    def openPicker(self, index, orig_color):
        self.picker.setColor(orig_color)
        self.picker.preview_color.connect(lambda orig_color : self.previewColor(index, orig_color))
        if self.picker.exec():
            new_color = self.picker.getColor()
            self.color_preview.setPrimaryColor(index, new_color)
            self.sendColorUpdate(index, new_color, orig_color)
        else:
            self.color_preview.setPrimaryColor(index, orig_color)
            self.previewColor(index, orig_color)
        self.picker.preview_color.disconnect()

    pyqtSlot(int, QColor)
    def sendColorUpdate(self, index, new_color, orig_color=None):
        self.data.setSprCol(self.current_palette, index, new_color, orig_color)

    pyqtSlot(QColor)
    def previewColor(self, index, color):
        self.color_preview.setPrimaryColor(index, color)
        self.data.previewSprCol(self.current_palette, index, color)

    pyqtSlot(str)
    def setPalette(self, palette):
        self.current_palette = palette
        widgets = [self.grid.itemAt(index) for index in range(self.grid.count())]
        for color, widget in zip(self.data.sprite_color_palettes[self.current_palette], widgets):
            widget.widget().fill(color)
            index = widgets.index(widget)
            if index == 0:
                color = QColor(0, 0, 0)
                if self.color_preview.secondary_index == 0:
                    self.color_preview.setSecondaryColor(color)
            self.color_preview.setPrimaryColor(index, color)
        self.grid.itemAt(0).widget().fill(QColor(0,0,0))
        self.palette_updated.emit(self.current_palette)

    pyqtSlot(int, QColor, Qt.MouseButton)
    def selectColor(self, index, color, button):
        if button == Qt.LeftButton:
            self.color_preview.setPrimaryIndex(index)
            self.color_preview.setPrimaryColor(index, color)
            for idx in range(self.grid.count()):
                if idx != index:
                    self.grid.itemAt(idx).widget().deselect()
            self.color_selected.emit(index)
        elif button == Qt.RightButton:
            self.color_preview.setSecondaryIndex(index)
            self.color_preview.setSecondaryColor(color)

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
        self.color_palette = ColorPalette(self)
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
        self.data = data
        self.data.spr_col_pal_renamed.connect(self.renamePalette)
        self.data.spr_col_pal_added.connect(self.addPalette)
        self.data.spr_col_pal_removed.connect(self.removePalette)
        self.color_palette.setup(self.data)
        self.color_palette_list.currentIndexChanged.connect(self.setColorPalette)
        self.color_palette_list.setEnabled(True)
        self.color_palette.setEnabled(True)
        self.add_palette.setEnabled(True)
        self.remove_palette.setEnabled(True)
        self.rename_palette.setEnabled(True)
        for name, palette in self.data.sprite_color_palettes.items():
            self.color_palette_list.addItem(name)

    def addPaletteReq(self, event=None):
        name, accepted = QInputDialog.getText(self, "Add", "Palette name:", QLineEdit.Normal, "New palette")
        if accepted:
            self.data.addSprColPal(name)

    def removePaletteReq(self, event=None):
        if self.color_palette_list.count() == 1:
            QMessageBox(QMessageBox.Critical, "Error", "There must be at least one sprite color palette in the project").exec()
        else:
            name = self.color_palette_list.currentText()
            self.data.remSprColPal(name)

    def renamePaletteReq(self, event=None):
        cur_name = self.color_palette_list.currentText()
        new_name, accepted = QInputDialog.getText(self, "Rename", "Palette name:", QLineEdit.Normal, cur_name)
        if accepted:
            self.data.setSprColPalName(cur_name, new_name)

    def addPalette(self, name, index):
        if name != None:
            self.color_palette_list.insertItem(index, name)
            self.color_palette_list.setCurrentIndex(index)
            self.color_palette.current_palette = name
        else:
            QMessageBox(QMessageBox.Critical, "Error", "Palette with that name already exists").exec()
            self.addPaletteReq()

    def removePalette(self, name):
        if name != None:
            index = self.color_palette_list.findText(name)
            self.color_palette_list.removeItem(index)
            name = self.color_palette_list.currentText()
            self.color_palette.current_palette = name
        else:
            QMessageBox(QMessageBox.Critical, "Error", "Unable to remove palette {}".format(name)).exec()

    def renamePalette(self, cur_name, new_name):
        if cur_name != new_name:
            self.color_palette_list.setItemText(self.color_palette_list.findText(cur_name), new_name)
            self.color_palette.current_palette = new_name
        else:
            QMessageBox(QMessageBox.Critical, "Error", "Palette with that name already exists").exec()
            self.renamePaletteReq()

    pyqtSlot(str)
    def verifyCurrentPalette(self, name):
        self.color_palette_list.setCurrentIndex(self.color_palette_list.findText(name))
        self.palette_updated.emit(name)

    def setColorPalette(self, index):
        self.color_palette.setPalette(self.color_palette_list.currentText())

    def closeEvent(self, event):
        event.ignore()