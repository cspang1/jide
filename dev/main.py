from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from jide import jide

app = QApplication(sys.argv)

window = jide()

# Start the event loop.
app.exec_()