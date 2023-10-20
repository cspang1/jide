from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QImage
from history import(
    cmdAddTileMap
)
from collections import namedtuple

Tile = namedtuple('Tile', ['color_palette_index', 'tile_palette_index'])

class TileMapData(QObject):

    tile_map_added = pyqtSignal(str)
    tile_map_removed = pyqtSignal(str)
    error_thrown = pyqtSignal(str)

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
        del self.tile_maps[tile_map_name]
        self.tile_map_removed.emit(tile_map_name)

    def get_tile_maps(self):
        return self.tile_maps

    def to_json(self):
        return [tile_map.to_json() for tile_map in self.tile_maps]

class TileMap:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.contents = [[Tile(0, 0) for _ in range(width)] for _ in range(height)]

    def get_tile(self, x, y):
            return self.contents[y][x]

    def set_tile(self, x, y, color_palette_index, tile_palette_index):
            self.contents[y][x] = Tile(color_palette_index, tile_palette_index)

    def to_json(self):
         return {
              "name": self.name,
              "width": self.width,
              "height": self.height,
              "contents": [
                   [tile.color_palette_index, tile.tile_palette_index] for row in self.contents for tile in row
                ]
         }

def history_add_tile_map(undo_stack, tile_map_data, tile_map_name):
    if tile_map_name in tile_map_data.get_tile_maps():
        tile_map_data.error_thrown.emit("A tile map with that name already exists")
        return

    undo_stack.push(
        cmdAddTileMap(
            tile_map_data,
            tile_map_name,
            [0, 0] * 40 * 30,
            "Add  tile map"
        )
    )
