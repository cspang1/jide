import json
import sys, os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
import pytest

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide
from source import Source
from colorpicker import upsample

dat_path = Path(__file__).parents[1] / "data" / "demo.jrf"


@pytest.fixture
def jide_instance(qtbot):
    app = jide()
    qtbot.addWidget(app)
    app.loadProject(dat_path)
    return app


def test_file_open(jide_instance):
    assert jide_instance.data.getGameName() == "JCAP Demo"


class TestDataLoad:
    @pytest.fixture(scope="class")
    def game_data(self):
        with open(dat_path, "r") as data_file:
            return json.load(data_file)

    def test_col_pal_names(self, jide_instance, game_data):
        col_pal_combo_box = jide_instance.sprite_color_palette_dock.color_palette_list
        gui_col_pal_names = [
            col_pal_combo_box.itemText(i) for i in range(col_pal_combo_box.count())
        ]
        print(gui_col_pal_names)
        dat_col_pals = []
        for col_pal in game_data["spriteColorPalettes"]:
            dat_col_pals.append(col_pal["name"])
        assert gui_col_pal_names == dat_col_pals

    def test_col_pal_contents(self, jide_instance, game_data):
        col_pal_combo_box = jide_instance.sprite_color_palette_dock.color_palette_list
        gui_col_pal_names = [
            col_pal_combo_box.itemText(i) for i in range(col_pal_combo_box.count())
        ]
        gui_col_pal = jide_instance.sprite_color_palette_dock.color_palette

        gui_pals = []
        for pal in gui_col_pal_names:
            col_pal_combo_box.setCurrentText(pal)
            gui_pals.append([col.color.rgb() for col in gui_col_pal.palette])

        data_pals = [pal["contents"] for pal in game_data["spriteColorPalettes"]]
        for pal in data_pals:
            pal[:] = [
                QColor(*upsample(color >> 5, (color >> 2) & 7, color & 3)).rgb()
                for color in pal
            ]

        assert gui_pals == data_pals
