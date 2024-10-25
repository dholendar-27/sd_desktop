import json
import os
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
import ctypes
import pytz
import requests
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QTimer, QCoreApplication, QEvent, Signal, Qt, QPoint, QSettings, QRect, QPropertyAnimation
from PySide6.QtGui import QPixmap, QAction, QIcon, QFont, QColor, QMovie, QPalette, QCursor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedLayout,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QApplication,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QLineEdit,
    QComboBox,
    QStackedWidget,
    QTimeEdit,
    QScrollArea,
    QCheckBox, QSystemTrayIcon, QMenu, QMessageBox, QGraphicsOpacityEffect, QDialogButtonBox, QDialog,
    QGraphicsBlurEffect, QToolTip, QToolButton
)


from .checkBox import CustomCheckBox
from AppKit import NSApplication, NSApp, NSApplicationActivationPolicyAccessory, NSApplicationActivationPolicyRegular
from Quartz import CGEventTapCreate, kCGEventKeyDown, kCGHIDEventTap, kCGEventTapOptionListenOnly, CFRunLoopRun, CFRunLoopSourceCreate, CFMachPortCreateRunLoopSource
from Quartz import kCGEventMaskForAllEvents, CGEventTapEnable, CFRunLoopAddSource, CFRunLoopGetCurrent, kCFRunLoopDefaultMode
from .toggleSwitch import SwitchControl
from deepdiff import DeepDiff

# Create a custom logger
# logger = logging.getLogger('my_logger')
# logger.setLevel(logging.DEBUG)

# # Create handlers
# console_handler = logging.StreamHandler()
# file_handler = logging.FileHandler('app.log')

# # Set level for handlers
# console_handler.setLevel(logging.INFO)
# file_handler.setLevel(logging.DEBUG)

# # Create formatters and add them to handlers
# console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# console_handler.setFormatter(console_format)
# file_handler.setFormatter(file_format)

# # Add handlers to the logger
# logger.addHandler(console_handler)
# logger.addHandler(file_handler)


# Importing custom modules
from sd_core.cache import cache_user_credentials, get_credentials, add_password, clear_credentials
from sd_core.launch_start import launch_app, delete_launch_app, set_autostart_registry

development = "0"
cached_credentials = None
current_file_path = os.path.abspath(__file__)
file_path = os.path.dirname(os.path.dirname(
    os.path.dirname(current_file_path)))
# logger.info(file_path)
if sys.platform == "darwin" and development == "1":
    folder_path = os.path.join(file_path, "sd_qt", "sd_desktop", "resources")
elif sys.platform == "win32" and development == "1":
    folder_path = os.path.join(
        file_path, "sd_desktop", "resources").replace("\\", "/")
    uparrow = os.path.join(folder_path, "uparrow.png").replace("\\", "/")
    downarrow = os.path.join(folder_path, "downarrow.png").replace("\\", "/")
    uparrow = os.path.join(folder_path, "uparrow.png").replace("\\", "/")
    downarrow = os.path.join(folder_path, "downarrow.png").replace("\\", "/")
    darkTheme = os.path.join(folder_path, 'DarkTheme').replace("\\", "/")
    lightTheme = os.path.join(folder_path, 'LightTheme').replace("\\", "/")
    dark_downarrow = os.path.join(
        darkTheme, "dark_downarrow.svg").replace("\\", "/")
    light_downarrow = os.path.join(
        lightTheme, "light_downarrow.png").replace("\\", "/")
    light_uparrow = os.path.join(
        lightTheme, "light_uparrow.png").replace("\\", "/")

elif sys.platform == "darwin" and development == "0":
    file_path = os.path.join(file_path, "sd_qt", "sd_desktop",)
    print(file_path)
    folder_path = os.path.join(file_path, "resources")
    darkTheme = os.path.join(folder_path, 'DarkTheme')
    lightTheme = os.path.join(folder_path, 'LightTheme')
    uparrow = os.path.join(folder_path, "uparrow.png")
    downarrow = os.path.join(folder_path, "downarrow.png")
    light_uparrow = os.path.join(lightTheme, "light_uparrow.png")
    light_downarrow = os.path.join(lightTheme, "light_downarrow.png")
    dark_downarrow = os.path.join(darkTheme, "dark_downarrow.svg")
elif sys.platform == "win32" and development == "0":
    current_file_path = os.path.abspath(__file__)
    file_path = os.path.dirname(current_file_path)
    folder_path = os.path.join(file_path, "resources").replace("\\", "/")
    uparrow = os.path.join(folder_path, "uparrow.png").replace("\\", "/")
    downarrow = os.path.join(folder_path, "downarrow.png").replace("\\", "/")
    darkTheme = os.path.join(folder_path, 'DarkTheme').replace("\\", "/")
    lightTheme = os.path.join(folder_path, 'LightTheme').replace("\\", "/")
    dark_downarrow = os.path.join(
        darkTheme, "dark_downarrow.svg").replace("\\", "/")
    light_downarrow = os.path.join(
        lightTheme, "light_downarrow.png").replace("\\", "/")
    light_uparrow = os.path.join(
        lightTheme, "light_uparrow.png").replace("\\", "/")

# Set up the paths for the images


host = "http://localhost:7600/api"

# Global settings and user details
settings = {}
userdetails = {}
week_schedule = {
    'Monday': True, 'Tuesday': True, 'Wednesday': True, 'Thursday': True,
    'Friday': True, 'Saturday': True, 'Sunday': True,
    'starttime': '00:00', 'endtime': '23:59'
}
default_week_schedule = week_schedule.copy()
first_name = ""
current_color_index = 0

light_colors_border = {
    "#F5E9DA": "#FA9C2B",
    "#E8C6E6": "#FF61F6",
    "#CDC8EF": "#1D0B77",
    "#C0D8EC": "#185ABD",
    "#C8E0FF": "#1A73E8",
    "#E2F0D6": "#7AC143"
}

dark_colors_border = {
    "#443C32": "#FA9C2B",
    "#271726": "#FF61F6",
    "#29263B": "#1D0B77",
    "#0E1E2B": "#185ABD",
    "#111D2C": "#1A73E8",
    "#20261B": "#7AC143",
}


def is_accessibility_enabled() -> bool:
    """
    Check if the application has accessibility permissions.
    @return: True if the accessibility permissions are enabled, False otherwise.
    """
    AXIsProcessTrusted = ctypes.CDLL("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices").AXIsProcessTrusted
    AXIsProcessTrusted.restype = ctypes.c_bool
    return AXIsProcessTrusted()

def event_tap_callback(proxy, event_type, event, refcon):
    """
    Callback function for event tap. This function is called every time a key or mouse event is detected.
    It doesn't do anything but allows us to "observe" events without affecting them.
    """
    return event

def start_event_monitoring():
    """
    Start monitoring global key and mouse events. This will trigger macOS to prompt for accessibility permissions
    without affecting user interaction.
    """
    event_mask = kCGEventMaskForAllEvents  # Monitor all events

    # Create an event tap to listen for key presses and mouse clicks
    event_tap = CGEventTapCreate(
        kCGHIDEventTap,  # Tap at the human interface device level to capture key/mouse events
        0,  # No flags
        kCGEventTapOptionListenOnly,  # Don't modify events, just listen
        event_mask,  # Monitor all events
        event_tap_callback,  # Callback function for event tap
        None  # No extra context
    )

    if not event_tap:
        print("Failed to create event tap.")
        return

    # Enable the event tap
    CGEventTapEnable(event_tap, True)

    # Create a run loop source from the event tap
    run_loop_source = CFMachPortCreateRunLoopSource(None, event_tap, 0)

    # Add the run loop source to the current run loop
    CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopDefaultMode)

    # Run the loop to start listening (this blocks the current thread)
    CFRunLoopRun()



class ClickableLabel(QLabel):
    clicked = Signal()  # Create a custom signal

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # Emit the clicked signal when the label is clicked
        # Call the base class method after emitting the signal
        super().mousePressEvent(event)


class CustomQTimeEdit(QTimeEdit):
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.clearFocus()



class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Password")

        self.layout = QVBoxLayout(self)

        self.password_field = QLineEdit(self)
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setPlaceholderText("Password")

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.password_field)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_password(self):
        return self.password_field.text()


