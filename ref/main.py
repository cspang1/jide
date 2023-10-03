import sys
from PyQt5.QtWidgets import QApplication
from jide import Jide

if __name__ == "__main__":
    app = QApplication(sys.argv)
    jide = Jide()
    jide.show()
    jide.showMaximized()
    sys.exit(app.exec())