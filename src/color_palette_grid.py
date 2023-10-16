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

    color_set = pyqtSignal(QColor, int)
    primary_color_selected = pyqtSignal(QColor, int)
    secondary_color_selected = pyqtSignal(QColor, int)
    primary_color_changed = pyqtSignal(QColor, int)
    color_previewed = pyqtSignal(QColor, int)
    color_previewing = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_width = 4  # Number of columns
        self.grid_height = 4  # Number of rows
        self.square_size = 75  # Size of each square
        self.line_width = 1  # Width of the lines
        self.total_width = (self.grid_width + 1) * self.line_width + self.grid_width * self.square_size + 2
        self.total_height = (self.grid_height + 1) * self.line_width + self.grid_height * self.square_size + 2
        self.setFixedSize(self.total_width, self.total_height)
        self.primary_cell = 0
        self.secondary_cell = 0
        self.original_color = QColor()
        self.current_index = 0
        self.has_transparency = True
        self.palette = [QColor(211, 211, 211)] * self.grid_width * self.grid_height

    def set_color(self, color, index):
        self.palette[index] = color
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.fillRect(0, 0, self.total_width, self.total_height, QColor(0, 0, 0))
        select_pen = QPen(QColor(255, 0, 0))
        select_pen.setJoinStyle(Qt.MiterJoin)
        select_pen.setWidth(6)
        trans_pen = QPen(Qt.red)
        trans_pen.setWidth(5)
        trans_pen.setCapStyle(Qt.RoundCap)

        selected_x = -1
        selected_y = -1

        for row_index, row in enumerate(range(self.grid_height)):
            for col_index, col in enumerate(range(self.grid_width)):
                x = col * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the left border
                y = row * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the top border
                cur_index = row_index * self.grid_width + col_index
                square_color = self.palette[cur_index]
                painter.fillRect(x, y, self.square_size, self.square_size, square_color)

                if cur_index == 0 and self.has_transparency:
                    painter.setPen(trans_pen)
                    painter.drawLine(x + 2, y + 2, self.square_size + 2, self.square_size + 2)

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
        if index == 0 and self.has_transparency:
            return
        self.open_color_picker(self.palette[index], index)

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

    def resizeEvent(self, event):
        self.setMinimumHeight(self.width())

    def open_color_picker(self, color, index):
        self.original_color = color
        self.current_index = index
        self.color_picker = ColorPickerDialog(color)
        self.set_preview_state(self.color_picker.preview_checkbox.isChecked())
        self.color_picker.color_previewed.connect(
            lambda preview_color: self.preview_color(preview_color, index)
        )
        self.color_picker.color_previewing.connect(self.set_preview_state)
        new_color = self.original_color
        if self.color_picker.exec():
            new_color = self.color_picker.get_color()
        else:
            self.set_preview_state(False)
        
        if new_color == self.original_color:
            self.primary_color_changed.emit(new_color, index)
        else:
            self.color_set.emit(new_color, index)

    @pyqtSlot(bool)
    def set_preview_state(self, previewing):
        if previewing:
            self.preview_color(self.color_picker.get_color(), self.current_index)
        else:
            self.preview_color(self.original_color, self.current_index)

    @pyqtSlot(QColor, int)
    def preview_color(self, color, index):
        self.set_color(color, index)
        self.color_previewed.emit(color, index)

    def select_primary_color(self, index):
        self.primary_cell = index
        self.primary_color_selected.emit(self.palette[index], index)
        self.update()

    def select_secondary_color(self, index):
        self.secondary_cell = index
        self.secondary_color_selected.emit(self.palette[index], index)
        self.update()

    def set_transparency(self, has_transparency):
        self.has_transparency = has_transparency
        self.update()

    @pyqtSlot()
    def swap_colors(self):
        temp_cell = self.primary_cell
        self.select_primary_color(self.secondary_cell)
        self.select_secondary_color(temp_cell)
