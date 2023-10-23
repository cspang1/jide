from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QImage
from history import(
    cmd_add_tile_map
)
from collections import namedtuple

Tile = namedtuple('Tile', ['color_palette_index', 'tile_palette_index'])

class TileMapData(QObject):

    tile_map_added = pyqtSignal(str)
    tile_map_removed = pyqtSignal(str)
    tile_map_renamed = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.tile_maps = []

    def add_tile_map(self, tile_map_name, tile_map_width, tile_map_height, tile_map_data):
        tile_map = TileMap(tile_map_name, tile_map_width, tile_map_height)

        for y in range(tile_map_height):
            for x in range(tile_map_width):
                tile_data = tile_map_data[y * tile_map_width + x]
                tile_map.set_tile(x, y, tile_data[0], tile_data[1])

        self.tile_maps.append(tile_map)
        self.tile_map_added.emit(tile_map_name)

    def remove_tile_map(self, tile_map_name):
        removed_tile_map = None

        for tile_map in self.tile_maps:
            if tile_map.name == tile_map_name:
                removed_tile_map = tile_map
                self.tile_maps.remove(tile_map)

        self.tile_map_removed.emit(tile_map_name)

        return removed_tile_map

    @pyqtSlot(str, str)
    def rename_tile_map(self, old_tile_map_name, new_tile_map_name):
        for tile_map in self.tile_maps:
            if tile_map.get_name() == old_tile_map_name:
                tile_map.set_name(new_tile_map_name)

        self.tile_map_renamed.emit(old_tile_map_name, new_tile_map_name)

    def get_tile_maps(self):
        return self.tile_maps

    def get_tile_map(self, tile_map_name):
        for tile in self.tile_maps:
            if tile.name == tile_map_name:
                return tile

    def to_json(self):
        return [tile_map.to_json() for tile_map in self.tile_maps]

class TileMap:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.data = [[Tile(0, 0) for _ in range(width)] for _ in range(height)]

    def get_tile(self, x, y):
        return self.data[y][x]

    def set_tile(self, x, y, color_palette_index, tile_palette_index):
        self.data[y][x] = Tile(color_palette_index, tile_palette_index)

    def set_name(self, tile_map_name):
        self.name = tile_map_name

    def get_name(self):
        return self.name

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_data(self):
        return [tile for row in self.data for tile in row]

    def to_json(self):
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "contents": [
                [tile.color_palette_index, tile.tile_palette_index] for row in self.data for tile in row
            ]
        }
