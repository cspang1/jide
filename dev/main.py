from PyQt5.QtWidgets import QApplication, QMainWindow
from jide import jide
import sys

app = QApplication(sys.argv)

window = jide()
window.resize(800,600)
window.showMaximized()

# Start the event loop.
app.exec_()