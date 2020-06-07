from collections import defaultdict
from copy import deepcopy
import math
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot,
    QTimer,
    QEvent,
    QLineF,
    QPointF,
    QRectF,
)
from PyQt5.QtGui import (
    QGuiApplication,
    QImage,
    QPixmap,
    QColor,
    QBrush,
    QPen,
    QPainter,
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QApplication,
    QStyleOptionGraphicsItem,
)
from canvastools import Tools
from source import Source


class GraphicsView(QGraphicsView):
    """QGraphicsView into sprite/tile canvas

    :param scene:   QGraphicsScene representing sprite/tile canvas
    :type scene:    QGraphicsScene, defaults to None
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget
    """

    def __init__(self, scene=None, parent=None):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene().installEventFilter(self)
        self.scale(50, 50)

    def eventFilter(self, source, event):
        """Event filter for handling zoom/pan events

        :param source:  Source of event
        :type source:   QObject
        :param event:   Triggered event
        :type event:    QEvent
        :return:        Whether to continue processing event downstream
        :rtype:         bool
        """
        if (
            event.type() == QEvent.GraphicsSceneWheel
            and QApplication.keyboardModifiers() == Qt.ControlModifier
        ):
            self.zoomCanvas(event)
            event.accept()
            return True
        return False

    def zoomCanvas(self, event):
        """Zoom view into sprite/tile canvas

        :param event:   Source event
        :type event:    QEvent
        """
        zoomFactor = 2
        oldPos = event.scenePos()

        detail = QStyleOptionGraphicsItem.levelOfDetailFromTransform(
            self.transform()
        )
        if detail < 100 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > 10 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())


class Subject(QGraphicsPixmapItem):
    """Object representing pixel contents of canvas

    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget
    """

    def __init__(self, parent=None):
        self.width = 8
        self.height = 8
        self.color_table = [0] * 16
        self.subject = QImage(
            bytes([0] * self.width * self.height),
            self.width,
            self.height,
            QImage.Format_Indexed8,
        )
        self.setColorTable(self.color_table)
        super().__init__(QPixmap.fromImage(self.subject), parent)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)

    def setPixel(self, x, y, value):
        """Set value of pixel in subject at (x,y) coordinates

        :param x:       X-coordinate of pixel
        :type x:        int
        :param y:       Y-coordinate of pixel
        :type y:        int
        :param value:   Color table index value to set pixel to
        :type value:    int
        """
        self.subject.setPixel(x, y, value)

    def setColorTable(self, colors):
        """Set color table of currently rendered subject

        :param colors:  List of colors to set color table to
        :type colors:   list(int)
        """
        self.color_table = colors
        self.subject.setColorTable(self.color_table)

    def update(self):
        """Trigger update of subject pixmap
        """
        self.setPixmap(QPixmap.fromImage(self.subject))

    def setWidth(self, width):
        """Set width of subject in pixels

        :param width:   New width of subject in pixels
        :type width:    int
        """
        self.width = width
        self.resizeSubject()

    def setHeight(self, height):
        """Set height of subject in pixels

        :param height:  New height of subject in pixels
        :type height:   int
        """
        self.height = height
        self.resizeSubject()

    def resizeSubject(self):
        """Perform re-generation of subject QImage proceeding resize
        """
        self.subject = QImage(
            bytes([0] * self.width * self.height),
            self.width,
            self.height,
            QImage.Format_Indexed8,
        )
        self.setColorTable(self.color_table)

    def copy(self, selected_region):
        """Copy selected region of pixels to the QGuiApplication clipboard

        :param selected_region: Rectangular region of pixels to copy to
                                clipboard
        :type selected_region:  QRect
        """
        QGuiApplication.clipboard().setImage(
            self.subject.copy(selected_region)
        )


