pyrcc5 -o src/views/resources_rc.py ./res/resources.qrc
pyuic5 --from-imports -o src/views/main_window_ui.py ./res/ui/MainWindow.ui
pyuic5 --from-imports -o src/views/pixel_palette_ui.py ./res/ui/PixelPalette.ui
pyuic5 --from-imports -o src/views/color_palette_ui.py ./res/ui/ColorPalette.ui
pyuic5 --from-imports -o src/views/preferences_dialog_ui.py ./res/ui/PreferencesDialog.ui
pyuic5 --from-imports -o src/views/color_preview_ui.py ./res/ui/ColorPreview.ui
pyuic5 --from-imports -o src/views/color_picker_dialog_ui.py ./res/ui/ColorPickerDialog.ui
pyuic5 --from-imports -o src/views/tile_map_picker.py ./res/ui/TileMapPicker.ui
