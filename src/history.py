from PyQt5.QtWidgets import QUndoCommand


class cmdSetCol(QUndoCommand):
    """Sets a color in a color palette

    :param palette: Target set of color palettes
    :type palette:  gamedata.ColorPalettes
    :param name:    Name of target color palette
    :type name:     str
    :param index:   Index of target color
    :type index:    int
    :param color:   New color to set to
    :type color:    QColor
    :param orig:    Original color
    :type orig:     QColor
    :param desc:    Text description of action
    :type desc:     Str
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, data_source, palette_name, update_color, update_index, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.update_index = update_index
        self.update_color = update_color
        self.original_color = self.data_source.get_color_palette(palette_name)[update_index]

    def redo(self):
        """Redo setting a color
        """
        self.data_source.update_color(self.palette_name, self.update_color, self.update_index)

    def undo(self):
        """Undo setting a color
        """
        self.data_source.update_color(self.palette_name, self.original_color, self.update_index)

class cmdRenameColPal(QUndoCommand):
    """Set the name of a color palette

    :param palette:     Target set of color palettes
    :type palette:      gamedata.ColorPalettes
    :param cur_name:    Target name of color palette
    :type cur_name:     str
    :param new_name:    New name for color palette
    :type new_name:     str
    :param desc:        Text description of action
    :type desc:         str
    :param parent:      Parent widget, defaults to None
    :type parent:       QWidget, optional
    """

    def __init__(self, data_source, current_name, new_name, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.current_name = current_name
        self.new_name = new_name

    def redo(self):
        """Redo setting a color palette name
        """
        self.data_source.rename_color_palette(self.current_name, self.new_name)

    def undo(self):
        """Undo setting a color palette name
        """
        self.data_source.rename_color_palette(self.new_name, self.current_name)


class cmdAddColPal(QUndoCommand):
    """Add a new sprite/tile color palette

    :param palette:     Target set of color palettes
    :type palette:      gamedata.ColorPalettes
    :param name:        Name of target color palette
    :type name:         str
    :param contents:    Contents of new color palette
    :type contents:     list
    :param desc:        Text description of action
    :type desc:         str
    :param parent:      Parent widget, defaults to None
    :type parent:       QWidget, optional
    """

    def __init__(self, data_source, palette_name, palette_contents, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.palette_contents = palette_contents

    def redo(self):
        """Redo adding a color palette
        """
        self.data_source.add_color_palette(self.palette_name, self.palette_contents)

    def undo(self):
        """Undo adding a color palette
        """
        self.data_source.remove_color_palette(self.palette_name)

class cmdRemoveColPal(QUndoCommand):
    """Add a new sprite/tile color palette

    :param palette:     Target set of color palettes
    :type palette:      gamedata.ColorPalettes
    :param name:        Name of target color palette
    :type name:         str
    :param contents:    Contents of new color palette
    :type contents:     list
    :param desc:        Text description of action
    :type desc:         str
    :param parent:      Parent widget, defaults to None
    :type parent:       QWidget, optional
    """

    def __init__(self, data_source, palette_name, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.original_contents = self.data_source.get_color_palette(palette_name)

    def redo(self):
        """Redo adding a color palette
        """
        self.data_source.remove_color_palette(self.palette_name)

    def undo(self):
        """Undo adding a color palette
        """
        self.data_source.add_color_palette(self.palette_name, self.original_contents)


class cmdAddPixelRow(QUndoCommand):
    """Add a row of sprite/tiles to a pixel palette

    :param palette: Target set of pixel palettes
    :type palette:  gamedata.PixelPalettes
    :param desc:    Text description of action
    :type desc:     str
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, data_source, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source

    def redo(self):
        """Redo adding a row of sprites/tiles
        """
        self.data_source.add_palette_row()

    def undo(self):
        """Undo addign a row of sprites/tiles
        """
        self.data_source.remove_palette_row()


class cmdRemovePixelRow(QUndoCommand):
    """Add a row of sprite/tiles to a pixel palette

    :param palette: Target set of pixel palettes
    :type palette:  gamedata.PixelPalettes
    :param desc:    Text description of action
    :type desc:     str
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, data_source, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.removed_row = None

    def redo(self):
        """Redo adding a row of sprites/tiles
        """
        self.removed_row = self.data_source.remove_palette_row()

    def undo(self):
        """Undo addign a row of sprites/tiles
        """
        self.data_source.add_palette_row(self.removed_row)

class cmdSetAssetName(QUndoCommand):
    """Add a row of sprite/tiles to a pixel palette

    :param palette: Target set of pixel palettes
    :type palette:  gamedata.PixelPalettes
    :param desc:    Text description of action
    :type desc:     str
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, data_source, asset_index, new_asset_name, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.asset_index = asset_index
        self.new_asset_name = new_asset_name
        self.original_asset_name = None

    def redo(self):
        """Redo adding a row of sprites/tiles
        """
        self.original_asset_name = self.data_source.get_name(self.asset_index)
        self.data_source.set_asset_name(self.asset_index, self.new_asset_name)

    def undo(self):
        """Undo addign a row of sprites/tiles
        """
        self.data_source.set_asset_name(self.asset_index, self.original_asset_name)

class cmdAddTileMap(QUndoCommand):
    """Add a new sprite/tile color palette

    :param palette:     Target set of color palettes
    :type palette:      gamedata.ColorPalettes
    :param name:        Name of target color palette
    :type name:         str
    :param contents:    Contents of new color palette
    :type contents:     list
    :param desc:        Text description of action
    :type desc:         str
    :param parent:      Parent widget, defaults to None
    :type parent:       QWidget, optional
    """

    def __init__(self, data_source, tile_map_name, tile_map_contents, desc, parent=None):
        super().__init__(desc, parent)
        self.data_source = data_source
        self.tile_map_name = tile_map_name
        self.tile_map_contents = tile_map_contents

    def redo(self):
        """Redo adding a tile map
        """
        self.data_source.add_tile_map(self.tile_map_name, self.tile_map_contents)

    def undo(self):
        """Undo adding a tile map
        """
        self.data_source.remove_color_palette(self.palette_name)