from PyQt5 import QtWidgets, uic
import sys

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super(jide, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.show()