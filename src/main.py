import sys
from PyQt5.QtWidgets import QApplication
from jide import jide

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = jide()
    window.resize(800, 600)
    window.showMaximized()

    # Start the event loop.
    app.exec_()
