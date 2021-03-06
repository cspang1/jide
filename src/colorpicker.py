from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRegExp, QEvent
from PyQt5.QtGui import (
    QColor,
    QValidator,
    QPixmap,
    QFont,
    QRegExpValidator,
    QPainter,
    QPen,
)
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QDialogButtonBox,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QLayout,
)


def upsample(red, green, blue):
    """Upsamples RGB from 8-bit to 24-bit

    :param red:     8-bit red value
    :type red:      int
    :param green:   8-bit green value
    :type green:    int
    :param blue:    8-bit blue value
    :type blue:     int
    :return:        24-bit upscaled RGB tuple
    :rtype:         tuple(int, int, int)
    """
    red = round((red / 7) * 255)
    green = round((green / 7) * 255)
    blue = round((blue / 3) * 255)
    return (red, green, blue)


def downsample(red, green, blue):
    """Downsamples RGB from 24-bit to 8-bit

    :param red:     24-bit red value
    :type red:      int
    :param green:   24-bit green value
    :type green:    int
    :param blue:    24-bit blue value
    :type blue:     int
    :return:        8-bit downscaled RGB tuple
    :rtype:         tuple(int, int, int)
    """
    red = round((red / 255) * 7)
    green = round((green / 255) * 7)
    blue = round((blue / 255) * 3)
    return (red, green, blue)


def normalize(red, green, blue):
    """Normalizes any RGB value to be representable by a whole 8-bit value

    :param red:     Red value
    :type red:      int
    :param green:   Green value
    :type green:    int
    :param blue:    Blue value
    :type blue:     int
    :return:        24-bit normalized RGB tuple
    :rtype:         tuple(int, int, int)
    """
    return upsample(*downsample(red, green, blue))


class Color(QLabel):
    """Represents a single color tile in the color picker

    :param index:   Index of the color tile
    :type index:    int
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    color = QColor()
    clicked = pyqtSignal(QColor)
    color_selected = pyqtSignal(int)

    def __init__(self, index, parent=None):
        QLabel.__init__(self, parent)
        self.index = index
        self.setPixmap(QPixmap(25, 25))
        self.selected = False

    def fill(self, color):
        """Fills the tile with the specified color

        :param color:   Target color
        :type color:    QColor
        """
        self.color = color
        self.pixmap().fill(self.color)

    def paintEvent(self, event):
        """Paint event for the color tile which draws the grid

        :param event:   QPaintEvent event
        :type event:    QPaintEvent
        """
        super().paintEvent(event)
        painter = QPainter(self)
        if self.selected:
            pen = QPen(Qt.red)
            pen.setWidth(5)
        else:
            pen = QPen(Qt.black)
            pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, 24, 24)

    def mousePressEvent(self, event):
        """Handles clicking on the color tile to select it

        :param event:   Source event
        :type event:    QMouseEvent
        """
        self.clicked.emit(self.color)
        self.select()

    def select(self):
        """Handles selecting the color tile
        """
        self.selected = True
        self.color_selected.emit(self.index)
        self.update()

    def deselect(self):
        """Handles de-selecting the color tile
        """
        self.selected = False
        self.update()


class ColorPalette(QFrame):
    """Represents the entire grid of color tiles in the color picker
    """

    def __init__(self):
        super().__init__()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.palette = [Color(n) for n in range(256)]
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.setFixedSize(
            400 + self.lineWidth() * 2, 400 + self.lineWidth() * 2
        )
        positions = [(row, col) for row in range(16) for col in range(16)]
        colors = [
            (red, green, blue)
            for blue in range(4)
            for red in range(8)
            for green in range(8)
        ]
        for position, color, swatch in zip(positions, colors, self.palette):
            color = QColor(*upsample(*color))
            swatch.fill(color)
            swatch.color_selected.connect(self.selectColor)
            self.grid.addWidget(swatch, *position)
        self.enabled = False

    pyqtSlot(int)

    def selectColor(self, index):
        """Selects a color in the color picker

        :param index:   Index of the selected color
        :type index:    int
        """
        for idx in range(self.grid.count()):
            if idx != index:
                self.grid.itemAt(idx).widget().deselect()


class ColorValidator(QValidator):
    """Provides input field validation to color picker RGB values

    :param top:     RGB value ceiling
    :type top:      int
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, top, parent=None):
        super().__init__(parent)
        self.top = top

    def validate(self, value, pos):
        """Validates an RGB input

        :param value:   Value of the RGB input
        :type value:    int
        :param pos:     Position of the cursor in the input field
        :type pos:      int
        :return:        Result of the validation
        :rtype:         QValidator
        """
        if value != "":
            try:
                int(value)
            except ValueError:
                return (QValidator.Invalid, value, pos)
        else:
            return (QValidator.Acceptable, value, pos)
        if 0 <= int(value) <= self.top:
            return (QValidator.Acceptable, value, pos)
        else:
            return (QValidator.Invalid, value, pos)


