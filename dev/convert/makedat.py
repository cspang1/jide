from __future__ import print_function
from itertools import zip_longest
import json
import os
import sys
import argparse
import re

def byteify(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def parse_hex(src, bytes_per_gp, perline, name, regex):
    data = []
    name_index = 0
    sprite_index = 0
    contents = ""
    regex = re.compile(regex)
    for line in src:
        for result in re.findall(regex, line):
            if sprite_index == 0:
                spr_name = name + str(name_index)
                name_index += 1
            result = result.replace("_","")
            contents += result
            sprite_index += 1
            if sprite_index == perline:
                contents = list(contents)
                if perline == 8:
                    contents = [int(x,16) for x in contents]
                if perline == 16:
                    contents = [x+y for x,y in zip(contents[0::2], contents[1::2])]
                    contents = [int(x,16) for x in contents]
                if perline == 56*34:
                    contents = [x+y for x,y in zip(contents[0::2], contents[1::2])]
                    contents = [int(x,16) for x in contents]
                    contents = [contents[i:i+2] for i in range (0, len(contents), 2)]
                data.append({
                    "name": spr_name,
                    "contents": contents
                })
                contents = []
                sprite_index = 0
    return data

def parse_colors(resource_file, name):
    return parse_hex(resource_file, 2, 16, name, r'(?<=\$)[0-9A-F]{2}')

def parse_tiles(resource_file, name):
    return parse_hex(resource_file, 8, 8, name, r'(?<=\$)[0-9A-F_]{15}')

def parse_tile_maps(resource_file, name):
    return parse_hex(resource_file, 4, 56*34, name, r'(?<=\$)[0-9A-F_]{5}')

def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('sprites', help="Sprites file", type=argparse.FileType('r'))
    parser.add_argument('tiles', help="Tiles file", type=argparse.FileType('r'))
    parser.add_argument('sprite_colors', help="Sprite color palettes file", type=argparse.FileType('r'))
    parser.add_argument('tile_colors', help="Tile color palettes file", type=argparse.FileType('r'))
    parser.add_argument('tile_maps', help="Tile maps file", type=argparse.FileType('r'))
    parser.add_argument('outfile', help="Output file", type=argparse.FileType('w'))

    args = parser.parse_args(arguments)

    data = {}
    data["gameName"] = "JCAP Demo"
    data["sprites"] = []
    data["tiles"] = []
    data["spriteColorPalettes"] = []
    data["tileColorPalettes"] = []
    data["tileMaps"] = []

    # Parse sprites
    with open(args.sprites.name, args.sprites.mode) as resource_file:
        data["sprites"] = parse_tiles(resource_file, "sprite")

    # Parse tiles
    with open(args.tiles.name, args.tiles.mode) as resource_file:
        data["tiles"] = parse_tiles(resource_file, "tile")

    # Parse sprite color palettes
    with open(args.sprite_colors.name, args.sprite_colors.mode) as resource_file:
        data["spriteColorPalettes"] = parse_colors(resource_file, "sprite_color_palette")

    # Parse tile color palettes
    with open(args.tile_colors.name, args.tile_colors.mode) as resource_file:
        data["tileColorPalettes"] = parse_colors(resource_file, "tile_color_palette")

    # Parse tile maps
    with open(args.tile_maps.name, args.tile_maps.mode) as resource_file:
        data["tileMaps"] = parse_tile_maps(resource_file, "tile_map")

    with open(args.outfile.name, args.outfile.mode) as dat_file:
        json.dump(data, dat_file, indent=4)

    with open(args.outfile.name) as json_file:
        data = json.load(json_file)
        for tileMap in data["tileMaps"]:
            print(len(tileMap["contents"]))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))