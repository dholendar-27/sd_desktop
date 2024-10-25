import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CustomCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(22, 22)
        self.tick_icon = None  # Placeholder for tick icon
        self.unchecked_icon = None  # Placeholder for unchecked icon

        # Initialize with default stylesheet
        self.updateStyleSheet()

    def updateStyleSheet(self):
        """Update the stylesheet with provided image paths."""
        tick_icon_path = f"url('{self.tick_icon}')" if self.tick_icon else ""
        unchecked_icon_path = f"url('{self.unchecked_icon}')" if self.unchecked_icon else ""

        self.setStyleSheet(f"""
            QCheckBox {{
                background: none;  /* Hide default checkbox background */
                border: none;  /* Hide default checkbox border */
                width: 22px;
                height: 22px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
            }}
            QCheckBox::indicator:checked {{
                image: {tick_icon_path}; /* Set the tick image */
            }}
            QCheckBox::indicator:unchecked {{
                image: {unchecked_icon_path}; /* Set the unchecked image */
            }}
        """)

    def setTickImage(self, image_path: str):
        """Set the tick image dynamically."""
        self.tick_icon = image_path
        self.updateStyleSheet()

    def setUncheckedImage(self, image_path: str):
        """Set the unchecked image dynamically."""
        self.unchecked_icon = image_path
        self.updateStyleSheet()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.checkbox = CustomCheckBox("Custom Checkbox")
        layout.addWidget(self.checkbox)

        # Set dynamic images (replace with actual paths)
        self.checkbox.setTickImage("/Users/pothireddy/Documents/Sundial/v2.0.0/activitywatch/sd-qt/sd_qt/sd_desktop/resources/LightTheme/checkedbox.svg")  # Path to tick image
        self.checkbox.setUncheckedImage("/Users/pothireddy/Documents/Sundial/v2.0.0/activitywatch/sd-qt/sd_qt/sd_desktop/resources/LightTheme/checkbox.svg")  # Path to unchecked image

        self.setLayout(layout)
        self.setWindowTitle("Custom Checkbox Example")
        self.setGeometry(100, 100, 300, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
