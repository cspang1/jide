from PyQt5 import QtGui
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot, 
    QRegExp,
    QEvent, 
    QRect,
    QPoint,
    QSize
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

    elements_selected = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid_cell_size = 8
        self.palette = QImage()
        self.aspect_ratio = 0.0
        self.scale_factor = 0.0
        self.select_start = QPoint()
        self.select_end = QPoint()
        self.selection = QRect()

        self.setMouseTracking(True)  # Enable mouse tracking

    def set_pixel_palette(self, pixel_palette_data):
        self.palette = pixel_palette_data
        self.aspect_ratio = self.palette.width() / self.palette.height()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Calculate the scale factor to fit the image into the widget
        scale_factor_x = self.width() / self.palette.width()
        scale_factor_y = self.height() / self.palette.height()
        self.scale_factor = min(scale_factor_x, scale_factor_y)

        # Calculate the position to center the image
        palette_x = round((self.width() - self.scale_factor * self.palette.width()) / 2)
        palette_y = 0

        # Scale and draw the image
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
            select_start_coordinates = QPoint(
                self.calculate_grid_coords(self.select_start.x()),
                self.calculate_grid_coords(self.select_start.y())
            )
            select_end_coordinates = QPoint(
                self.constrain_coords(
                    self.calculate_grid_coords(self.select_end.x()),
                    self.width(),
                    0
                ),
                self.constrain_coords(
                    self.calculate_grid_coords(self.select_end.y()),
                    self.height(),
                    0
                )
            )
            if select_start_coordinates.x() <= select_end_coordinates.x():
                select_end_coordinates.setX(select_end_coordinates.x() + round(self.grid_cell_size * self.scale_factor))
            if select_start_coordinates.y() <= select_end_coordinates.y():
                select_end_coordinates.setY(select_end_coordinates.y() + round(self.grid_cell_size * self.scale_factor))
            selection_pen = QPen(Qt.red)
            selection_pen.setWidth(6)
            painter.setPen(selection_pen)  # Red outline
            painter.drawRect(
                QRect(
                    select_start_coordinates,
                    select_end_coordinates
                )
            )

    def resizeEvent(self, event):
        self.setMinimumHeight(round(self.width() / self.aspect_ratio))

    def mousePressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.buttons() == Qt.LeftButton:
            self.select_start = event.pos()
            self.select_end = event.pos()
            self.calculate_selection(self.select_start, self.select_end)
            self.update()

    def mouseMoveEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.buttons() == Qt.LeftButton:
            self.select_end = event.pos()
            self.calculate_selection(self.select_start, self.select_end)
            self.update()

    def calculate_selection(self, start_point, end_point):
        self.selection = QRect(
            QPoint(
                round(
                    max(
                        0,
                        min(
                            start_point.x() // (self.grid_cell_size * self.scale_factor),
                            (self.width() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)
                        )
                    )
                ),
                round(
                    max(
                        0,
                        min(
                            start_point.y() // (self.grid_cell_size * self.scale_factor),
                            (self.height() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)
                        )
                    )
                )
            ),
            QPoint(
                round(
                    max(
                        0,
                        min(
                            end_point.x() // (self.grid_cell_size * self.scale_factor),
                            (self.width() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)
                        )
                    )
                ),
                round(
                    max(
                        0,
                        min(
                            end_point.y() // (self.grid_cell_size * self.scale_factor),
                            (self.height() - self.grid_cell_size * self.scale_factor) // (self.grid_cell_size * self.scale_factor)
                        )
                    )
                )
            )
        )

        self.elements_selected.emit(self.selection)

    def calculate_grid_coords(self, mouse_pos):
        return round(
            (mouse_pos // (self.grid_cell_size * self.scale_factor)) * self.grid_cell_size * self.scale_factor
        )

    def constrain_coords(self, coords, upper_limit, lower_limit):
        return max(lower_limit, min(coords, upper_limit - round(self.grid_cell_size * self.scale_factor)))
