from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from colorpalette import upsample
import json

class GameData(QObject):
    def __init__(self, data):
        QObject.__init__(self)
        self.sprite_color_palettes = {}
        for spr_pal in data["spriteColorPalettes"]:
            palette = spr_pal["contents"]
            palette[:] = [QColor(*upsample(color>>5, (color>>2)&7, color&3)) for color in palette]
            palette[0] = QColor(0,0,0,0)
            self.sprite_color_palettes[spr_pal["name"]] = palette
        self.tile_color_palettes = {}
        for tile_pal in data["tileColorPalettes"]:
            self.tile_color_palettes[tile_pal["name"]] = tile_pal["contents"]
        self.sprite_pixel_palettes = {}
        for sprite in data["sprites"]:
            self.sprite_pixel_palettes[sprite["name"]] = sprite["contents"]
        self.tile_pixel_palettes = {}
        for tile in data["tiles"]:
            self.tile_pixel_palettes[tile["name"]] = tile["contents"]
        self.tile_maps = {}
        for tile_map in data["tileMaps"]:
            self.tile_maps[tile_map["name"]] = tile_map["contents"]

    def getSprite(self, name):
        return self.sprite_pixel_palettes[name]

    def getTile(self, name):
        return self.tile_pixel_palettes[name]

    def getSprColPal(self, name):
        return self.sprite_color_palettes[name]

    def getTileColPal(self, name):
        return self.tile_color_palettes[name]

    def getTileMap(self, name):
        return self.tile_maps[name]

    @classmethod
    def from_filename(cls, file_name):
        with open(file_name, 'r') as data_file:
                return cls(json.load(data_file))
