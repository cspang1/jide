import copy
import json
from pathlib import Path
from PyQt5.QtCore import (
    QSettings,
    QCoreApplication,
    pyqtSlot,
    QRect
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QActionGroup
)
from views.main_window_ui import Ui_main_window
from preferences_dialog import PreferencesDialog
from models.pixel_data import (
    PixelData,
    cmd_add_pixel_palette_row,
    cmd_remove_pixel_palette_row,
    cmd_set_asset_name,
    cmd_set_pixels
)
from models.color_data import (
    ColorData,
    cmd_add_color_palette,
    cmd_remove_color_palette,
    cmd_rename_color_palette,
    cmd_set_color,
)
from models.tile_map_data import (
    TileMapData,
    cmd_add_tile_map,
    cmd_remove_tile_map,
    cmd_rename_tile_map
)
from pixel_palette import PixelPalette
from color_palette import ColorPalette
from asset_editor_scene import AssetEditorScene
from map_editor_scene import (
    MapEditorScene,
    RenderedTile
)
from tools.asset_base_tool import AssetToolType
from models.undo_stack import UndoStack

class Jide(QMainWindow, Ui_main_window):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_window()
        self.init_models()
        self.init_ui()
        self.setup_editor()
        self.prefs = QSettings()
        QCoreApplication.setOrganizationName("Connor Spangler")
        QCoreApplication.setOrganizationDomain("https://github.com/cspang1")
        QCoreApplication.setApplicationName("JIDE")
        QApplication.processEvents()

        self.load_project("./data/demo.jrf")

    def setup_window(self):
        self.tile_map_picker_dock.hide()
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()

        self.tool_actions = QActionGroup(self)
        self.tool_actions.addAction(self.action_select_tool)
        self.tool_actions.addAction(self.action_pen_tool)
        self.tool_actions.addAction(self.action_fill_tool)
        self.tool_actions.addAction(self.action_line_tool)
        self.tool_actions.addAction(self.action_rectangle_tool)
        self.tool_actions.addAction(self.action_ellipse_tool)

        self.undo_stack = UndoStack(self)
        action_undo = self.undo_stack.createUndoAction(self, "&Undo")
        action_undo.setShortcut(QKeySequence.Undo)
        action_redo = self.undo_stack.createRedoAction(self, "&Redo")
        action_redo.setShortcut(QKeySequence.Redo)
        self.menu_edit.addActions([action_undo, action_redo])

        self.action_new.triggered.connect(self.new_project)
        self.action_save.triggered.connect(self.save_project)
        self.action_open.triggered.connect(self.select_file)
        self.action_close.triggered.connect(self.close_project)
        self.action_exit.triggered.connect(self.quit_application)
        self.action_preferences.triggered.connect(self.open_preferences)
        self.action_gen_dat_files.triggered.connect(lambda temp: print("this will generate .DAT files"))
        self.action_load_jcap_system.triggered.connect(lambda temp: print("this will load the JCAP system"))

        self.editor_tabs.currentChanged.connect(self.select_tab)

    def init_models(self):
        self.sprite_color_data = ColorData()
        self.tile_color_data = ColorData()
        self.sprite_pixel_data = PixelData()
        self.tile_pixel_data = PixelData()
        self.tile_map_data = TileMapData()

        self.undo_stack.error_thrown.connect(self.show_error_dialog)

        self.sprite_color_palette.color_set.connect(
            lambda update_color, update_index:
            self.undo_stack.push(
                cmd_set_color(
                    self.sprite_color_data,
                    self.sprite_color_palette.color_palette_name_combo.currentText(),
                    update_color,
                    update_index
                )
            )
        )
        self.tile_color_palette.color_set.connect(
            lambda update_color, update_index:
            self.undo_stack.push(
                cmd_set_color(
                    self.tile_color_data,
                    self.tile_color_palette.color_palette_name_combo.currentText(),
                    update_color,
                    update_index
                )
            )
        )

        self.sprite_color_palette.color_palette_renamed.connect(
            lambda old_palette_name, new_palette_name:
            self.undo_stack.push(
                cmd_rename_color_palette(
                    self.sprite_color_data,
                    old_palette_name,
                    new_palette_name
                )
            )
        )
        self.tile_color_palette.color_palette_renamed.connect(
            lambda old_palette_name, new_palette_name:
            self.undo_stack.push(
                cmd_rename_color_palette(
                    self.tile_color_data,
                    old_palette_name,
                    new_palette_name
                )
            )
        )

        self.sprite_color_palette.color_palette_added.connect(
            lambda palette_name: 
            self.undo_stack.push(
                cmd_add_color_palette(
                    self.sprite_color_data,
                    palette_name
                )
            )
        )
        self.tile_color_palette.color_palette_added.connect(
            lambda palette_name: 
            self.undo_stack.push(
                cmd_add_color_palette(
                    self.tile_color_data,
                    palette_name
                )
            )
        )

        self.sprite_color_palette.color_palette_removed.connect(
            lambda palette_name: 
            self.undo_stack.push(
                cmd_remove_color_palette(
                    self.sprite_color_data,
                    palette_name
                )
            )
        )
        self.tile_color_palette.color_palette_removed.connect(
            lambda palette_name: 
            self.undo_stack.push(
                cmd_remove_color_palette(
                    self.tile_color_data,
                    palette_name
                )
            )
        )

        self.sprite_pixel_palette.add_palette_row.connect(
            lambda: 
            self.undo_stack.push(
                cmd_add_pixel_palette_row(
                    self.sprite_pixel_data
                )
            )
        )
        self.tile_pixel_palette.add_palette_row.connect(
            lambda: 
            self.undo_stack.push(
                cmd_add_pixel_palette_row(
                    self.tile_pixel_data
                )
            )
        )

        self.sprite_pixel_palette.remove_palette_row.connect(
            lambda: 
            self.undo_stack.push(
                cmd_remove_pixel_palette_row(
                    self.sprite_pixel_data
                )
            )
        )
        self.tile_pixel_palette.remove_palette_row.connect(
            lambda: 
            self.undo_stack.push(
                cmd_remove_pixel_palette_row(
                    self.tile_pixel_data
                )
            )
        )

        self.sprite_pixel_palette.asset_renamed.connect(
            lambda asset_index, new_asset_name:
            self.undo_stack.push(
                cmd_set_asset_name(
                    self.sprite_pixel_data,
                    asset_index,
                    new_asset_name
                )
            )
        )
        self.tile_pixel_palette.asset_renamed.connect(
            lambda asset_index, new_asset_name:
            self.undo_stack.push(
                cmd_set_asset_name(
                    self.tile_pixel_data,
                    asset_index,
                    new_asset_name
                )
            )
        )

        self.sprite_editor_view.scene_edited.connect(
            lambda new_pixels:
            self.undo_stack.push(
                cmd_set_pixels(
                    self.sprite_pixel_data,
                    new_pixels,
                    self.sprite_pixel_palette.get_selection()
                )
            )
        )
        self.tile_editor_view.scene_edited.connect(
            lambda new_pixels:
            self.undo_stack.push(
                cmd_set_pixels(
                    self.tile_pixel_data,
                    new_pixels,
                    self.tile_pixel_palette.get_selection(),
                )
            )
        )

        self.tile_map_picker.tile_map_added.connect(
            lambda tile_map_name:
            self.undo_stack.push(
                cmd_add_tile_map(
                    self.tile_map_data,
                    tile_map_name
                )
            )
        )
        self.tile_map_picker.tile_map_removed.connect(
            lambda tile_map_name:
            self.undo_stack.push(
                cmd_remove_tile_map(
                    self.tile_map_data,
                    tile_map_name
                )
            )
        )
        self.tile_map_picker.tile_map_renamed.connect(
            lambda old_tile_map_name, new_tile_map_name:
            self.undo_stack.push(
                cmd_rename_tile_map(
                    self.tile_map_data,
                    old_tile_map_name,
                    new_tile_map_name
                )
            )
        )

    def init_ui(self):
        self.sprite_color_palette.set_transparency(True)
        self.tile_color_palette.set_transparency(False)

        self.sprite_color_palette.color_palette_changed.connect(
            lambda palette_name: self.sprite_color_palette.change_palette(
                self.sprite_color_data.get_color_palette(palette_name)
            )
        )
        self.sprite_color_palette.color_palette_changed.connect(
            lambda palette_name: self.sprite_pixel_palette.set_color_table(
                self.sprite_color_data.get_color_palette(palette_name)
            )
        )
        self.tile_color_palette.color_palette_changed.connect(
            lambda palette_name: self.tile_color_palette.change_palette(
                self.tile_color_data.get_color_palette(palette_name)
            )
        )
        self.tile_color_palette.color_palette_changed.connect(
            lambda palette_name: self.tile_pixel_palette.set_color_table(
                self.tile_color_data.get_color_palette(palette_name)
            )
        )

        self.sprite_color_palette.color_previewed.connect(self.sprite_pixel_palette.set_color)
        self.tile_color_palette.color_previewed.connect(self.tile_pixel_palette.set_color)

        self.sprite_color_data.color_palette_added.connect(self.sprite_color_palette.add_color_palette)
        self.sprite_color_data.color_palette_removed.connect(self.sprite_color_palette.remove_color_palette)
        self.tile_color_data.color_palette_added.connect(self.tile_color_palette.add_color_palette)
        self.tile_color_data.color_palette_removed.connect(self.tile_color_palette.remove_color_palette)
        self.sprite_color_data.color_palette_renamed.connect(self.sprite_color_palette.rename_color_palette)
        self.tile_color_data.color_palette_renamed.connect(self.tile_color_palette.rename_color_palette)

        self.tile_map_data.tile_map_added.connect(self.tile_map_picker.add_tile_map)
        self.tile_map_data.tile_map_removed.connect(self.tile_map_picker.remove_tile_map)
        self.tile_map_data.tile_map_renamed.connect(self.tile_map_picker.rename_tile_map)

        self.sprite_color_data.color_updated.connect(self.sprite_color_palette.update_color)
        self.tile_color_data.color_updated.connect(self.tile_color_palette.update_color)
        self.sprite_color_data.color_updated.connect(
            lambda _, color, index: self.sprite_pixel_palette.set_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index: self.tile_pixel_palette.set_color(color, index)
        )
        self.sprite_color_data.color_updated.connect(
            lambda _, color, index: self.sprite_color_palette.color_preview.set_primary_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index: self.tile_color_palette.color_preview.set_primary_color(color, index)
        )
        self.sprite_color_data.color_updated.connect(
            lambda _, _color, index: self.sprite_color_palette.color_palette_grid.select_primary_color(index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, _color, index: self.tile_color_palette.color_palette_grid.select_primary_color(index)
        )

        self.sprite_pixel_data.data_updated.connect(
            lambda: self.sprite_pixel_palette.set_pixel_palette(self.sprite_pixel_data.get_image())
        )
        self.tile_pixel_data.data_updated.connect(
            lambda: self.tile_pixel_palette.set_pixel_palette(self.tile_pixel_data.get_image())
        )

    def setup_editor(self):
        self.sprite_scene = AssetEditorScene()
        self.tile_scene = AssetEditorScene()
        self.tile_map_scene = MapEditorScene()
        self.sprite_editor_view.setScene(self.sprite_scene)
        self.tile_editor_view.setScene(self.tile_scene)
        self.map_editor_view.setScene(self.tile_map_scene)

        self.action_select_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.SELECT)
        )
        self.action_select_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.SELECT)
        )
        self.action_pen_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.PEN)
        )
        self.action_pen_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.PEN)
        )
        self.action_line_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.LINE)
        )
        self.action_line_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.LINE)
        )
        self.action_rectangle_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.RECTANGLE)
        )
        self.action_rectangle_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.RECTANGLE)
        )
        self.action_ellipse_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.ELLIPSE)
        )
        self.action_ellipse_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.ELLIPSE)
        )
        self.action_fill_tool.triggered.connect(
            lambda: self.sprite_editor_view.set_tool(AssetToolType.FILL)
        )
        self.action_fill_tool.triggered.connect(
            lambda: self.tile_editor_view.set_tool(AssetToolType.FILL)
        )
        self.action_select_tool.trigger()

        self.action_copy.triggered.connect(self.get_active_view().copy)
        self.action_paste.triggered.connect(self.get_active_view().paste)

        #TODO: TEMPORARY
        self.sprite_editor_view.selection_made.connect(
            lambda enabled: self.action_copy.setEnabled(enabled)
        )
        self.sprite_editor_view.selection_copied.connect(
            lambda: self.action_paste.setEnabled(True)
        )

        self.sprite_color_palette.color_selected.connect(self.sprite_editor_view.set_tool_color)
        self.tile_color_palette.color_selected.connect(self.tile_editor_view.set_tool_color)

        self.sprite_pixel_data.data_updated.connect(
            lambda: self.sprite_scene.set_image(self.sprite_pixel_data.get_image())
        )
        self.tile_pixel_data.data_updated.connect(
            lambda: self.tile_scene.set_image(self.tile_pixel_data.get_image())
        )

        self.sprite_color_palette.color_previewed.connect(self.sprite_scene.set_color)
        self.sprite_pixel_palette.assets_selected.connect(self.sprite_scene.select_cells)
        self.tile_color_palette.color_previewed.connect(self.tile_scene.set_color)
        self.tile_pixel_palette.assets_selected.connect(self.tile_scene.select_cells)
        self.tile_color_palette.color_previewed.connect(
            lambda color, index:
            self.tile_map_scene.set_color(
                self.tile_color_palette.color_palette_name_combo.currentText(),
                color,
                index
            )
        )
        # This will determine what tiles will be placed with the place tile tool
        # self.tile_pixel_palette.assets_selected.connect(
        #     self.tile_map_scene.select_cells
        # )

        self.sprite_pixel_palette.assets_selected.connect(
            lambda _: self.sprite_editor_view.clear_selection()
        )
        self.tile_pixel_palette.assets_selected.connect(
            lambda _: self.tile_editor_view.clear_selection()
        )

        self.sprite_color_data.color_updated.connect(
            lambda _, color, index: self.sprite_scene.set_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index:  self.tile_scene.set_color(color, index)
        )
        self.tile_color_data.color_updated.connect(self.tile_map_scene.set_color)

        self.sprite_color_palette.color_palette_changed.connect(
            lambda palette_name: self.sprite_scene.set_color_table(
                self.sprite_color_data.get_color_palette(palette_name)
            )
        )
        self.tile_color_palette.color_palette_changed.connect(
            lambda palette_name: self.tile_scene.set_color_table(
                self.tile_color_data.get_color_palette(palette_name)
            )
        )
        # This will determine what color palette newly placed tiles will use
        # self.tile_color_palette.color_palette_changed.connect(
        #     lambda palette_name: self.tile_map_scene.set_color_table(
        #         self.tile_color_data.get_color_palette(palette_name)
        #     )
        # )

        self.tile_map_picker.tile_map_changed.connect(
            lambda tile_map_name: self.tile_map_scene.set_tile_map(
                RenderedTile.render_tile_map(
                    self.tile_map_data.get_tile_map(tile_map_name),
                    self.tile_color_data,
                    self.tile_pixel_data
                )
            )
        )

    def load_project(self, file_name):
        if not file_name:
            return

        self.project_file = file_name
        project_data = None
        try:
            with open(self.project_file, "r") as project_file:
                project_data = json.load(project_file)

        except OSError:
            self.show_error_dialog("Unable to open project file")
            return
        except KeyError:
            self.show_error_dialog("Unable to load project due to malformed data")
            return

        self.populate_models(project_data)
        self.enable_ui()

        self.editor_tabs.setCurrentIndex(0)

    def populate_models(self, project_data):
        for palette in ColorData.parse_color_data(project_data["sprite_color_palettes"]):
            self.sprite_color_data.add_color_palette(*palette)
        for palette in ColorData.parse_color_data(project_data["tile_color_palettes"]):
            self.tile_color_data.add_color_palette(*palette)
        sprite_data = PixelData.parse_pixel_data(project_data["sprites"])
        tile_data = PixelData.parse_pixel_data(project_data["tiles"])
        self.sprite_pixel_data.set_image(*sprite_data[:3])
        self.sprite_pixel_data.set_asset_names(sprite_data[-1])
        self.tile_pixel_data.set_image(*tile_data[:3])
        self.tile_pixel_data.set_asset_names(tile_data[-1])

        for tile_map in project_data["tile_maps"]:
            self.tile_map_data.add_tile_map(
                tile_map["name"],
                tile_map["width"],
                tile_map["height"],
                tile_map["contents"]
            )

        self.sprite_pixel_palette.pixel_palette_grid.set_asset_names(self.sprite_pixel_data.get_names())
        self.tile_pixel_palette.pixel_palette_grid.set_asset_names(self.tile_pixel_data.get_names())

        self.sprite_pixel_palette.set_pixel_palette(self.sprite_pixel_data.get_image())
        self.tile_pixel_palette.set_pixel_palette(self.tile_pixel_data.get_image())

        self.sprite_pixel_palette.set_selection(QRect(0, 0, 1, 1))
        self.tile_pixel_palette.set_selection(QRect(0, 0, 1, 1))

        self.sprite_pixel_data.set_color_table(
            [color.rgba() for color in self.sprite_color_data.get_color_palette(
                self.sprite_color_palette.get_current_palette_name()
            )]
        )
        self.tile_pixel_data.set_color_table(
            [color.rgba() for color in self.tile_color_data.get_color_palette(
                self.tile_color_palette.get_current_palette_name()
            )]
        )

        # self.sprite_color_palette.color_palette_engaged.connect(
        #     lambda: self.editor_tabs.setCurrentIndex(0)
        # )
        # self.tile_color_palette.color_palette_engaged.connect(
        #     lambda: self.editor_tabs.setCurrentIndex(1)
        # )
        # self.sprite_pixel_palette.pixel_palette_engaged.connect(
        #     lambda: self.editor_tabs.setCurrentIndex(0)
        # )
        # self.tile_pixel_palette.pixel_palette_engaged.connect(
        #     lambda: self.editor_tabs.setCurrentIndex(1)
        # )

        self.sprite_pixel_data.name_updated.connect(
            self.sprite_pixel_palette.set_asset_name
        )
        self.tile_pixel_data.name_updated.connect(
            self.tile_pixel_palette.set_asset_name
        )

        self.sprite_color_palette.color_palette_name_combo.setCurrentIndex(0)
        self.tile_color_palette.color_palette_name_combo.setCurrentIndex(0)
        self.tile_map_picker.tile_map_name_combo.setCurrentIndex(0)

    def enable_ui(self):
        self.tool_bar.setEnabled(True)
        self.editor_tabs.setEnabled(True)
        self.action_save.setEnabled(True)
        self.action_close.setEnabled(True)
        self.action_gen_dat_files.setEnabled(True)
        self.action_load_jcap_system.setEnabled(True)
        self.sprite_color_palette.setEnabled(True)
        self.tile_color_palette.setEnabled(True)
        self.sprite_pixel_palette.setEnabled(True)
        self.tile_pixel_palette.setEnabled(True)
        self.tile_map_picker.setEnabled(True)

    def select_tab(self, index):
        dock_visibility = {
            0: (True, True, False, False, False),
            1: (False, False, False, True, True),
            2: (False, False, True, True, True)
        }

        self.sprite_color_palette_dock.setVisible(dock_visibility[index][0])
        self.sprite_pixel_palette_dock.setVisible(dock_visibility[index][1])
        self.tile_map_picker_dock.setVisible(dock_visibility[index][2])
        self.tile_color_palette_dock.setVisible(dock_visibility[index][3])
        self.tile_pixel_palette_dock.setVisible(dock_visibility[index][4])

    def get_active_view(self):
        views = [self.sprite_editor_view, self.tile_editor_view, self.map_editor_view]
        return views[self.editor_tabs.currentIndex()]

    def select_file(self):
        if not self.check_unsaved_changes():
            return

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            str(Path(__file__)),
            "JCAP Resource File (*.jrf)",
        )
        self.load_project(file_name)

    def open_preferences(self):
        prefs = QSettings()
        cpu_port = None
        gpu_port = None
        jcap_path = None
        prefs.beginGroup("ports")
        if prefs.contains("cpu_port"):
            cpu_port = prefs.value("cpu_port")
        if prefs.contains("gpu_port"):
            gpu_port = prefs.value("gpu_port")
        prefs.endGroup()
        prefs.beginGroup("paths")
        if prefs.contains("jcap_path"):
            jcap_path = prefs.value("jcap_path")
        prefs.endGroup()

        prefs_dialog = PreferencesDialog(cpu_port, gpu_port, jcap_path)
        valid_prefs = False
        while not valid_prefs:
            if prefs_dialog.exec():
                cpu_port = prefs_dialog.get_cpu_port()
                gpu_port = prefs_dialog.get_gpu_port()
                jcap_path = prefs_dialog.get_jcap_path()
            if cpu_port and gpu_port and cpu_port == gpu_port:
                self.show_error_dialog("CPU and GPU COM ports must be different")
            else:
                valid_prefs = True

        prefs.beginGroup("ports")
        prefs.setValue("cpu_port", cpu_port)
        prefs.setValue("gpu_port", gpu_port)
        prefs.endGroup()
        prefs.beginGroup("paths")
        prefs.setValue("jcap_path", jcap_path)
        prefs.endGroup()

    @pyqtSlot(str)
    def show_error_dialog(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()

    @pyqtSlot()
    def new_project(self):
        self.close_project()

        sprites = []
        tiles = []
        sprite_color_palettes = []
        tile_color_palettes = []
        tile_maps = []

        blank_asset = [[0 for _ in range(8)] for _ in range(8)]
        sprite_names = ["sprite_" + str(i) for i in range(16)]
        tile_names = ["tile_" + str(i) for i in range(16)]
        blank_color_palette = [227 for _ in range(16)]
        blank_tile_map = [[0, 0] for _ in range(30 * 40)]

        sprites = [{"name": name, "contents": copy.deepcopy(blank_asset)} for name in sprite_names]
        tiles = [{"name": name, "contents": copy.deepcopy(blank_asset)} for name in tile_names]
        sprite_color_palettes = [{
            "name": "sprite_color_palette_0",
            "contents": blank_color_palette.copy()
        }]
        tile_color_palettes = [{
            "name": "tile_color_palette_0",
            "contents": blank_color_palette.copy()
        }]
        tile_maps = [{
            "name": "tile_map_0",
            "width": 40,
            "height": 30,
            "contents": copy.deepcopy(blank_tile_map)
        }]

        project_data = {
            "sprites": sprites,
            "tiles": tiles,
            "sprite_color_palettes": sprite_color_palettes,
            "tile_color_palettes": tile_color_palettes,
            "tile_maps": tile_maps
        }

        self.populate_models(project_data)
        self.enable_ui()

        self.editor_tabs.setFocus()

    @pyqtSlot()
    def save_project(self):
        if self.undo_stack.isClean():
            return

        sprites = self.sprite_pixel_data.to_json()
        tiles = self.tile_pixel_data.to_json()
        sprite_color_palettes = self.sprite_color_data.to_json()
        tile_color_palettes = self.tile_color_data.to_json()
        tile_maps = self.tile_map_data.to_json()

        project_data = {
            "sprites": sprites,
            "tiles": tiles,
            "sprite_color_palettes": sprite_color_palettes,
            "tile_color_palettes": tile_color_palettes,
            "tile_maps": tile_maps
        }

        if not self.project_file:
            self.project_file, _ = QFileDialog.getSaveFileName(
                self, 
                'Save File',
                '',
                'JCAP Resource File (*.jrf)',
                options = QFileDialog.Options() | QFileDialog.ReadOnly | QFileDialog.HideNameFilterDetails
            )

            if not self.project_file:
                return

        try:
            with open(self.project_file, "w") as project_file:
                json.dump(project_data, project_file)
            self.undo_stack.setClean()
        except (IOError, PermissionError, OSError) as e:
            self.show_error_dialog(f"Error while saving the project file: {e}")

    @pyqtSlot()
    def close_project(self):
        if not self.check_unsaved_changes():
            return

        self.tool_bar.setEnabled(False)
        self.action_save.setEnabled(False)
        self.action_close.setEnabled(False)
        self.action_gen_dat_files.setEnabled(False)
        self.action_load_jcap_system.setEnabled(False)
        self.editor_tabs.setCurrentIndex(0)
        self.editor_tabs.setEnabled(False)

        self.sprite_color_palette = ColorPalette()
        self.sprite_color_palette_dock.setWidget(self.sprite_color_palette)
        self.tile_color_palette = ColorPalette()
        self.tile_color_palette_dock.setWidget(self.tile_color_palette)
        self.sprite_pixel_palette = PixelPalette()
        self.sprite_pixel_palette_dock.setWidget(self.sprite_pixel_palette)
        self.tile_pixel_palette = PixelPalette()
        self.tile_pixel_palette_dock.setWidget(self.tile_pixel_palette)

        self.sprite_color_palette.setEnabled(False)
        self.tile_color_palette.setEnabled(False)
        self.sprite_pixel_palette.setEnabled(False)
        self.tile_pixel_palette.setEnabled(False)
        self.tile_map_picker.setEnabled(False)

        self.undo_stack.clear()
        self.project_file = None

        self.init_models()
        self.init_ui()
        self.setup_editor()

    @pyqtSlot()
    def quit_application(self):
        if not self.check_unsaved_changes():
            return
        
        self.close()

    def check_unsaved_changes(self):
        if self.undo_stack.isClean():
            return True

        save_prompt = QMessageBox()
        save_prompt.setIcon(QMessageBox.Question)
        save_prompt.setText("You have unsaved changes. Would you like to save them before closing the current project?")
        save_prompt.setWindowTitle("Save Changes?")
        save_prompt.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        # Show the QMessageBox and wait for the user's response
        response = save_prompt.exec()

        if response == QMessageBox.Cancel:
            return False

        # Check the user's response
        if response == QMessageBox.Yes:
            self.save_project()
        
        return True
