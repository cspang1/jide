import json
from pathlib import Path
from PyQt5.QtCore import (
    QSettings,
    QCoreApplication,
    pyqtSlot,
    pyqtSignal,
    QRect
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QActionGroup,
    QUndoStack
)
from ui.main_window_ui import Ui_main_window
from preferences_dialog import PreferencesDialog
from pixel_data import (
    PixelData,
    parse_pixel_data,
    history_add_pixel_palette_row,
    history_remove_pixel_palette_row
)
from color_data import (
    ColorData,
    parse_color_data,
    history_set_color,
    history_rename_color_palette,
    history_add_color_palette,
    history_remove_color_palette
)
from pixel_palette import PixelPalette
from color_palette import ColorPalette
from editor_scene import EditorScene

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
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()
        self.map_color_palette_dock.hide()
        self.map_pixel_palette_dock.hide()

        self.tool_actions = QActionGroup(self)
        self.tool_actions.addAction(self.action_select_tool)
        self.tool_actions.addAction(self.action_pen_tool)
        self.tool_actions.addAction(self.action_fill_tool)
        self.tool_actions.addAction(self.action_line_tool)
        self.tool_actions.addAction(self.action_rectangle_tool)
        self.tool_actions.addAction(self.action_ellipse_tool)

        self.undo_stack = QUndoStack(self)
        action_undo = self.undo_stack.createUndoAction(self, "&Undo")
        action_undo.setShortcut(QKeySequence.Undo)
        action_redo = self.undo_stack.createRedoAction(self, "&Redo")
        action_redo.setShortcut(QKeySequence.Redo)
        self.menu_edit.addActions([action_undo, action_redo])

        self.action_new.triggered.connect(lambda temp: print("this will create a new project"))
        self.action_save.triggered.connect(lambda temp: print("this will save the current project"))
        self.action_copy.triggered.connect(lambda temp: print("this will copy the current selection"))
        self.action_paste.triggered.connect(lambda temp: print("this will paste the current selection"))
        self.action_gen_dat_files.triggered.connect(lambda temp: print("this will generate .DAT files"))
        self.action_load_jcap_system.triggered.connect(lambda temp: print("this will load the JCAP system"))
        self.action_open.triggered.connect(self.select_file)
        self.action_close.triggered.connect(self.close_project)
        self.action_exit.triggered.connect(self.quit_application)
        self.action_preferences.triggered.connect(self.open_preferences)

        self.editor_tabs.currentChanged.connect(self.select_tab)

    def init_models(self):
        self.sprite_color_data = ColorData()
        self.tile_color_data = ColorData()
        self.sprite_pixel_data = PixelData()
        self.tile_pixel_data = PixelData()

        self.sprite_color_data.error_thrown.connect(self.show_error_dialog)
        self.tile_color_data.error_thrown.connect(self.show_error_dialog)
        self.sprite_pixel_data.error_thrown.connect(self.show_error_dialog)
        self.tile_pixel_data.error_thrown.connect(self.show_error_dialog)

        self.sprite_color_palette.color_set.connect(
            lambda new_color, change_index:
            history_set_color(
                self.undo_stack,
                self.sprite_color_data,
                self.sprite_color_palette.color_palette_name_combo.currentText(),
                new_color,
                change_index,
            )
        )
        self.tile_color_palette.color_set.connect(
            lambda new_color, change_index:
            history_set_color(
                self.undo_stack,
                self.tile_color_data,
                self.tile_color_palette.color_palette_name_combo.currentText(),
                new_color,
                change_index,
            )
        )

        self.sprite_color_palette.color_palette_renamed.connect(
            lambda old_palette_name, new_palette_name: 
            history_rename_color_palette(
                self.undo_stack,
                self.sprite_color_data,
                old_palette_name,
                new_palette_name,
            )
        )
        self.tile_color_palette.color_palette_renamed.connect(
            lambda old_palette_name, new_palette_name: 
            history_rename_color_palette(
                self.undo_stack,
                self.tile_color_data,
                old_palette_name,
                new_palette_name,
            )
        )

        self.sprite_color_palette.color_palette_added.connect(
            lambda palette_name: 
            history_add_color_palette(
                self.undo_stack,
                self.sprite_color_data,
                palette_name
            )
        )
        self.tile_color_palette.color_palette_added.connect(
            lambda palette_name: 
            history_add_color_palette(
                self.undo_stack,
                self.tile_color_data,
                palette_name
            )
        )

        self.sprite_color_palette.color_palette_removed.connect(
            lambda palette_name: 
            history_remove_color_palette(
                self.undo_stack,
                self.sprite_color_data,
                palette_name
            )
        )
        self.tile_color_palette.color_palette_removed.connect(
            lambda palette_name: 
            history_remove_color_palette(
                self.undo_stack,
                self.tile_color_data,
                palette_name
            )
        )

        self.sprite_pixel_palette.add_palette_row.connect(
            lambda: 
            history_add_pixel_palette_row(
                self.undo_stack,
                self.sprite_pixel_data,
            )
        )
        self.tile_pixel_palette.add_palette_row.connect(
            lambda: 
            history_add_pixel_palette_row(
                self.undo_stack,
                self.tile_pixel_data
            )
        )

        self.sprite_pixel_palette.remove_palette_row.connect(
            lambda: 
            history_remove_pixel_palette_row(
                self.undo_stack,
                self.sprite_pixel_data,
            )
        )
        self.tile_pixel_palette.remove_palette_row.connect(
            lambda: 
            history_remove_pixel_palette_row(
                self.undo_stack,
                self.tile_pixel_data
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
        self.tile_color_palette.color_palette_changed.connect(
            lambda palette_name: self.tile_color_palette.change_palette(
                self.tile_color_data.get_color_palette(palette_name)
            )
        )
        self.sprite_color_palette.color_palette_changed.connect(
            lambda palette_name: self.sprite_pixel_palette.set_color_table(
                self.sprite_color_data.get_color_palette(palette_name)
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

        self.sprite_color_data.color_updated.connect(self.sprite_color_palette.update_color)
        self.tile_color_data.color_updated.connect(self.tile_color_palette.update_color)
        self.sprite_color_data.color_updated.connect(
            lambda _, color, index: self.sprite_pixel_palette.set_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index: self.tile_pixel_palette.set_color(color, index)
        )

        self.sprite_pixel_data.data_updated.connect(
            lambda: self.sprite_pixel_palette.set_pixel_palette(self.sprite_pixel_data.get_image())
        )
        self.tile_pixel_data.data_updated.connect(
            lambda: self.tile_pixel_palette.set_pixel_palette(self.tile_pixel_data.get_image())
        )

    def setup_editor(self):
        self.sprite_scene = EditorScene()
        self.tile_scene = EditorScene()
        self.sprite_editor_view.setScene(self.sprite_scene)
        self.tile_editor_view.setScene(self.tile_scene)

        self.sprite_pixel_data.data_updated.connect(
            lambda: self.sprite_scene.set_scene_image(self.sprite_pixel_data.get_image())
        )
        self.tile_pixel_data.data_updated.connect(
            lambda: self.tile_scene.set_scene_image(self.tile_pixel_data.get_image())
        )

        self.sprite_color_palette.color_previewed.connect(self.sprite_scene.set_color)
        self.tile_color_palette.color_previewed.connect(self.tile_scene.set_color)
        self.sprite_pixel_palette.elements_selected.connect(self.sprite_scene.select_cells)
        self.tile_pixel_palette.elements_selected.connect(self.tile_scene.select_cells)

        self.sprite_color_data.color_updated.connect(
            lambda _, color, index: self.sprite_scene.set_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index:  self.tile_scene.set_color(color, index)
        )

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

    def load_project(self, file_name):
        if not file_name:
            return

        project_data = None
        try:
            with open(file_name, "r") as data_file:
                project_data = json.load(data_file)

        except OSError:
            self.show_error_dialog("Unable to open project file")
            return
        except KeyError:
            self.show_error_dialog("Unable to load project due to malformed data")
            return

        self.populate_models(project_data)
        self.enable_ui()

    def populate_models(self, project_data):
        for palette in parse_color_data(project_data["sprite_color_palettes"]):
            self.sprite_color_data.add_color_palette(*palette)
        for palette in parse_color_data(project_data["tile_color_palettes"]):
            self.tile_color_data.add_color_palette(*palette)
        
        sprite_data = parse_pixel_data(project_data["sprites"])
        tile_data = parse_pixel_data(project_data["tiles"])
        self.sprite_pixel_data.set_image(*sprite_data[:3])
        self.sprite_pixel_data.set_names(sprite_data[-1])
        self.tile_pixel_data.set_image(*tile_data[:3])
        self.tile_pixel_data.set_names(tile_data[-1])

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

        self.sprite_color_palette.color_palette_engaged.connect(
            lambda: self.editor_tabs.setCurrentIndex(0)
        )
        self.tile_color_palette.color_palette_engaged.connect(
            lambda: self.editor_tabs.setCurrentIndex(1)
        )
        self.sprite_pixel_palette.pixel_palette_engaged.connect(
            lambda: self.editor_tabs.setCurrentIndex(0)
        )
        self.tile_pixel_palette.pixel_palette_engaged.connect(
            lambda: self.editor_tabs.setCurrentIndex(1)
        )

    def enable_ui(self):
        self.tool_bar.setEnabled(True)
        self.editor_tabs.setEnabled(True)
        self.action_save.setEnabled(True)
        self.action_close.setEnabled(True)
        self.action_gen_dat_files.setEnabled(True)
        self.action_load_jcap_system.setEnabled(True)
        for palette in self.findChildren(ColorPalette):
            palette.setEnabled(True)
        for palette in self.findChildren(PixelPalette):
            palette.setEnabled(True)

    def select_tab(self, index):
        if index == 0:
            self.sprite_color_palette_dock.show()
            self.sprite_pixel_palette_dock.show()
            self.tile_color_palette_dock.hide()
            self.tile_pixel_palette_dock.hide()
            self.map_color_palette_dock.hide()
            self.map_pixel_palette_dock.hide()
        elif index == 1:
            self.sprite_color_palette_dock.hide()
            self.sprite_pixel_palette_dock.hide()
            self.tile_color_palette_dock.show()
            self.tile_pixel_palette_dock.show()
            self.map_color_palette_dock.hide()
            self.map_pixel_palette_dock.hide()
        else:
            self.sprite_color_palette_dock.hide()
            self.sprite_pixel_palette_dock.hide()
            self.tile_color_palette_dock.hide()
            self.tile_pixel_palette_dock.hide()
            self.map_color_palette_dock.show()
            self.map_pixel_palette_dock.show()

    def select_file(self):
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
        self.check_unsaved_changes()

    @pyqtSlot()
    def save_project(self):
        pass

    @pyqtSlot()
    def close_project(self):
        self.check_unsaved_changes()

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

        for palette in self.findChildren(ColorPalette):
            palette.setEnabled(False)
        for palette in self.findChildren(PixelPalette):
            palette.setEnabled(False)

        self.undo_stack.clear()

        self.init_models()
        self.init_ui()
        self.setup_editor()

    def check_unsaved_changes(self):
        if self.undo_stack.isClean():
            return

        save_prompt = QMessageBox()
        save_prompt.setIcon(QMessageBox.Question)
        save_prompt.setText("You have unsaved changes. Would you like to save them before closing the current project?")
        save_prompt.setWindowTitle("Save Changes?")
        save_prompt.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Show the QMessageBox and wait for the user's response
        response = save_prompt.exec()

        # Check the user's response
        if response == QMessageBox.Yes:
            print("User clicked Yes")
        else:
            print("User clicked No")

    @pyqtSlot()
    def quit_application(self):
        self.check_unsaved_changes()
        self.close()
