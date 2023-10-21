from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot,
    QRect,
    QPoint
) 
from PyQt5.QtWidgets import (
    QWidget,
    QToolTip,
    QInputDialog,
    QLineEdit
)
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QImage,
    QColor
)

class PixelPaletteGrid(QWidget):

    assets_selected = pyqtSignal(QRect)
    asset_renamed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid_cell_size = 8
        self.palette = QImage(0, 0, QImage.Format_Indexed8)
        self.aspect_ratio = 1.0
        self.scale_factor = 0.0
        self.select_start = QPoint()
        self.select_end = QPoint()
        self.selection = QRect()

        self.names = []

        self.setMouseTracking(True)  # Enable mouse tracking

    def set_pixel_palette(self, pixel_palette_data):
        if pixel_palette_data.height() < self.palette.height():
            self.selection = QRect(0, 0, 1, 1)
            self.update_from_selection()
        self.palette = pixel_palette_data
        self.aspect_ratio = self.palette.width() / self.palette.height()
        self.setFixedHeight(round(self.width() / self.aspect_ratio))
        self.update()

    def set_color_table(self, color_table):
        for index, color in enumerate(color_table):
            self.palette.setColor(index, color.rgb())
        self.update()

    @pyqtSlot(QColor, int)
    def set_color(self, color, index):
        self.palette.setColor(index, color.rgb())
        self.update()

    def set_asset_names(self, names):
        self.names = names

    @pyqtSlot(int, str)
    def set_asset_name(self, asset_index, new_asset_name):
        self.names[asset_index] = new_asset_name

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Calculate the scale factor to fit the image into the widget
        if self.palette.width() != 0 and self.palette.height() != 0:
            scale_factor_x = self.width() / self.palette.width()
            scale_factor_y = self.height() / self.palette.height()
            self.scale_factor = min(scale_factor_x, scale_factor_y)

        # Calculate the position to center the image
        palette_x = round((self.width() - self.scale_factor * self.palette.width()) / 2)
        palette_y = 0

        # Scale and draw the image
        if not self.palette.isNull():
            scaled_image = self.palette.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
            painter.drawImage(palette_x, palette_y, scaled_image)

        for row in range(0, self.palette.height(), self.grid_cell_size):
            y_grid = round(palette_y + row * self.scale_factor)
            self.grid_height = round(self.grid_cell_size * self.scale_factor)
            for col in range(0, self.palette.width(), self.grid_cell_size):
                x_grid = round(palette_x + col * self.scale_factor)
                grid_width = round(self.grid_cell_size * self.scale_factor)
                painter.drawRect(x_grid, y_grid, grid_width, self.grid_height)

        # Draw the selection rectangle if it's not empty
        if self.selection:
            x = round(self.selection.x() * self.scale_factor * self.grid_cell_size)
            y = round(self.selection.y() * self.scale_factor * self.grid_cell_size)
            width = round(self.selection.width() * self.scale_factor * self.grid_cell_size)
            height = round(self.selection.height() * self.scale_factor * self.grid_cell_size)
            selection_rect = QRect(x, y, width, height)
            selection_pen = QPen(Qt.red)
            selection_pen.setWidth(6)
            painter.setPen(selection_pen)  # Red outline
            painter.drawRect(selection_rect)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedHeight(int(self.width() / self.aspect_ratio))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.select_start = event.pos()
            self.select_end = event.pos()
            self.calculate_selection(self.select_start, self.select_end)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.select_end = event.pos()
            self.calculate_selection(self.select_start, self.select_end)
            self.update()

        cell_x = event.x() // (self.grid_cell_size * self.scale_factor)
        cell_y = event.y() // (self.grid_cell_size * self.scale_factor)
        asset_index = round(cell_x + cell_y * 16)
        hex_address = "0x{:02X}".format(asset_index)
        QToolTip.showText(event.globalPos(), f'{hex_address}\n{self.names[asset_index]}', self)

    def mouseDoubleClickEvent(self, event):
        cell_x = event.x() // (self.grid_cell_size * self.scale_factor)
        cell_y = event.y() // (self.grid_cell_size * self.scale_factor)
        asset_index = round(cell_x + cell_y * 16)
        old_asset_name = self.names[asset_index]

        new_asset_name, accepted = QInputDialog.getText(
            self, "Rename Asset", "Asset name:", QLineEdit.Normal, old_asset_name
        )
        if accepted:
            self.asset_renamed.emit(asset_index, new_asset_name)

    def calculate_selection(self, start_point, end_point):
        x_start = start_point.x() // (self.grid_cell_size * self.scale_factor)
        y_start = start_point.y() // (self.grid_cell_size * self.scale_factor)
        x_end = end_point.x() // (self.grid_cell_size * self.scale_factor)
        y_end = end_point.y() // (self.grid_cell_size * self.scale_factor)
        x_max = (self.width() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)
        y_max = (self.height() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)

        if x_start > x_end:
            x_start, x_end = x_end, x_start
        if y_start > y_end:
            y_start, y_end = y_end, y_start

        self.selection = QRect(
            QPoint(
                round(max(0, min(x_start, x_max))),
                round(max(0, min(y_start, y_max)))
            ),
            QPoint(
                round(max(0, min(x_end, x_max))),
                round(max(0, min(y_end, y_max)))
            )
        )

        self.update_from_selection()

    def update_from_selection(self):
        self.assets_selected.emit(self.selection)

    def set_selection(self, selection):
        self.selection = selection
        self.update_from_selection()
