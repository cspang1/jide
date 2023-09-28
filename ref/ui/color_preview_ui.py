# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './res/ui/ColorPreview.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_color_preview(object):
    def setupUi(self, color_preview):
        color_preview.setObjectName("color_preview")
        color_preview.resize(95, 95)
        self.switch_color = QtWidgets.QToolButton(color_preview)
        self.switch_color.setEnabled(True)
        self.switch_color.setGeometry(QtCore.QRect(-1, 63, 28, 28))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/switch_color.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.switch_color.setIcon(icon)
        self.switch_color.setShortcut("")
        self.switch_color.setObjectName("switch_color")

        self.retranslateUi(color_preview)
        QtCore.QMetaObject.connectSlotsByName(color_preview)

    def retranslateUi(self, color_preview):
        _translate = QtCore.QCoreApplication.translate
        color_preview.setWindowTitle(_translate("color_preview", "Form"))
        self.switch_color.setToolTip(_translate("color_preview", "Switch Color (X)"))
        self.switch_color.setText(_translate("color_preview", "..."))
import resources_rc
