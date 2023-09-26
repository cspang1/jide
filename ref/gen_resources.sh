pyrcc5 ../res/resources.qrc -o resources_rc.py
pyuic5 -o main_window_ui.py ../res/ui/MainWindow.ui
pyuic5 -o pixel_palette_ui.py ../res/ui/PixelPalette.ui
pyuic5 -o color_palette_ui.py ../res/ui/ColorPalette.ui
pyuic5 -o preferences_dialog_ui.py ../res/ui/PreferencesDialog.ui
pyuic5 -o color_preview_ui.py ../res/ui/ColorPreview.ui