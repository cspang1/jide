# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './res/ui/ColorPickerDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_color_picker_dialog(object):
    def setupUi(self, color_picker_dialog):
        color_picker_dialog.setObjectName("color_picker_dialog")
        color_picker_dialog.resize(684, 578)
        color_picker_dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(color_picker_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.color_swatches_frame = QtWidgets.QFrame(color_picker_dialog)
        self.color_swatches_frame.setMinimumSize(QtCore.QSize(406, 406))
        self.color_swatches_frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.color_swatches_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.color_swatches_frame.setObjectName("color_swatches_frame")
        self.main_layout.addWidget(self.color_swatches_frame)
        self.values_layout = QtWidgets.QVBoxLayout()
        self.values_layout.setObjectName("values_layout")
        self.color_preview = QtWidgets.QLabel(color_picker_dialog)
        self.color_preview.setMinimumSize(QtCore.QSize(100, 50))
        self.color_preview.setFrameShape(QtWidgets.QFrame.Panel)
        self.color_preview.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.color_preview.setText("")
        self.color_preview.setObjectName("color_preview")
        self.values_layout.addWidget(self.color_preview)
        self.e_bit_val_frame = QtWidgets.QFrame(color_picker_dialog)
        self.e_bit_val_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.e_bit_val_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.e_bit_val_frame.setObjectName("e_bit_val_frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.e_bit_val_frame)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.e_bit_color_header = QtWidgets.QLabel(self.e_bit_val_frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.e_bit_color_header.setFont(font)
        self.e_bit_color_header.setTextFormat(QtCore.Qt.PlainText)
        self.e_bit_color_header.setAlignment(QtCore.Qt.AlignCenter)
        self.e_bit_color_header.setObjectName("e_bit_color_header")
        self.verticalLayout_4.addWidget(self.e_bit_color_header)
        self.e_bit_val_layout = QtWidgets.QFormLayout()
        self.e_bit_val_layout.setObjectName("e_bit_val_layout")
        self.ebit_red_value = QtWidgets.QLineEdit(self.e_bit_val_frame)
        self.ebit_red_value.setObjectName("ebit_red_value")
        self.e_bit_val_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ebit_red_value)
        self.e_bit_red_label = QtWidgets.QLabel(self.e_bit_val_frame)
        self.e_bit_red_label.setObjectName("e_bit_red_label")
        self.e_bit_val_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.e_bit_red_label)
        self.e_bit_green_label = QtWidgets.QLabel(self.e_bit_val_frame)
        self.e_bit_green_label.setObjectName("e_bit_green_label")
        self.e_bit_val_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.e_bit_green_label)
        self.ebit_green_value = QtWidgets.QLineEdit(self.e_bit_val_frame)
        self.ebit_green_value.setObjectName("ebit_green_value")
        self.e_bit_val_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ebit_green_value)
        self.e_bit_blue_label = QtWidgets.QLabel(self.e_bit_val_frame)
        self.e_bit_blue_label.setObjectName("e_bit_blue_label")
        self.e_bit_val_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.e_bit_blue_label)
        self.ebit_blue_value = QtWidgets.QLineEdit(self.e_bit_val_frame)
        self.ebit_blue_value.setObjectName("ebit_blue_value")
        self.e_bit_val_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ebit_blue_value)
        self.e_bit_hex_label = QtWidgets.QLabel(self.e_bit_val_frame)
        self.e_bit_hex_label.setObjectName("e_bit_hex_label")
        self.e_bit_val_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.e_bit_hex_label)
        self.ebit_hex_value = QtWidgets.QLineEdit(self.e_bit_val_frame)
        self.ebit_hex_value.setObjectName("ebit_hex_value")
        self.e_bit_val_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.ebit_hex_value)
        self.verticalLayout_4.addLayout(self.e_bit_val_layout)
        self.values_layout.addWidget(self.e_bit_val_frame)
        self.f_color_val_frame = QtWidgets.QFrame(color_picker_dialog)
        self.f_color_val_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_color_val_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.f_color_val_frame.setObjectName("f_color_val_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.f_color_val_frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.f_bit_color_header = QtWidgets.QLabel(self.f_color_val_frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.f_bit_color_header.setFont(font)
        self.f_bit_color_header.setAlignment(QtCore.Qt.AlignCenter)
        self.f_bit_color_header.setObjectName("f_bit_color_header")
        self.verticalLayout_5.addWidget(self.f_bit_color_header)
        self.f_bit_val_layout = QtWidgets.QFormLayout()
        self.f_bit_val_layout.setObjectName("f_bit_val_layout")
        self.f_bit_red_label = QtWidgets.QLabel(self.f_color_val_frame)
        self.f_bit_red_label.setObjectName("f_bit_red_label")
        self.f_bit_val_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.f_bit_red_label)
        self.f_bit_red_value = QtWidgets.QLineEdit(self.f_color_val_frame)
        self.f_bit_red_value.setObjectName("f_bit_red_value")
        self.f_bit_val_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.f_bit_red_value)
        self.f_bit_green_label = QtWidgets.QLabel(self.f_color_val_frame)
        self.f_bit_green_label.setObjectName("f_bit_green_label")
        self.f_bit_val_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.f_bit_green_label)
        self.f_bit_green_value = QtWidgets.QLineEdit(self.f_color_val_frame)
        self.f_bit_green_value.setObjectName("f_bit_green_value")
        self.f_bit_val_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.f_bit_green_value)
        self.f_bit_blue_label = QtWidgets.QLabel(self.f_color_val_frame)
        self.f_bit_blue_label.setObjectName("f_bit_blue_label")
        self.f_bit_val_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.f_bit_blue_label)
        self.f_bit_blue_value = QtWidgets.QLineEdit(self.f_color_val_frame)
        self.f_bit_blue_value.setObjectName("f_bit_blue_value")
        self.f_bit_val_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.f_bit_blue_value)
        self.f_bit_hex_label = QtWidgets.QLabel(self.f_color_val_frame)
        self.f_bit_hex_label.setObjectName("f_bit_hex_label")
        self.f_bit_val_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.f_bit_hex_label)
        self.f_bit_hex_value = QtWidgets.QLineEdit(self.f_color_val_frame)
        self.f_bit_hex_value.setObjectName("f_bit_hex_value")
        self.f_bit_val_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.f_bit_hex_value)
        self.verticalLayout_5.addLayout(self.f_bit_val_layout)
        self.values_layout.addWidget(self.f_color_val_frame)
        self.main_layout.addLayout(self.values_layout)
        self.verticalLayout.addLayout(self.main_layout)
        self.buttons = QtWidgets.QDialogButtonBox(color_picker_dialog)
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.verticalLayout.addWidget(self.buttons)

        self.retranslateUi(color_picker_dialog)
        self.buttons.accepted.connect(color_picker_dialog.accept) # type: ignore
        self.buttons.rejected.connect(color_picker_dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(color_picker_dialog)

    def retranslateUi(self, color_picker_dialog):
        _translate = QtCore.QCoreApplication.translate
        color_picker_dialog.setWindowTitle(_translate("color_picker_dialog", "Color Picker"))
        self.e_bit_color_header.setText(_translate("color_picker_dialog", "8-Bit Color"))
        self.e_bit_red_label.setText(_translate("color_picker_dialog", "Red:"))
        self.e_bit_green_label.setText(_translate("color_picker_dialog", "Green:"))
        self.e_bit_blue_label.setText(_translate("color_picker_dialog", "Blue:"))
        self.e_bit_hex_label.setText(_translate("color_picker_dialog", "Hex:"))
        self.f_bit_color_header.setText(_translate("color_picker_dialog", "Full Color"))
        self.f_bit_red_label.setText(_translate("color_picker_dialog", "Red:"))
        self.f_bit_green_label.setText(_translate("color_picker_dialog", "Green:"))
        self.f_bit_blue_label.setText(_translate("color_picker_dialog", "Blue:"))
        self.f_bit_hex_label.setText(_translate("color_picker_dialog", "Hex:"))
