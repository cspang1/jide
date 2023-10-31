from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from tools.asset_base_tool import AssetToolType
from base_editor_view import BaseEditorView

class AssetEditorView(BaseEditorView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_tool_type(AssetToolType)

    @pyqtSlot(QColor, int)
    def set_tool_color(self, color, color_index):
        for tool in self.tools.values():
            tool.set_color(color, color_index)
