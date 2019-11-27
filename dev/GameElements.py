from dataclasses import dataclass, field
from typing import List
import inspect
from colr import Colr as C

@dataclass
class Color:
    red: int = 0
    green: int = 0
    blue: int = 0 

    def validate_color(func):
        sig = inspect.signature(func)
        def wrapper(cls, *args, **kwargs):
            bound_args = sig.bind(cls, *args, **kwargs)
            bound_args.apply_defaults()
            bound_args = tuple(bound_args.arguments.values())
            if len(bound_args) is 5:
                if bound_args[4]:
                    for color in bound_args[1:4]:
                        if 0 > color or color > 255:
                            raise AttributeError
                else:
                    for color in bound_args[1:3]:
                        if 0 > color or color > 7:
                            raise AttributeError
                    if 0 > bound_args[3] or bound_args[3] > 3:
                        raise AttributeError
            elif len(bound_args) is 3:
                if (bound_args[2] and bound_args[1] > 0xFFFFFF) or (not bound_args[2] and bound_args[1] > 0xFF):
                    raise AttributeError
            else:
                raise AttributeError
            return func(cls, *bound_args[1:5])
        return wrapper

    def downsample(red, green, blue):
        red = round((red/255)*7)
        green = round((green/255)*7)
        blue = round((blue/255)*3)
        return (red, green, blue)

    def upsample(self):
        red = round((self.red/7)*255)
        green = round((self.green/7)*255)
        blue = round((self.blue/3)*255)
        return (red, green, blue)

    def __repr__(self):
        return '0x{:02X}'.format((self.red << 5) | (self.green << 2) | (self.blue))

    @classmethod
    @validate_color
    def from_RGB_comps(cls, red, green, blue, true_color=False):
        if true_color:
            return cls(*cls.downsample(red, green, blue))
        return cls(red, green, blue)

    @classmethod
    @validate_color
    def from_RGB(cls, rgb, true_color=False):
        red = rgb >> (16 if true_color else 5)
        green = rgb >> (8 if true_color else 2) & (0xFF if true_color else 0x7)
        blue = rgb & (0xFF if true_color else 0x3)
        if true_color:
            return cls(*cls.downsample(red, green, blue))
        return cls(red, green, blue)

@dataclass
class ColorPalette:
    palette: List[Color] = field(default_factory=lambda: [Color()]*16)

    def __repr__(self):
        return "\n".join(map(str, zip(*(iter(self.palette),) * 4)))

    def set_color(self, index, color:Color):
        self.palette[index] = color

    def get_color(self, index) -> Color:
        return self.palette[index]

@dataclass
class TilePalette:
    pixels: List[int] = field(default_factory=lambda: [0]*64)

    def __repr__(self):
        return "\n".join(map(str, zip(*(iter(self.pixels),) * 8)))

    def set_pixel(self, index, color_index):
        self.pixels[index] = color_index

    def get_pixel(self, index) -> int:
        return self.pixels[index]

def render(tile_palette:TilePalette, color_palette:ColorPalette):
    for iter in range(8):
        print(
            C()
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+0]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+1]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+2]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+3]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+4]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+5]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+6]).upsample()).rgb(0, 0, 0, '  ')
            .b_rgb(*color_palette.get_color(tile_palette.pixels[iter*8+7]).upsample()).rgb(0, 0, 0, '  ')
        )

try:

    c = ColorPalette(
        [
            Color.from_RGB(0xFF00FF, True), Color.from_RGB(0xEC), Color.from_RGB(0xF4), Color.from_RGB(0x0B),
            Color.from_RGB(0xFF), Color.from_RGB(0x00), Color.from_RGB(0x00), Color.from_RGB(0x00),
            Color.from_RGB(0x00), Color.from_RGB(0x00), Color.from_RGB(0x00), Color.from_RGB(0x00),
            Color.from_RGB(0x00), Color.from_RGB(0x00), Color.from_RGB(0x00), Color.from_RGB(0x00)
        ]
    )

    t = TilePalette(
        [
            0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,
            1,1,1,1,0,0,0,0,
            1,2,2,1,0,0,0,0,
            2,2,3,2,1,1,0,0,
            1,4,2,2,2,2,1,1,
            1,4,4,4,4,4,4,5
        ]
    )

    render(t,c)

except AttributeError:
    print("Invalid RGB values")
