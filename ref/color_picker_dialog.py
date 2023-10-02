from math import pow
from PyQt5.QtWidgets import (
    QDialog
)
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
from ui.color_picker_dialog_ui import Ui_color_picker_dialog
from color_data import upsample, downsample

class ColorPickerDialog(QDialog, Ui_color_picker_dialog):
    def __init__(self, index, color, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.index = index
        self.color = color

        self.color_swatches_grid.color_selected.connect(self.color_selected)
        self.color_swatches_grid.select_color(color)

        e_bit_red_width = 3
        e_bit_green_width = 3
        e_bit_blue_width = 2
        f_color_red_width = 8
        f_color_green_width = 8
        f_color_blue_width = 8

        self.e_bit_red_value.setValidator(ColorValidator(pow(2, e_bit_red_width) - 1))
        self.e_bit_green_value.setValidator(ColorValidator(pow(2, e_bit_green_width) - 1))
        self.e_bit_blue_value.setValidator(ColorValidator(pow(2, e_bit_blue_width) - 1))
        self.e_bit_hex_value.setValidator(
            QRegExpValidator(QRegExp(r"#?(?:[0-9a-fA-F]{2})"))
        )
        self.f_color_red_value.setValidator(ColorValidator(pow(2, f_color_red_width) - 1))
        self.f_color_green_value.setValidator(ColorValidator(pow(2, f_color_green_width) - 1))
        self.f_color_blue_value.setValidator(ColorValidator(pow(2, f_color_blue_width) - 1))
        self.f_color_hex_value.setValidator(
            QRegExpValidator(QRegExp(r"#?(?:[0-9a-fA-F]{6})"))
        )
        self.e_bit_red_value.editingFinished.connect(self.e_bit_color_changed)
        self.e_bit_green_value.editingFinished.connect(self.e_bit_color_changed)
        self.e_bit_blue_value.editingFinished.connect(self.e_bit_color_changed)
        self.f_color_red_value.editingFinished.connect(self.f_color_changed)
        self.f_color_green_value.editingFinished.connect(self.f_color_changed)
        self.f_color_blue_value.editingFinished.connect(self.f_color_changed)

    def e_bit_color_changed(self):
        r, g, b = downsample(
            int(self.f_color_red_value.text()),
            int(self.f_color_green_value.text()),
            int(self.f_color_blue_value.text())
            )
        r = r if self.e_bit_red_value.text() == "" else int(self.e_bit_red_value.text())
        g = g if self.e_bit_green_value.text() == "" else int(self.e_bit_green_value.text())
        b = b if self.e_bit_blue_value.text() == "" else int(self.e_bit_blue_value.text())
        self.color_swatches_grid.select_color(QColor(*upsample(r, g, b)))

    def f_color_changed(self):
        r, g, b = upsample(
            int(self.e_bit_red_value.text()),
            int(self.e_bit_green_value.text()),
            int(self.e_bit_blue_value.text())
            )
        print(f'Before: {r}, {g}, {b}')
        r = r if self.f_color_red_value.text() == "" else int(self.f_color_red_value.text())
        g = g if self.f_color_green_value.text() == "" else int(self.f_color_green_value.text())
        b = b if self.f_color_blue_value.text() == "" else int(self.f_color_blue_value.text())
        print(f'After: {r}, {g}, {b}')
        self.color_swatches_grid.select_color(QColor(r, g, b))

    def color_selected(self, color):
        print(f'Selecting: {color.red()}, {color.green()}, {color.blue()}')
        preview_palette = self.color_preview.palette()
        preview_palette.setColor(self.color_preview.backgroundRole(), color)
        self.color_preview.setPalette(preview_palette)

        e_bit_red, e_bit_green, e_bit_blue = downsample(color.red(), color.green(), color.blue())
        e_bit_hex = format(
            (e_bit_red << 5) | (e_bit_green << 2) | e_bit_blue, "X"
        ).zfill(2)
        self.e_bit_red_value.setText(str(e_bit_red))
        self.e_bit_green_value.setText(str(e_bit_green))
        self.e_bit_blue_value.setText(str(e_bit_blue))
        self.e_bit_hex_value.setText("#" + e_bit_hex)
        self.f_color_red_value.setText(str(color.red()))
        self.f_color_green_value.setText(str(color.green()))
        self.f_color_blue_value.setText(str(color.blue()))
        self.f_color_hex_value.setText(color.name().upper())

class ColorValidator(QValidator):
    def __init__(self, top, parent=None):
        super().__init__(parent)
        self.top = top

    def validate(self, value, pos):
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