class Overlay(QGraphicsPixmapItem):
    """Overlay of canvas which handles graphics tools interactions

    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, parent=None):
        self.start_pos = None
        self.last_pos = None
        self.cur_pos = None
        self.start_scene_pos = None
        self.cur_scene_pos = None
        self.selecting = False
        self.pasting = False
        self.pasted = None
        self.copied = None
        self.tool = None
        self.width = 8
        self.height = 8
        self.color = 0
        self.filled = False
        self.select_timer = QTimer()
        self.select_timer.timeout.connect(self.marchAnts)
        self.ants_offset = 0
        self.setColor(self.color)
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap, parent)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setAcceptHoverEvents(True)

    # Currently disabling selection when switching tools...
    # should make it more interactive...
    def setTool(self, tool, filled=False):
        """Sets the active tool based on user selection in toolbar

        :param tool:    Tool selection
        :type tool:     Tools
        :param filled:  Whether a selected shape tool will be filled or
                        outline, defaults to False
        :type filled:   bool, optional
        """
        self.tool = tool
        self.filled = filled
        self.selecting = False
        self.select_timer.stop()
        self.scene.update()
        self.scene.region_selected.emit(False)

    def setColor(self, color):
        """Sets the color of the selected tool

        :param color: Color of the selected tool to set
        :type color: int
        """
        self.color = color if color != 0 else QColor(Qt.magenta).rgba()

    def setWidth(self, width):
        """Set the width of the overlay to remain consistent with the
        underlying subject

        :param width: New width of the overlay
        :type width: int
        """
        self.width = width
        self.setPixmap(self.pixmap().scaled(self.width, self.height))

    def setHeight(self, height):
        """Set the height of the overlay to remain consistent with the
        underlying subject

        :param width: New height of the overlay
        :type width: int
        """
        self.height = height
        self.setPixmap(self.pixmap().scaled(self.width, self.height))

    def clear(self):
        """Clear the overlay
        """
        pixmap = self.pixmap()
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)

    def floodFill(self, x, y):
        """Recursive floodfill tool entry point

        :param x:   Starting x coordinate for floodfill
        :type x:    int
        :param y:   Starting y coordinate for floodfill
        :type y:    int
        """
        self.base_image = self.scene.subject.subject.copy()
        old_color = self.base_image.pixelIndex(x, y)
        new_color = self.base_image.colorTable().index(
            0 if self.color == QColor(Qt.magenta).rgba() else self.color
        )
        self.fillPixel(x, y, old_color, new_color)

    def fillPixel(self, x, y, old_color, new_color):
        """Recursive floodfill function

        :param x:           Current x coordinate
        :type x:            int
        :param y:           Current y coordinate
        :type y:            int
        :param old_color:   Target color to fill
        :type old_color:    int
        :param new_color:   New color to replace target color
        :type new_color:    int
        """
        if (
            not 0 <= x < self.base_image.width()
            or not 0 <= y < self.base_image.height()
        ):
            return
        if old_color == new_color:
            return
        elif self.base_image.pixelIndex(x, y) != old_color:
            return
        else:
            self.base_image.setPixel(x, y, new_color)
        self.fillPixel(x + 1, y, old_color, new_color)
        self.fillPixel(x, y + 1, old_color, new_color)
        self.fillPixel(x - 1, y, old_color, new_color)
        self.fillPixel(x, y - 1, old_color, new_color)

    def paste(self):
        """Entry point for pasting a pixel region after a selection is copied
        """
        self.selecting = False
        self.pasting = True
        self.select_timer.stop()
        self.scene.update()
        self.copied = QGuiApplication.clipboard().image()
        self.scene.region_selected.emit(False)
        self.renderPaste(self.last_pos)

    def setColorTable(self, color_table):
        """Set color table used by overlay when pasting

        :param color_table: List of RGB values to set color table to
        :type color_table:  list(int)
        """
        if self.pasting:
            self.copied.setColorTable(color_table)
            self.renderPaste(self.last_pos)

    def hoverMoveEvent(self, event):
        """Mouse hover move event for handling updating pasting location

        :param event:   Source event
        :type event:    QGraphicsSceneHoverEvent
        """
        self.last_pos = event.pos()
        if self.pasting:
            self.renderPaste(self.last_pos)

    def renderPaste(self, position):
        """Render a currently pasting pixel region onto the overlay

        :param position:    Location on overlay to render paste
        :type position:     QPointF
        """
        x = int(position.x())
        y = int(position.y())
        cur_x = cur_y = 0
        self.pasted = QImage(
            bytes([16] * self.width * self.height),
            self.width,
            self.height,
            QImage.Format_Indexed8,
        )
        color_table = deepcopy(self.copied.colorTable())
        color_table.append(0)
        if self.scene.source is Source.SPRITE:
            color_table[0] = QColor(Qt.magenta).rgba()
        self.pasted.setColorTable(color_table)
        height_range = range(
            y, min(self.pasted.height(), self.copied.height() + y)
        )
        width_range = range(
            x, min(self.pasted.width(), self.copied.width() + x)
        )
        for i in height_range:
            for j in width_range:
                self.pasted.setPixel(
                    j, i, self.copied.pixelIndex(cur_x, cur_y)
                )
                cur_x += 1
            cur_x = 0
            cur_y += 1
        self.setPixmap(QPixmap().fromImage(self.pasted))

    def mousePressEvent(self, event):
        """Mouse press event to handle mouse clicks with various tools

        :param event:   Source event
        :type event:    QGraphicsSceneMouseEvent
        """
        if event.buttons() == Qt.LeftButton and not self.pasting:
            self.scene.setColorSwitchEnabled(False)
            if self.start_pos is None:
                self.start_pos = QPointF(
                    math.floor(event.pos().x()), math.floor(event.pos().y())
                )
                self.start_scene_pos = QPointF(
                    math.floor(event.scenePos().x()),
                    math.floor(event.scenePos().y()),
                )
            self.last_pos = self.start_pos
            if self.tool is Tools.SELECT:
                self.selecting = False
                self.select_timer.stop()
                self.scene.update()
            if self.tool is Tools.PEN:
                pixmap = self.pixmap()
                painter = QPainter(pixmap)
                pen = QPen(QColor.fromRgba(self.color))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawPoint(self.start_pos)
                self.setPixmap(pixmap)
                painter.end()

    def mouseMoveEvent(self, event):
        """Mouse move event to handle mouse movement after clicking with various tools

        :param event:   Source event
        :type event:    QGraphicsSceneMouseEvent
        """
        if event.buttons() == Qt.LeftButton:
            if not self.pasting:
                if self.tool is not Tools.PEN:
                    self.clear()
                pixmap = self.pixmap()
                painter = QPainter(pixmap)
                self.cur_pos = QPointF(
                    math.floor(event.pos().x()), math.floor(event.pos().y())
                )
                self.cur_scene_pos = QPointF(
                    math.ceil(event.scenePos().x()),
                    math.ceil(event.scenePos().y()),
                )
                pen = QPen(QColor.fromRgba(self.color))
                pen.setWidth(1)
                painter.setPen(pen)
                if self.filled:
                    brush = QBrush(QColor.fromRgba(self.color))
                    painter.setBrush(brush)
                if self.tool is Tools.LINE:
                    painter.drawLine(self.start_pos, self.cur_pos)
                elif self.tool is Tools.ELLIPSE:
                    painter.drawEllipse(QRectF(self.start_pos, self.cur_pos))
                elif self.tool is Tools.RECTANGLE:
                    painter.drawRect(QRectF(self.start_pos, self.cur_pos))
                elif self.tool is Tools.PEN:
                    painter.drawLine(self.last_pos, self.cur_pos)
                elif self.tool is Tools.SELECT:
                    self.selecting = True
                    if not self.select_timer.isActive():
                        self.select_timer.start(500)
                    self.updateSceneForeground()

                self.setPixmap(pixmap)
                self.last_pos = self.cur_pos
                painter.end()
            else:
                self.hoverMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event to handle mouse release with various tools

        :param event:   Source event
        :type event:    QGraphicsSceneMouseEvent
        """
        self.start_pos = None
        self.scene.setColorSwitchEnabled(True)
        if event.button() == Qt.LeftButton and self.tool is Tools.FLOODFILL:
            self.floodFill(
                math.floor(event.pos().x()), math.floor(event.pos().y())
            )
            self.scene.bakeDiff(self.base_image)
        elif event.button() == Qt.LeftButton and self.tool is not Tools.SELECT:
            self.scene.bakeOverlay(self.pixmap().toImage())
        if self.selecting:
            self.scene.selectRegion(
                QRectF(self.start_scene_pos, self.cur_scene_pos).normalized()
            )
        else:
            self.scene.region_selected.emit(False)
        if event.button() == Qt.LeftButton and self.pasting:
            self.scene.bakeDiff(self.pasted)
            self.pasting = False
        elif event.button() != Qt.LeftButton and self.pasting:
            self.pasting = False
        self.clear()

    def marchAnts(self):
        """Simply updates the offset of marching ants offset for box around a
        selected area
        """
        self.ants_offset += 4
        self.updateSceneForeground()

    def updateSceneForeground(self):
        """Updates the foreground of the overlay to update selection box when selecting
        """
        ssx = self.start_scene_pos.x()
        ssy = self.start_scene_pos.y()
        csx = self.cur_scene_pos.x()
        csy = self.cur_scene_pos.y()
        scene_rect = self.scene.itemsBoundingRect()
        self.start_scene_pos = QPointF(
            max(min(ssx, scene_rect.right()), scene_rect.left()),
            max(min(ssy, scene_rect.bottom()), scene_rect.top()),
        )
        self.cur_scene_pos = QPointF(
            max(min(csx, scene_rect.right()), scene_rect.left()),
            max(min(csy, scene_rect.bottom()), scene_rect.top()),
        )
        if (
            self.start_scene_pos.x() != self.cur_scene_pos.x()
            and self.start_scene_pos.y() != self.cur_scene_pos.y()
        ):
            self.selecting = True
            self.scene.update()
        else:
            self.selecting = False


