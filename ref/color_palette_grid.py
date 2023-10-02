from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRegExp, QEvent, QRect
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
    QPen
)
from color_picker_dialog import ColorPickerDialog

class ColorPaletteGrid(QWidget):

    primary_color_selected = pyqtSignal(QColor, int)
    secondary_color_selected = pyqtSignal(QColor, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_width = 4  # Number of columns
        self.grid_height = 4  # Number of rows
        self.square_size = 75  # Size of each square
        self.line_width = 1  # Width of the lines
        self.total_width = (self.grid_width + 1) * self.line_width + self.grid_width * self.square_size + 2
        self.total_height = (self.grid_height + 1) * self.line_width + self.grid_height * self.square_size + 2
        self.setFixedSize(self.total_width, self.total_height)
        self.primary_cell = None
        self.secondary_cell = None
        self.palette = [QColor(211, 211, 211)] * self.grid_width * self.grid_height

    def set_color(self, index, color):
        self.palette[index] = color
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        painter.fillRect(0, 0, self.total_width, self.total_height, QColor(0, 0, 0))
        select_pen = QPen(QColor(255, 0, 0))
        select_pen.setJoinStyle(Qt.MiterJoin)
        select_pen.setWidth(6)

        selected_x = -1
        selected_y = -1

        for row_index, row in enumerate(range(self.grid_height)):
            for col_index, col in enumerate(range(self.grid_width)):
                x = col * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the left border
                y = row * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the top border
                cur_index = row_index * self.grid_width + col_index
                square_color = self.palette[cur_index]
                painter.fillRect(x, y, self.square_size, self.square_size, square_color)

                # Draw horizontal lines
                if row < self.grid_height - 1:
                    y_line = (row + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the top border
                    painter.fillRect(x, y_line, self.square_size, self.line_width, QColor(0, 0, 0))
                
                # Draw vertical lines
                if col < self.grid_width - 1:
                    x_line = (col + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the left border
                    painter.fillRect(x_line, y, self.line_width, self.square_size, QColor(0, 0, 0))

                if (col, row) == (self.primary_cell % self.grid_width, self.primary_cell // self.grid_width):
                    selected_x = x
                    selected_y = y

        if selected_x > -1 and selected_y > -1:
            painter.setPen(select_pen)
            painter.drawRect(selected_x, selected_y, self.square_size, self.square_size)

    def mouseDoubleClickEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return
        
        mouse_pos = event.pos()
        col = (mouse_pos.x() - self.line_width) // (self.square_size + self.line_width)
        row = (mouse_pos.y() - self.line_width) // (self.square_size + self.line_width)
        index = max(0, min(row * self.grid_width + col, self.grid_width * self.grid_height - 1))
        self.open_color_picker(index, self.palette[index])

    def mousePressEvent(self, event):
        # Calculate the cell index based on the mouse click position
        col = event.x() // (self.square_size + self.line_width)
        row = event.y() // (self.square_size + self.line_width)

        if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
            index = max(0, min(row * self.grid_width + col, self.grid_width * self.grid_height - 1))
            if event.buttons() == Qt.LeftButton:
                self.select_primary_color(index)
            elif event.buttons() == Qt.RightButton:
                self.select_secondary_color(index)

    def open_color_picker(self, index, color):
        color_picker = ColorPickerDialog(color)
        if color_picker.exec():
            self.set_color(index, color_picker.get_color())

    def select_primary_color(self, index):
        self.primary_cell = index
        self.primary_color_selected.emit(self.palette[index], index)
        self.update()

    def select_secondary_color(self, index):
        self.secondary_cell = index
        self.secondary_color_selected.emit(self.palette[index], index)
        self.update()

    @pyqtSlot()
    def swap_colors(self):
        temp_cell = self.primary_cell
        self.select_primary_color(self.secondary_cell)
        self.select_secondary_color(temp_cell)
