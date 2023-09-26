import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem
from PyQt5.QtGui import QPixmap, QPainter, QColor

app = QApplication(sys.argv)
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)

# Create a QGraphicsPixmapItem
pixmap_item = QGraphicsPixmapItem(QPixmap("E:\JCAP\jide\\res\icons\\add.png"))
scene.addItem(pixmap_item)

# Create a QGraphicsLineItem (your drawn shape)
line_item = QGraphicsLineItem(50, 50, 200, 200)
line_item.setPen(QColor(255, 0, 0))  # Red color for the line (customize as needed)
scene.addItem(line_item)

# Capture the content of the QGraphicsPixmapItem into a QPixmap
pixmap = QPixmap(pixmap_item.pixmap())  # Copy the pixmap

# Create a QPainter to draw on the QPixmap
painter = QPainter(pixmap)
scene.render(painter)  # Render the scene onto the QPixmap
painter.end()  # End the painting operation

# Set the QGraphicsPixmapItem's pixmap to the updated QPixmap
pixmap_item.setPixmap(pixmap)

view.show()
sys.exit(app.exec_())
