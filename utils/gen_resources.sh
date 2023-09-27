pyrcc5 -o resources_rc.py ./res/resources.qrc
pyuic5 -o ref/ui/main_window_ui.py ./res/ui/MainWindow.ui
pyuic5 -o ref/ui/pixel_palette_ui.py ./res/ui/PixelPalette.ui
pyuic5 -o ref/ui/color_palette_ui.py ./res/ui/ColorPalette.ui
pyuic5 -o ref/ui/preferences_dialog_ui.py ./res/ui/PreferencesDialog.ui
pyuic5 -o ref/ui/color_preview_ui.py ./res/ui/ColorPreview.ui
pyuic5 -o ref/ui/color_picker_dialog_ui.py ./res/ui/ColorPickerDialog.ui
