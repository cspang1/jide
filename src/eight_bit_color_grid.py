from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRegExp, QEvent, QRect
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QFrame
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
from color_data import (
    upsample,
    downsample,
    normalize
)

class EightBitColorGrid(QWidget):

    color_selected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_width = 16  # Number of columns
        self.grid_height = 16  # Number of rows
        self.square_size = 50  # Size of each square
        self.line_width = 1  # Width of the lines
        self.total_width = (self.grid_width + 1) * self.line_width + self.grid_width * self.square_size
        self.total_height = (self.grid_height + 1) * self.line_width + self.grid_height * self.square_size
        parent.setMinimumSize(self.total_width, self.total_height)
        parent.setFixedSize(self.total_width, self.total_height)
        self.selected_cell = None

        self.palette = [
            QColor(*upsample(red, green, blue))
            for blue in range(4)
            for red in range(8)
            for green in range(8)
        ]

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        painter.fillRect(1, 1, self.total_width, self.total_height, QColor(0, 0, 0))
        select_pen = QPen(QColor(255, 0, 0))
        select_pen.setJoinStyle(Qt.MiterJoin)
        select_pen.setWidth(6)

        selected_x = -1
        selected_y = -1

        for row_index, row in enumerate(range(self.grid_height)):
            for col_index, col in enumerate(range(self.grid_width)):
                x = col * (self.square_size + self.line_width) + self.line_width  # Add 1 for the left border
                y = row * (self.square_size + self.line_width) + self.line_width  # Add 1 for the top border
                cur_index = row_index * self.grid_width + col_index
                square_color = self.palette[cur_index]
                painter.fillRect(x, y, self.square_size, self.square_size, square_color)

                # Draw horizontal lines
                if row < self.grid_height - 1:
                    y_line = (row + 1) * (self.square_size + self.line_width)  # Add 1 for the top border
                    painter.fillRect(x, y_line, self.square_size, self.line_width, QColor(0, 0, 0))

                # Draw vertical lines
                if col < self.grid_width - 1:
                    x_line = (col + 1) * (self.square_size + self.line_width)  # Add 1 for the left border
                    painter.fillRect(x_line, y, self.line_width, self.square_size, QColor(0, 0, 0))

                if (col, row) == self.selected_cell:
                    selected_x = x
                    selected_y = y

        if selected_x > -1 and selected_y > -1:
            painter.setPen(select_pen)
            painter.drawRect(selected_x, selected_y, self.square_size, self.square_size)

    def mousePressEvent(self, event):
        # Calculate the cell index based on the mouse click position
        col = event.x() // (self.square_size + self.line_width)
        row = event.y() // (self.square_size + self.line_width)
        
        if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
            index = max(0, min(row * self.grid_width + col, self.grid_width * self.grid_height - 1))
            self.select_color(self.palette[index])

    def select_color(self, color):
        for index, palette_color in enumerate(self.palette):
            if palette_color.rgb() == color.rgb():
                self.selected_cell = (index % self.grid_width, index // self.grid_width)
                self.color_selected.emit(self.palette[index])
                self.update()
                return
