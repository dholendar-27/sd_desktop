import os
import sys

from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QRect, QObject, Signal
from PySide6 import QtGui, QtCore

from sd_qt.sd_desktop.toggleSwitch import SwitchControl


class Communicator(QObject):
    notify_other_classes = Signal()

class TransparentLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoFillBackground(False)
        # Set the stylesheet here to make the background transparent and customize the text color
        self.setStyleSheet("""
            background-color: transparent;
        """)

class Onboarding(QWidget):
    def __init__(self,sundial_reference, darkTheme,LightTheme):
        super().__init__()
        self.darkTheme = darkTheme
        self.LightTheme = LightTheme
        self.sundial_reference = sundial_reference
        self.setFixedSize(800, 600)
        self.onboard_layout = QStackedLayout(self)  # Use self instead of creating another QWidget
        self.onboard_layout.addWidget(self.privacyinfo())
        self.onboard_layout.addWidget(self.data_security())
        self.onboard_layout.addWidget(self.onboard_settings())
        # self.onboard_layout.addWidget(self.accessibility_permission())  # Placeholder for your actual method
        self.communicator = Communicator()
        self.onboard_layout.setContentsMargins(0, 0, 0, 0)
        self.onboard_layout.setSpacing(0)

        self.update_app_layout()  # Call the update method on initialization

    def go_to_next_page(self):
        current_index = self.onboard_layout.currentIndex()
        if current_index < self.onboard_layout.count() - 1:  # Ensure we don't go out of range
            self.onboard_layout.setCurrentIndex(current_index + 1)
            self.update_app_layout()  # No need to pass the page index

    def go_to_previous_page(self):
        current_index = self.onboard_layout.currentIndex()
        if current_index > 0:  # Ensure we don't go out of range
            self.onboard_layout.setCurrentIndex(current_index - 1)
            self.update_app_layout()  # No need to pass the page index

    def privacyinfo(self):
        self.privacy = QWidget()
        self.privacy.setStyleSheet("background: transparent;")  # Set the entire widget background to transparent

        # Background setup
        self.privacy_background = TransparentLabel(self.privacy)
        self.privacy_background.setGeometry(0, 0, 800, 600)


        # Privacy image setup
        self.privacy_img = TransparentLabel(self.privacy)
        self.privacy_img.setGeometry(395, 30, 450, 500)
        self.privacy_img.setScaledContents(True)
        self.privacy_img.setStyleSheet("background: transparent;")  # Make sure the label background is transparent

        # Sundiallogo setup
        self.privacy_sundial_logo = TransparentLabel(self.privacy)
        self.privacy_sundial_logo.setGeometry(20, 20, 150, 40)
        self.privacy_sundial_logo.setScaledContents(True)

        # Header with dynamic font sizing
        font = QtGui.QFont()
        font.setPointSize(28 if sys.platform == "darwin" else 12)
        font.setWeight(QFont.Weight.Bold)
        self.privacy_header = TransparentLabel(self.privacy)
        self.privacy_header.setGeometry(30, 160, 400, 40)
        self.privacy_header.setText('Our Pledge to Privacy')
        self.privacy_header.setFont(font)

        # Privacy info text setup
        info_font = QtGui.QFont()
        info_font.setPointSize(12 if sys.platform == "darwin" else 8)

        self.privacy_info = TransparentLabel(self.privacy)
        self.privacy_info.setGeometry(30, 229, 332, 90)
        self.privacy_info.setText(
            'We understand how important your privacy is. That’s why all your data is securely encrypted and used '
            'only to match your activities with the right projects. Rest assured, it’s protected and won’t be shared '
            'with anyone outside the system.'
        )
        self.privacy_info.setFont(info_font)
        self.privacy_info.setWordWrap(True)

        self.privacy_info_2 = TransparentLabel(self.privacy)
        self.privacy_info_2.setGeometry(30, 320, 332, 80)
        self.privacy_info_2.setText(
            'With Ralvie Cloud, you can trust that your data is handled with care, so you can focus on your work '
            'with peace of mind.'
        )
        self.privacy_info_2.setFont(info_font)
        self.privacy_info_2.setWordWrap(True)
        self.privacy_info_2.setStyleSheet("background: transparent;")  # Transparent background for this text too

        # Next button styling and setup
        self.privacy_next_btn = QPushButton(self.privacy)
        self.privacy_next_btn.setGeometry(QtCore.QRect(30, 401, 80, 40))
        self.privacy_next_btn.setText("Next")
        self.privacy_next_btn.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2); "
            "border-radius: 5px; color: #FFFFFF; border: 1px solid #1D0B77;"
        )

        self.privacy_next_btn.clicked.connect(self.go_to_next_page)
        return self.privacy

    def data_security(self):
        self.datasecurity = QWidget()

        # Create a TransparentLabel for the background image
        self.datasecurity_background = TransparentLabel(self.datasecurity)
        self.datasecurity_background.setGeometry(0, 0, 800, 600)  # Set the size of the background
        self.datasecurity_background.setScaledContents(True)  # Ensure the background scales properly

        self.datasecurity_img = TransparentLabel(self.datasecurity)
        self.datasecurity_img.setGeometry(452, 193, 308, 223)  # Set the size of the background

        self.datasecurity_img.setScaledContents(True)  # Ensure the background scales properly

        self.datasecurity_sundial_logo = TransparentLabel(self.datasecurity)
        self.datasecurity_sundial_logo.setGeometry(20, 20, 150, 40)  # Set the size of the background
        self.datasecurity_sundial_logo.setScaledContents(True)

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(28)
        else:
            font.setPointSize(12)
        font.setWeight(QFont.Weight.Bold)
        self.datasecurity_header = TransparentLabel(self.datasecurity)
        self.datasecurity_header.setGeometry(30, 160, 400, 40)  # Set the size of the background
        self.datasecurity_header.setText('Data Security & Encryption')
        self.datasecurity_header.setFont(font)

        info_font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(8)
        self.datasecurity_info = TransparentLabel(self.datasecurity)
        self.datasecurity_info.setGeometry(30, 225, 332, 80)  # Set the size of the background
        self.datasecurity_info.setText(
            "The database where your data is stored is fully encrypted, and it's securely synced to Ralvie Cloud with end-to-end encryption. Your information stays protected throughout the entire process.")
        self.datasecurity_info.setFont(info_font)
        self.datasecurity_info.setWordWrap(True)

        self.datasecurity_back_btn = QPushButton(self.datasecurity)
        self.datasecurity_back_btn.setGeometry(QtCore.QRect(30, 330, 80, 40))
        self.datasecurity_back_btn.setText("Back")

        self.datasecurity_next_btn = QPushButton(self.datasecurity)
        self.datasecurity_next_btn.setGeometry(QtCore.QRect(130, 330, 80, 40))
        self.datasecurity_next_btn.setText("Next")

        self.datasecurity_next_btn.clicked.connect(self.go_to_next_page)
        self.datasecurity_back_btn.clicked.connect(self.go_to_previous_page)

        return self.datasecurity

    def onboard_settings(self):
        self.onboardsettings = QWidget()

        self.settings_background = TransparentLabel(self.onboardsettings)
        self.settings_background.setGeometry(0, 0, 800, 600)
        self.settings_background.setScaledContents(True)

        self.settings_sundial_logo = TransparentLabel(self.onboardsettings)
        self.settings_sundial_logo.setGeometry(20, 20, 150, 40)
        self.settings_sundial_logo.setScaledContents(True)

        font = QtGui.QFont()
        font.setPointSize(28 if sys.platform == "darwin" else 12)
        font.setWeight(QFont.Weight.Bold)
        self.settings_header = TransparentLabel(self.onboardsettings)
        self.settings_header.setGeometry(30, 99, 400, 40)
        self.settings_header.setText('Settings')
        self.settings_header.setFont(font)

        self.start_up = QWidget(self.onboardsettings)
        self.start_up.setGeometry(QtCore.QRect(30, 168, 740, 60))

        self.start_up_label = TransparentLabel(self.start_up)
        self.start_up_label.setGeometry(QtCore.QRect(20, 22, 211, 16))
        self.start_up_label.setText("Launch Sundial on system startup")
        font.setPointSize(12 if sys.platform == "darwin" else 10)
        self.start_up_label.setFont(font)

        self.start_up_checkbox = SwitchControl(
            self.start_up,
            bg_color="#888888",
            circle_color="#FFFFFF",
            active_color="#FFA500",  # Orange when active
            animation_duration=300
        )
        self.start_up_checkbox.setGeometry(QRect(680, 20, 100, 21))

        settings_font = QtGui.QFont()
        settings_font.setPointSize(12 if sys.platform == "darwin" else 8)

        self.start_up_info = TransparentLabel(self.onboardsettings)
        self.start_up_info.setGeometry(30, 220, 700, 30)
        self.start_up_info.setText("Automatically capture your break time when you take a nap.")
        self.start_up_info.setFont(settings_font)
        self.start_up_info.setWordWrap(True)

        self.idle_time = QWidget(self.onboardsettings)
        self.idle_time.setGeometry(QtCore.QRect(30, 285, 740, 60))
        self.idle_time_label = TransparentLabel(parent=self.idle_time)
        self.idle_time_label.setGeometry(QtCore.QRect(20, 22, 211, 16))
        self.idle_time_label.setText("Enable idle time detection")

        self.idle_time_checkbox = SwitchControl(
            self.idle_time,
            bg_color="#888888",
            circle_color="#FFFFFF",
            active_color="#FFA500",  # Orange when active
            animation_duration=300
        )
        self.idle_time_checkbox.setGeometry(QtCore.QRect(680, 20, 100, 21))
        self.idle_time_checkbox.raise_()

        self.idle_time_info = TransparentLabel(self.onboardsettings)
        self.idle_time_info.setGeometry(30, 340, 700, 30)
        self.idle_time_info.setText(
            "We recommend to let Sundial launch on system start up automatically to avoid missing any activity hours"
        )
        self.idle_time_info.setFont(settings_font)
        self.idle_time_info.setWordWrap(True)

        self.settings_back_btn = QPushButton(self.onboardsettings)
        self.settings_back_btn.setGeometry(QtCore.QRect(460, 422, 145, 40))
        self.settings_back_btn.setText("Skip && do it later")

        self.settings_next_btn = QPushButton(self.onboardsettings)
        self.settings_next_btn.setGeometry(QtCore.QRect(625, 422, 145, 40))
        self.settings_next_btn.setText("Save && continue")

        # Retrieve settings and update checkboxes

        # self.update_checkboxes()

        # Connect checkbox signals to slot methods
        # self.start_up_checkbox.stateChanged.connect(self.start_up_status)
        # self.idle_time_checkbox.stateChanged.connect(self.idle_time_status)

        self.settings_back_btn.clicked.connect(self.go_to_next_page)
        self.settings_next_btn.clicked.connect(self.sundial_reference.redirect_to_login)



        return self.onboardsettings

    def notify_classes(self):
        print("ClassA button clicked. Emitting signal to notify other classes.")
        self.communicator.notify_other_classes.emit()

    def _onboard_settings_show_event(self, event):
        """This method is invoked when the onboard_settings widget is shown."""
        # self.update_checkboxes()  # Fetch the settings here when the widget is shown
        QWidget.showEvent(self, event)


    def update_app_layout(self):
        """Update the background based on the current page index and theme."""
        current_palette = QApplication.palette()
        page_index = self.onboard_layout.currentIndex()
        print(f"Current page index: {page_index}")

        # Determine if it's a light or dark theme based on the background color
        if current_palette.color(QtGui.QPalette.ColorRole.Window).lightness() > 128:
            # Set styles for containers
            container_style = """
                                    background-color: rgba(252, 252, 252, 0.8);  /* 80% opacity */
                                    border-radius: 5px;
                                """
            # Set styles for buttons
            gradient_style = """
                                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2);
                                    border-radius: 5px;
                                    color: #FFFFFF;
                                    border: 1px solid #1D0B77;
                                """
            solid_button_style = """
                                    background: #A1A3A5;
                                    border-radius: 5px;
                                    color: #FFFFFF;
                                """
            if page_index == 0:
                # Page 0 (Privacy Info)
                self.setStyleSheet("background-color: #f0f0f0;")  # Example light background color
                self.privacy_next_btn.setStyleSheet(gradient_style)
                self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join(self.LightTheme, "darkSundialLogo.svg")))
                self.privacy_background.setPixmap(QPixmap(os.path.join(self.LightTheme, "BackgroundImage.svg")))
                self.privacy_img.setPixmap(QPixmap(os.path.join(self.LightTheme, "privacy.png")))
                self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join(self.LightTheme, "signin_logo.svg")))
            elif page_index == 1:
                # Page 1 (Data Security)
                self.setStyleSheet("background-color: #e0e0e0;")
                self.datasecurity_next_btn.setStyleSheet(gradient_style)
                self.datasecurity_back_btn.setStyleSheet(solid_button_style)
                self.datasecurity_background.setPixmap(QPixmap(os.path.join(self.LightTheme, "BackgroundImage.svg")))
                self.datasecurity_img.setPixmap(QPixmap(os.path.join(self.LightTheme, "Dataprivacy_light.svg")))
                self.datasecurity_sundial_logo.setPixmap(QPixmap(os.path.join(self.LightTheme, "signin_logo.svg")))
            elif page_index == 2:
                # Page 2 (Onboard Settings)
                self.setStyleSheet("background-color: #d0d0d0;")
                self.settings_back_btn.setStyleSheet(solid_button_style)
                self.settings_next_btn.setStyleSheet(gradient_style)
                self.idle_time.setStyleSheet(container_style)
                self.start_up.setStyleSheet(container_style)
                self.settings_sundial_logo.setPixmap(QPixmap(os.path.join(self.LightTheme, "signin_logo.svg")))
                self.settings_background.setPixmap(QPixmap(os.path.join(self.LightTheme, "BackgroundImage.svg")))
            elif page_index == 3:
                # Page 3 (Accessibility Permission)
                self.setStyleSheet("background-color: #c0c0c0;")

        else:
            gradient_style = """
                            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2);
                            border-radius: 5px;
                            color: #FFFFFF;
                            border: 1px solid #1D0B77;
                        """
            solid_button_style = """
                            background: #393939;
                            border-radius: 5px;
                        """
            container_style = """
                            background-color: rgba(10, 10, 10, 0.8);  /* 80% opacity */
                            border-radius: 5px;
                        """
            if page_index == 0:
                # Page 0 (Privacy Info)
                self.setStyleSheet("background-color: #f0f0f0;")  # Example light background color
                self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join( self.darkTheme, "darkSundialLogo.svg")))
                self.privacy_background.setPixmap(QPixmap(os.path.join( self.darkTheme, "darkBackground.svg")))
                self.privacy_img.setPixmap(QPixmap(os.path.join(self.darkTheme, "privacy.png")))
                self.privacy_next_btn.setStyleSheet(gradient_style)
            elif page_index == 1:
                self.datasecurity_background.setPixmap(QPixmap(os.path.join(self.darkTheme, "darkBackground.svg")))
                self.datasecurity_img.setPixmap(QPixmap(os.path.join(self.darkTheme, "Dataprivacy.svg")))
                self.datasecurity_sundial_logo.setPixmap(QPixmap(os.path.join(self.darkTheme, "darkSundialLogo.svg")))
                self.setStyleSheet("background-color: #e0e0e0;")
                self.datasecurity_next_btn.setStyleSheet(gradient_style)
                self.datasecurity_back_btn.setStyleSheet(solid_button_style)
            elif page_index == 2:
                # Page 2 (Onboard Settings)
                self.settings_sundial_logo.setPixmap(QPixmap(os.path.join(self.darkTheme, "darkSundialLogo.svg")))
                self.settings_background.setPixmap(QPixmap(os.path.join(self.darkTheme, "darkBackground.svg")))
                self.setStyleSheet("background-color: #d0d0d0;")
                self.settings_back_btn.setStyleSheet(solid_button_style)
                self.settings_next_btn.setStyleSheet(gradient_style)
                self.idle_time.setStyleSheet(container_style)
                self.start_up.setStyleSheet(container_style)
            elif page_index == 3:
                # Page 3 (Accessibility Permission)
                self.setStyleSheet("background-color: #c0c0c0;")

    def toggle_theme(self):
        self.update_app_layout()


# Example usage
if __name__ == "__main__":
    app = QApplication([])
    development = "0"
    current_file_path = os.path.abspath(__file__)
    # Determine file path
    base_file_path = os.path.dirname(
        os.path.dirname(os.path.dirname(current_file_path))) if development == "1" else os.path.dirname(
        current_file_path)
    file_path = os.path.join(base_file_path, "sd_qt",
                             "sd_desktop") if sys.platform == "darwin" and development == "1" else base_file_path

    # Define folder paths
    if sys.platform == "darwin":
        folder_path = os.path.join(file_path, "resources") if development == "0" else os.path.join(file_path,
                                                                                                   "resources")
    elif sys.platform == "win32":
        folder_path = os.path.join(file_path, "resources").replace("\\", "/")

    # Define common theme paths
    darkTheme = os.path.join(folder_path, 'DarkTheme').replace("\\", "/")
    self.LightTheme = os.path.join(folder_path, 'LightTheme').replace("\\", "/")
    window = Onboarding(LightTheme=self.LightTheme, darkTheme=darkTheme)
    window.show()

    # Simulate testing the page switching


    app.exec()
