from PyQt5.QtGui import QImage
from PyQt5.QtCore import (
    pyqtSignal,
    QPoint
)
from tools.asset_base_tool import AssetBaseTool

class AssetFillTool(AssetBaseTool):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.color = None
        self.color_index = None

    def mousePressEvent(self, event):
        scene = self.view.scene()
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = scene.sceneRect()
        selection_rect = self.view.get_selection()
        x_limit = selection_rect.x() if selection_rect else 0
        y_limit = selection_rect.y() if selection_rect else 0
        width_limit = selection_rect.width() + x_limit if selection_rect else scene_rect.width()
        height_limit = selection_rect.height() + y_limit if selection_rect else scene_rect.height()
        if not (x_limit <= scene_pos.x() < width_limit and y_limit <= scene_pos.y() < height_limit):
            return

        # TODO: Check if there will be no change because target color = starting pixel color

        self.image = self.view.scene().get_image(cropped=True)
        self.flood_fill(
            QPoint(
                int(scene_pos.x()),
                int(scene_pos.y())
            )
        )
        self.scene_edited.emit(self.image)

    def flood_fill(self, start_point):
        width = self.image.width()
        height = self.image.height()
        target_color = self.image.pixelIndex(start_point)
        selection_rect = self.view.get_selection()
        visited = set()

        def is_valid_point(point):
            x, y = point.x(), point.y()
            return (
                0 <= x < width and
                0 <= y < height and
                self.image.pixelIndex(point) == target_color and
                (selection_rect is None or selection_rect.contains(point))
            )

        stack = [start_point]

        while stack:
            point = stack.pop()

            if (point.x(), point.y()) not in visited:
                visited.add((point.x(), point.y()))
                self.image.setPixel(point, self.color_index)

                neighbors = [
                    QPoint(point.x(), point.y() - 1),
                    QPoint(point.x(), point.y() + 1),
                    QPoint(point.x() - 1, point.y()),
                    QPoint(point.x() + 1, point.y())
                ]

                for neighbor in neighbors:
                    if is_valid_point(neighbor):
                        stack.append(neighbor)

    def set_color(self, color, color_index):
        self.color = color
        self.color_index = color_index