class GraphicsScene(QGraphicsScene):
    """Canvas representing the current state of the subject including
    overlayed grid lines

    :param data:    Source of sprite/tile data
    :type data:     GameData
    :param source:  Specifies the subject of the table, either tile or sprite
    :type source:   Source
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    set_pixel_palette = pyqtSignal(int, int, int)
    region_selected = pyqtSignal(bool)
    region_copied = pyqtSignal(bool)
    set_color_switch_enabled = pyqtSignal(bool)

    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.data = data
        self.source = source
        self.root = None
        self.selected_region = None
        self.copied_region = None
        self.current_color_palette = None
        self.subject = Subject()
        self.overlay = Overlay()
        self.overlay.scene = self
        self.addItem(self.subject)
        self.addItem(self.overlay)
        self.primary_color = 0

    def setColorSwitchEnabled(self, enabled):
        """Emits signal to disable the color palette primary/secondary color
        switch functionality

        :param enabled: Whether to enable or disable the switch functionality
        :type enabled:  bool
        """
        self.set_color_switch_enabled.emit(enabled)

    @pyqtSlot(int, int, int)
    def setSubject(self, root, width, height):
        """Sets the pixel contents of the canvas

        :param root:    The root index of the tiles/sprites to be rendered
        :type root:     int
        :param width:   The width of sprites/tiles starting at the root to
                        render
        :type width:    int
        :param height:  The height of sprites/tiles starting at the root to
                        render
        :type height:   int
        """
        self.root = root
        self.subject.setWidth(width * 8)
        self.subject.setHeight(height * 8)
        self.overlay.setWidth(width * 8)
        self.overlay.setHeight(height * 8)
        data = self.data.getPixelPalettes(self.source)
        for row in range(height):
            for col in range(width):
                cur_subject = data[root + col + (row * 16)]
                for y in range(8):
                    for x in range(8):
                        self.subject.setPixel(
                            8 * col + x, 8 * row + y, cur_subject[y][x]
                        )

        self.subject.update()
        if self.overlay.selecting:
            self.overlay.updateSceneForeground()
        self.setSceneRect(self.itemsBoundingRect())

    @pyqtSlot(Tools)
    def setTool(self, tool):
        """Set the current tool being used on the canvas

        :param tool:    Current tool to be used
        :type tool:     Tools
        """
        self.overlay.setTool(tool, True)  # Need True to be based on tool

    @pyqtSlot(str)
    def setColorPalette(self, palette):
        """Set the color palette used by the canvas subject

        :param palette: Name of the target color palette
        :type palette:  str
        """
        self.current_color_palette = self.data.getColPal(palette, self.source)
        color_table = [color.rgba() for color in self.current_color_palette]
        self.subject.setColorTable(color_table)
        self.overlay.setColorTable(color_table)
        self.setPrimaryColor(self.primary_color)
        self.subject.update()

    @pyqtSlot(int)
    def setPrimaryColor(self, color):
        """Set the color used by graphics tools

        :param color:   Index of the color in the current color table to be
                        set as the primary
        :type color:    int
        """
        self.primary_color = color
        self.overlay.setColor(
            self.current_color_palette[self.primary_color].rgba()
        )

    @pyqtSlot()
    def copy(self):
        """Initiate copying of a selected region of pixels
        """
        self.region_copied.emit(True)
        self.subject.copy(self.selected_region)

    @pyqtSlot()
    def startPasting(self):
        """Initiate pasting a copied region of pixels
        """
        self.overlay.paste()

    def selectRegion(self, region):
        """Select a region of pixels chosen with the select tool

        :param region:  Rectangular region of pixels to select
        :type region:   QRect
        """
        self.selected_region = region.toRect()
        self.region_selected.emit(True)

    def bakeDiff(self, image):
        """Generate a differential list of pixel values based on the overlay
        and bake it onto the centralized GameData data.

        :param image:   Image derived from overlay to bake
        :type image:    QImage
        """
        original = self.subject.subject
        batch = defaultdict(list)
        for row in range(image.height()):
            for col in range(image.width()):
                new_pixel = image.pixelIndex(col, row)
                old_pixel = original.pixelIndex(col, row)
                if old_pixel != new_pixel and new_pixel != 16:
                    index = (
                        self.root
                        + math.floor(col / 8)
                        + 16 * math.floor(row / 8)
                    )
                    row_norm = row % 8
                    col_norm = col % 8
                    batch[index].append((row_norm, col_norm, new_pixel))
        if batch:
            self.data.setPixBatch(batch, self.source)

    def bakeOverlay(self, overlay):
        """Bake the overlay data directly into the centralized GameData data

        :param overlay: Overlay to bake
        :type overlay:  QImage
        """
        batch = defaultdict(list)
        for row in range(overlay.height()):
            for col in range(overlay.width()):
                if overlay.pixel(col, row) != 0:
                    index = (
                        self.root
                        + math.floor(col / 8)
                        + 16 * math.floor(row / 8)
                    )
                    row_norm = row % 8
                    col_norm = col % 8
                    batch[index].append(
                        (row_norm, col_norm, self.primary_color)
                    )
        if batch:
            self.data.setPixBatch(batch, self.source)

    def drawForeground(self, painter, rect):
        """Draw the gridlines overlaying the canvas

        :param painter: QPainter object to paint with
        :type painter:  QPainter
        :param rect:    Exposed rectangle to paint over
        :type rect:     QRectF
        """
        pen = QPen(Qt.darkCyan)
        pen.setWidth(0)
        painter.setPen(pen)
        thin_lines = []
        thick_lines = []
        for longitude in range(self.subject.width + 1):
            line = QLineF(longitude, 0, longitude, self.subject.height)
            if longitude % 8 == 0:
                thick_lines.append(line)
            thin_lines.append(line)
        for latitude in range(self.subject.height + 1):
            line = QLineF(0, latitude, self.subject.width, latitude)
            if latitude % 8 == 0:
                thick_lines.append(line)
            thin_lines.append(line)
        pen = QPen(Qt.darkCyan)
        pen.setWidth(1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(thin_lines)
        pen.setColor(Qt.white)
        painter.setPen(pen)
        painter.drawLines(thick_lines)
        if self.overlay.selecting:
            pen = QPen(Qt.white)
            pen.setJoinStyle(Qt.MiterJoin)
            pen.setWidth(3)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawRect(
                QRectF(
                    self.overlay.start_scene_pos, self.overlay.cur_scene_pos
                )
            )
            pen.setColor(Qt.black)
            pen.setStyle(Qt.DotLine)
            pen.setDashOffset(self.overlay.ants_offset)
            painter.setPen(pen)
            painter.drawRect(
                QRectF(
                    self.overlay.start_scene_pos, self.overlay.cur_scene_pos
                )
            )

    def drawBackground(self, painter, rect):
        """Draw the magenta transparency background, used by the sprite canvas

        :param painter: QPainter object to paint with
        :type painter: QPainter
        :param rect: Exposed rectangle to paint over
        :type rect: QRectF
        """
        painter.setBrush(QBrush(Qt.magenta, Qt.SolidPattern))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.subject.width, self.subject.height)