class MainWindow(QMainWindow):
    loginSuccess = Signal(dict)
    loginFailed = Signal(str)
    showLoaderSignal = Signal(bool)
    showLoadersSignal = Signal(bool)
    goToCompanyPageSignal = Signal()


    def __init__(self):
        super().__init__()
        self.onboarding_status = QSettings("ralvie.ai", "Sundial")
        self.setupUi(self)
        self.is_dark_mode = self.detect_system_theme()
        self.is_dark_themed = False
        self.update_theme()
        self.load_custom_font()
        self.companies = []
        self.sundail_token = None
        self.companyid = None
        self.companyname = None
        self.loginSuccess.connect(self.process_login_response)
        self.loginFailed.connect(self.show_error_message)
        self.showLoaderSignal.connect(self.showLoader)
        self.showLoadersSignal.connect(self.showLoaders)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.add_dynamic_blocks)
        self.timer.timeout.connect(self.update_events_style)
        self.timer.timeout.connect(self.update_date)
        self.goToCompanyPageSignal.connect(self.go_to_company_page)
        if sys.platform == "darwin" and NSApplication:
            self.update_dock_icon_policy()
            self.accessibility_timer = None

        # self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)

        self.setupSystemTray()
        self.onboarding_status.remove("Sundial")


    def load_custom_font(self):
        font_id = QtGui.QFontDatabase.addApplicationFont(
            os.path.join(folder_path, "fonts", "Poppins-light.ttf"))
        if font_id != -1:
            font_families = QtGui.QFontDatabase.applicationFontFamilies(
                font_id)
            if font_families:
                custom_font = QtGui.QFont(font_families[0])
                QApplication.setFont(custom_font)


    def setupUi(self, Widget):
        Widget.resize(800, 600)
        Widget.setMinimumSize(QtCore.QSize(800, 600))
        Widget.setMaximumSize(QtCore.QSize(800, 600))
        Widget.setWindowTitle("Sundial")
        # Widget.setWindowIcon(
        #     QIcon(os.path.join(folder_path, "Sundial_logo.svg")))

        container = QWidget()
        self.setCentralWidget(container)

        self.app_layout = QStackedLayout()
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.app_layout.setSpacing(0)

        self.onboard = self.onboarding()
        self.loader_page = self.loaderPage()
        self.signin_page = self.signIn()
        self.app_ui = self.create_third_widget()


        self.app_layout.addWidget(self.loader_page)
        self.app_layout.addWidget(self.signin_page)
        self.app_layout.addWidget(self.onboard)
        self.app_layout.addWidget(self.app_ui)

        self.app_layout.setCurrentWidget(self.onboard)

        if self.onboarding_status.value("onboarding_complete", False) == "j?KEgMKb:^kNMpX:Bx=7":
            # If onboarding is complete, skip it and go to the sign-in or main page
            self.app_layout.setCurrentWidget(self.app_ui)
        else:
            # Show the onboarding screen only once
            self.app_layout.setCurrentWidget(self.onboard)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.app_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container.setLayout(main_layout)


    def loaderPage(self):
        self.loader = QWidget()

        self.background = QLabel(self.loader)
        self.background.setContentsMargins(0, 0, 0, 0)
        self.background.setScaledContents(True)
        self.background.setGeometry(0, 0, 800, 600)

        self.Sundial_logo = QLabel("Sundial Logo", parent=self.loader)
        self.Sundial_logo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.Sundial_logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        logo_width = 400
        logo_height = 100
        self.Sundial_logo.setGeometry(
            (800 - logo_width) // 2, (600 - logo_height) // 2, logo_width, logo_height)
        return self.loader

    def signIn(self):
        self.stacked_widget = QWidget()
        self.stacked_layout = QStackedLayout(self.stacked_widget)

        page1 = self.homepage()
        self.stacked_layout.addWidget(page1)

        page2 = self.signin_page()
        self.stacked_layout.addWidget(page2)

        page3 = self.company_page()
        self.stacked_layout.addWidget(page3)

        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setSpacing(0)

        return self.stacked_widget

    def homepage(self):
        self.homepage = QWidget()

        self.homepage_background = QLabel(self.homepage)
        self.homepage_background.setContentsMargins(0, 0, 0, 0)
        self.homepage_background.setScaledContents(True)
        self.homepage_background.setGeometry(0, 0, 800, 600)

        self.homepage_Sundial_logo = QLabel(
            "Sundial Logo", parent=self.homepage)
        self.homepage_Sundial_logo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.homepage_Sundial_logo.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)

        logo_width = 350
        logo_height = 100
        self.homepage_Sundial_logo.setGeometry(
            220, 50, logo_width, logo_height)

        self.homepage_subtitle = QLabel(parent=self.homepage)
        self.homepage_subtitle.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.homepage_subtitle.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        self.homepage_subtitle.setGeometry(125, 200, 550, 124)
        self.homepage_subtitle.setStyleSheet(
            "background: transparent; color: black; font-size: 20px;")

        self.description = QLabel(
            "Automated, AI-driven time tracking software of the future", parent=self.homepage)
        self.description.setGeometry(QtCore.QRect(180, 350, 480, 30))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(16)
        else:
            font.setPointSize(12)
        self.description.setFont(font)
        self.description.setStyleSheet(
            "background: transparent; color: black;")

        self.signIn_button = QPushButton("Sign in", parent=self.homepage)
        self.signIn_button.setGeometry(QtCore.QRect(150, 450, 500, 60))
        self.signIn_button.setObjectName("signInButton")
        self.signIn_button.clicked.connect(self.go_to_signin_page)
        self.signIn_button.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))

        return self.homepage

    def go_to_signin_page(self):
        self.stacked_layout.setCurrentIndex(1)

    def signin_page(self):
        self.sign_in = QWidget()

        # Background setup
        self.sign_in_background = QLabel(self.sign_in)
        self.sign_in_background.setContentsMargins(0, 0, 0, 0)
        self.sign_in_background.setScaledContents(True)
        self.sign_in_background.setGeometry(0, 0, 800, 600)

        # Sundial Logo
        self.sign_in_Sundial_logo = QLabel("Sundial Logo", parent=self.sign_in)
        self.sign_in_Sundial_logo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.sign_in_Sundial_logo.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)

        logo_width = 283
        logo_height = 100
        self.sign_in_Sundial_logo.setGeometry(250, 30, logo_width, logo_height)

        # Sign-in widget
        self.signin_widget = QWidget(self.sign_in)
        self.signin_widget.setGeometry(135, 130, 534, 409)

        self.welcomeMessage = QLabel(
            "Welcome back!", parent=self.signin_widget)
        self.welcomeMessage.setGeometry(QtCore.QRect(40, 25, 280, 39))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(28)
        else:
            font.setPointSize(26)
        self.welcomeMessage.setFont(font)

        self.newUserLabel = QLabel(parent=self.signin_widget)
        self.newUserLabel.setGeometry(QtCore.QRect(40, 80, 81, 20))
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.newUserLabel.setFont(font)
        self.newUserLabel.setText("New user?")

        self.signupLabel = QLabel(parent=self.signin_widget)
        self.signupLabel.setGeometry(QtCore.QRect(120, 80, 150, 20))
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.signupLabel.setFont(font)
        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        if self.is_dark_mode:
            urlLink = '<a href="https://ralvie.minervaiotstaging.com/pages/verify-email" style="color: #A49DC8; text-decoration: none;">Sign up here</a>'
        else:
            urlLink = '<a href="https://ralvie.minervaiotstaging.com/pages/verify-email" style="color: #1D0B77; text-decoration: none;">Sign up here</a>'
        self.signupLabel.setText(urlLink)
        self.signupLabel.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.signupLabel.setOpenExternalLinks(True)

        if sys.platform == "darwin":
            font.setPointSize(16)
        else:
            font.setPointSize(10)

        self.emailField = QLineEdit(parent=self.signin_widget)
        self.emailField.setGeometry(QtCore.QRect(40, 120, 444, 60))
        self.emailField.setPlaceholderText("User name or Email")
        self.emailField.setFont(font)

        self.passwordField = QLineEdit(self.signin_widget)
        self.passwordField.setGeometry(40, 200, 444, 60)
        self.passwordField.setPlaceholderText("Password")
        self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordField.setFont(font)


        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        if self.is_dark_mode:
            palette = self.emailField.palette()
            palette.setColor(QPalette.PlaceholderText,
                             QColor(248, 248, 248))  # Set color to light gray with 50% opacity
            self.emailField.setPalette(palette)

            palette = self.passwordField.palette()
            palette.setColor(QPalette.PlaceholderText,
                             QColor(248, 248, 248))  # Set color to light gray with 50% opacity
            self.passwordField.setPalette(palette)
        else:
            palette = self.emailField.palette()
            palette.setColor(QPalette.PlaceholderText,
                             QColor(71, 75, 79))  # Set color to dark gray with 50% opacity
            self.emailField.setPalette(palette)

            palette = self.passwordField.palette()
            palette.setColor(QPalette.PlaceholderText,
                             QColor(71, 75, 79))  # Set color to dark gray with 50% opacity
            self.passwordField.setPalette(palette)

        # Create a QToolButton to toggle password visibility
        icon_path = os.path.join(lightTheme, 'show_pass.svg')
        icon = QPixmap(icon_path).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.showPassButton = QToolButton(self)
        self.showPassButton.setGeometry(0,0,44,44)
        self.showPassButton.setIcon(QIcon(icon))
        self.showPassButton.setCheckable(True)
        self.showPassButton.setToolTip('View password')
        self.showPassButton.setCursor(QCursor(Qt.PointingHandCursor))

        print(f"ToolTip set: {self.showPassButton.toolTip()}")

        # Connect the toggle action to show/hide password
        self.showPassButton.toggled.connect(self.showPassword)

        # Create a layout to insert the QToolButton inside the QLineEdit
        layout = QHBoxLayout(self.passwordField)
        layout.addStretch()
        layout.addWidget(self.showPassButton)
        layout.setContentsMargins(0, 0, 10, 0)
        self.passwordField.setLayout(layout)

        self.errorMessageLabel = QLabel(parent=self.signin_widget)
        self.errorMessageLabel.setGeometry(QtCore.QRect(40, 280, 334, 20))
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(10)
        self.errorMessageLabel.setFont(font)
        self.errorMessageLabel.setVisible(False)

        self.Forgot_password_Label = QLabel(parent=self.signin_widget)
        self.Forgot_password_Label.setGeometry(QtCore.QRect(360, 280, 200, 23))
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.Forgot_password_Label.setFont(font)
        urlLink = '<a href="https://ralvie.minervaiotstaging.com/pages/verify-user" style="text-decoration: none;color:#474B4F">Forgot password?</a>'
        self.Forgot_password_Label.setText(urlLink)
        self.Forgot_password_Label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.Forgot_password_Label.setOpenExternalLinks(True)

        self.sign_In_button = QPushButton("Sign in", parent=self.signin_widget)
        self.sign_In_button.setGeometry(QtCore.QRect(40, 320, 444, 60))
        self.sign_In_button.setObjectName("sign_In_button")
        self.sign_In_button.clicked.connect(self.initiate_login)
        self.sign_In_button.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.sign_In_button.setFont(font)

        self.signin_message = QWidget(parent=self.sign_in)
        self.signin_message.setGeometry(QtCore.QRect(800, 480, 400, 60))
        self.signin_message_label = QLabel(self.signin_message)
        self.signin_message_label.setGeometry(QtCore.QRect(20, 10, 330, 40))

        self.loader_ = QLabel(self.sign_in)
        self.loader_.setContentsMargins(0, 0, 0, 0)
        self.loader_.setScaledContents(True)
        # Full size of the sign_in widget
        self.loader_.setGeometry(0, 0, 800, 600)

        self.loader_gif = QLabel(self.loader_)
        self.loader_gif.setContentsMargins(0, 0, 0, 0)
        self.loader_gif.setScaledContents(True)
        self.loader_gif.setGeometry(350, 250, 100, 100)

        black_with_opacity = QColor(0, 0, 0, int(0.3 * 255))  # 0.3 opacity
        palette = QPalette()
        palette.setColor(QPalette.Window, black_with_opacity)
        self.loader_gif.setPalette(palette)
        self.loader_.setVisible(False)

        movie = QMovie(os.path.join(folder_path, "loader.gif"))
        self.loader_gif.setMovie(movie)
        self.loader_gif.setAlignment(Qt.AlignCenter)
        movie.start()

        QToolTip.showText(self.showPassButton.mapToGlobal(QPoint(0, 0)), 'View password', self.showPassButton)
        return self.sign_in

    def showPassword(self, checked):
        """Toggle password visibility and update the icon."""
        if checked:
            self.passwordField.setEchoMode(QLineEdit.EchoMode.Normal)
            icon_path = os.path.join(lightTheme, 'hide_pass.svg')
            # print(f"Setting hide password icon: {icon_path}")  # Debugging: check the icon path
            icon = QIcon(icon_path)
            self.showPassButton.setIcon(icon)
            self.showPassButton.setToolTip('Hide password')
        else:
            self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)
            icon_path = os.path.join(lightTheme, 'show_pass.svg')
            # print(f"Setting show password icon: {icon_path}")  # Debugging: check the icon path
            icon = QIcon(icon_path)
            self.showPassButton.setIcon(icon)
            self.showPassButton.setToolTip('View password')

    def showLoader(self, show):
        self.loader_.setVisible(show)

    def showLoaders(self, show):
        self.loaders_.setVisible(show)

    def signin_toast_message(self):
        self.signin_message.show()
        self.signin_message_label.setStyleSheet(
            "background: none; color: white; font-size: 14px; border-radius: 5px;")
        self.signin_message_label.setText("Signing in, please wait...")
        self.animation = QtCore.QPropertyAnimation(
            self.signin_message, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QtCore.QRect(800, 480, 534, 409))
        self.animation.setEndValue(QtCore.QRect(380, 480, 534, 409))
        self.signin_message_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)  # Center text
        self.animation.start()

        # Timer to hide the message after 3 seconds
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_signin_message)
        self.timer.start(3000)

    def hide_signin_message(self):
        self.signin_message.hide()


    def company_page(self):
        self.company = QWidget()

        self.company_background = QLabel(self.company)
        self.company_background.setContentsMargins(0, 0, 0, 0)
        self.company_background.setScaledContents(True)
        self.company_background.setGeometry(0, 0, 800, 600)

        self.company_Sundial_logo = QLabel("Sundial Logo", parent=self.company)
        self.company_Sundial_logo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.company_Sundial_logo.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)

        logo_width = 283
        logo_height = 100
        self.company_Sundial_logo.setGeometry(250, 30, logo_width, logo_height)

        self.company_widget = QWidget(self.company)
        self.company_widget.setGeometry(135, 170, 534, 309)

        self.CompanyMessage = QLabel(
            "Organization", parent=self.company_widget)
        self.CompanyMessage.setGeometry(QtCore.QRect(40, 25, 280, 39))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(24)
        else:
            font.setPointSize(18)
        self.CompanyMessage.setFont(font)

        self.companySelect = QComboBox(self.company_widget)
        self.companySelect.setGeometry(QtCore.QRect(40, 100, 434, 60))

        self.companyErrorMessageLabel = QLabel(parent=self.company_widget)
        self.companyErrorMessageLabel.setGeometry(
            QtCore.QRect(42, 170, 334, 20))
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(10)
        self.companyErrorMessageLabel.setFont(font)
        self.companyErrorMessageLabel.setVisible(False)

        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)

        self.company_select_button = QPushButton(
            "Get started", parent=self.company_widget)
        self.company_select_button.setGeometry(QtCore.QRect(40, 200, 434, 50))
        self.company_select_button.clicked.connect(
            self.handle_company_selection)
        self.company_select_button.setFont(font)

        self.loaders_ = QLabel(self.company)
        self.loaders_.setContentsMargins(0, 0, 0, 0)
        self.loaders_.setScaledContents(True)
        # Full size of the sign_in widget
        self.loaders_.setGeometry(0, 0, 800, 600)

        self.loaders_gif = QLabel(self.loaders_)
        self.loaders_gif.setContentsMargins(0, 0, 0, 0)
        self.loaders_gif.setScaledContents(True)
        self.loaders_gif.setGeometry(350, 250, 100, 100)

        black_with_opacity = QColor(0, 0, 0, int(0.3 * 255))  # 0.3 opacity
        palette = QPalette()
        palette.setColor(QPalette.Window, black_with_opacity)
        self.loaders_gif.setPalette(palette)
        self.loaders_.setVisible(False)

        movie = QMovie(os.path.join(folder_path, "loader.gif"))
        self.loaders_gif.setMovie(movie)
        self.loaders_gif.setAlignment(Qt.AlignCenter)
        movie.start()

        return self.company

    def onboarding(self):
        self.onboard = QWidget()
        self.onboard_layout = QStackedLayout(self.onboard)
        self.onboard_layout.addWidget(self.privacyinfo())  # Correct
        self.onboard_layout.addWidget(self.data_security())
        self.onboard_layout.addWidget(self.onboard_settings())
        self.onboard_layout.addWidget(self.accessibility_permission())

        self.onboard_layout.setContentsMargins(0, 0, 0, 0)
        self.onboard_layout.setSpacing(0)

        return self.onboard

    def go_to_next_page(self):
        current_index = self.onboard_layout.currentIndex()
        if current_index < self.onboard_layout.count() - 1:  # Ensure we don't go out of range
            self.onboard_layout.setCurrentIndex(current_index + 1)

    # Method to move to the previous widget
    def go_to_previous_page(self):
        current_index = self.onboard_layout.currentIndex()
        if current_index > 0:  # Ensure we don't go out of range
            self.onboard_layout.setCurrentIndex(current_index - 1)

    def privacyinfo(self):
        self.privacy = QWidget()
        self.privacy.setStyleSheet("background: transparent;")  # Set the entire widget background to transparent

        # Background setup
        self.privacy_background = QLabel(self.privacy)
        self.privacy_background.setGeometry(0, 0, 800, 600)
        self.privacy_background.setScaledContents(True)

        # Privacy image setup
        self.privacy_img = QLabel(self.privacy)
        self.privacy_img.setGeometry(395, 30,450,500)
        self.privacy_img.setScaledContents(True)
        self.privacy_img.setStyleSheet("background: transparent;")  # Make sure the label background is transparent

        # Sundiallogo setup
        self.privacy_sundial_logo = QLabel(self.privacy)
        self.privacy_sundial_logo.setGeometry(20, 20, 150, 40)
        self.privacy_sundial_logo.setScaledContents(True)


        # Header with dynamic font sizing
        font = QtGui.QFont()
        font.setPointSize(28 if sys.platform == "darwin" else 12)
        font.setWeight(QFont.Weight.Bold)
        self.privacy_header = QLabel(self.privacy)
        self.privacy_header.setGeometry(30, 160, 400, 40)
        self.privacy_header.setText('Our Pledge to Privacy')
        self.privacy_header.setFont(font)

        # Privacy info text setup
        info_font = QtGui.QFont()
        info_font.setPointSize(12 if sys.platform == "darwin" else 8)

        self.privacy_info = QLabel(self.privacy)
        self.privacy_info.setGeometry(30, 229, 332, 90)
        self.privacy_info.setText(
            'We understand how important your privacy is. That’s why all your data is securely encrypted and used '
            'only to match your activities with the right projects. Rest assured, it’s protected and won’t be shared '
            'with anyone outside the system.'
        )
        self.privacy_info.setFont(info_font)
        self.privacy_info.setWordWrap(True)

        self.privacy_info_2 = QLabel(self.privacy)
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

        # Create a QLabel for the background image
        self.datasecurity_background = QLabel(self.datasecurity)
        self.datasecurity_background.setGeometry(0, 0, 800, 600)  # Set the size of the background
        self.datasecurity_background.setScaledContents(True)  # Ensure the background scales properly

        self.datasecurity_img = QLabel(self.datasecurity)
        self.datasecurity_img.setGeometry(452, 193, 308, 223)  # Set the size of the background

        self.datasecurity_img.setScaledContents(True)  # Ensure the background scales properly

        self.datasecurity_sundial_logo = QLabel(self.datasecurity)
        self.datasecurity_sundial_logo.setGeometry(20, 20, 150, 40)  # Set the size of the background
        self.datasecurity_sundial_logo.setScaledContents(True)

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(28)
        else:
            font.setPointSize(12)
        font.setWeight(QFont.Weight.Bold)
        self.datasecurity_header = QLabel(self.datasecurity)
        self.datasecurity_header.setGeometry(30, 160, 400, 40)  # Set the size of the background
        self.datasecurity_header.setText('Data Security & Encryption')
        self.datasecurity_header.setFont(font)

        info_font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(8)
        self.datasecurity_info = QLabel(self.datasecurity)
        self.datasecurity_info.setGeometry(30, 225, 332, 80)  # Set the size of the background
        self.datasecurity_info.setText("The database where your data is stored is fully encrypted, and it's securely synced to Ralvie Cloud with end-to-end encryption. Your information stays protected throughout the entire process.")
        self.datasecurity_info.setFont(info_font)
        self.datasecurity_info.setWordWrap(True)

        self.back_btn = QPushButton(self.datasecurity)
        self.back_btn.setGeometry(QtCore.QRect(30, 330, 80, 40))
        self.back_btn.setText("Back")

        self.next_btn = QPushButton(self.datasecurity)
        self.next_btn.setGeometry(QtCore.QRect(130, 330, 80, 40))
        self.next_btn.setText("Next")

        self.next_btn.clicked.connect(self.go_to_next_page)
        self.back_btn.clicked.connect(self.go_to_previous_page)

        return self.datasecurity

    def onboard_settings(self):
        self.onboardsettings = QWidget()

        self.settings_background = QLabel(self.onboardsettings)
        self.settings_background.setGeometry(0, 0, 800, 600)
        self.settings_background.setScaledContents(True)

        self.settings_sundial_logo = QLabel(self.onboardsettings)
        self.settings_sundial_logo.setGeometry(20, 20, 150, 40)
        self.settings_sundial_logo.setScaledContents(True)

        font = QtGui.QFont()
        font.setPointSize(28 if sys.platform == "darwin" else 12)
        font.setWeight(QFont.Weight.Bold)
        self.settings_header = QLabel(self.onboardsettings)
        self.settings_header.setGeometry(30, 99, 400, 40)
        self.settings_header.setText('Settings')
        self.settings_header.setStyleSheet("color:#ffffff")
        self.settings_header.setFont(font)

        self.start_up = QWidget(self.onboardsettings)
        self.start_up.setGeometry(QtCore.QRect(30, 168, 740, 60))

        self.start_up_label = QLabel(self.start_up)
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

        self.start_up_info = QLabel(self.onboardsettings)
        self.start_up_info.setGeometry(30, 220, 700, 30)
        self.start_up_info.setText("Automatically capture your break time when you take a nap.")
        self.start_up_info.setFont(settings_font)
        self.start_up_info.setWordWrap(True)

        self.idle_time = QWidget(self.onboardsettings)
        self.idle_time.setGeometry(QtCore.QRect(30, 285, 740, 60))
        self.idle_time_label = QLabel(parent=self.idle_time)
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


        self.idle_time_info = QLabel(self.onboardsettings)
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


        self.update_checkboxes()

        # Connect checkbox signals to slot methods
        self.start_up_checkbox.stateChanged.connect(self.start_up_status)
        self.idle_time_checkbox.stateChanged.connect(self.idle_time_status)


        self.settings_back_btn.clicked.connect(self.go_to_next_page)
        self.settings_next_btn.clicked.connect(self.go_to_next_page)

        self.onboardsettings.showEvent = self._onboard_settings_show_event

        return self.onboardsettings

    def _onboard_settings_show_event(self, event):
        """This method is invoked when the onboard_settings widget is shown."""
        self.update_checkboxes()  # Fetch the settings here when the widget is shown
        QWidget.showEvent(self, event)

    def update_checkboxes(self):
        retrieve_settings()
        self.start_up_checkbox.setChecked(settings.get('launch', False))
        print(settings.get('launch', False), settings.get('idle_time', False))
        self.idle_time_checkbox.setChecked(settings.get('idle_time', False))
        # Process events to update the UI immediately after state change
        self.start_up_checkbox.stateChanged.connect(lambda: QApplication.processEvents())
        self.idle_time_checkbox.stateChanged.connect(lambda: QApplication.processEvents())

    def accessibility_permission(self):
        self.accessibilitypermission = QWidget()

        self.accessibility_background = QLabel(self.accessibilitypermission)
        self.accessibility_background.setGeometry(0, 0, 800, 600)  # Set the size of the background
        self.accessibility_background.setScaledContents(True)  # Ensure

        self.accessibility_sundial_logo = QLabel(self.accessibilitypermission)
        self.accessibility_sundial_logo.setGeometry(20, 20, 150, 40)  # Set the size of the background
        self.accessibility_sundial_logo.setScaledContents(True)

        self.accessibility_img = QLabel(self.accessibilitypermission)
        self.accessibility_img.setGeometry(436, 154, 344, 293)
        self.accessibility_img.setScaledContents(True)
        self.accessibility_img.setStyleSheet("background: transparent;")  # Make sure the label background is transparent

        font = QtGui.QFont()
        font.setPointSize(28 if sys.platform == "darwin" else 24)
        font.setWeight(QFont.Weight.Bold)
        self.accessibility_header = QLabel(self.accessibilitypermission)
        self.accessibility_header.setGeometry(30, 160, 400, 40)
        self.accessibility_header.setText('Accessibility Permissions')
        self.accessibility_header.setFont(font)

        info_font = QtGui.QFont()
        info_font.setPointSize(12 if sys.platform == "darwin" else 8)

        self.accessibility_info = QLabel(self.accessibilitypermission)
        self.accessibility_info.setGeometry(30, 220, 332, 90)
        self.accessibility_info.setText(
            'To enhance your experience with the app, please enable Sundial in the accessibility permissions. This allows the app to track your system activities for better functionality.'
        )
        self.accessibility_info.setFont(info_font)
        self.accessibility_info.setWordWrap(True)

        self.accessibility_back_btn = QPushButton(self.accessibilitypermission)
        self.accessibility_back_btn.setGeometry(QtCore.QRect(30, 330, 80, 40))
        self.accessibility_back_btn.setText("Back")

        self.accessibility_next_btn = QPushButton(self.accessibilitypermission)
        self.accessibility_next_btn.setGeometry(QtCore.QRect(130, 330, 100, 40))
        self.accessibility_next_btn.setText("Complete")

        # Connect the "Next" button to the function to check and prompt for accessibility permissions
        self.accessibility_back_btn.clicked.connect(self.go_to_previous_page)
        self.accessibility_next_btn.clicked.connect(self.redirect_to_login)

        return self.accessibilitypermission




    def update_CheckboxStates(self, weekdays):
        self.monday_checkbox.setChecked(weekdays.get('Monday', False))
        self.Tuesday_checkbox.setChecked(weekdays.get('Tuesday', False))
        self.Wednesday_checkBox.setChecked(weekdays.get('Wednesday', False))
        self.Thursday_checkbox.setChecked(weekdays.get('Thursday', False))
        self.Friday_checkBox.setChecked(weekdays.get('Friday', False))
        self.saturday_checkBox.setChecked(weekdays.get('Saturday', False))
        self.Sunday_checkBox.setChecked(weekdays.get('Sunday', False))


    def start_up_status(self):
        status = ""
        if self.start_up_checkbox.isChecked():  # Removed redundant check for `idle_time_checkbox`
            status = "start"
        else:
            status = "stop"
        self.launch_on_start(status)

    def idle_time_status(self):
        status = ""
        if self.idle_time_checkbox.isChecked():  # Removed redundant check for `idle_time_checkbox`
            status = "start"
            self.idle_time_checkbox.setChecked(True)
        else:
            status = "stop"
            self.idle_time_checkbox.setChecked(False)
        self.enable_idletime(status)

    def redirect_to_login(self):
        creds = credentials()
        if creds and creds.get("Authenticated"):
            self.update_settings()
            # Directly to the main UI if already authenticated
            self.onboarding_status.setValue("onboarding_complete", "j?KEgMKb:^kNMpX:Bx=7")
            self.app_layout.setCurrentIndex(3)
            self.change_page(0)

    def create_third_widget(self):
        self.app = QWidget()

        self.horizontalLayout = QHBoxLayout(self.app)
        self.horizontalLayout.setContentsMargins(0, 0, -1, 0)

        self.setupSidebar(self.app)
        self.horizontalLayout.addWidget(self.sidebar)

        self.setupStack(self.app)
        self.horizontalLayout.addWidget(self.stackedWidget)

        self.connectSignals()

        return self.app

    def setupSidebar(self, Widget):

        self.sidebar = QWidget(parent=Widget)
        self.sidebar.setEnabled(True)
        self.sidebar.setMinimumSize(QtCore.QSize(200, 570))
        self.sidebar.setMaximumSize(QtCore.QSize(200, 570))
        self.sidebar.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.verticalLayout_2 = QVBoxLayout(self.sidebar)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.AppLogo = QWidget(parent=self.sidebar)
        self.AppLogo.setMinimumSize(QtCore.QSize(0, 40))
        self.AppLogo.setMaximumSize(QtCore.QSize(200, 40))

        self.label = QLabel(parent=self.AppLogo)
        self.label.setGeometry(QtCore.QRect(10, 0, 150, 40))

        self.verticalLayout_2.addWidget(self.AppLogo)
        self.setupSidebarButtons()

        self.widget = QWidget(parent=self.sidebar)
        self.widget.setMinimumSize(QtCore.QSize(0, 150))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 150))

        # Button Height
        button_height = 40  # Same height for all buttons
        button_spacing = 10  # Spacing between buttons

        # Username Button
        self.username_widget = QPushButton(parent=self.widget)
        self.username_widget.setGeometry(
            QtCore.QRect(2, 0, 190, button_height))
        self.username_widget.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))

        self.username_icon = QLabel(parent=self.username_widget)
        self.username_icon.setGeometry(QtCore.QRect(
            20, 10, 21, 21))  # Adjusted icon size
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.username_widget.setFont(font)
        self.arrow_icon = QLabel(parent=self.username_widget)
        self.arrow_icon.setGeometry(QtCore.QRect(
            170, 13, 16, 16))  # Adjusted icon size
        self.arrow_icon.setPixmap(QtGui.QPixmap(
            folder_path + "/open_arrow.svg"))

        self.username_widget.setText("Profile settings")

        # Signout Button
        self.Signout = QPushButton(
            parent=self.widget,
        )
        self.Signout.setGeometry(QtCore.QRect(
            2, button_height + button_spacing, 190, button_height))
        self.Signout.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.Signout.setFont(font)

        self.Signout_logo = QLabel(parent=self.Signout)
        self.Signout_logo.setGeometry(QtCore.QRect(22, 10, 21, 21))
        self.Signout_logo.setPixmap(
            QtGui.QPixmap(folder_path + "/signout.svg"))

        self.Signout.setText("Sign out")
        # Theme Button
        self.theme = QPushButton(parent=self.widget)
        self.theme.setGeometry(QtCore.QRect(
            2, 2 * (button_height + button_spacing), 190, 40))
        self.theme.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.theme_logo = QLabel(parent=self.theme)
        self.theme_logo.setGeometry(QtCore.QRect(
            10, 0, 90, 40))  # Adjusted icon size

        self.theme_label = QLabel(parent=self.theme)
        self.theme_label.setGeometry(QtCore.QRect(60, 10, 100, 20))
        self.theme_label.setFont(font)
        self.theme.clicked.connect(self.toggle_theme)

        self.verticalLayout_2.addWidget(self.widget)

    def setupSidebarButtons(self):
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.widget_6 = QWidget(parent=self.sidebar)
        self.widget_6.setMinimumSize(QtCore.QSize(0, 420))

        self.Activity = QPushButton("Activities", parent=self.widget_6)
        self.Activity.setGeometry(QtCore.QRect(2, 10, 190, 40))
        self.Activity.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.Activity.setFont(font)

        self.Activity_icon = QLabel(parent=self.Activity)
        self.Activity_icon.setGeometry(QtCore.QRect(20, 10, 21, 21))
        self.Activity_icon.setPixmap(
            QtGui.QPixmap(folder_path + "/Activity.svg"))

        self.settings = QPushButton("General settings", parent=self.widget_6)
        self.settings.setGeometry(QtCore.QRect(2, 55, 190, 40))
        self.settings.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.settings.setFont(font)

        self.settings_logo = QLabel(parent=self.settings)
        self.settings_logo.setGeometry(QtCore.QRect(20, 10, 21, 21))
        self.settings_logo.setPixmap(QtGui.QPixmap(
            folder_path + "/generalSettings.svg"))

        self.schedule = QPushButton("Schedule", parent=self.widget_6)
        self.schedule.setGeometry(QtCore.QRect(2, 100, 190, 40))
        self.schedule.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))
        self.schedule.setFont(font)

        self.schedule_logo = QLabel(parent=self.schedule)
        self.schedule_logo.setGeometry(QtCore.QRect(20, 10, 21, 21))
        self.schedule_logo.setPixmap(
            QtGui.QPixmap(folder_path + "/schedule.svg"))

        # self.Version = QPushButton("Version && update", parent=self.widget_6)
        # self.Version.setGeometry(QtCore.QRect(2, 145, 190, 40))
        # self.Version.setCursor(QtGui.QCursor(
        #     QtCore.Qt.CursorShape.PointingHandCursor))
        # self.Version.setFont(font)
        #
        # self.Version_icon = QLabel(parent=self.Version)
        # self.Version_icon.setGeometry(QtCore.QRect(20, 10, 21, 21))
        # self.Version_icon.setPixmap(
        #     QtGui.QPixmap(folder_path + "/version.svg"))

        self.verticalLayout_2.addWidget(self.widget_6)

    def setupStack(self, Widget):
        self.stackedWidget = QStackedWidget(parent=Widget)
        self.stackedWidget.setMinimumSize(QtCore.QSize(1134, 0))
        self.stackedWidget.setMaximumSize(QtCore.QSize(1134, 16777215))
        self.stackedWidget.setStyleSheet(
            "background-color: rgb(255, 255, 255);")


        self.setupActivitiesPage()
        self.setupGeneralSettingsPage()
        self.setupSchedulePage()
        # self.setupVersionPage()
        self.setupUserDrawer()

        self.stackedWidget.addWidget(self.Activites)
        self.stackedWidget.addWidget(self.GeneralSettings)
        self.stackedWidget.addWidget(self.Schedule)
        # self.stackedWidget.addWidget(self.Version_and_update)
        self.stackedWidget.addWidget(self.userProfile_widget)

        self.stackedWidget.currentChanged.connect(self.on_page_changed)



    def setupActivitiesPage(self):
        self.Activites = QWidget()
        self.displayed_events = set()
        self.Activites_header = QLabel(parent=self.Activites)
        self.Activites_header.setGeometry(QtCore.QRect(10, 15, 191, 40))
        self.Activites_header.setText("Activities")
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(20)
        else:
            font.setPointSize(16)
        font.setWeight(QFont.Weight.Bold)
        self.Activites_header.setFont(font)

        self.Date_display = QWidget(parent=self.Activites)
        self.Date_display.setGeometry(QtCore.QRect(10, 70, 560, 51))

        self.Day = QLabel(parent=self.Date_display)
        self.Day.setGeometry(QtCore.QRect(22, 15, 58, 20))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        font.setWeight(QFont.Weight.Bold)
        self.Day.setText("Today")
        self.Day.setFont(font)

        self.Date = QLabel(parent=self.Date_display)
        self.Date.setGeometry(QtCore.QRect(65, 15, 300, 20))
        font.setWeight(QFont.Weight.Bold)
        self.Date.setFont(font)

        self.scrollArea = QScrollArea(self.Activites)
        self.scrollArea.setGeometry(QtCore.QRect(10, 120, 560, 460))
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 560, 460))

        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.setSpacing(10)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.add_dynamic_blocks()

        self.update_date()  # Initial update of the date

    def on_page_changed(self, index):
        """This method is called when the current page changes in the stacked widget."""
        if index == 0:  # Assuming Activities page is the first page (index 0)
            self.start_timer()  # Start the timer for Activities page
        else:
            self.stop_timer()  # Stop the timer for other pages

    def start_timer(self):
        """Start the timer."""
        self.timer.start(30000)  # Start the timer

    def stop_timer(self):
        """Stop the timer."""
        self.timer.stop()

    def update_date(self):
        # Update the date label with the current date
        self.Date.setText(f" -  {datetime.today().strftime('%d %B %Y')}")

    def setupGeneralSettingsPage(self):
        self.GeneralSettings = QWidget()

        # Header label
        self.GeneralSettings_header = QLabel(parent=self.GeneralSettings)
        self.GeneralSettings_header.setGeometry(QRect(10, 15, 300, 44))
        font = QtGui.QFont()
        font.setWeight(QFont.Weight.Bold)
        font.setPointSize(20 if sys.platform == "darwin" else 16)
        self.GeneralSettings_header.setFont(font)
        self.GeneralSettings_header.setText("General settings")

        # Startup setting
        self.setup_startup_section()

        # Idle time detection setting
        self.setup_idletime_section()

        # Version and Update Section
        self.setup_version_section()

        # Retrieve and set initial settings
        self.load_settings()


    def setup_startup_section(self):
        self.startup = QWidget(parent=self.GeneralSettings)
        self.startup.setGeometry(QRect(10, 70, 550, 80))

        # Startup label
        self.startup_label = QLabel(parent=self.startup)
        self.startup_label.setGeometry(QRect(20, 30, 300, 16))
        self.startup_label.setText("Launch Sundial on system startup")
        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 10)
        self.startup_label.setFont(font)

        # Startup checkbox
        self.startup_checkbox = SwitchControl(
            self.startup,
            bg_color="#888888",
            circle_color="#FFFFFF",
            active_color="#FFA500",  # Orange when active
            animation_duration=300
        )
        self.startup_checkbox.setGeometry(QRect(490, 30, 80, 21))

        # Connect checkbox state change
        self.startup_checkbox.stateChanged.connect(self.startup_status)

    def setup_idletime_section(self):
        self.idletime = QWidget(parent=self.GeneralSettings)
        self.idletime.setGeometry(QRect(10, 160, 550, 80))

        # Idle time label
        self.idletime_label = QLabel(parent=self.idletime)
        self.idletime_label.setGeometry(QRect(20, 30, 211, 16))
        self.idletime_label.setText("Enable idle time detection")
        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 10)
        self.idletime_label.setFont(font)

        # Idle time checkbox
        self.idletime_checkbox = SwitchControl(
            self.idletime,
            bg_color="#888888",
            circle_color="#FFFFFF",
            active_color="#FFA500",  # Orange when active
            animation_duration=300
        )
        self.idletime_checkbox.setGeometry(QRect(490, 30, 100, 21))

        # Connect checkbox state change
        self.idletime_checkbox.stateChanged.connect(self.idletime_status)

    def setup_version_section(self):
        self.Version_2 = QWidget(parent=self.GeneralSettings)
        self.Version_2.setGeometry(QRect(10, 250, 550, 130))

        # Update header
        self.update_header = QLabel(parent=self.Version_2)
        self.update_header.setGeometry(QRect(20, 20, 311, 16))
        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 10)
        font.setWeight(QFont.Weight.Bold)
        self.update_header.setFont(font)
        self.update_header.setText("Update")

        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 8)
        # Update description
        self.update_description = QLabel(parent=self.Version_2)
        self.update_description.setGeometry(QRect(20, 50, 311, 16))
        self.update_description.setFont(font)
        self.update_description.setText("Your Sundial application is up to date")

        # Display current version
        self.current_version = QLabel(parent=self.Version_2)
        self.current_version.setGeometry(QRect(20, 80, 311, 20))
        self.current_version.setFont(font)
        self.update_version_display()

        self.startup_toast_message = QWidget(parent=self.GeneralSettings)
        self.startup_toast_message.setGeometry(QRect(830, 520, 350, 60))
        self.startup_toast_label = QLabel(self.startup_toast_message)
        self.startup_toast_label.setGeometry(QRect(20, 10, 330, 40))
        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 12)
        self.startup_toast_label.setFont(font)
        self.startup_toast_message.setStyleSheet(
            "border-radius: 10px; background-color:#BFF6C3")

        # Initially hide the toast
        self.startup_toast_message.setVisible(False)

        # Animation setup for sliding in the toast message
        self.toast_animation = QPropertyAnimation(self.startup_toast_message, b"geometry")
        self.toast_animation.setDuration(500)  # Animation duration in ms
        self.toast_animation.setStartValue(QRect(830, 520, 350, 60))  # Start position off the screen
        self.toast_animation.setEndValue(QRect(220, 520, 350, 60))  # End position on the screen
        self.toast_animation.setEasingCurve(QtCore.QEasingCurve.OutBounce)  # Easing effect for smoothness

    # Function to trigger the toast animation
    def show_toast_message(self, message):
        self.startup_toast_label.setText(message)
        self.startup_toast_message.setVisible(True)
        self.toast_animation.start()
        self.startup_toast_label.setStyleSheet("background:transparent")

        # Optionally hide the toast after a certain delay
        QtCore.QTimer.singleShot(3000, self.hide_toast_message)

    def hide_toast_message(self):
        self.startup_toast_message.setVisible(False)

    def get_toggle_style(self):
        return ("QToggle{"
                "qproperty-bg_color:#A2A4A6;"
                "qproperty-circle_color:#FFFFFF;"
                "qproperty-active_color:#FA9C2B;"
                "qproperty-disabled_color:#777;"
                "qproperty-text_color:#A0F;}")

    def load_settings(self):
        settings = retrieve_settings()
        self.startup_checkbox.setChecked(settings.get('launch', False))
        self.idletime_checkbox.setChecked(settings.get('idle_time', False))
        self.update_version_display()

    def version(self):
        settings = retrieve_settings()
        version = settings.get("version", "Unknown")
        return version

    def update_version_display(self):
        # Update the version label based on the system theme (dark/light mode)
        new_version = self.version()
        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        if self.is_dark_mode:
            self.current_version.setText(
                f'<span style="color: rgba(248, 248, 248, 0.5);">Current app version: </span>'
                f'<span style="color: white;">2.0.0_<span style="font-size=10px">beta</span></span>'
            )
        else:
            self.current_version.setText(
                f'<span style="color: rgba(71, 75, 79, 1);">Current app version: </span>'
                f'<span style="color: black;background:transparent;">2.0.0_<span style="font-size=10px">beta</span></span>'
            )
        self.current_version.update()

    def check_for_updates(self):
        def fetch_version():
            # Simulate fetching version from an external source or server
            new_version = self.get_version_from_server()  # Implement this
            settings = retrieve_settings()
            settings['version'] = new_version
            save_settings(settings)
            self.update_version_display()  # Update the UI after fetching version

        # Run the version check in a separate thread
        threading.Thread(target=fetch_version).start()

    def startup_status(self):
        status = ""
        if self.startup_checkbox.isChecked():  # Removed redundant check for `idle_time_checkbox`
            self.startup_checkbox.setChecked(True)
            status = "start"
            # self.show_toast_message("launch on start has been enabled")
        else:
            self.startup_checkbox.setChecked(False)
            status = "stop"
            # self.show_toast_message("launch on start has been disabled")
        self.launch_on_start(status)

    def idletime_status(self):
        if self.idletime_checkbox.isChecked():  # Removed redundant check for `idle_time_checkbox`
            status = "start"
            self.idletime_checkbox.setChecked(True)
        else:
            status = "stop"
            self.idletime_checkbox.setChecked(False)
            # self.show_toast_message("idletime has been disabled")
        self.enable_idletime(status)


    def setupSchedulePage(self):
        self.Schedule = QWidget(self)

        self.Schedule_label = QLabel(parent=self.Schedule)
        self.Schedule_label.setGeometry(QtCore.QRect(10, 15, 131, 44))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(20)
        else:
            font.setPointSize(16)
        font.setWeight(QFont.Weight.Bold)
        self.Schedule_label.setFont(font)

        self.Schedule_enabler = QWidget(parent=self.Schedule)
        self.Schedule_enabler.setGeometry(QtCore.QRect(10, 70, 550, 80))

        self.Schedule_enabler_label = QLabel(parent=self.Schedule_enabler)
        self.Schedule_enabler_label.setGeometry(QtCore.QRect(20, 30, 360, 20))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.Schedule_enabler_label.setFont(font)

        self.Schedule_enabler_checkbox = SwitchControl(
            self.Schedule_enabler,
            bg_color="#888888",
            circle_color="#FFFFFF",
            active_color="#FFA500",  # Orange when active
            animation_duration=300
        )
        self.Schedule_enabler_checkbox.setGeometry(
            QtCore.QRect(490, 30, 100, 21))

        self.day_widget = QWidget(parent=self.Schedule)
        self.day_widget.setGeometry(QtCore.QRect(10, 154, 550, 300))

        self.Working_days_label = QLabel(parent=self.day_widget)
        self.Working_days_label.setGeometry(QtCore.QRect(20, 20, 200, 20))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(16)
        else:
            font.setPointSize(12)
        font.setWeight(QFont.Weight.Bold)
        self.Working_days_label.setFont(font)

        self.info_message = QWidget(parent=self.day_widget)
        self.info_message.setGeometry(QtCore.QRect(120, 45, 400, 130))
        self.info_message.setVisible(False)

        self.info_message_label = QLabel("Schedule Info", self.info_message)
        self.info_message_label.setGeometry(QtCore.QRect(15, 15, 380, 20))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(8)
        font.setWeight(QFont.Weight.Bold)
        self.info_message_label.setFont(font)

        self.info_cancel_button = QPushButton(parent=self.info_message)
        self.info_cancel_button.setGeometry(QtCore.QRect(370, 15, 15, 15))
        self.info_cancel_button.clicked.connect(lambda: self.info_message.setVisible(False))

        self.info_message_des = QLabel(
            "Please be aware that this update will affect all future events. Any activities that were previously recorded outside of scheduled times will remain visible in your activities list.",
            self.info_message
        )
        self.info_message_des.setGeometry(QtCore.QRect(15, 50, 380, 60))
        self.info_message_des.setWordWrap(True)

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(8)
        self.info_message_des.setFont(font)

        shadow = QGraphicsDropShadowEffect(self.info_message)
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 160))  # Semi-transparent black shadow
        self.info_message.setGraphicsEffect(shadow)

        self.info_icon = QPushButton(parent=self.day_widget)
        self.info_icon.setGeometry(QtCore.QRect(120, 20, 40, 20))
        self.info_icon.clicked.connect(self.show_message)

        self.setupScheduleCheckboxes()

        self.Working_hours_label = QLabel(parent=self.day_widget)
        self.Working_hours_label.setGeometry(QtCore.QRect(20, 140, 200, 20))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(16)
        else:
            font.setPointSize(12)
        font.setWeight(QFont.Weight.Bold)
        self.Working_hours_label.setFont(font)
        self.Working_hours_label.setText("Working hours")

        self.From_time = QTimeEdit(parent=self.day_widget)
        self.From_time.setGeometry(QtCore.QRect(20, 180, 250, 40))
        self.From_time.setDisplayFormat("hh:mm")
        self.To_time = QTimeEdit(parent=self.day_widget)
        self.To_time.setGeometry(QtCore.QRect(285, 180, 250, 40))
        self.To_time.setDisplayFormat("hh:mm")
        self.From_time.timeChanged.connect(self.update_to_time_min)
        self.To_time.timeChanged.connect(self.update_from_time_max)

        self.result_label = QLabel(self.day_widget)
        self.result_label.setGeometry(QtCore.QRect(20, 230, 450, 30))

        self.To_time.timeChanged.connect(self.compare_times)
        self.From_time.timeChanged.connect(self.compare_times)

        self.Reset = QPushButton(parent=self.day_widget)
        self.Reset.setGeometry(QtCore.QRect(315, 235, 100, 50))
        self.Reset.clicked.connect(self.resetSchedule)

        self.From_time.timeChanged.connect(self.update_save_button_state)
        self.To_time.timeChanged.connect(self.update_save_button_state)

        self.Save = QPushButton(parent=self.day_widget)
        self.Save.setGeometry(QtCore.QRect(435, 235, 100, 50))
        self.Save.clicked.connect(self.saveSchedule)
        self.Reset.setText("Reset")
        self.Save.setText("Save")

        self.Schedule_enabler_checkbox.stateChanged.connect(
            self.toggle_schedule_visibility)

        self.day_widget.hide()
        retrieve_settings()
        self.Schedule_enabler_checkbox.setChecked(settings.get('schedule', False))
        if settings.get('schedule', False):
            self.day_widget.hide()
        else:
            self.day_widget.show()

        self.Schedule_enabler_checkbox.stateChanged.connect(
            self.toggle_schedule_visibility)

        self.updateCheckboxStates(settings.get('weekdays_schedule', {}))
        self.update_save_button_state()

        # Set up event filter to detect clicks outside the info_message
        self.Schedule.installEventFilter(self)

    def show_message(self):
        # Toggle the visibility of the info_message widget
        if self.info_message.isVisible():
            self.info_message.setVisible(False)
        else:
            self.info_message.setVisible(True)
            self.info_message.raise_()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # Convert global coordinates to local coordinates of info_message
            global_pos = event.globalPos()
            local_pos = self.info_message.mapFromGlobal(global_pos)
            # Check if the click is outside the info_message when it's visible
            if self.info_message.isVisible() and not self.info_message.rect().contains(local_pos):
                self.info_message.setVisible(False)
        return super().eventFilter(obj, event)


    def setupScheduleCheckboxes(self):

        self.monday_checkbox = CustomCheckBox(parent=self.day_widget)
        self.monday_checkbox.setGeometry(QtCore.QRect(20, 58, 30, 40))
        self.monday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px;}")

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)


        self.monday_label = QLabel(parent=self.day_widget)
        self.monday_label.setGeometry(QtCore.QRect(50, 50, 110, 40))

        self.monday_label.setFont(font)

        self.Tuesday_checkbox = CustomCheckBox(parent=self.day_widget)
        self.Tuesday_checkbox.setGeometry(QtCore.QRect(160, 58, 30, 40))
        self.Tuesday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Tuesday_label = QLabel(parent=self.day_widget)
        self.Tuesday_label.setGeometry(QtCore.QRect(190, 50, 110, 40))
        self.Tuesday_label.setFont(font)

        self.Wednesday_checkBox = CustomCheckBox(parent=self.day_widget)
        self.Wednesday_checkBox.setGeometry(QtCore.QRect(300, 58, 50, 40))
        self.Wednesday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Wednesday_label = QLabel(parent=self.day_widget)
        self.Wednesday_label.setGeometry(QtCore.QRect(330, 50, 120, 40))
        self.Wednesday_label.setFont(font)

        self.Thursday_checkbox = CustomCheckBox(parent=self.day_widget)
        self.Thursday_checkbox.setGeometry(QtCore.QRect(440, 58, 40, 40))
        self.Thursday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Thursday_label = QLabel(parent=self.day_widget)
        self.Thursday_label.setGeometry(QtCore.QRect(470, 50, 110, 40))
        self.Thursday_label.setFont(font)

        self.Friday_checkBox = CustomCheckBox(parent=self.day_widget)
        self.Friday_checkBox.setGeometry(QtCore.QRect(20, 98, 40, 40))
        self.Friday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Friday_label = QLabel(parent=self.day_widget)
        self.Friday_label.setGeometry(QtCore.QRect(50, 90, 70, 40))
        self.Friday_label.setFont(font)

        self.saturday_checkBox = CustomCheckBox(parent=self.day_widget)
        self.saturday_checkBox.setGeometry(QtCore.QRect(160, 98, 40, 40))
        self.saturday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Saturday_label = QLabel(parent=self.day_widget)
        self.Saturday_label.setGeometry(QtCore.QRect(190, 90, 70, 40))
        self.Saturday_label.setFont(font)

        self.Sunday_checkBox = CustomCheckBox(parent=self.day_widget)
        self.Sunday_checkBox.setGeometry(QtCore.QRect(300, 98, 40, 40))
        self.Sunday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Sunday_label_2 = QLabel(parent=self.day_widget)
        self.Sunday_label_2.setGeometry(QtCore.QRect(330, 90, 70, 40))
        self.Sunday_label_2.setFont(font)

        self.monday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Tuesday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Wednesday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.Thursday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Friday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.saturday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.Sunday_checkBox.stateChanged.connect(
            self.update_save_button_state)

        self.Schedule_label.setText("Schedule")
        self.Schedule_enabler_label.setText(
            "Record data only during my scheduled work hours.")
        self.Working_days_label.setText("Working days")

        self.monday_label.setText("Monday")
        self.Wednesday_label.setText("Wednesday")
        self.Tuesday_label.setText("Tuesday")
        self.Saturday_label.setText("Saturday")
        self.Thursday_label.setText("Thursday")
        self.Friday_label.setText("Friday")
        self.Sunday_label_2.setText("Sunday")

        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        # if not self.is_dark_mode:


    def setupUserDrawer(self):
        self.userProfile_widget = QWidget()

        self.profile_header = QLabel(parent=self.userProfile_widget)
        self.profile_header.setGeometry(QtCore.QRect(10, 15, 300, 44))
        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(20)
        else:
            font.setPointSize(16)
        font.setWeight(QFont.Weight.Bold)
        self.profile_header.setFont(font)
        self.profile_header.setText("Profile Settings")

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(14)
        else:
            font.setPointSize(10)


        self.profile_container = QWidget(parent=self.userProfile_widget)
        self.profile_container.setGeometry(QtCore.QRect(10, 70, 550, 140))

        self.profile_image = QWidget(parent=self.profile_container)
        self.profile_image.setGeometry(QtCore.QRect(20, 20, 82, 82))

        self.FirstName = QLabel("Name", parent=self.profile_container)
        self.FirstName.setGeometry(QtCore.QRect(140, 20, 121, 20))
        self.FirstName.setFont(font)

        self.Email = QLabel("Email", parent=self.profile_container)
        self.Email.setGeometry(QtCore.QRect(140, 50, 121, 20))
        self.Email.setFont(font)

        self.mobile = QLabel("Mobile", parent=self.profile_container)
        self.mobile.setGeometry(QtCore.QRect(140, 80, 121, 20))
        self.mobile.setFont(font)

        self.company = QLabel("Company", parent=self.profile_container)
        self.company.setGeometry(QtCore.QRect(140, 110, 121, 20))
        self.company.setFont(font)

        self.first_name_value = QLabel(parent=self.profile_container)
        self.first_name_value.setGeometry(QtCore.QRect(220, 20, 500, 20))
        self.first_name_value.setFont(font)

        self.email_value = QLabel(parent=self.profile_container)
        self.email_value.setGeometry(QtCore.QRect(220, 50, 221, 20))
        self.email_value.setFont(font)

        self.mobile_value = QLabel(parent=self.profile_container)
        self.mobile_value.setGeometry(QtCore.QRect(220, 80, 221, 20))
        self.mobile_value.setFont(font)

        self.company_value = QLabel(parent=self.profile_container)
        self.company_value.setGeometry(QtCore.QRect(220, 110, 500, 20))
        self.company_value.setFont(font)
        QTimer.singleShot(0,self.load_user_details)


    def connectSignals(self):
        self.Activity.clicked.connect(lambda: self.change_page(0))
        self.settings.clicked.connect(lambda: self.change_page(1))
        self.schedule.clicked.connect(lambda: self.change_page(2))
        # self.Version.clicked.connect(lambda: self.change_page(3))
        self.username_widget.clicked.connect(lambda: self.change_page(3))
        self.Signout.clicked.connect(self.sign_out)

        self.buttons = [self.Activity, self.settings,
                        self.schedule, self.username_widget]

    def change_page(self, index=0):
        # Detect system theme (dark mode) if not already detected
        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        # Define styles for light and dark mode
        dark_mode_button_style = """
            QPushButton {
                border: none;
                background: none;
                color: #FFFFFF;
                text-align: left;
                padding-left: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(50, 50, 50, 1),
                    stop: 1 rgba(0, 0, 0, 0.6)
                );
                color: #A49DC8;
            }
            QPushButton:checked {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(50, 50, 50, 1),
                    stop: 1 rgba(0, 0, 0, 0.6)
                );
                color: #A49DC8;
            }
            QLabel {
                background: none;
                color: #A49DC8;
            }
        """

        light_mode_button_style = """
            QPushButton {
                border: none;
                background: none;
                color: #474B4F;
                text-align: left;
                padding-left: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(232, 230, 241, 0.3),
                    stop: 1 rgba(232, 230, 241, 0.1)
                );
                color: #1D0B77;
            }
            QPushButton:checked {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(232, 230, 241, 1),
                    stop: 1 rgba(232, 230, 241, 0.4)
                );
                color: #1D0B77;
            }
            QLabel {
                background: none;
                color: #000000;
            }
        """

        dark_mode_signout_style = """
            QPushButton {
                border: none;
                background: none;
                color: #F8F8F8;
                text-align: left;
                padding-left: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;
            }
            QPushButton:checked {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;
            }
            QPushButton QLabel {
                background: none;
                color: #000000;
            }
        """

        light_mode_signout_style = """
            QPushButton {
                border: none;
                background: none;
                color: #474B4F;
                text-align: left;
                padding-left: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;
            }
            QPushButton:checked {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;
            }
            QPushButton QLabel {
                background: none;
                color: #000000;
            }
        """

        # Apply styles for buttons and signout button
        for button in self.buttons:
            button.setStyleSheet(dark_mode_button_style if self.is_dark_mode else light_mode_button_style)

        self.Signout.setStyleSheet(dark_mode_signout_style if self.is_dark_mode else light_mode_signout_style)

        # Handle selected page and button styling for specific pages
        if index == 4:
            self.load_user_details()
            self.stackedWidget.setCurrentIndex(index)

            username_style = """
                QPushButton {{
                    border: none;
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {gradient_start},
                        stop: 1 {gradient_end}
                    );
                    color: {text_color};
                    text-align: left;
                    padding-left: 60px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {gradient_start},
                        stop: 1 {gradient_end}
                    );
                    color: {text_color};
                }}
            """.format(
                gradient_start='rgba(50, 50, 50, 1)' if self.is_dark_mode else 'rgba(232, 230, 241, 1)',
                gradient_end='rgba(0, 0, 0, 0.6)' if self.is_dark_mode else 'rgba(232, 230, 241, 0.1)',
                text_color='#A49DC8' if self.is_dark_mode else '#1D0B77'
            )
            self.username_widget.setStyleSheet(username_style)
        else:
            self.stackedWidget.setCurrentIndex(index)
            selected_button_style = """
                QPushButton {{
                    border: none;
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {gradient_start},
                        stop: 1 {gradient_end}
                    );
                    color: {text_color};
                    text-align: left;
                    padding-left: 60px;
                }}
                QLabel {{
                    color: {label_color};
                    background-color: none;
                }}
            """.format(
                gradient_start='rgba(50, 50, 50, 1)' if self.is_dark_mode else 'rgba(232, 230, 241, 1)',
                gradient_end='rgba(0, 0, 0, 0.6)' if self.is_dark_mode else 'rgba(232, 230, 241, 0.4)',
                text_color='#A49DC8' if self.is_dark_mode else '#1D0B77',
                label_color='#A49DC8' if self.is_dark_mode else '#1D0B77'
            )
            self.buttons[index].setStyleSheet(selected_button_style)


    def update_to_time_min(self, time):
        self.To_time.setMinimumTime(time)

    def update_from_time_max(self, time):
        self.From_time.setMaximumTime(time)

    def toggle_schedule_visibility(self):
        if self.Schedule_enabler_checkbox.isChecked():
            self.Schedule_enabler_checkbox.setChecked(True)
            self.day_widget.setVisible(True)
        else:
            self.day_widget.setVisible(False)
            self.Schedule_enabler_checkbox.setChecked(False)
        threading.Thread(target=self.run_add_settings).start()

    def run_add_settings(self):
        add_settings('schedule', self.Schedule_enabler_checkbox.isChecked())


    def ellipsis(self, value, length):
        if len(value) > length:
            return value[:length] + "..."
        else:
            return value

    def initiate_login(self):
        email = self.emailField.text()
        password = self.passwordField.text()
        self.showLoaderSignal.emit(True)
        if not email and not password:
            self.showLoaderSignal.emit(False)
            self.show_error_message("User name and Password empty.")
            return

        if not email:
            self.showLoaderSignal.emit(False)
            self.show_error_message("User name is empty.")
            return
        elif not password:
            self.showLoaderSignal.emit(False)
            self.show_error_message("Password is empty.")
            return

        if not self.check_server_status():
            self.show_error_message(
                "Server not available. Please try again later.")
            return
        QCoreApplication.processEvents()  # Ensure UI updates

        # Run the login request in a separate thread
        threading.Thread(target=self.perform_login_request,
                         args=(email, password)).start()

    def perform_login_request(self, email, password):
        from sd_core.util import get_mac_address
        payload = {"userName": email, "password": password,
                   "companyId": self.companyid or "","deviceAddress":get_mac_address()}
        try:
            response = requests.post(host + "/0/ralvie/login", json=payload,
                                     headers={'Content-Type': 'application/json'})
            if response.ok:
                # Emit signal with the response
                self.loginSuccess.emit(response.json())
            else:
                self.loginFailed.emit("Server error. Please try again.")
        except Exception as e:
            self.loginFailed.emit(f"Error during login: {str(e)}")
        finally:
            self.showLoaderSignal.emit(False)
            self.showLoadersSignal.emit(False)  # Use signal to hide loader

    def process_login_response(self, response_data):
        if response_data["code"] == "UASI0011":
            self.sundail_token = response_data['data']['token']
            clear_credentials("SD_KEYS")
            cached_credentials = credentials()
            cached_credentials['Authenticated'] = True
            add_password("SD_KEYS", json.dumps(cached_credentials))
            user_details()
            self.clear_activities()
            self.add_dynamic_blocks()
            clear_credentials("SD_KEYS")
            self.loader_.setVisible(False)
            QCoreApplication.processEvents()
            self.update_settings()
            self.update_theme()
            if self.onboarding_status.value("onboarding_complete", False) == "j?KEgMKb:^kNMpX:Bx=7":
                # If onboarding is complete, skip it and go to the sign-in or main page
                self.app_layout.setCurrentWidget(self.app_ui)
                self.change_page(0)
            else:
                # Show the onboarding screen only once
                self.app_layout.setCurrentWidget(self.onboard)

        elif response_data["code"] == 'RCW00001':
            self.companies = response_data['data']['companies']

            if self.companies:
                self.populate_company_combobox()
                self.showLoaderSignal.emit(False)
                self.goToCompanyPageSignal.emit()
            else:
                self.showLoaderSignal.emit(False)
                self.show_error_message(
                    "No companies available for selection.")
        elif response_data["code"] == 'RCE0024':
            self.showLoaderSignal.emit(False)
            self.show_compnay_error_message(response_data["message"])
        elif response_data["code"] == 'RCE0103':
            self.showLoaderSignal.emit(False)
            self.show_compnay_error_message(response_data["message"])
        else:
            self.showLoaderSignal.emit(False)
            self.show_error_message(
                response_data.get("message", "Unknown error"))

    def show_error_message(self, message):
        self.errorMessageLabel.setText(message)
        self.errorMessageLabel.setVisible(True)
        QTimer.singleShot(
            5000, lambda: self.errorMessageLabel.setVisible(False))

    def show_compnay_error_message(self, message):
        self.companyErrorMessageLabel.setText(message)
        self.companyErrorMessageLabel.setVisible(True)
        QTimer.singleShot(
            5000, lambda: self.companyErrorMessageLabel.setVisible(False))

    def showLoader(self, show):
        self.loader_.setVisible(show)

    def load_user_details(self):
        """Load and display the logged-in user's details."""
        # Fetch user details from the storage or API (you can adjust this as needed)
        user_details = self.get_user_details_from_cache()

        if user_details:
            # Update the UI components with the fetched user details

            if len(user_details.get('firstname', '')) > 30:
                # Add tooltip for the full app name
                self.first_name_value.setText(self.ellipsis(user_details.get('firstname', ''), 30))
                self.first_name_value.setToolTip(user_details.get('firstname', ''))
            else:
                self.first_name_value.setText(user_details.get('firstname', ''))

            if len(user_details.get('email', '')) > 30:
                # Add tooltip for the full app name
                self.email_value.setText(self.ellipsis(user_details.get('email', ''), 30))
                self.email_value.setToolTip(user_details.get('email', ''))
            else:
                 self.email_value.setText(user_details.get('email', ''))
            self.mobile_value.setText(user_details.get('phone', ''))

            if len(user_details.get('companyName', '')) > 30:
                # Add tooltip for the full app name
                self.company_value.setText(self.ellipsis(user_details.get('companyName', ''), 30))
                self.company_value.setToolTip(user_details.get('companyName', ''))
            else:
                self.company_value.setText(user_details.get('companyName', ''))


            self.first_name_value.update()
            self.email_value.update()
            self.mobile_value.update()
            self.company_value.update()


    def get_user_details_from_cache(self):
        """Retrieve user details from the cache or persistent storage."""
        # Assuming you have a method to get user credentials or details from storage
        creds = credentials()
        if creds and creds.get("Authenticated"):
            user_details = {
                'firstname': creds.get('firstname', ''),
                'email': creds.get('email', ''),
                'phone': creds.get('phone', ''),
                'companyName': creds.get('companyName', '')
            }
            return user_details
        else:
            return {}

    def go_to_company_page(self):
        self.loader_.setVisible(False)
        self.stacked_layout.setCurrentIndex(2)

    def populate_company_combobox(self):
        self.companySelect.clear()
        unique_company_names = {company['name'] for company in self.companies}
        self.companySelect.addItems(unique_company_names)

    def handle_company_selection(self):
        self.selected_company = self.companySelect.currentText()
        self.continue_with_selected_company()

    def continue_with_selected_company(self):
        self.companyid = next(
            (comp['id'] for comp in self.companies if comp['name'] == self.selected_company), None)
        if self.companyid:
            self.showLoadersSignal.emit(True)
            self.initiate_login()
        else:
            self.show_error_message("Company selection error.")

    def check_server_status(self):
        try:
            response = requests.get(
                "http://localhost:7600/api/0/server_status")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def update_settings(self):
        retrieve_settings()
        self.updateCheckboxStates(settings.get('weekdays_schedule', {}))
        self.Schedule_enabler_checkbox.setChecked(
            settings.get('schedule', False))
        if settings.get('schedule'):
            self.day_widget.show()
        else:
            self.day_widget.hide()
        self.load_user_details()
        self.startup_checkbox.setChecked(settings.get('launch', False))
        self.idletime_checkbox.setChecked(settings.get('idle_time', False))

    def app_authentication(self):
        self.app_layout.setCurrentIndex(0)  # Start with the loader page
        self.server_check_timer = QTimer(self)
        self.server_check_timer.timeout.connect(self.check_server_status_async)
        # Check every second for server status
        self.server_check_timer.start(1000)

    def check_server_status_async(self):
        if self.check_server_status():  # Check if the server is up
            self.server_check_timer.stop()  # Stop the timer once the server is running
            creds = credentials()
            if creds and creds.get("Authenticated"):
                self.update_settings()
                # Directly to the main UI if already authenticated
                if self.onboarding_status.value("onboarding_complete", False) == "j?KEgMKb:^kNMpX:Bx=7":
                    # If onboarding is complete, skip it and go to the sign-in or main page
                    self.app_layout.setCurrentWidget(self.app_ui)
                else:
                    # Show the onboarding screen only once
                    self.app_layout.setCurrentWidget(self.onboard)
                    self.change_page(0)
            else:
                self.app_layout.setCurrentIndex(1)  # Show the sign-in page
        else:
            print("Waiting for the server to start...")

    def add_dynamic_blocks(self):
        # Get schedule times and format them
        start_time_utc1, end_time_utc1 = self.get_schedule_times()
        start_time = start_time_utc1.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time_utc1.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fetching events from {start_time} to {end_time}")

        # Retrieve credentials
        creds = credentials()
        if creds:
            sundial_token = creds['token']
        else:
            print("No credentials found")
            return

        try:
            # Fetch events from the server
            response = requests.get(
                host +
                f"/0/dashboard/events?start={start_time}&end={end_time}",
                headers={"Authorization": sundial_token}
            )
            event_data = response.json()
            # Clear old events from the layout
            for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

            if event_data and 'events' in event_data and len(event_data['events']) > 0:
                list_view_events = listView(event_data['events'])
                self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                for event in list_view_events:
                    event_id = event['app'] + event['time']
                    color = get_next_color()  # Get the correct color
                    self.event_details = QtWidgets.QWidget(
                        parent=self.scrollAreaWidgetContents)
                    self.event_details.setFixedSize(540, 60)

                    # Store the color as a property on the widget
                    self.event_details.setProperty(
                        'light_color', color.get('light_color'))
                    self.event_details.setProperty(
                        'darker_color', color.get('dark_color'))

                    self.application_name = QtWidgets.QLabel(parent=self.event_details)
                    self.application_name.setObjectName("application_name")
                    self.application_name.setGeometry(
                        QtCore.QRect(17, 15, 420, 30))
                    font = QtGui.QFont()
                    if sys.platform == "darwin":
                        font.setPointSize(14)
                    else:
                        font.setPointSize(10)
                    self.application_name.setFont(font)
                    truncated_text = self.truncate_text(event['app'], 50)
                    self.application_name.setText(truncated_text)
                    if len(event['app']) > 50:
                        # Add tooltip for the full app name
                        self.application_name.setToolTip(event['app'])

                    font = QtGui.QFont()
                    if sys.platform == "darwin":
                        font.setPointSize(12)
                    else:
                        font.setPointSize(8)

                    self.time_label = QtWidgets.QLabel(parent=self.event_details)
                    self.time_label.setObjectName("time_label")
                    self.time_label.setGeometry(QtCore.QRect(425, 15, 261, 30))
                    self.time_label.setFont(font)
                    self.time_label.setText(event['time'])

                    # Set transparent background
                    self.application_name.setStyleSheet("background:transparent;")
                    self.time_label.setStyleSheet("background:transparent;")

                    self.layout.addWidget(self.event_details)
                self.layout.update()

            else:
                print("No events found or empty event list")

        except Exception as e:
            print(f"Error retrieving or processing events: {e}")

    def get_schedule_times(self):
        current_utc_date = datetime.utcnow().date()
        start_time_utc = datetime(
            current_utc_date.year, current_utc_date.month, current_utc_date.day)
        end_time_utc = start_time_utc + \
            timedelta(days=1) - timedelta(seconds=1)
        return start_time_utc, end_time_utc

    def truncate_text(self, text, max_words):
        return text[:max_words] + "..." if len(text) > max_words else text

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.update_theme()

    # Your existing update_theme method, assuming the tooltip style gets updated here
    def update_theme(self):
        if self.is_dark_mode:
            self.apply_dark_theme()
            self.update_events_style()
            self.change_page(0)
        else:
            self.apply_light_theme()
            self.update_events_style()
            self.change_page(0)


            # Ensure version display is updated regardless of theme
        self.update_version_display()


    def update_events_style(self):
        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_theme = self.detect_system_theme()


        for event_widget in self.scrollAreaWidgetContents.findChildren(QWidget):
            light_color = event_widget.property(
                'light_color')  # Retrieve the stored color
            dark_color = event_widget.property(
                'darker_color')  # Retrieve the stored color
            if dark_color and light_color:
                dynamic_stylesheet = self.get_dynamic_block_stylesheet(
                    light_color, dark_color)

                combined_stylesheet = dynamic_stylesheet
                # Apply the combined stylesheet to the widget
                event_widget.setStyleSheet(combined_stylesheet)
                # Assuming application_name and time_label are QLabel widgets inside each event_widget
                application_name = event_widget.findChild(
                    QLabel, "application_name")
                time_label = event_widget.findChild(QLabel, "time_label")
                if application_name and time_label:
                    application_name.setStyleSheet("background:transparent;")
                    time_label.setStyleSheet("background:transparent;")

    def get_dynamic_block_stylesheet(self, light_color, dark_color):
        # Base styles for QWidget based on mode
        if self.is_dark_mode:
            block_style = (
                ".QWidget {"
                f"background-color: {dark_color};"
                f"color: white;"
                f"border-radius: 5px;"
                f"margin-left: 20px;"
                f"margin-top: 5px;"
                f"opacity: 0.9;"  # Slight transparency for a lighter look
                f"border-left: 3px solid {dark_colors_border.get(dark_color)};"
                "}"
                "QWidget {"
                f"background-color: {dark_color};"
                f"color: white;"
                f"border-radius: 5px;"
                f"margin-left: 20px;"
                f"margin-top: 5px;"
                f"opacity: 0.9;"  #
                "}"

            )
        else:
            block_style = (
                ".QWidget {"
                f"background-color: {light_color};"
                f"border-radius: 5px;"
                f"margin-top: 5px;"
                f"border-left: 3px solid {light_colors_border.get(light_color)};"
                "}"
                "QWidget {"
                f"background-color: {light_color};"
                f"color: black;"
                f"border-radius: 5px;"
                f"margin-left: 20px;"
                f"margin-top: 5px;"
                "}"
            )

        # Combine the QWidget and QToolTip styles
        combined_stylesheet = block_style

        return combined_stylesheet

    def button_style(self):
        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()
        if self.is_dark_mode:
            self.Reset.setStyleSheet(
                "color:#6A5FA2; border: 1px solid #6A5FA2; border-radius: 5px;")
            self.Save.setStyleSheet(
                "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2); border-radius: 5px; color: #FFFFFF; border: 1px solid #1D0B77;")
        else:
            self.Reset.setStyleSheet(
                "color:#1D0B77; border: 1px solid #1D0B77; border-radius: 5px;")
            self.Save.setStyleSheet(
                "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2); border-radius: 5px; color: #FFFFFF; border: 1px solid #1D0B77;")

    def launch_status(self):
        launch_settings = retrieve_settings()
        launch_status = launch_settings.get("launch")
        return launch_status

    def launch_on_start(self, status):
        params = {"status": status}

        # Get the credentials
        creds = credentials()  # Assuming this function returns a dictionary with a token
        if creds and "token" in creds:
            sundial_token = creds["token"]

            try:
                response = requests.get(
                    host + "/0/launchOnStart",
                    headers={"Authorization": f"Bearer {sundial_token}"},
                    params=params
                )
                if response.status_code == 200:
                    print("Launch on start updated successfully")
                else:
                    print(f"Failed to update idle time: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"An error occurred while sending the request: {e}")
        else:
            print("No valid credentials found")

    def enable_idletime(self, status):
        params = {"status": status}

        # Get the credentials
        creds = credentials()  # Assuming this function returns a dictionary with a token
        if creds and "token" in creds:
            sundial_token = creds["token"]

            try:
                # Send the request with query parameters and the authorization token
                response = requests.get(
                    host + "/0/idletime",
                    headers={"Authorization": f"Bearer {sundial_token}"},
                    params=params
                )

                # Handle the response
                if response.status_code == 200:
                    print("Idle time updated successfully")
                else:
                    print(f"Failed to update idle time: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"An error occurred while sending the request: {e}")
        else:
            print("No valid credentials found")

    def updateCheckboxStates(self, weekdays):
        self.monday_checkbox.setChecked(weekdays.get('Monday', False))
        self.Tuesday_checkbox.setChecked(weekdays.get('Tuesday', False))
        self.Wednesday_checkBox.setChecked(weekdays.get('Wednesday', False))
        self.Thursday_checkbox.setChecked(weekdays.get('Thursday', False))
        self.Friday_checkBox.setChecked(weekdays.get('Friday', False))
        self.saturday_checkBox.setChecked(weekdays.get('Saturday', False))
        self.Sunday_checkBox.setChecked(weekdays.get('Sunday', False))
        self.From_time.setTime(QtCore.QTime.fromString(
            weekdays.get('starttime', "09:30"), "HH:mm"))
        self.To_time.setTime(QtCore.QTime.fromString(
            weekdays.get('endtime', "18:30"), "HH:mm"))

    def compare_times(self):
        from_time = self.From_time.time()
        to_time = self.To_time.time()
        if from_time > to_time:
            self.result_label.setText("From Time is greater than To Time")
        else:
            week_schedule['starttime'] = self.From_time.time().toString(
                "hh:mm")
            week_schedule['endtime'] = self.To_time.time().toString("hh:mm")
        self.update_save_button_state()

    def resetSchedule(self):
        global week_schedule
        threading.Thread(target=self.save_schedule,
                         args=(default_week_schedule,)).start()
        self.updateCheckboxStates(default_week_schedule)
        self.update_save_button_state()

    def save_schedule(self, schedule):
        add_settings('weekdays_schedule', schedule)
        self.update_save_button_state()

    def check_all_days_false(self):
        return not any([
            self.monday_checkbox.isChecked(),
            self.Tuesday_checkbox.isChecked(),
            self.Wednesday_checkBox.isChecked(),
            self.Thursday_checkbox.isChecked(),
            self.Friday_checkBox.isChecked(),
            self.saturday_checkBox.isChecked(),
            self.Sunday_checkBox.isChecked()
        ])

    def saveSchedule(self):
        if self.check_all_days_false():

            return  # Do not proceed with saving if all days are unchecked

        week_schedule = {
            'Monday': self.monday_checkbox.isChecked(),
            'Tuesday': self.Tuesday_checkbox.isChecked(),
            'Wednesday': self.Wednesday_checkBox.isChecked(),
            'Thursday': self.Thursday_checkbox.isChecked(),
            'Friday': self.Friday_checkBox.isChecked(),
            'Saturday': self.saturday_checkBox.isChecked(),
            'Sunday': self.Sunday_checkBox.isChecked(),
            'starttime': self.From_time.time().toString("HH:mm"),
            'endtime': self.To_time.time().toString("HH:mm"),
        }
        threading.Thread(target=self.save_schedule,
                         args=(week_schedule,)).start()

        self.updateCheckboxStates(week_schedule)

    def update_save_button_state(self):
        current_schedule = {
            'Monday': self.monday_checkbox.isChecked(),
            'Tuesday': self.Tuesday_checkbox.isChecked(),
            'Wednesday': self.Wednesday_checkBox.isChecked(),
            'Thursday': self.Thursday_checkbox.isChecked(),
            'Friday': self.Friday_checkBox.isChecked(),
            'Saturday': self.saturday_checkBox.isChecked(),
            'Sunday': self.Sunday_checkBox.isChecked(),
            'starttime': self.From_time.time().toString("HH:mm"),
            'endtime': self.To_time.time().toString("HH:mm")
        }

        if not DeepDiff(current_schedule, settings.get('weekdays_schedule')) or self.check_all_days_false():
            self.Save.setEnabled(False)
            self.Reset.setEnabled(True)
            if not hasattr(self, 'is_dark_mode'):
                self.is_dark_mode = self.detect_system_theme()
            # Set styles based on dark mode
            if self.is_dark_mode:
                # Styles for Reset button in dark mode
                self.Reset.setStyleSheet(
                    "color:#6A5FA2; border: 1px solid #6A5FA2; border-radius: 5px;")

                # Styles for Save button in dark mode
                self.Save.setStyleSheet(
                    """
                    background: qlineargradient(
                        spread: pad,
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(45, 35, 100, 76),  /* Duller #1D0B77 with opacity */
                        stop: 1 rgba(90, 80, 130, 76)  /* Duller #6A5FA2 with opacity */
                    );
                    border-radius: 5px;
                    color: rgba(255, 255, 255, 0.3);
                    """
                )
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0.1)  # Set opacity to 0.3
                self.Save.setGraphicsEffect(opacity_effect)
                self.Reset.setGraphicsEffect(opacity_effect)
            else:
                # Styles for Reset button in light mode
                self.Reset.setStyleSheet(
                    "color:#1D0B77; border: 1px solid #1D0B77; border-radius: 5px;")

                # Styles for Save button in light mode
                self.Save.setStyleSheet(
                    """
                    background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(45, 35, 100, 76),  /* Duller #1D0B77 with opacity */
                    stop: 1 rgba(90, 80, 130, 76)  /* Duller #6A5FA2 with opacity */
                );
                border-radius: 5px;
                color: rgba(255, 255, 255, 0.3);
                    """
                )
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0.1)  # Set opacity to 0.3
                self.Save.setGraphicsEffect(opacity_effect)
                self.Reset.setGraphicsEffect(opacity_effect)
        else:
            self.button_style()
            self.Save.setEnabled(True)
            self.Reset.setEnabled(True)

    def sign_out(self):
        global cached_credentials
        cached_creds = cache_user_credentials("SD_KEYS")
        cached_creds['Authenticated'] = False
        add_password("SD_KEYS", json.dumps(cached_creds))

        # Clear user-specific fields
        self.emailField.clear()
        self.passwordField.clear()
        self.companyid = ""
        self.sundail_token = None  # Clear the token as well

        self.clear_activities()

        self.app_layout.setCurrentIndex(1)
        self.stacked_layout.setCurrentIndex(0)

    def clear_activities(self):
        """Clear the activities displayed in the activities list."""
        # Clear the layout that holds the activities
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.displayed_events.clear()  # Clear the set that tracks displayed events

    def detect_system_theme(self):
        palette = QApplication.instance().palette()
        base_color = palette.color(QPalette.ColorRole.Window)
        return base_color.lightness() < 128

    def apply_dark_theme(self):
        # Set general stylesheet for the window
        self.setStyleSheet("color: #F8F8F8;")

        # Apply tooltip colors using QPalette for dark theme
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet("""
                QToolTip {
                    color: #5e5e5d;
                    background-color: #000000;
                    padding: 5px;
                    border-radius: 3px;
                }
                * {
                    color: #F8F8F8;
                }
            """)
        self.theme.setStyleSheet("background-color")
        self.monday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px;}")
        # loading page background
        background_image = os.path.join(darkTheme, "darkBackground.svg")
        # Load the background image
        background_pixmap = QPixmap(background_image)
        self.background.setPixmap(background_pixmap)
        # Make the pixmap scale with the label
        self.background.setScaledContents(True)

        self.monday_checkbox.setStyleSheet("""
                        QCheckBox::indicator {
                            width: 25px;
                            height: 25px;
                        }
                        QCheckBox {
                            font-size: 18px;
                        }
                    """)

        # loading page logo
        SundialLogo = os.path.join(darkTheme, "darkSundialLogo.svg")
        pixmap = QPixmap(SundialLogo)  # Load the background image
        self.Sundial_logo.setPixmap(pixmap)
        self.Sundial_logo.setStyleSheet("background: transparent;")

        # -------------------------Dashboard-----------------------------#
        # Dashboard background
        self.homepage_background.setPixmap(background_pixmap)
        self.homepage_background.setScaledContents(True)

        # Dashboard Logo
        homepage_SundialLogo = os.path.join(darkTheme, "dark_des_logo.svg")
        homepage_pixmap = QPixmap(homepage_SundialLogo)
        self.homepage_Sundial_logo.setPixmap(homepage_pixmap)
        self.homepage_Sundial_logo.setStyleSheet("background: transparent;")

        # Dashboard_subtitle
        homepage_subtitle = os.path.join(darkTheme, "signin_subtitle.svg")
        homepage_subtitle_pixmap = QPixmap(homepage_subtitle)
        self.homepage_subtitle.setPixmap(homepage_subtitle_pixmap)
        self.homepage_subtitle.setStyleSheet("background-color: none;")

        self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join(darkTheme, "darkSundialLogo.svg")))
        self.background.setPixmap(QPixmap(os.path.join(darkTheme, "darkBackground.svg")))
        self.privacy_background.setPixmap(QPixmap(os.path.join(darkTheme, "darkBackground.svg")))
        self.datasecurity_background.setPixmap(QPixmap(os.path.join(darkTheme, "darkBackground.svg")))
        self.settings_background.setPixmap(QPixmap(os.path.join(darkTheme, "darkBackground.svg")))
        self.accessibility_background.setPixmap(QPixmap(os.path.join(darkTheme, "darkBackground.svg")))

        self.privacy_img.setPixmap(QPixmap(os.path.join(darkTheme, "privacy.png")))
        self.datasecurity_img.setPixmap(QPixmap(os.path.join(darkTheme, "Dataprivacy.svg")))
        self.datasecurity_sundial_logo.setPixmap(QPixmap(os.path.join(darkTheme, "darkSundialLogo.svg")))
        self.settings_sundial_logo.setPixmap(QPixmap(os.path.join(darkTheme, "darkSundialLogo.svg")))
        self.accessibility_sundial_logo.setPixmap(QPixmap(os.path.join(darkTheme, "darkSundialLogo.svg")))
        self.accessibility_img.setPixmap(QPixmap(
            os.path.join(darkTheme, "accessibilty_Image.png")))


        # Set styles for containers
        container_style = """
                background-color: rgba(10, 10, 10, 0.8);  /* 80% opacity */
                border-radius: 5px;
            """

        self.idle_time.setStyleSheet(container_style)
        self.start_up.setStyleSheet(container_style)

        # Set styles for buttons
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

        self.privacy_next_btn.setStyleSheet(gradient_style)
        self.next_btn.setStyleSheet(gradient_style)
        self.back_btn.setStyleSheet(solid_button_style)
        self.accessibility_back_btn.setStyleSheet(solid_button_style)
        self.accessibility_next_btn.setStyleSheet(gradient_style)
        self.settings_back_btn.setStyleSheet(solid_button_style)
        self.settings_next_btn.setStyleSheet(gradient_style)

        # Ensure transparent backgrounds for necessary elements
        transparent_style = "background: none;"

        self.settings_sundial_logo.setStyleSheet(transparent_style)
        self.privacy_header.setStyleSheet(transparent_style)
        self.privacy_info.setStyleSheet(transparent_style)
        self.privacy_info_2.setStyleSheet(transparent_style)
        self.privacy_img.setStyleSheet(transparent_style)
        self.privacy_sundial_logo.setStyleSheet(transparent_style)
        self.datasecurity_img.setStyleSheet(transparent_style)
        self.datasecurity_sundial_logo.setStyleSheet(transparent_style)
        self.datasecurity_info.setStyleSheet(transparent_style)
        self.datasecurity_header.setStyleSheet(transparent_style)
        self.accessibility_img.setStyleSheet(transparent_style)
        self.accessibility_header.setStyleSheet(transparent_style)
        self.accessibility_sundial_logo.setStyleSheet(transparent_style)
        self.accessibility_info.setStyleSheet(transparent_style)

        self.settings_header.setStyleSheet(transparent_style)
        self.idle_time_info.setStyleSheet(transparent_style)
        self.start_up_info.setStyleSheet(transparent_style)
        # Dashboard Description
        self.description.setStyleSheet("background-color: none;")
        self.signIn_button.setStyleSheet("""
                                QPushButton#signInButton {
                                    border: none;
                                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                    color: #ffffff;
                                    border-radius: 10px;
                                    padding: 10px;
                                    font-size: 16px;
                                }
                                QPushButton:focus {
                                    outline: none;  /* Remove the focus outline */
                                }
                            """)

        # ------------------------------SignIn--------------------------#
        # Dashboard background
        self.sign_in_background.setPixmap(background_pixmap)
        self.sign_in_background.setScaledContents(True)

        # Dashboard Logo
        sign_in_SundialLogo = os.path.join(darkTheme, "dark_signin_logo.svg")
        sign_in_pixmap = QPixmap(sign_in_SundialLogo)
        self.sign_in_Sundial_logo.setPixmap(sign_in_pixmap)
        self.sign_in_Sundial_logo.setStyleSheet("background: transparent;")

        self.signin_widget.setStyleSheet(
            "background-color: #010101; border-radius: 10px;"
        )
        self.signin_widget.setWindowOpacity(1.0)
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))

        self.signin_widget.setGraphicsEffect(shadow_effect)

        # Welcome Message
        self.welcomeMessage.setStyleSheet(
            "color: #F8F8F8;background: transparent;")

        # signup label
        self.newUserLabel.setStyleSheet(
            "color: #F8F8F8;background: transparent;")
        self.signupLabel.setStyleSheet(
            "color: #A49DC8; background: transparent;"
        )

        self.emailField.setStyleSheet("""
                                                    QLineEdit {
                                                        background: #010101;
                                                        border: 1px solid #313131;
                                                        border-radius: 10px;
                                                        padding: 10px;
                                                        opacity: 1;
                                                    }
                                                    QLineEdit::placeholder {
                                                        color: #F8F8F8;
                                                        font-size: 14px;
                                                    }
                                                    QLineEdit:focus {
                                                        border: 1px solid #007BFF;
                                                        background: #010101;
                                                    }
                                                """)
        self.showPassButton.setStyleSheet("background: transparent; border: none;")
        self.passwordField.setStyleSheet("""
                                                    QLineEdit {
                                                        background: #010101;
                                                        border: 1px solid #313131;
                                                        border-radius: 10px;
                                                        padding: 10px;
                                                        opacity: 1;
                                                        padding-right: 60px;
                                                    }
                                                    QLineEdit::placeholder {
                                                        color: #F8F8F8;
                                                        font-size: 14px;
                                                    }
                                                    QLineEdit:focus {
                                                        border: 1px solid #007BFF;
                                                        background: #010101;
                                                    }
                                                    QLineEdit:disabled {
                                                        background: #E0E0E0;
                                                        border: 1px solid #B0B0B0;
                                                    }
                                                """)
        self.sign_In_button.setStyleSheet("""
                                                    QPushButton#sign_In_button {
                                                        border: none;
                                                        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                                        color: #ffffff;
                                                        border-radius: 10px;
                                                        padding: 10px;
                                                        font-size: 16px;
                                                    }

                                                    QPushButton:focus {
                                                        outline: none;  /* Remove the focus outline */
                                                    }
                                                """)
        self.Forgot_password_Label.setStyleSheet(
            "background: transparent;color:#242424;text-decoration: none;")

        self.company_background.setPixmap(background_pixmap)
        self.company_background.setScaledContents(True)

        # signin Logo
        company_SundialLogo = os.path.join(darkTheme, "dark_signin_logo.svg")
        company_pixmap = QPixmap(sign_in_SundialLogo)
        self.company_Sundial_logo.setPixmap(company_pixmap)
        self.company_Sundial_logo.setStyleSheet("background: transparent;")

        self.company_widget.setStyleSheet(
            "background-color: #010101; border-radius: 10px;"
        )
        self.signin_widget.setWindowOpacity(1.0)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))

        self.company_widget.setGraphicsEffect(shadow_effect)
        self.CompanyMessage.setStyleSheet(
            "color: #F8F8F8;background: transparent;")
        self.companySelect.setStyleSheet(f"""
                        QComboBox {{
                            background: #010101; /* Background color */
                            border: 1px solid #313131; /* Border color */
                            border-radius: 10px; /* Rounded corners */ 
                            color: white; /* Text color */
                            font-size: 16px; /* Font size */
                            padding-left: 10px;
                        }}
                        QComboBox::drop-down {{
                            border: none; /* Remove border */
                            subcontrol-origin: padding; /* Position the arrow */
                            subcontrol-position: center Right; /* Position the arrow */
                            margin-right: 10px;
                        }}
                        QComboBox::down-arrow {{
                            image: url({dark_downarrow}); /* Use the variable for the arrow image */
                            width: 16px; /* Width of the arrow */
                            height: 16px; /* Height of the arrow */
                            margin: 10px;
                            margin-right: 20px;
                        }}
                    """)
        self.company_select_button.setStyleSheet("""
                                                    QPushButton {
                                                        border: none;
                                                        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                                        color: #ffffff;
                                                        border-radius: 10px;
                                                        padding: 10px;
                                                        font-size: 16px;
                                                    }
                                                    QPushButton:focus {
                                                        outline: none;  /* Remove the focus outline */
                                                    }
                                                """)
        self.app.setStyleSheet("background-color:#010101")
        self.sidebar.setStyleSheet("background-color:#010101")
        self.widget_6.setStyleSheet("background-color:#010101")
        self.widget.setStyleSheet("background-color:#010101")
        self.Activites.setStyleSheet("background-color:#010101")
        self.GeneralSettings.setStyleSheet("background-color:#010101")
        self.Schedule.setStyleSheet("background-color:#010101")
        # self.Version_and_update.setStyleSheet("background-color:#010101")
        self.label.setPixmap(QtGui.QPixmap(
            os.path.join(darkTheme, "dark_sundial_homepage.svg")))
        self.label.setStyleSheet("background: none;")
        self.AppLogo.setStyleSheet("background: none;")
        self.label.setScaledContents(1)

        # self.version_label.setStyleSheet(
        #     "background:none;rgba(248, 248, 248, 0.8)")
        self.GeneralSettings_header.setStyleSheet(
            "background-color:#010101;rgba(248, 248, 248, 0.8)")
        self.Activites_header.setStyleSheet(
            "background-color:#010101;rgba(248, 248, 248, 0.8)")
        self.Schedule_label.setStyleSheet(
            "background-color:#010101;rgba(248, 248, 248, 0.8)")

        self.startup.setStyleSheet(
            "border-radius: 10px; background-color:#171717;")
        self.idletime.setStyleSheet(
            "border-radius: 10px; background-color:#171717;")

        self.Schedule_enabler.setStyleSheet(
            f"""
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            background-color:#171717;
            """)
        self.Version_2.setStyleSheet(
            "border-radius: 10px; background-color:#171717;")
        self.profile_container.setStyleSheet(
            "border-radius: 10px; background-color:#171717;")
        self.day_widget.setStyleSheet(f"""QWidget {{
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;  background-color: #171717;
                }}
            """)
        self.scrollArea.setStyleSheet("border:None;background-color:#101010;")
        self.scrollAreaWidgetContents.setStyleSheet(
            "border:None;background-color:#101010;")
        self.scrollArea.verticalScrollBar().setStyleSheet("""
                    QScrollBar:vertical {
                        width: 5px;
                        margin: 0px 0px 0px 0px;
                        border-radius: 5px;
                    }
                    QScrollBar::handle:vertical {
                        background: #B0B0B0;
                        min-height: 20px;
                        border-radius: 5px;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                        width: 0px;
                    }
                    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                        background: none;
                    }
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                    }
                """)
        self.Date_display.setStyleSheet("""
            background-color: #171717;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
        """)

        self.scrollArea.setStyleSheet(
            "border:None; background-color:#101010;border-bottom-left-radius: 10px;border-bottom-right-radius: 10px;")
        self.Day.setStyleSheet("background: transparent")
        self.Date.setStyleSheet("background: transparent")
        self.Schedule_enabler_label.setStyleSheet("background: transparent")
        self.label.setPixmap(QtGui.QPixmap(
            os.path.join(darkTheme, "dark_signin_logo.svg")))
        self.Working_days_label.setStyleSheet("background: transparent")
        self.Working_hours_label.setStyleSheet("background: transparent")
        self.result_label.setStyleSheet("background: transparent")
        self.update_header.setStyleSheet("background: transparent")
        self.label.setScaledContents(True)

        self.monday_checkbox.setStyleSheet("background-color: none;")
        self.Tuesday_checkbox.setStyleSheet("background-color: none;")
        self.Wednesday_checkBox.setStyleSheet("background-color: none;")
        self.Thursday_checkbox.setStyleSheet("background-color: none;")
        self.Friday_checkBox.setStyleSheet("background-color: none;")
        self.saturday_checkBox.setStyleSheet("background-color: none;")
        self.Sunday_checkBox.setStyleSheet("background-color: none;")

        self.monday_checkbox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.monday_checkbox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.Tuesday_checkbox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.Tuesday_checkbox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.Wednesday_checkBox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.Wednesday_checkBox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.Thursday_checkbox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.Thursday_checkbox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.Friday_checkBox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.Friday_checkBox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.saturday_checkBox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.saturday_checkBox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))
        self.Sunday_checkBox.setTickImage(os.path.join(darkTheme, 'checkedbox.svg'))
        self.Sunday_checkBox.setUncheckedImage(os.path.join(darkTheme, 'checkbox.svg'))

        self.monday_label.setStyleSheet("background-color: none;")
        self.Tuesday_label.setStyleSheet("background-color: none;")
        self.Wednesday_label.setStyleSheet("background-color: none;")
        self.Thursday_label.setStyleSheet("background-color: none;")
        self.Friday_label.setStyleSheet("background-color: none;")
        self.Saturday_label.setStyleSheet("background-color: none;")
        self.Sunday_label_2.setStyleSheet("background-color: none;")

        self.username_icon.setStyleSheet("background-color: none;")

        self.Activity_icon.setStyleSheet("background-color: none;")

        self.settings_logo.setStyleSheet("background-color: none;")


        # self.Version_icon.setStyleSheet("background-color: none;")

        self.theme_logo.setStyleSheet("background-color: none;")
        self.theme_label.setStyleSheet("background-color: none;color:#F8F8F8;")

        self.startup_toast_message.setStyleSheet(
            "border-radius: 10px; background-color:#BFF6C3;")
        self.theme_logo.setPixmap(QtGui.QPixmap(
            os.path.join(darkTheme, "dark_theme.svg")))
        self.theme_label.setText("Dark mode")
        self.theme.setStyleSheet("""
                                            QPushButton{
                                                border:none;
                                            }
                                            QLabel {
                                                background: transparent;
                                            }
                                            QPushButton:focus {
                                                outline: none;  /* Remove the focus outline */
                                            }
                                        """)
        timefields = f"""
                            QTimeEdit {{
                                border: 1px solid #313131;
                                background-color: #010101;
                                border-radius: 5px;
                                padding-left: 10px;
                                color: #FFFFFF;
                            }}

                            QTimeEdit::up-button {{
                                subcontrol-origin: border;
                                subcontrol-position: top right;
                                width: 20px;
                                border: none; /* Removed border */
                                border-top-right-radius: 5px;
                                background: url({uparrow}) no-repeat center;
                                padding-right: 10px
                            }}

                            QTimeEdit::down-button {{
                                subcontrol-origin: border;
                                subcontrol-position: bottom right;
                                width: 20px;
                                border: none; /* Removed border */
                                border-bottom-right-radius: 5px;
                                background: url({downarrow}) no-repeat center;
                                padding-right: 10px
                            }}
                        """
        self.To_time.setStyleSheet(timefields)
        self.From_time.setStyleSheet(timefields)
        self.errorMessageLabel.setStyleSheet("color: red;")
        self.companyErrorMessageLabel.setStyleSheet("color: red;")
        self.arrow_icon.setStyleSheet("background: transparent")
        self.homepage_subtitle.setStyleSheet("background-color: none;")
        self.homepage_Sundial_logo.setStyleSheet("background: transparent;")
        # self.widget_2.setStyleSheet("border-radius: 10px;")
        self.update_save_button_state()
        self.info_message.setStyleSheet("background-color: #2E2E2E; color: white; border-radius: 10px;")
        self.loader_gif.setStyleSheet("background:None;")
        self.loader_.setStyleSheet("background-color:rgba(0, 0, 0, 0.4);")
        self.loaders_gif.setStyleSheet("background:None;")
        self.loaders_.setStyleSheet("background-color:rgba(0, 0, 0, 0.4);")

        self.username_icon.setPixmap(QtGui.QPixmap(
            os.path.join(darkTheme, "dark_user_icon.svg")))
        self.Signout.setStyleSheet("""
            QPushButton {
                border: none;
                color: #474B4F;  /* Default text color */
                text-align: left;  /* Align text to the left */
                padding-left: 40px;  /* Add padding to accommodate the icon */
            }
            QPushButton:hover {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;  /* Text color on hover */
            }
        """)
        self.Signout_logo.setStyleSheet("background:none")
        self.Forgot_password_Label.setStyleSheet("""
                    QLabel {
                        color: #474B4F;
                    }
                    QLabel a {
                        color: #474B4F;
                    }
                """)
        self.profile_image.setFixedSize(100, 100)
        user_img = os.path.join(folder_path, "user_img.svg")
        self.profile_image.setStyleSheet(f"""
            border-radius: 50%;
            background-color: rgba(1, 1, 1, 1);  /* Transparent background */
            background-image: url({user_img}); /* Insert the path to the image */
            background-position: center; /* Center the image */
            background-repeat: no-repeat; /* Do not repeat the image */
        """)
        self.FirstName.setStyleSheet("color:rgba(248, 248, 248, 0.5)")
        self.company.setStyleSheet("color:rgba(248, 248, 248, 0.5)")
        self.mobile.setStyleSheet("color:rgba(248, 248, 248, 0.5)")
        # self.Company.setStyleSheet("color:rgba(248, 248, 248, 0.5)")
        self.Email.setStyleSheet("color:rgba(248, 248, 248, 0.5)")
        # self.check_updates_btn.setStyleSheet(
        #     """
        #     background-color: #171717 !important;
        #     color: rgba(106, 95, 162, 1);
        #     border: 1px solid rgba(106, 95, 162, 1);
        #     border-radius: 5px;
        #     """
        # )
        self.current_version.setText(
            f'<span style="color: rgba(248, 248, 248, 0.5);">Current app version: </span>'
            f'<span style="color: white;">{self.version}</span>'
        )
        self.info_icon.setIcon(QtGui.QPixmap(os.path.join(darkTheme, "info_icon.svg")))
        self.info_icon.setStyleSheet("background:none")
        self.info_cancel_button.setIcon(QtGui.QPixmap(os.path.join(folder_path, "Close_Icon.svg")))
        self.startup_checkbox.set_circle_color("#010101")
        self.idletime_checkbox.set_circle_color("#010101")
        self.Schedule_enabler_checkbox.set_circle_color("#010101")
        self.start_up_checkbox.set_circle_color("#010101")
        self.idle_time_checkbox.set_circle_color("#010101")
        palette = self.emailField.palette()
        palette.setColor(QPalette.PlaceholderText,
                         QColor(248, 248, 248))  # Set color to light gray with 50% opacity
        self.emailField.setPalette(palette)

        palette = self.passwordField.palette()
        palette.setColor(QPalette.PlaceholderText,
                         QColor(248, 248, 248))  # Set color to light gray with 50% opacity
        self.passwordField.setPalette(palette)


    def apply_light_theme(self):
        # Set general stylesheet for the window
        self.setStyleSheet("""
            background-color: rgb(255, 255, 255); /* Background color of the window */
            color: black; /* Text color of the window */
        """)
        # Apply styles to all child widgets (only general widget styles, no tooltip)
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet("""
                QToolTip {
                    color: #5e5e5d;               /* Tooltip text color */
                    background-color: #ffffff;      /* Tooltip background color */
                    padding: 5px;
                    border-radius: 3px;
                }
                * {
                    background-color: rgb(255, 255, 255); /* Background color */ 
                    color: black
                }
            """)
        background_image = os.path.join(lightTheme, "BackgroundImage.svg")
        self.monday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px;}")
        # Load the background image
        background_pixmap = QPixmap(background_image)
        self.background.setPixmap(background_pixmap)
        # Make the pixmap scale with the label
        self.background.setScaledContents(True)

        # loading page logo
        SundialLogo = os.path.join(lightTheme, "SundialLogo.svg")
        pixmap = QPixmap(SundialLogo)  # Load the background image
        self.Sundial_logo.setPixmap(pixmap)
        self.Sundial_logo.setStyleSheet("background: transparent;")

        # sign in background
        self.homepage_background.setPixmap(background_pixmap)
        self.homepage_background.setScaledContents(True)

        # signin_page Logo
        homepage_SundialLogo = os.path.join(lightTheme, "description_logo.svg")
        homepage_pixmap = QPixmap(homepage_SundialLogo)
        self.homepage_Sundial_logo.setPixmap(homepage_pixmap)
        self.homepage_Sundial_logo.setStyleSheet("""QPushButton {
                   background: transparent;
                   }
                   """)

        # signinpage_subtitle
        homepage_subtitle = os.path.join(lightTheme, "signin_subtitle.svg")
        homepage_subtitle_pixmap = QPixmap(homepage_subtitle)
        self.homepage_subtitle.setPixmap(homepage_subtitle_pixmap)
        self.description.setStyleSheet("background-color: none;")
        # Updated for dark mode
        self.signIn_button.setStyleSheet("""
                               QPushButton#signInButton {
                                   border: none;
                                   background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                   color: #ffffff;
                                   border-radius: 10px;
                                   padding: 10px;
                                   font-size: 16px;
                               }
                           """)

        # ------------------------------SignIn--------------------------#
        # signin background
        self.sign_in_background.setPixmap(background_pixmap)
        self.sign_in_background.setScaledContents(True)

        # signin Logo
        sign_in_SundialLogo = os.path.join(lightTheme, "signin_logo.svg")
        sign_in_pixmap = QPixmap(sign_in_SundialLogo)
        self.sign_in_Sundial_logo.setPixmap(sign_in_pixmap)
        self.sign_in_Sundial_logo.setStyleSheet("background: transparent;")

        # sigin background
        self.signin_widget.setStyleSheet(
            "background-color: #FFFFFF; border-radius: 10px; opacity: 1;"
        )
        self.signin_widget.setWindowOpacity(1.0)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))

        self.signin_widget.setGraphicsEffect(shadow_effect)

        # Welcome Message
        self.welcomeMessage.setStyleSheet(
            "color: #474B4F;background: transparent;")

        # signup label
        self.newUserLabel.setStyleSheet(
            "color: #242424;background: transparent;")
        self.signupLabel.setStyleSheet(
            "color: #1D0B77;background: transparent;")

        self.emailField.setStyleSheet("""
                                       QLineEdit {
                                           background: #FFFFFF;
                                           border: 1px solid #DDDDDD;
                                           border-radius: 10px;
                                           padding: 10px;
                                           opacity: 1;
                                       }
                                       QLineEdit::placeholder {
                                           color: #474B4F;
                                           font-size: 14px;
                                       }
                                       QLineEdit:focus {
                                           border: 1px solid #007BFF;
                                           background: #FFFFFF;
                                       }
                                   """)
        self.showPassButton.setStyleSheet("background: transparent; border: none;")
        self.passwordField.setStyleSheet("""
                                       QLineEdit {
                                           background: #FFFFFF;
                                           border: 1px solid #DDDDDD;
                                           border-radius: 10px;
                                           padding: 10px;
                                           opacity: 1;
                                           padding-right: 60px;
                                       }
                                       QLineEdit::placeholder {
                                           color: #474B4F;
                                           font-size: 14px;
                                       }
                                       QLineEdit:focus {
                                           border: 1px solid #007BFF;
                                           background: #FFFFFF;
                                       }
                                       QLineEdit:disabled {
                                           background: #E0E0E0;
                                           border: 1px solid #B0B0B0;
                                       }
                                   """)
        self.sign_In_button.setStyleSheet("""
                                                       QPushButton#sign_In_button {
                                                           border: none;
                                                           background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                                           color: #ffffff;
                                                           border-radius: 10px;
                                                           padding: 10px;
                                                           font-size: 16px;
                                                       }

                                                   """)
        self.Forgot_password_Label.setStyleSheet(
            "background: transparent;color:#242424;text-decoration: none;")

        self.company_background.setPixmap(background_pixmap)
        self.company_background.setScaledContents(True)

        # signin Logo
        company_SundialLogo = os.path.join(lightTheme, "signin_logo.svg")
        company_pixmap = QPixmap(sign_in_SundialLogo)
        resized_company_in_pixmap = sign_in_pixmap.scaled(181, 64)
        self.company_Sundial_logo.setPixmap(company_pixmap)
        self.company_Sundial_logo.setStyleSheet("background: transparent;")

        self.company_widget.setStyleSheet(
            "background-color: #FFFFFF; border-radius: 10px; opacity: 1;"
        )
        self.signin_widget.setWindowOpacity(1.0)
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))

        self.company_widget.setGraphicsEffect(shadow_effect)

        self.CompanyMessage.setStyleSheet(
            "color: #474B4F;background: transparent;")
        self.companySelect.setStyleSheet(f"""
                                   QComboBox {{
                                       background: #FFFFFF; /* Background color */
                                       border: 1px solid #DDDDDD; /* Border color */
                                       border-radius: 10px; /* Rounded corners */
                                       color: black; /* Text color */
                                       font-size: 16px; /* Font size */
                                       padding-right: 20px;
                                       padding-left: 10px;
                                   }}
                                   QComboBox::drop-down {{
                                       border: none; /* Remove border */
                                       subcontrol-origin: padding; /* Position the arrow */
                                       subcontrol-position: center Right; /* Position the arrow */
                                       margin-right: 10px;

                                   }}
                                   QComboBox::down-arrow {{
                                       image: url({light_downarrow}); /* Use the variable for the arrow image */
                                       width: 16px; /* Width of the arrow */
                                       height: 16px; /* Height of the arrow */
                                       margin:10px;
                                       margin-right:30px;
                                   }}
                               """)
        self.company_select_button.setStyleSheet("""
                                                       QPushButton {
                                                           border: none;
                                                           background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1D0B77, stop:1 #6A5FA2);
                                                           color: #ffffff;
                                                           border-radius: 10px;
                                                           padding: 10px;
                                                           font-size: 16px;
                                                       }
                                                   """)

        self.startup.setStyleSheet(
            "border-radius: 10px; background-color:#F9F9F9;")
        self.idletime.setStyleSheet(
            "border-radius: 10px; background-color:#F9F9F9;")
        self.Schedule_enabler.setStyleSheet(f"""
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px; background-color:#F9F9F9;""")
        self.day_widget.setStyleSheet(f"""QWidget {{
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;  background-color: #F9F9F9;
                }}
            """)
        self.Version_2.setStyleSheet(
            "border-radius: 10px; background-color:#F9F9F9;")
        self.profile_container.setStyleSheet(
            "border-radius: 10px; background-color:#F9F9F9;")

        self.scrollAreaWidgetContents.setStyleSheet(
            "border:None;background-color:#F9F9F9;")
        self.scrollArea.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: #F9F9F9;
                width: 5px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #B0B0B0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                width: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.Date_display.setStyleSheet("""
                    background-color: #EFEFEF;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                """)
        self.scrollArea.setStyleSheet(
            "border:None; background-color:#F9F9F9;border-bottom-left-radius: 10px;border-bottom-right-radius: 10px;")
        self.Day.setStyleSheet("background: transparent")
        self.Date.setStyleSheet("background: transparent")
        self.Schedule_enabler_label.setStyleSheet("background: transparent")
        self.startup_label.setStyleSheet("background: transparent")
        self.idletime_label.setStyleSheet("background: transparent")
        self.label.setPixmap(QtGui.QPixmap(
            os.path.join(lightTheme, "Sundial_homepage.svg")))
        self.label.setScaledContents(1)
        self.Working_days_label.setStyleSheet("background: transparent")
        self.Working_hours_label.setStyleSheet("background: transparent")
        self.result_label.setStyleSheet("background: transparent")
        self.update_header.setStyleSheet("background: transparent")
        self.arrow_icon.setStyleSheet("background: transparent")

        self.monday_checkbox.setStyleSheet("background-color: none;")
        self.Tuesday_checkbox.setStyleSheet("background-color: none;")
        self.Wednesday_checkBox.setStyleSheet("background-color: none;")
        self.Thursday_checkbox.setStyleSheet("background-color: none;")
        self.Friday_checkBox.setStyleSheet("background-color: none;")
        self.saturday_checkBox.setStyleSheet("background-color: none;")
        self.Sunday_checkBox.setStyleSheet("background-color: none;")

        self.monday_checkbox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.monday_checkbox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.Tuesday_checkbox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.Tuesday_checkbox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.Wednesday_checkBox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.Wednesday_checkBox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.Thursday_checkbox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.Thursday_checkbox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.Friday_checkBox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.Friday_checkBox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.saturday_checkBox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.saturday_checkBox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))
        self.Sunday_checkBox.setTickImage(os.path.join(lightTheme, 'checkedbox.svg'))
        self.Sunday_checkBox.setUncheckedImage(os.path.join(lightTheme, 'checkbox.svg'))

        self.monday_label.setStyleSheet("background-color: none;")
        self.Tuesday_label.setStyleSheet("background-color: none;")
        self.Wednesday_label.setStyleSheet("background-color: none;")
        self.Thursday_label.setStyleSheet("background-color: none;")
        self.Friday_label.setStyleSheet("background-color: none;")
        self.Saturday_label.setStyleSheet("background-color: none;")
        self.Sunday_label_2.setStyleSheet("background-color: none;")

        self.username_icon.setStyleSheet("background-color: none;")

        self.Activity_icon.setStyleSheet("background-color: none;")
        self.settings_logo.setStyleSheet("background-color: none;")
        self.schedule_logo.setStyleSheet("background-color: none;")
        # self.Version_icon.setStyleSheet("background-color: none;")
        self.theme.setStyleSheet("""
                                    QPushButton{
                                        border:none;
                                    }
                                    QLabel {
                                        background: transparent;
                                    }
                                """)
        self.theme_logo.setPixmap(QtGui.QPixmap(
            os.path.join(lightTheme, "light_theme.svg")))
        self.theme_label.setText("Light mode")
        self.signin_message.setStyleSheet(
            "border-radius: 10px;\nbackground-color:#BFF6C3;")
        self.To_time.setStyleSheet(f"""
                                    QTimeEdit {{
                                        border: 1px solid #DDDDDD;
                                        background-color: white;
                                        border-radius: 5px;
                                        padding-left: 10px
                                    }}

                                    QTimeEdit::up-button {{
                                        subcontrol-origin: border;
                                        subcontrol-position: top right;
                                        width: 20px;
                                        border: none; /* Removed border */
                                        border-top-right-radius: 5px;
                                        background: url({light_uparrow}) no-repeat center;
                                        padding-right: 10px
                                    }}

                                    QTimeEdit::down-button {{
                                        subcontrol-origin: border;
                                        subcontrol-position: bottom right;
                                        width: 20px;
                                        border: none; /* Removed border */
                                        border-bottom-right-radius: 5px;
                                        background: url({light_downarrow}) no-repeat center;
                                        padding-right: 10px
                                    }}
                                """)
        self.From_time.setStyleSheet(f"""
                                    QTimeEdit {{
                                        border: 1px solid #DDDDDD;
                                        background-color: white;
                                        border-radius: 5px;
                                        padding-left: 10px
                                    }}

                                    QTimeEdit::up-button {{
                                        subcontrol-origin: border;
                                        subcontrol-position: top right;
                                        width: 20px;
                                        border: none; /* Removed border */
                                        border-top-right-radius: 5px;
                                        background: url({light_uparrow}) no-repeat center;
                                        padding-right: 10px
                                    }}

                                    QTimeEdit::down-button {{
                                        subcontrol-origin: border;
                                        subcontrol-position: bottom right;
                                        width: 20px;
                                        border: none; /* Removed border */
                                        border-bottom-right-radius: 5px;
                                        background: url({light_downarrow}) no-repeat center;
                                        padding-right: 10px
                                    }}
                                """)
        self.errorMessageLabel.setStyleSheet("color: red;")
        self.companyErrorMessageLabel.setStyleSheet("color: red;")
        self.homepage_subtitle.setStyleSheet("background-color: none;")
        self.homepage_Sundial_logo.setStyleSheet("background: transparent;")
        # self.widget_2.setStyleSheet("border-radius: 10px;")
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)  # Adjust the blur radius
        shadow_effect.setOffset(5, 5)    # Adjust the offset (x, y)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 160))
        # self.widget_2.setGraphicsEffect(shadow_effect)
        self.info_icon.setIcon(QtGui.QPixmap(os.path.join(lightTheme, "info.svg")))
        self.info_cancel_button.setIcon(QtGui.QPixmap(os.path.join(lightTheme,"Close_icon.svg")))
        self.info_icon.setStyleSheet("background:none")
        self.info_message.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.loader_gif.setStyleSheet("background:None;")
        self.loader_.setStyleSheet("background-color:rgba(0, 0, 0, 0.4);")
        self.loaders_gif.setStyleSheet("background:None;")
        self.loaders_.setStyleSheet("background-color:rgba(0, 0, 0, 0.4);")

        self.username_icon.setPixmap(QtGui.QPixmap(
            os.path.join(lightTheme, "light_user_icon.svg")))
        self.Signout.setStyleSheet("""
            QPushButton {
                border: none;
                color: #474B4F;  /* Default text color */
                text-align: left;  /* Align text to the left */
                padding-left: 40px;  /* Add padding to accommodate the icon */
            }
            QPushButton:hover {
                background: qlineargradient(
                    spread:pad, x1:1, y1:0, x2:0, y2:0,
                    stop:0 rgba(217, 83, 79, 0.05),
                    stop:1 rgba(217, 83, 79, 0.5)
                );
                color: #FE5050;  /* Text color on hover */
            }
        """)
        self.Signout_logo.setStyleSheet("background:none")
        self.Forgot_password_Label.setStyleSheet("""
            QLabel {
                color: #474B4F;
            }
            QLabel a {
                color: #474B4F;
            }
        """)
        self.update_save_button_state()
        # self.version_label.setStyleSheet(
        #     "background:none;rgba(248, 248, 248, 0.8)")
        self.GeneralSettings_header.setStyleSheet(
            "background-color:none;rgba(248, 248, 248, 0.8)")
        self.Activites_header.setStyleSheet(
            "background-color:none;rgba(248, 248, 248, 0.8)")
        self.Schedule_label.setStyleSheet(
            "background-color:none;rgba(248, 248, 248, 0.8)")
        self.FirstName.setStyleSheet("color:rgba(71, 75, 79, 0.5)")
        self.company.setStyleSheet("color:rgba(71, 75, 79, 0.5)")
        self.profile_image.setStyleSheet("""
            border-radius: 50%;
            background-color: rgba(1, 1, 1, 1);
        """)

        self.mobile.setStyleSheet("color:rgba(71, 75, 79, 0.5)")
        self.Email.setStyleSheet("color:rgba(71, 75, 79, 0.5)")
        # self.check_updates_btn.setStyleSheet(
        #     """
        #     background-color: #171717 !important;
        #     color: rgba(106, 95, 162, 1);
        #     border: 1px solid rgba(106, 95, 162, 1);
        #     border-radius: 5px;
        #     """
        # )
        self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join(lightTheme, "darkSundialLogo.svg")))
        self.background.setPixmap(QPixmap(os.path.join(lightTheme, "BackgroundImage.svg")))
        self.privacy_background.setPixmap(QPixmap(os.path.join(lightTheme, "BackgroundImage.svg")))
        self.datasecurity_background.setPixmap(QPixmap(os.path.join(lightTheme, "BackgroundImage.svg")))
        self.settings_background.setPixmap(QPixmap(os.path.join(lightTheme, "BackgroundImage.svg")))
        self.accessibility_background.setPixmap(QPixmap(os.path.join(lightTheme, "BackgroundImage.svg")))

        self.privacy_img.setPixmap(QPixmap(os.path.join(lightTheme, "privacy.png")))
        self.datasecurity_img.setPixmap(QPixmap(os.path.join(lightTheme, "Dataprivacy_light.svg")))
        self.datasecurity_sundial_logo.setPixmap(QPixmap(os.path.join(lightTheme, "signin_logo.svg")))
        self.privacy_sundial_logo.setPixmap(QPixmap(os.path.join(lightTheme, "signin_logo.svg")))
        self.settings_sundial_logo.setPixmap(QPixmap(os.path.join(lightTheme, "signin_logo.svg")))
        self.accessibility_sundial_logo.setPixmap(QPixmap(os.path.join(lightTheme, "signin_logo.svg")))
        self.accessibility_img.setPixmap(QPixmap(
            os.path.join(lightTheme, "accessibility_Images.png")))

        # Set styles for containers
        container_style = """
                        background-color: rgba(252, 252, 252, 0.8);  /* 80% opacity */
                        border-radius: 5px;
                    """

        self.idle_time.setStyleSheet(container_style)
        self.start_up.setStyleSheet(container_style)

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

        self.privacy_next_btn.setStyleSheet(gradient_style)
        self.next_btn.setStyleSheet(gradient_style)
        self.back_btn.setStyleSheet(solid_button_style)
        self.accessibility_back_btn.setStyleSheet(solid_button_style)
        self.accessibility_next_btn.setStyleSheet(gradient_style)
        self.settings_back_btn.setStyleSheet(solid_button_style)
        self.settings_next_btn.setStyleSheet(gradient_style)

        # Ensure transparent backgrounds for necessary elements
        transparent_style = "background: none;"

        self.settings_sundial_logo.setStyleSheet(transparent_style)
        self.privacy_header.setStyleSheet(transparent_style)
        self.privacy_info.setStyleSheet(transparent_style)
        self.privacy_info_2.setStyleSheet(transparent_style)
        self.privacy_img.setStyleSheet(transparent_style)
        self.privacy_sundial_logo.setStyleSheet(transparent_style)
        self.datasecurity_img.setStyleSheet(transparent_style)
        self.datasecurity_sundial_logo.setStyleSheet(transparent_style)
        self.datasecurity_info.setStyleSheet(transparent_style)
        self.datasecurity_header.setStyleSheet(transparent_style)
        self.accessibility_img.setStyleSheet(transparent_style)
        self.accessibility_header.setStyleSheet(transparent_style)
        self.accessibility_sundial_logo.setStyleSheet(transparent_style)
        self.accessibility_info.setStyleSheet(transparent_style)
        self.settings_header.setStyleSheet(transparent_style)
        self.idle_time_info.setStyleSheet(transparent_style)
        self.start_up_info.setStyleSheet(transparent_style)
        self.idle_time_label.setStyleSheet(transparent_style)
        self.start_up_label.setStyleSheet(transparent_style)

        self.profile_image.setFixedSize(100, 100)
        user_img = os.path.join(folder_path, "user_img.svg")
        self.profile_image.setStyleSheet(f"""
                                border-radius: 50%;
                                background-color: rgba(255, 255, 255, 1);  /* Transparent background */
                                background-image: url({user_img}); /* Insert the path to the image */
                                background-position: center; /* Center the image */
                                background-repeat: no-repeat; /* Do not repeat the image */
                            """)
        self.mobile_value.setStyleSheet(transparent_style)
        self.first_name_value.setStyleSheet(transparent_style)
        self.email_value.setStyleSheet(transparent_style)
        self.company_value.setStyleSheet(transparent_style)
        self.update_description.setStyleSheet(transparent_style)
        self.current_version.setStyleSheet(transparent_style)
        self.current_version.setText(
            f'<span style="color: rgba(71, 75, 79, 1);">Current app version: </span>'
            f'<span style="color: black;background:transparent;">{self.version}</span>'
        )
        self.startup_checkbox.set_circle_color("#FFFFFF")
        self.idletime_checkbox.set_circle_color("#FFFFFF")
        self.Schedule_enabler_checkbox.set_circle_color("#FFFFFF")
        self.start_up_checkbox.set_circle_color("#FFFFFF")
        self.idle_time_checkbox.set_circle_color("#FFFFFF")
        palette = self.emailField.palette()
        palette.setColor(QPalette.PlaceholderText,
                         QColor(71, 75, 79))  # Set color to dark gray with 50% opacity
        self.emailField.setPalette(palette)

        palette = self.passwordField.palette()
        palette.setColor(QPalette.PlaceholderText,
                         QColor(71, 75, 79))  # Set color to dark gray with 50% opacity
        self.passwordField.setPalette(palette)

    def setupSystemTray(self):
        scriptdir = Path(__file__).parent.parent

        # Set icon search paths
        QtCore.QDir.addSearchPath("icons", str(scriptdir.parent / "media/logo/"))
        QtCore.QDir.addSearchPath("icons", str(scriptdir.parent.parent / "Resources/sd_qt/media/logo/"))

        # Set the tray icon based on the platform (macOS uses a different icon)
        if sys.platform == "darwin":
            icon = QtGui.QIcon("icons:black-monochrome-logo.png")
        else:
            icon = QtGui.QIcon("icons:logo.png")

        # Create the system tray icon
        self.tray_icon = QtWidgets.QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Sundial Application")

        # Create a menu for the tray icon
        tray_menu = QtWidgets.QMenu()

        # "Open" action to show the window
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.show_window)
        tray_menu.addAction(open_action)

        # "Quit" action to quit the application
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        # Set the context menu for the tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Show the tray icon
        self.tray_icon.show()

        # Connect the tray icon activation to a function
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def update_dock_icon_policy(self):
        """Update the dock icon based on the current window state (macOS specific)."""
        if sys.platform == "darwin":
            app = NSApplication.sharedApplication()
            if not self.isVisible():
                # Hide from dock only if the window is hidden
                app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            else:
                # Always show in dock if the window is visible or minimized
                app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

    def showEvent(self, event):
        """Ensure dock icon updates when the window is shown (macOS specific)."""
        super().showEvent(event)
        if sys.platform == "darwin":
            self.update_dock_icon_policy()

    def hideEvent(self, event):
        """Ensure dock icon updates when the window is hidden (macOS specific)."""
        super().hideEvent(event)
        if sys.platform == "darwin":
            self.update_dock_icon_policy()

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing."""
        event.ignore()  # Ignore the close event to prevent application from closing
        self.hide()  # Hide the window to the tray instead
        self.tray_icon.showMessage(
            "Tray Application",
            "Application minimized to tray. Click the tray icon to restore.",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )
        if sys.platform == "darwin":
            self.update_dock_icon_policy()  # Update the dock icon visibility

    def show_window(self):
        """Show the window when the 'Open' option in tray is clicked."""
        self.show()  # Show the window
        self.raise_()  # Bring the window to the front
        self.activateWindow()  # Activate the window to give it focus
        if sys.platform == "darwin":
            self.update_dock_icon_policy()
        self.showNormal()  # Restore the window from minimized state if minimized

    def quit_application(self):
        """Quit the application gracefully."""
        from sd_core.util import stop_server  # Import the stop_server function
        stop_server()
        QtWidgets.QApplication.quit()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show_window()  # Show the window when the tray icon is clicked

    def changeEvent(self, event):
        """Handle window state changes to adjust the look and feel."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isActiveWindow():
                # Set active window style (example)
                self.setStyleSheet("background-color: white;")
            else:
                # Set inactive window style (example)
                self.setStyleSheet("background-color: lightgray;")
        super(MainWindow, self).changeEvent(event)


    def check_updates(self):
        creds = credentials()
        sundial_token = ""
        if creds:
            sundial_token = creds["token"] if creds['token'] else None
        try:
            response = requests.get("http://10.10.10.142:9010/api/v1/sundial_version_control", headers={"Authorization": sundial_token})
            print(response.json())
            data = response.json().get('data')
            updated_version = data.get('sundialPackages')[0].get('version')
            return updated_version
        except:
           print("error")

    def new_version(self):
        # Retrieve settings and check for updates
        settings = retrieve_settings()
        version = settings.get("version")
        updated_version = self.check_updates()

        if not hasattr(self, 'is_dark_mode'):
            self.is_dark_mode = self.detect_system_theme()

        # Proceed only if there is an update
        if version and updated_version and version != updated_version and updated_version != "error":

            if hasattr(self, 'Version_2') and self.Version_2 is not None:
                self.Version_2.deleteLater()
                self.Version_2 = None

            self.Version_2 = QWidget(parent=self.GeneralSettings)
            self.Version_2.setGeometry(QtCore.QRect(10, 250, 550, 150))

            if self.is_dark_mode:
                self.Version_2.setStyleSheet("border-radius: 10px; background-color:#171717;")
            else:
                self.Version_2.setStyleSheet("border-radius: 10px; background-color:#F9F9F9;")

            # Set up the palette for current version label
            self.current_version = QLabel(parent=self.Version_2)
            self.current_version.setGeometry(QtCore.QRect(20, 80, 311, 16))

            palette = self.current_version.palette()

            if self.is_dark_mode:
                palette.setColor(self.current_version.foregroundRole(), QtGui.QColor(248, 248, 248))
            else:
                palette.setColor(self.current_version.foregroundRole(), QtGui.QColor(0, 0, 0))

            self.current_version.setPalette(palette)
            self.current_version.setText(f"Current app version: {self.version()}")

            # Updated version label
            self.Updated_version = QLabel(parent=self.Version_2)
            self.Updated_version.setGeometry(QtCore.QRect(20, 110, 311, 16))
            self.Updated_version.setPalette(palette)
            self.Updated_version.setText(f"New app version: {updated_version}")

            # Update button
            self.update_btn = QPushButton(parent=self.Version_2)
            self.update_btn.setGeometry(QtCore.QRect(420, 50, 100, 40))
            self.update_btn.setText("Update Now")
            # Uncomment the following line to connect the button to an actual update method
            # self.update_btn.clicked.connect(self.perform_update)
            self.update_btn.setStyleSheet(
                "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D0B77, stop:1 #6A5FA2);"
                "border-radius: 5px; color: #FFFFFF; border: 1px solid #1D0B77;"
            )

            # Show the update widget
            self.Version_2.show()
            self.Version_2.repaint()  # Force UI refresh

    def schedulecheckboxes(self):

        font = QtGui.QFont()
        if sys.platform == "darwin":
            font.setPointSize(12)
        else:
            font.setPointSize(10)

        self.Sunday_checkBox = QCheckBox(parent=self.weekday_container)
        self.Sunday_checkBox.setGeometry(QtCore.QRect(20, 53, 30, 30))
        self.Sunday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Sunday_label_2 = QLabel(parent=self.weekday_container)
        self.Sunday_label_2.setGeometry(QtCore.QRect(44, 52, 45, 30))
        self.Sunday_label_2.setFont(font)

        self.monday_checkbox = QCheckBox(parent=self.weekday_container)
        self.monday_checkbox.setGeometry(QtCore.QRect(129, 53, 30, 30))
        self.monday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px;}")

        self.monday_label = QLabel(parent=self.weekday_container)
        self.monday_label.setGeometry(QtCore.QRect(153, 52, 50, 30))

        self.monday_label.setFont(font)

        self.Tuesday_checkbox = QCheckBox(parent=self.weekday_container)
        self.Tuesday_checkbox.setGeometry(QtCore.QRect(228, 53, 45, 30))
        self.Tuesday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Tuesday_label = QLabel(parent=self.weekday_container)
        self.Tuesday_label.setGeometry(QtCore.QRect(252, 52, 50, 30))
        self.Tuesday_label.setFont(font)

        self.Wednesday_checkBox = QCheckBox(parent=self.weekday_container)
        self.Wednesday_checkBox.setGeometry(QtCore.QRect(317, 53, 50, 30))
        self.Wednesday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Wednesday_label = QLabel(parent=self.weekday_container)
        self.Wednesday_label.setGeometry(QtCore.QRect(341, 52, 70, 30))
        self.Wednesday_label.setFont(font)

        self.Thursday_checkbox = QCheckBox(parent=self.weekday_container)
        self.Thursday_checkbox.setGeometry(QtCore.QRect(431, 53, 40, 30))
        self.Thursday_checkbox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Thursday_label = QLabel(parent=self.weekday_container)
        self.Thursday_label.setGeometry(QtCore.QRect(455, 52, 55, 30))
        self.Thursday_label.setFont(font)

        self.Friday_checkBox = QCheckBox(parent=self.weekday_container)
        self.Friday_checkBox.setGeometry(QtCore.QRect(530, 53, 40, 30))
        self.Friday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Friday_label = QLabel(parent=self.weekday_container)
        self.Friday_label.setGeometry(QtCore.QRect(554, 52, 40, 30))
        self.Friday_label.setFont(font)

        self.saturday_checkBox = QCheckBox(parent=self.weekday_container)
        self.saturday_checkBox.setGeometry(QtCore.QRect(614, 53, 40, 30))
        self.saturday_checkBox.setStyleSheet(
            ".QCheckBox::indicator { width: 40px; height: 40px; }")

        self.Saturday_label = QLabel(parent=self.weekday_container)
        self.Saturday_label.setGeometry(QtCore.QRect(638, 52, 60, 30))
        self.Saturday_label.setFont(font)

        self.monday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Tuesday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Wednesday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.Thursday_checkbox.stateChanged.connect(
            self.update_save_button_state)
        self.Friday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.saturday_checkBox.stateChanged.connect(
            self.update_save_button_state)
        self.Sunday_checkBox.stateChanged.connect(
            self.update_save_button_state)

        self.Schedule_label.setText(
            "Record data only during my scheduled work hours.")
        self.Working_days_label.setText("Working days")

        self.monday_label.setText("Monday")
        self.Wednesday_label.setText("Wednesday")
        self.Tuesday_label.setText("Tuesday")
        self.Saturday_label.setText("Saturday")
        self.Thursday_label.setText("Thursday")
        self.Friday_label.setText("Friday")
        self.Sunday_label_2.setText("Sunday")

