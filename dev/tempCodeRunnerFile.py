from PyQt5.QtWidgets import QApplication, QMainWindow
from jide import jide
import sys

app = QApplication(sys.argv)

window = jide()
window.showMaximized()

# Start the event loop.
app.exec_()