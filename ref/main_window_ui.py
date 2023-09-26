# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../res/ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(772, 597)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.editor_tabs = QtWidgets.QTabWidget(self.central_widget)
        self.editor_tabs.setEnabled(False)
        self.editor_tabs.setStyleSheet("")
        self.editor_tabs.setObjectName("editor_tabs")
        self.sprite_tab = QtWidgets.QWidget()
        self.sprite_tab.setStyleSheet("background-color: #494949;")
        self.sprite_tab.setObjectName("sprite_tab")
        self.editor_tabs.addTab(self.sprite_tab, "")
        self.tile_tab = QtWidgets.QWidget()
        self.tile_tab.setStyleSheet("background-color: #494949;")
        self.tile_tab.setObjectName("tile_tab")
        self.editor_tabs.addTab(self.tile_tab, "")
        self.map_tab = QtWidgets.QWidget()
        self.map_tab.setStyleSheet("background-color: #494949;")
        self.map_tab.setObjectName("map_tab")
        self.editor_tabs.addTab(self.map_tab, "")
        self.horizontalLayout.addWidget(self.editor_tabs)
        main_window.setCentralWidget(self.central_widget)
        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName("status_bar")
        main_window.setStatusBar(self.status_bar)
        self.tool_bar = QtWidgets.QToolBar(main_window)
        self.tool_bar.setObjectName("tool_bar")
        main_window.addToolBar(QtCore.Qt.LeftToolBarArea, self.tool_bar)
        self.sprite_color_palette_dock = QtWidgets.QDockWidget(main_window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sprite_color_palette_dock.sizePolicy().hasHeightForWidth())
        self.sprite_color_palette_dock.setSizePolicy(sizePolicy)
        self.sprite_color_palette_dock.setAutoFillBackground(False)
        self.sprite_color_palette_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.sprite_color_palette_dock.setObjectName("sprite_color_palette_dock")
        self.sprite_color_palette = ColorPalette()
        self.sprite_color_palette.setObjectName("sprite_color_palette")
        self.sprite_color_palette_dock.setWidget(self.sprite_color_palette)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.sprite_color_palette_dock)
        self.sprite_pixel_palette_dock = QtWidgets.QDockWidget(main_window)
        self.sprite_pixel_palette_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.sprite_pixel_palette_dock.setObjectName("sprite_pixel_palette_dock")
        self.sprite_pixel_palette = QtWidgets.QWidget()
        self.sprite_pixel_palette.setObjectName("sprite_pixel_palette")
        self.sprite_pixel_palette_dock.setWidget(self.sprite_pixel_palette)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.sprite_pixel_palette_dock)
        self.tile_color_palette_dock = QtWidgets.QDockWidget(main_window)
        self.tile_color_palette_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.tile_color_palette_dock.setObjectName("tile_color_palette_dock")
        self.tile_color_palette = ColorPalette()
        self.tile_color_palette.setObjectName("tile_color_palette")
        self.tile_color_palette_dock.setWidget(self.tile_color_palette)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.tile_color_palette_dock)
        self.tile_pixel_palette_dock = QtWidgets.QDockWidget(main_window)
        self.tile_pixel_palette_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.tile_pixel_palette_dock.setObjectName("tile_pixel_palette_dock")
        self.tile_pixel_palette = QtWidgets.QWidget()
        self.tile_pixel_palette.setObjectName("tile_pixel_palette")
        self.tile_pixel_palette_dock.setWidget(self.tile_pixel_palette)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.tile_pixel_palette_dock)
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 772, 22))
        self.menu_bar.setDefaultUp(False)
        self.menu_bar.setObjectName("menu_bar")
        self.menuFile = QtWidgets.QMenu(self.menu_bar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menu_bar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuJCAP = QtWidgets.QMenu(self.menu_bar)
        self.menuJCAP.setObjectName("menuJCAP")
        main_window.setMenuBar(self.menu_bar)
        self.action_open = QtWidgets.QAction(main_window)
        self.action_open.setObjectName("action_open")
        self.action_preferences = QtWidgets.QAction(main_window)
        self.action_preferences.setObjectName("action_preferences")
        self.action_exit = QtWidgets.QAction(main_window)
        self.action_exit.setObjectName("action_exit")
        self.action_undo = QtWidgets.QAction(main_window)
        self.action_undo.setEnabled(False)
        self.action_undo.setObjectName("action_undo")
        self.action_redo = QtWidgets.QAction(main_window)
        self.action_redo.setEnabled(False)
        self.action_redo.setObjectName("action_redo")
        self.action_copy = QtWidgets.QAction(main_window)
        self.action_copy.setEnabled(False)
        self.action_copy.setObjectName("action_copy")
        self.action_paste = QtWidgets.QAction(main_window)
        self.action_paste.setEnabled(False)
        self.action_paste.setObjectName("action_paste")
        self.action_gen_dat_files = QtWidgets.QAction(main_window)
        self.action_gen_dat_files.setEnabled(False)
        self.action_gen_dat_files.setObjectName("action_gen_dat_files")
        self.action_load_jcap_system = QtWidgets.QAction(main_window)
        self.action_load_jcap_system.setEnabled(False)
        self.action_load_jcap_system.setObjectName("action_load_jcap_system")
        self.action_select_tool = QtWidgets.QAction(main_window)
        self.action_select_tool.setEnabled(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/select_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_select_tool.setIcon(icon)
        self.action_select_tool.setObjectName("action_select_tool")
        self.action_pen_tool = QtWidgets.QAction(main_window)
        self.action_pen_tool.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/pencil_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_pen_tool.setIcon(icon1)
        self.action_pen_tool.setObjectName("action_pen_tool")
        self.action_fill_tool = QtWidgets.QAction(main_window)
        self.action_fill_tool.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/fill_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_fill_tool.setIcon(icon2)
        self.action_fill_tool.setObjectName("action_fill_tool")
        self.action_line_tool = QtWidgets.QAction(main_window)
        self.action_line_tool.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/line_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_line_tool.setIcon(icon3)
        self.action_line_tool.setObjectName("action_line_tool")
        self.action_rectangle_tool = QtWidgets.QAction(main_window)
        self.action_rectangle_tool.setEnabled(False)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/rect_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_rectangle_tool.setIcon(icon4)
        self.action_rectangle_tool.setObjectName("action_rectangle_tool")
        self.action_ellipse_tool = QtWidgets.QAction(main_window)
        self.action_ellipse_tool.setEnabled(False)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/ellipse_tool.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_ellipse_tool.setIcon(icon5)
        self.action_ellipse_tool.setObjectName("action_ellipse_tool")
        self.tool_bar.addAction(self.action_select_tool)
        self.tool_bar.addAction(self.action_pen_tool)
        self.tool_bar.addAction(self.action_fill_tool)
        self.tool_bar.addAction(self.action_line_tool)
        self.tool_bar.addAction(self.action_rectangle_tool)
        self.tool_bar.addAction(self.action_ellipse_tool)
        self.menuFile.addAction(self.action_open)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_preferences)
        self.menuFile.addAction(self.action_exit)
        self.menuEdit.addAction(self.action_undo)
        self.menuEdit.addAction(self.action_redo)
        self.menuEdit.addAction(self.action_copy)
        self.menuEdit.addAction(self.action_paste)
        self.menuJCAP.addAction(self.action_gen_dat_files)
        self.menuJCAP.addAction(self.action_load_jcap_system)
        self.menu_bar.addAction(self.menuFile.menuAction())
        self.menu_bar.addAction(self.menuEdit.menuAction())
        self.menu_bar.addAction(self.menuJCAP.menuAction())

        self.retranslateUi(main_window)
        self.editor_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "JCAP IDE"))
        self.editor_tabs.setTabText(self.editor_tabs.indexOf(self.sprite_tab), _translate("main_window", "Sprites"))
        self.editor_tabs.setTabText(self.editor_tabs.indexOf(self.tile_tab), _translate("main_window", "Tiles"))
        self.editor_tabs.setTabText(self.editor_tabs.indexOf(self.map_tab), _translate("main_window", "Maps"))
        self.tool_bar.setWindowTitle(_translate("main_window", "toolBar"))
        self.sprite_color_palette_dock.setWindowTitle(_translate("main_window", "Color Palettes"))
        self.sprite_pixel_palette_dock.setWindowTitle(_translate("main_window", "Sprite Palettes"))
        self.tile_color_palette_dock.setWindowTitle(_translate("main_window", "Color Palettes"))
        self.tile_pixel_palette_dock.setWindowTitle(_translate("main_window", "Tile Palettes"))
        self.menuFile.setTitle(_translate("main_window", "File"))
        self.menuEdit.setTitle(_translate("main_window", "Edit"))
        self.menuJCAP.setTitle(_translate("main_window", "JCAP"))
        self.action_open.setText(_translate("main_window", "Open"))
        self.action_open.setShortcut(_translate("main_window", "Ctrl+O"))
        self.action_preferences.setText(_translate("main_window", "Preferences"))
        self.action_exit.setText(_translate("main_window", "Exit"))
        self.action_exit.setShortcut(_translate("main_window", "Ctrl+Q"))
        self.action_undo.setText(_translate("main_window", "Undo"))
        self.action_undo.setShortcut(_translate("main_window", "Ctrl+Z"))
        self.action_redo.setText(_translate("main_window", "Redo"))
        self.action_redo.setShortcut(_translate("main_window", "Ctrl+Y"))
        self.action_copy.setText(_translate("main_window", "Copy"))
        self.action_copy.setShortcut(_translate("main_window", "Ctrl+C"))
        self.action_paste.setText(_translate("main_window", "Paste"))
        self.action_paste.setShortcut(_translate("main_window", "Ctrl+S"))
        self.action_gen_dat_files.setText(_translate("main_window", "Generate .DAT Files"))
        self.action_gen_dat_files.setShortcut(_translate("main_window", "Ctrl+D"))
        self.action_load_jcap_system.setText(_translate("main_window", "Load JCAP System"))
        self.action_load_jcap_system.setShortcut(_translate("main_window", "Ctrl+S"))
        self.action_select_tool.setText(_translate("main_window", "Select Tool"))
        self.action_select_tool.setToolTip(_translate("main_window", "Select Tool"))
        self.action_pen_tool.setText(_translate("main_window", "Pen Tool"))
        self.action_pen_tool.setToolTip(_translate("main_window", "Pen Tool"))
        self.action_fill_tool.setText(_translate("main_window", "Fill Tool"))
        self.action_fill_tool.setToolTip(_translate("main_window", "Fill Tool"))
        self.action_line_tool.setText(_translate("main_window", "Line Tool"))
        self.action_line_tool.setToolTip(_translate("main_window", "Line Tool"))
        self.action_rectangle_tool.setText(_translate("main_window", "Rectangle Tool"))
        self.action_rectangle_tool.setToolTip(_translate("main_window", "Rectangle Tool"))
        self.action_ellipse_tool.setText(_translate("main_window", "Ellipse Tool"))
        self.action_ellipse_tool.setToolTip(_translate("main_window", "Ellipse Tool"))
from color_palette import ColorPalette
import resources_rc
