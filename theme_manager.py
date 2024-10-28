# theme_manager.py
from qt_material import apply_stylesheet
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

class ThemeManager(QObject):
    _instance = None

    theme_changed = Signal(str)  # Signal to notify theme change

    @staticmethod
    def get_instance():
        if ThemeManager._instance is None:
            ThemeManager()
        return ThemeManager._instance

    def __init__(self):
        super().__init__()
        if ThemeManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ThemeManager._instance = self
            self.current_theme = "light"

    def apply_light_theme(self, widget):
        if self.current_theme != "light":
            apply_stylesheet(widget, theme='light_cyan_500.xml')
            self.current_theme = "light"
            self.theme_changed.emit("light")

    def apply_dark_theme(self, widget):
        if self.current_theme != "dark":
            apply_stylesheet(widget, theme='dark_teal.xml')
            self.current_theme = "dark"
            self.theme_changed.emit("dark")

    def toggle_theme(self, widget):
        """Toggle between light and dark themes."""
        if self.current_theme == "light":
            self.apply_dark_theme(widget)
        else:
            self.apply_light_theme(widget)

    def set_theme_based_on_system(self, widget=None):
        """Set the theme based on the system's current theme."""
        # If widget is None, use QApplication's palette as a fallback
        if widget is None:
            widget = QApplication.instance()

        if widget:
            current_palette = widget.palette()
            if current_palette.color(QPalette.ColorRole.Window).lightness() > 128:
                self.apply_light_theme(widget)
            else:
                self.apply_dark_theme(widget)
        else:
            print("No valid widget found to determine the theme.")
