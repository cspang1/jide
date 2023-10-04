from math import floor
from PyQt5 import QtGui
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot, 
    QRegExp,
    QEvent, 
    QRect,
    QPoint
) 
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy
)
from PyQt5.QtGui import (
    QColor,
    QValidator,
    QPixmap,
    QFont,
    QRegExpValidator,
    QPainter,
    QPen,
    QImage
)

class PixelPaletteGrid(QWidget):

    # primary_color_selected = pyqtSignal(QColor, int)
    # secondary_color_selected = pyqtSignal(QColor, int)
    # primary_color_changed = pyqtSignal(QColor, int)
    # color_previewed = pyqtSignal(QColor, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid_cell_size = 8
        self.selection_start = None  # Start position of the selection box
        self.selection_end = None    # End position of the selection box
        self.palette = QImage()
        self.scaled_image = QImage()
        self.aspect_ratio = 0.0

    def set_pixel_palette(self, pixel_palette_data):
        self.palette = pixel_palette_data
        self.aspect_ratio = self.palette.width() / self.palette.height()
        initial_width = self.width()
        self.setMinimumHeight(floor(initial_width / self.aspect_ratio))
        print(self.height())
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Calculate the scale factor to fit the image into the widget
        scale_factor_x = self.width() / self.palette.width()
        scale_factor_y = self.height() / self.palette.height()
        scale_factor = min(scale_factor_x, scale_factor_y)

        # Calculate the position to center the image
        palette_x = floor((self.width() - scale_factor * self.palette.width()) / 2)
        palette_y = 0

        # Scale and draw the image
        self.scaled_image = self.palette.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        painter.drawImage(palette_x, palette_y, self.scaled_image)

        for row in range(0, self.palette.height(), self.grid_cell_size):
            y_grid = floor(palette_y + row * scale_factor)
            self.grid_height = floor(self.grid_cell_size * scale_factor)
            for col in range(0, self.palette.width(), self.grid_cell_size):
                x_grid = floor(palette_x + col * scale_factor)
                grid_width = floor(self.grid_cell_size * scale_factor)
                painter.drawRect(x_grid, y_grid, grid_width, self.grid_height)


        # Draw red outline for the selection box
        if self.selection_start and self.selection_end:
            red_pen = QPen()
            red_pen.setColor(QColor(255, 0, 0))  # Red color for outline
            red_pen.setWidth(6)  # Adjust the outline width as needed
            painter.setPen(red_pen)

            x1 = (self.selection_start.x() // 8) * 8
            y1 = (self.selection_start.y() // 8) * 8
            x2 = (self.selection_end.x() // 8) * 8
            y2 = (self.selection_end.y() // 8) * 8

            x = min(x1, x2) * self.grid_cell_size
            y = min(y1, y2) * self.grid_cell_size
            width = (abs(x2 - x1) + 1) * self.grid_cell_size
            height = (abs(y2 - y1) + 1) * self.grid_cell_size

            painter.drawRect(x, y, width, height)

    def mousePressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.button() == Qt.LeftButton:
            # Calculate the starting position of the selection box
            cell_x = event.pos().x() // self.grid_cell_size
            cell_y = event.pos().y() // self.grid_cell_size
            self.selection_start = QPoint(cell_x, cell_y)
            self.selection_end = QPoint(cell_x, cell_y)
            self.update()  # Update the widget to redraw the selection

    def mouseMoveEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.buttons() == Qt.LeftButton:
            # Calculate the current position of the selection box while dragging
            cell_x = event.pos().x() // self.grid_cell_size
            cell_y = event.pos().y() // self.grid_cell_size
            self.selection_end = QPoint(cell_x, cell_y)
            self.update()  # Update the widget to redraw the selection

    def resizeEvent(self, event):
        self.setMinimumHeight(floor(self.width() / self.aspect_ratio))



    # def set_color(self, color, index):
    #     self.palette[index] = color
    #     self.update()

    # def paintEvent(self, event):
    #     super().paintEvent(event)
    #     painter = QPainter(self)

    #     painter.fillRect(0, 0, self.total_width, self.total_height, QColor(0, 0, 0))
    #     select_pen = QPen(QColor(255, 0, 0))
    #     select_pen.setJoinStyle(Qt.MiterJoin)
    #     select_pen.setWidth(6)
    #     trans_pen = QPen(Qt.red)
    #     trans_pen.setWidth(5)
    #     trans_pen.setCapStyle(Qt.RoundCap)

    #     selected_x = -1
    #     selected_y = -1

    #     for row_index, row in enumerate(range(self.grid_height)):
    #         for col_index, col in enumerate(range(self.grid_width)):
    #             x = col * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the left border
    #             y = row * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the top border
    #             cur_index = row_index * self.grid_width + col_index
    #             square_color = self.palette[cur_index]
    #             painter.fillRect(x, y, self.square_size, self.square_size, square_color)

    #             if cur_index == 0:
    #                 painter.setPen(trans_pen)
    #                 painter.drawLine(x + 2, y + 2, self.square_size + 2, self.square_size + 2)

    #             # Draw horizontal lines
    #             if row < self.grid_height - 1:
    #                 y_line = (row + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the top border
    #                 painter.fillRect(x, y_line, self.square_size, self.line_width, QColor(0, 0, 0))
                
    #             # Draw vertical lines
    #             if col < self.grid_width - 1:
    #                 x_line = (col + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the left border
    #                 painter.fillRect(x_line, y, self.line_width, self.square_size, QColor(0, 0, 0))

    #             if (col, row) == (self.primary_cell % self.grid_width, self.primary_cell // self.grid_width):
    #                 selected_x = x
    #                 selected_y = y

    #     if selected_x > -1 and selected_y > -1:
    #         painter.setPen(select_pen)
    #         painter.drawRect(selected_x, selected_y, self.square_size, self.square_size)

    # def mouseDoubleClickEvent(self, event):
    #     if event.buttons() != Qt.LeftButton:
    #         return
        
    #     mouse_pos = event.pos()
    #     col = (mouse_pos.x() - self.line_width) // (self.square_size + self.line_width)
    #     row = (mouse_pos.y() - self.line_width) // (self.square_size + self.line_width)
    #     index = max(0, min(row * self.grid_width + col, self.grid_width * self.grid_height - 1))
    #     if index == 0:
    #         return
    #     self.open_color_picker(self.palette[index], index)

    # def mousePressEvent(self, event):
    #     # Calculate the cell index based on the mouse click position
    #     col = event.x() // (self.square_size + self.line_width)
    #     row = event.y() // (self.square_size + self.line_width)

    #     if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
    #         index = max(0, min(row * self.grid_width + col, self.grid_width * self.grid_height - 1))
    #         if event.buttons() == Qt.LeftButton:
    #             self.select_primary_color(index)
    #         elif event.buttons() == Qt.RightButton:
    #             self.select_secondary_color(index)

    # def open_color_picker(self, color, index):
    #     color_picker = ColorPickerDialog(color)
    #     color_picker.color_previewed.connect(
    #         lambda preview_color: self.preview_color(preview_color, index)
    #     )
    #     new_color = color
    #     if color_picker.exec():
    #         new_color = color_picker.get_color()
    #     self.primary_color_changed.emit(new_color, index)

    # @pyqtSlot(QColor, int)
    # def preview_color(self, color, index):
    #     self.set_color(color, index)
    #     self.color_previewed.emit(color, index)

    # def select_primary_color(self, index):
    #     self.primary_cell = index
    #     self.primary_color_selected.emit(self.palette[index], index)
    #     self.update()

    # def select_secondary_color(self, index):
    #     self.secondary_cell = index
    #     self.secondary_color_selected.emit(self.palette[index], index)
    #     self.update()

    # @pyqtSlot()
    # def swap_colors(self):
    #     temp_cell = self.primary_cell
    #     self.select_primary_color(self.secondary_cell)
    #     self.select_secondary_color(temp_cell)
