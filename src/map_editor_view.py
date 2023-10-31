from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage
from tools.map_base_tool import MapToolType
from base_editor_view import BaseEditorView

class MapEditorView(BaseEditorView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_tool_type(MapToolType)

    @pyqtSlot(QImage)
    def set_tool_tiles(self, color, color_index):
        for tool in self.tools.values():
            tool.set_color(color, color_index)
