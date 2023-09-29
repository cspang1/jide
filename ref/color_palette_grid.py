from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRegExp, QEvent
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

class ColorPaletteGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_width = 4  # Number of columns
        self.grid_height = 4  # Number of rows
        self.square_size = 75  # Size of each square
        self.line_width = 1  # Width of the lines
        self.total_width = (self.grid_width + 1) * self.line_width + self.grid_width * self.square_size + 2
        self.total_height = (self.grid_height + 1) * self.line_width + self.grid_height * self.square_size + 2
        self.setFixedSize(self.total_width, self.total_height)
        self.palette = [QColor(211, 211, 211)] * self.grid_width * self.grid_height

    def update_palette(self, color_data):
        self.palette = color_data
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        painter.fillRect(0, 0, self.total_width, self.total_height, QColor(0, 0, 0))

        for row_index, row in enumerate(range(self.grid_height)):
            for col_index, col in enumerate(range(self.grid_width)):
                x = col * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the left border
                y = row * (self.square_size + self.line_width) + self.line_width + 1  # Add 1 for the top border
                square_color = self.palette[row_index * self.grid_width + col_index]
                painter.fillRect(x, y, self.square_size, self.square_size, square_color)
                
                # Draw horizontal lines
                if row < self.grid_height - 1:
                    y_line = (row + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the top border
                    painter.fillRect(x, y_line, self.square_size, self.line_width, QColor(0, 0, 0))
                
                # Draw vertical lines
                if col < self.grid_width - 1:
                    x_line = (col + 1) * (self.square_size + self.line_width) + 1  # Add 1 for the left border
                    painter.fillRect(x_line, y, self.line_width, self.square_size, QColor(0, 0, 0))

