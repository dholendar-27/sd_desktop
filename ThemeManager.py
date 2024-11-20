import sys
import qdarktheme  # type: ignore
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget
from PySide6.QtCore import QSettings, Signal, QObject
from PySide6.QtGui import QPalette, QColor, Qt




class ThemeManager(QObject):  # Inherit from QObject
    theme_Changed = Signal(str)  # Define the signal as a class attribute

    def __init__(self):
        super().__init__()
        self.settings = QSettings('ralvie.ai', 'theme')
        self.apply_theme(self.get_theme())
        self.theme_Changed.connect(self.apply_theme)  # Apply theme whenever theme_Changed is emitted

    def set_theme(self, theme: str) -> None:
        current_theme = self.get_theme()
        if theme != current_theme:
            print(f"Emitting theme_Changed signal for theme: {theme}")  # Debug
            self.settings.setValue('theme', theme)
            self.theme_Changed.emit(theme)  # Emit signal without parameters

    def get_theme(self) -> str:
        return self.settings.value('theme', 'auto')

    def apply_theme(self, theme: str) -> None:
        """
        Apply the selected theme to the application and set background color.
        """
        if theme == "dark":
            qdarktheme.setup_theme("dark")
        elif theme == "light":
            qdarktheme.setup_theme("light")
        else:  # 'auto' mode
            palette = QApplication.instance().palette()
            auto_theme = "light" if palette.color(QPalette.ColorRole.Window).lightness() > 128 else "dark"
            qdarktheme.setup_theme(auto_theme)

    def set_background_color(self, color: str) -> None:
        """
        Set the application background color.
        @param color: str, color code in hex format.
        """
        palette = QApplication.instance().palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        QApplication.instance().setPalette(palette)

    def switch_theme(self) -> None:
        current_theme = self.get_theme()
        if current_theme == "light":
            self.set_theme("dark")
        elif current_theme == "dark":
            self.set_theme("light")
        else:  # 'auto' mode, switch to light or dark based on current brightness
            palette = QApplication.instance().palette()
            auto_theme = "light" if palette.color(QPalette.ColorRole.Window).lightness() > 128 else "dark"
            self.set_theme(auto_theme)


class ThemedWidget(QWidget):
    def __init__(self, theme_manager: ThemeManager, name: str):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowTitle(name)

        # Set up a simple layout and button for theme toggle
        self.button = QPushButton(f"{name} - Toggle Theme", self)
        self.button.clicked.connect(self.toggle_theme)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Connect theme_Changed signal to update widget's theme dynamically
        self.theme_manager.theme_Changed.connect(self.update_widget_theme)

        # Initial theme application
        self.update_widget_theme(self.theme_manager.get_theme())

    def toggle_theme(self):
        self.theme_manager.switch_theme()

    def update_widget_theme(self, theme: str):
        """
        Update the widget's appearance based on the selected theme.
        """
        if theme == "dark":
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
        elif theme == "light":
            self.setStyleSheet("background-color: white; color: black;")
        else:
            self.setStyleSheet("")  # Reset to default stylesheet if 'auto'


class MainWindow(QMainWindow):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowTitle("Theme Switcher")

        # Create a stacked widget to switch between the widgets
        self.stacked_widget = QStackedWidget()

        # Create different themed widgets
        self.widget1 = ThemedWidget(theme_manager, "Widget 1")
        self.widget2 = ThemedWidget(theme_manager, "Widget 2")
        self.widget3 = ThemedWidget(theme_manager, "Widget 3")

        # Add the widgets to the stacked widget
        self.stacked_widget.addWidget(self.widget1)
        self.stacked_widget.addWidget(self.widget2)
        self.stacked_widget.addWidget(self.widget3)

        # Set the current widget to the first one (initially active)
        self.stacked_widget.setCurrentWidget(self.widget1)

        # Add the stacked widget to the main layout
        self.setCentralWidget(self.stacked_widget)

        # Add buttons to switch between the widgets
        self.button1 = QPushButton("Show Widget 1", self)
        self.button1.clicked.connect(self.show_widget1)
        self.button2 = QPushButton("Show Widget 2", self)
        self.button2.clicked.connect(self.show_widget2)
        self.button3 = QPushButton("Show Widget 3", self)
        self.button3.clicked.connect(self.show_widget3)

        # Layout to hold buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)

        button_container = QWidget()
        button_container.setLayout(button_layout)

        # Connect the theme change signal to update the window
        self.theme_manager.theme_Changed.connect(self.update_window_theme)

        # Initial theme application
        self.update_window_theme(self.theme_manager.get_theme())

    def show_widget1(self):
        self.stacked_widget.setCurrentWidget(self.widget1)

    def show_widget2(self):
        self.stacked_widget.setCurrentWidget(self.widget2)

    def show_widget3(self):
        self.stacked_widget.setCurrentWidget(self.widget3)

    def update_window_theme(self, theme: str):
        """
        Update the window theme when the global theme changes.
        """
        self.widget1.update_widget_theme(theme)
        self.widget2.update_widget_theme(theme)
        self.widget3.update_widget_theme(theme)
        self.setStyleSheet("background-color: #2e2e2e; color: white;" if theme == "dark" else "background-color: white; color: black;")


if __name__ == '__main__':
    app = QApplication([])  # Initialize QApplication
    theme_manager = ThemeManager()

    # Set up main window with theme manager
    main_window = MainWindow(theme_manager)
    main_window.show()

    sys.exit(app.exec())
