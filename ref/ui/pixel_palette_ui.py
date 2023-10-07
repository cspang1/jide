# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './res/ui/PixelPalette.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_pixel_palette(object):
    def setupUi(self, pixel_palette):
        pixel_palette.setObjectName("pixel_palette")
        pixel_palette.resize(383, 328)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pixel_palette.sizePolicy().hasHeightForWidth())
        pixel_palette.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(pixel_palette)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tool_layout = QtWidgets.QHBoxLayout()
        self.tool_layout.setObjectName("tool_layout")
        self.add_palette_line_btn = QtWidgets.QToolButton(pixel_palette)
        self.add_palette_line_btn.setEnabled(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/add_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_palette_line_btn.setIcon(icon)
        self.add_palette_line_btn.setObjectName("add_palette_line_btn")
        self.tool_layout.addWidget(self.add_palette_line_btn)
        self.rem_palette_line_btn = QtWidgets.QToolButton(pixel_palette)
        self.rem_palette_line_btn.setEnabled(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/remove_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rem_palette_line_btn.setIcon(icon1)
        self.rem_palette_line_btn.setObjectName("rem_palette_line_btn")
        self.tool_layout.addWidget(self.rem_palette_line_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.tool_layout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.tool_layout)
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setObjectName("vertical_layout")
        self.pixel_palette_grid = PixelPaletteGrid(pixel_palette)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pixel_palette_grid.sizePolicy().hasHeightForWidth())
        self.pixel_palette_grid.setSizePolicy(sizePolicy)
        self.pixel_palette_grid.setMinimumSize(QtCore.QSize(0, 8))
        self.pixel_palette_grid.setObjectName("pixel_palette_grid")
        self.vertical_layout.addWidget(self.pixel_palette_grid)
        self.verticalLayout_2.addLayout(self.vertical_layout)

        self.retranslateUi(pixel_palette)
        QtCore.QMetaObject.connectSlotsByName(pixel_palette)

    def retranslateUi(self, pixel_palette):
        _translate = QtCore.QCoreApplication.translate
        pixel_palette.setWindowTitle(_translate("pixel_palette", "Form"))
        self.add_palette_line_btn.setText(_translate("pixel_palette", "..."))
        self.rem_palette_line_btn.setText(_translate("pixel_palette", "..."))
from pixel_palette_grid import PixelPaletteGrid
import resources_rc
