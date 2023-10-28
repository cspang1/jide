pyrcc5 -o src/ui/resources_rc.py ./res/resources.qrc
pyuic5 --from-imports -o src/ui/main_window_ui.py ./res/ui/MainWindow.ui
pyuic5 --from-imports -o src/ui/pixel_palette_ui.py ./res/ui/PixelPalette.ui
pyuic5 --from-imports -o src/ui/color_palette_ui.py ./res/ui/ColorPalette.ui
pyuic5 --from-imports -o src/ui/preferences_dialog_ui.py ./res/ui/PreferencesDialog.ui
pyuic5 --from-imports -o src/ui/color_preview_ui.py ./res/ui/ColorPreview.ui
pyuic5 --from-imports -o src/ui/color_picker_dialog_ui.py ./res/ui/ColorPickerDialog.ui
pyuic5 --from-imports -o src/ui/tile_map_picker.py ./res/ui/TileMapPicker.ui