class ColorPicker(QDialog):
    """Represents the dialog containing the color picker

    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    preview_color = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Color")
        actions = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        actions.accepted.connect(self.accept)
        actions.rejected.connect(self.reject)
        self.color = QColor()

        dialog_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        value_layout = QVBoxLayout()
        eight_bit_form = QFormLayout()
        fullcolor_form = QFormLayout()

        self.preview = QLabel()
        self.preview_pixmap = QPixmap(100, 50)
        self.preview.setFrameShape(QFrame.Panel)
        self.preview.setFrameShadow(QFrame.Sunken)
        self.preview.setLineWidth(3)
        self.preview.setScaledContents(True)
        value_layout.addWidget(self.preview)

        header = QFont()
        header.setBold(True)
        ebframe = QFrame()
        ebframe.setFrameShape(QFrame.StyledPanel)
        eight_bit_form.addRow(QLabel("8-bit color"))
        eight_bit_form.itemAt(0).setAlignment(Qt.AlignCenter)
        eight_bit_form.itemAt(0).widget().setFont(header)
        self.r8 = QLineEdit()
        self.r8.setFixedWidth(60)
        self.r8.setValidator(ColorValidator(7))
        self.r8.editingFinished.connect(self.set8BitColors)
        self.g8 = QLineEdit()
        self.g8.setFixedWidth(60)
        self.g8.setValidator(ColorValidator(7))
        self.g8.editingFinished.connect(self.set8BitColors)
        self.b8 = QLineEdit()
        self.b8.setFixedWidth(60)
        self.b8.setValidator(ColorValidator(3))
        self.b8.editingFinished.connect(self.set8BitColors)
        self.hex8 = QLineEdit()
        self.hex8.setValidator(
            QRegExpValidator(QRegExp(r"#?(?:[0-9a-fA-F]{2})"))
        )
        self.hex8.setFixedWidth(60)
        self.hex8.editingFinished.connect(self.set8BitHex)
        self.hex8.installEventFilter(self)
        eight_bit_form.addRow(QLabel("Red:"), self.r8)
        eight_bit_form.addRow(QLabel("Green:"), self.g8)
        eight_bit_form.addRow(QLabel("Blue:"), self.b8)
        eight_bit_form.addRow(QLabel("Hex:"), self.hex8)
        ebframe.setLayout(eight_bit_form)
        value_layout.addWidget(ebframe)

        fcframe = QFrame()
        fcframe.setFrameShape(QFrame.StyledPanel)
        fullcolor_form.addRow(QLabel("Full color"))
        fullcolor_form.itemAt(0).setAlignment(Qt.AlignCenter)
        fullcolor_form.itemAt(0).widget().setFont(header)
        self.r24 = QLineEdit()
        self.r24.setFixedWidth(60)
        self.r24.setValidator(ColorValidator(255))
        self.r24.editingFinished.connect(self.set24BitColors)
        self.g24 = QLineEdit()
        self.g24.setValidator(ColorValidator(255))
        self.g24.setFixedWidth(60)
        self.g24.editingFinished.connect(self.set24BitColors)
        self.b24 = QLineEdit()
        self.b24.setValidator(ColorValidator(255))
        self.b24.setFixedWidth(60)
        self.b24.editingFinished.connect(self.set24BitColors)
        self.hex24 = QLineEdit()
        self.hex24.setValidator(
            QRegExpValidator(QRegExp(r"#?(?:[0-9a-fA-F]{6})"))
        )
        self.hex24.setFixedWidth(60)
        self.hex24.installEventFilter(self)
        fullcolor_form.addRow(QLabel("Red:"), self.r24)
        fullcolor_form.addRow(QLabel("Green:"), self.g24)
        fullcolor_form.addRow(QLabel("Blue:"), self.b24)
        fullcolor_form.addRow(QLabel("Hex:"), self.hex24)
        fcframe.setLayout(fullcolor_form)
        value_layout.addWidget(fcframe)

        self.color_palette = ColorPalette()
        for swatch in self.color_palette.palette:
            swatch.clicked.connect(self.setColor)
        main_layout.addWidget(self.color_palette)
        main_layout.addLayout(value_layout)
        dialog_layout.setSizeConstraint(QLayout.SetFixedSize)
        dialog_layout.addLayout(main_layout)
        dialog_layout.addWidget(actions)

        self.setLayout(dialog_layout)

    def eventFilter(self, source, event):
        """Event filter to handle the dialog losing focus

        :param source:  Event source
        :type source:   QObject
        :param event:   Source event
        :type event:    QEvent
        :return:        Whether to handle the event further down
        :rtype:         bool
        """
        if event.type() == QEvent.FocusOut:
            if source is self.hex8:
                self.set8BitHex()
            else:
                self.set24BitHex()
        return False

    def getColor(self):
        """Gets the chosen color from the color picker

        :return:    Chosen color
        :rtype:     QColor
        """
        return self.color

    @pyqtSlot(QColor)
    def setColor(self, value):
        """Sets the chosen color of the color picker

        :param value:   The color to be set
        :type value:    QColor
        """
        self.color = QColor(
            *normalize(value.red(), value.green(), value.blue())
        )
        self.preview_color.emit(self.color)
        self.preview_pixmap.fill(self.color)
        self.preview.setPixmap(self.preview_pixmap)
        self.cur_r24 = self.color.red()
        self.cur_g24 = self.color.green()
        self.cur_b24 = self.color.blue()
        self.cur_hex24 = self.color.name().upper()
        self.r24.setText(str(self.cur_r24))
        self.g24.setText(str(self.cur_g24))
        self.b24.setText(str(self.cur_b24))
        self.hex24.setText(self.cur_hex24)

        for swatch in self.color_palette.palette:
            if swatch.color == self.color:
                swatch.select()

        self.cur_r8, self.cur_g8, self.cur_b8 = downsample(
            self.cur_r24, self.cur_g24, self.cur_b24
        )
        self.cur_hex8 = format(
            (self.cur_r8 << 5) | (self.cur_g8 << 2) | self.cur_b8, "X"
        ).zfill(2)
        self.r8.setText(str(self.cur_r8))
        self.g8.setText(str(self.cur_g8))
        self.b8.setText(str(self.cur_b8))
        self.hex8.setText("#" + self.cur_hex8)

    def set8BitColors(self):
        """Sets the active color to that chosen by the 8-bit input fields
        """
        r = self.cur_r8 if self.r8.text() == "" else int(self.r8.text())
        g = self.cur_g8 if self.g8.text() == "" else int(self.g8.text())
        b = self.cur_b8 if self.b8.text() == "" else int(self.b8.text())
        self.setColor(QColor(*upsample(r, g, b)))

    def set24BitColors(self):
        """Sets the active color to that chosen by the 24-bit input fields
        """
        r = self.cur_r24 if self.r24.text() == "" else int(self.r24.text())
        g = self.cur_g24 if self.g24.text() == "" else int(self.g24.text())
        b = self.cur_b24 if self.b24.text() == "" else int(self.b24.text())
        self.setColor(QColor(r, g, b))

    def set8BitHex(self):
        """Sets the active color to that chosen by the 8-bit hex input field
        """
        hex = self.hex8.text().lstrip("#")
        hex = int(self.cur_hex8, 16) if hex == "" else int(hex, 16)
        r = (hex >> 5) & 7
        g = (hex >> 2) & 7
        b = hex & 3
        self.setColor(QColor(*upsample(r, g, b)))

    def set24BitHex(self):
        """Sets the active color to that chosen by the 24-bit hex input field
        """
        hex = self.hex24.text().lstrip("#")
        hex = self.cur_hex24 if hex == "" else "#" + hex.zfill(6)
        self.setColor(QColor(hex))