def credentials():
    cache_service = "Sundial"
    global cached_credentials
    if not cached_credentials:
        creds = cache_user_credentials("SD_KEYS")
        return creds
    else:
        return cached_credentials


def user_details():
    cached_credentials = credentials()
    userdetails['firstname'] = cached_credentials['firstname']
    userdetails['phone'] = cached_credentials['phone']
    userdetails['email'] = cached_credentials['email']
    userdetails['companyName'] = cached_credentials['companyName']


def retrieve_settings():
    global settings
    creds = credentials()
    sundail_token = ""
    if creds:
        sundail_token = creds["token"] if creds['token'] else None
    try:
        sett = requests.get("http://localhost:7600/api/0/getallsettings",
                            headers={"Authorization": sundail_token})
        settings = sett.json()
        print(settings)
    except:
        settings = {}
    return settings


def add_settings(key, value):
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = json.dumps({"code": key, "value": value})
    requests.post(host + "/0/settings", data=data, headers=headers)
    retrieve_settings()


def listView(events):
    list_view_events = []
    local_tz = datetime.now().astimezone().tzinfo

    for event in events:
        start_time_utc = datetime.strptime(
            event['start'], "%Y-%m-%dT%H:%M:%SZ")
        end_time_utc = datetime.strptime(event['end'], "%Y-%m-%dT%H:%M:%SZ")

        start_time_local = start_time_utc.replace(
            tzinfo=pytz.utc).astimezone(local_tz).strftime("%H:%M")
        end_time_local = end_time_utc.replace(
            tzinfo=pytz.utc).astimezone(local_tz).strftime("%H:%M")

        formatted_event = {
            'time': f"{start_time_local} - {end_time_local}", 'app': event['title']}
        list_view_events.append(formatted_event)
    return list_view_events


def get_next_color():
    global current_color_index

    light_colors = [
        "#F5E9DA",
        "#E8C6E6",
        "#CDC8EF",
        "#C0D8EC",
        "#C8E0FF",
        "#E2F0D6"
    ]

    dark_colors = [
        "#443C32",
        "#271726",
        "#29263B",
        "#0E1E2B",
        "#111D2C",
        "#20261B",
        "#24263A"
    ]

    colors = {
        "light_color": light_colors[current_color_index % len(light_colors)],
        "dark_color": dark_colors[current_color_index % len(dark_colors)]
    }

    current_color_index += 1
    current_color_index %= len(light_colors)

    return colors


def run_application():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.app_authentication()
    sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    window.app_authentication()
    sys.exit(app.exec())
