# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './res/ui/PreferencesDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_preferences_dialog(object):
    def setupUi(self, preferences_dialog):
        preferences_dialog.setObjectName("preferences_dialog")
        preferences_dialog.resize(330, 221)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(preferences_dialog.sizePolicy().hasHeightForWidth())
        preferences_dialog.setSizePolicy(sizePolicy)
        preferences_dialog.setSizeGripEnabled(False)
        preferences_dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(preferences_dialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cpu_port_layout = QtWidgets.QHBoxLayout()
        self.cpu_port_layout.setObjectName("cpu_port_layout")
        self.cpu_port_label = QtWidgets.QLabel(preferences_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cpu_port_label.sizePolicy().hasHeightForWidth())
        self.cpu_port_label.setSizePolicy(sizePolicy)
        self.cpu_port_label.setObjectName("cpu_port_label")
        self.cpu_port_layout.addWidget(self.cpu_port_label)
        self.cpu_port_combo = QtWidgets.QComboBox(preferences_dialog)
        self.cpu_port_combo.setObjectName("cpu_port_combo")
        self.cpu_port_layout.addWidget(self.cpu_port_combo)
        self.verticalLayout.addLayout(self.cpu_port_layout)
        self.gpu_port_layout = QtWidgets.QHBoxLayout()
        self.gpu_port_layout.setObjectName("gpu_port_layout")
        self.gpu_port_label = QtWidgets.QLabel(preferences_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_port_label.sizePolicy().hasHeightForWidth())
        self.gpu_port_label.setSizePolicy(sizePolicy)
        self.gpu_port_label.setObjectName("gpu_port_label")
        self.gpu_port_layout.addWidget(self.gpu_port_label)
        self.gpu_port_combo = QtWidgets.QComboBox(preferences_dialog)
        self.gpu_port_combo.setObjectName("gpu_port_combo")
        self.gpu_port_layout.addWidget(self.gpu_port_combo)
        self.verticalLayout.addLayout(self.gpu_port_layout)
        self.com_port_warning = QtWidgets.QLabel(preferences_dialog)
        self.com_port_warning.setEnabled(True)
        self.com_port_warning.setTextFormat(QtCore.Qt.RichText)
        self.com_port_warning.setScaledContents(False)
        self.com_port_warning.setAlignment(QtCore.Qt.AlignCenter)
        self.com_port_warning.setWordWrap(True)
        self.com_port_warning.setObjectName("com_port_warning")
        self.verticalLayout.addWidget(self.com_port_warning)
        self.jcap_path_layout = QtWidgets.QHBoxLayout()
        self.jcap_path_layout.setObjectName("jcap_path_layout")
        self.jcap_path_label = QtWidgets.QLabel(preferences_dialog)
        self.jcap_path_label.setObjectName("jcap_path_label")
        self.jcap_path_layout.addWidget(self.jcap_path_label)
        self.jcap_path_edit = QtWidgets.QLineEdit(preferences_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jcap_path_edit.sizePolicy().hasHeightForWidth())
        self.jcap_path_edit.setSizePolicy(sizePolicy)
        self.jcap_path_edit.setObjectName("jcap_path_edit")
        self.jcap_path_layout.addWidget(self.jcap_path_edit)
        self.jcap_path_browse = QtWidgets.QPushButton(preferences_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jcap_path_browse.sizePolicy().hasHeightForWidth())
        self.jcap_path_browse.setSizePolicy(sizePolicy)
        self.jcap_path_browse.setObjectName("jcap_path_browse")
        self.jcap_path_layout.addWidget(self.jcap_path_browse)
        self.verticalLayout.addLayout(self.jcap_path_layout)
        self.dialog_buttons = QtWidgets.QDialogButtonBox(preferences_dialog)
        self.dialog_buttons.setOrientation(QtCore.Qt.Horizontal)
        self.dialog_buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialog_buttons.setObjectName("dialog_buttons")
        self.verticalLayout.addWidget(self.dialog_buttons)

        self.retranslateUi(preferences_dialog)
        self.dialog_buttons.accepted.connect(preferences_dialog.accept) # type: ignore
        self.dialog_buttons.rejected.connect(preferences_dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(preferences_dialog)

    def retranslateUi(self, preferences_dialog):
        _translate = QtCore.QCoreApplication.translate
        preferences_dialog.setWindowTitle(_translate("preferences_dialog", "JIDE Preferences"))
        self.cpu_port_label.setText(_translate("preferences_dialog", "CPU Port:"))
        self.gpu_port_label.setText(_translate("preferences_dialog", "GPU Port:"))
        self.com_port_warning.setText(_translate("preferences_dialog", "<html><head/><body><p><span style=\" color:#ff0000;\">Not enough COM ports are populated to support both the CPU and GPU. Check the connections between your PC and the JCAP board.</span></p></body></html>"))
        self.jcap_path_label.setText(_translate("preferences_dialog", "JCAP Path:"))
        self.jcap_path_browse.setText(_translate("preferences_dialog", "Browse"))
