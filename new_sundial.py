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

# from .checkBox import CustomCheckBox
# from .toggleSwitch import SwitchControl
from deepdiff import DeepDiff
from qt_material import apply_stylesheet
from sd_core.cache import cache_user_credentials, get_credentials, add_password, clear_credentials
from sd_core.launch_start import launch_app, delete_launch_app, set_autostart_registry
from sd_qt.sd_desktop.dashboard import Dashboard
from sd_qt.sd_desktop.onboarding import Onboarding

# Determine development mode
development = "1"  # or "1" for development
cached_credentials = None
current_file_path = os.path.abspath(__file__)
host = "http://localhost:7600/api"
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


# Determine file path
base_file_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))) if development == "1" else os.path.dirname(current_file_path)
file_path = os.path.join(base_file_path, "sd_qt", "sd_desktop") if sys.platform == "darwin" and development == "1" else base_file_path

# Define folder paths
if sys.platform == "darwin":
    folder_path = os.path.join(file_path, "resources") if development == "0" else os.path.join(file_path, "resources")
elif sys.platform == "win32":
    folder_path = os.path.join(file_path, "resources").replace("\\", "/")

# Define common theme paths
darkTheme = os.path.join(folder_path, 'DarkTheme').replace("\\", "/")
lightTheme = os.path.join(folder_path, 'LightTheme').replace("\\", "/")

# Define icons for both themes
uparrow = os.path.join(folder_path, "uparrow.png").replace("\\", "/")
downarrow = os.path.join(folder_path, "downarrow.png").replace("\\", "/")
dark_downarrow = os.path.join(darkTheme, "dark_downarrow.svg").replace("\\", "/")
light_downarrow = os.path.join(lightTheme, "light_downarrow.png").replace("\\", "/")
light_uparrow = os.path.join(lightTheme, "light_uparrow.png").replace("\\", "/")

# Define light and dark orange theme options for qt-material

def setup_font( font_size: int) -> QtGui.QFont:
    font = QtGui.QFont()
    # Use setPointSizeF for better scaling on high-DPI screens
    scaled_font_size = get_scaled_font_size(font_size)
    font.setPointSizeF(scaled_font_size)
    return font


def get_scaled_font_size(base_size: int) -> float:
    screen = QApplication.primaryScreen()

    # Use logicalDotsPerInch for better cross-platform DPI scaling
    dpi = screen.logicalDotsPerInch()
    scale_factor = screen.devicePixelRatio()

    if sys.platform == "darwin":
        # macOS scaling, assume standard DPI of 72
        return base_size * (dpi / 72) * scale_factor
    else:
        # Windows/Linux scaling, assume standard DPI of 96
        return base_size * (dpi / 96) * scale_factor

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


def credentials():
    cache_service = "Sundial"
    global cached_credentials
    if not cached_credentials:
        creds = cache_user_credentials("SD_KEYS")
        return creds
    else:
        return cached_credentials


class MainWindow(QMainWindow):
    loginSuccess = Signal(dict)
    loginFailed = Signal(str)
    showLoaderSignal = Signal(bool)
    showLoadersSignal = Signal(bool)
    goToCompanyPageSignal = Signal()


    def __init__(self):
        super().__init__()
        self.companies = []
        self.companyname = None
        self.companyid = None
        self.selected_company = None
        self.onboarding_status = QSettings("ralvie.ai", "Sundial")
        self.settings = retrieve_settings()
        self.setupUi(self)
        self.current_theme = "light"
        self.loginSuccess.connect(self.process_login_response)
        self.goToCompanyPageSignal.connect(self.go_to_company_page)
        # Connect system palette change signal to theme change handler
        app.paletteChanged.connect(self.handle_palette_change)

    def load_custom_font(self):
        # Load the custom font from the specified path
        font_id = QtGui.QFontDatabase.addApplicationFont(
            os.path.join(folder_path, "fonts", "Poppins-light.ttf"))

        # Check if the font was loaded successfully
        if font_id != -1:
            font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)

            # If there are font families, set the custom font as the application's default font
            if font_families:
                custom_font = QtGui.QFont(font_families[0])
                QApplication.setFont(custom_font)
            else:
                print("No font families found for the loaded font.")
        else:
            print("Failed to load custom font.")

    def apply_light_theme(self):
        """Apply the default light theme using qt-material."""
        apply_stylesheet(self, theme='light_cyan_500.xml')

    def apply_dark_theme(self):
        """Apply the default dark theme using qt-material."""
        apply_stylesheet(self, theme='dark_teal.xml')

    def setupUi(self, Widget):
        # Set window size and title
        Widget.resize(800, 600)
        Widget.setMinimumSize(QtCore.QSize(800, 600))
        Widget.setMaximumSize(QtCore.QSize(800, 600))
        Widget.setWindowTitle("Sundial")
        self.current_theme = "light"
        # Apply the light theme initially
        self.apply_light_theme()

        # Uncomment and check the path if you want to set an icon
        # Widget.setWindowIcon(QIcon(os.path.join(folder_path, "Sundial_logo.svg")))

        # Create the central container widget and layout
        container = QWidget()
        self.setCentralWidget(container)

        # Set up the main layout as a QStackedLayout
        self.app_layout = QStackedLayout()
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.app_layout.setSpacing(0)

        # Initialize the pages/widgets
        self.loader_page = self.loaderPage()  # Loader page
        self.signin_page = self.signIn()
        self.onboard_page = Onboarding(self,darkTheme=darkTheme,LightTheme=lightTheme )
        self.dashboard = Dashboard(self,settings=self.settings,darkTheme=darkTheme,LightTheme=lightTheme)

        # Add loader page to the stacked layout
        self.app_layout.addWidget(self.loader_page)
        self.app_layout.addWidget(self.signin_page)
        self.app_layout.addWidget(self.onboard_page)
        self.app_layout.addWidget(self.dashboard)

        # Check onboarding status and set the appropriate page
        onboarding_complete = self.onboarding_status.value("onboarding_complete", False)

        # Set up the main layout for the container
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.app_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Set the layout for the container widget
        container.setLayout(main_layout)

    def loaderPage(self):
        self.loader = QWidget()

        # Create a label for the background
        self.background = QLabel(self.loader)
        self.background.setContentsMargins(0, 0, 0, 0)
        self.background.setScaledContents(True)
        self.background.setGeometry(0, 0, 800, 600)

        # Sundial logo label
        self.Sundial_logo = QLabel(parent=self.loader)
        self.Sundial_logo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.Sundial_logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.Sundial_logo.setScaledContents(True)  # Ensure it scales if necessary

        # Use a layout instead of manual geometry for better flexibility
        layout = QVBoxLayout(self.loader)
        layout.addStretch()  # Add stretchable space at the top
        layout.addWidget(self.Sundial_logo, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)  # Center logo horizontally
        layout.addStretch()  # Add stretchable space at the bottom

        # Set the layout to the loader widget
        self.update_background_image()
        self.loader.setLayout(layout)

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

        self.stacked_layout.currentChanged.connect(self.update_app_layout)

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

        self.description = QLabel(
            "Automated, AI-driven time tracking software of the future", parent=self.homepage)
        self.description.setGeometry(QtCore.QRect(180, 350, 480, 30))
        self.description.setFont(setup_font(40))

        self.signIn_button = QPushButton("Sign in", parent=self.homepage)
        self.signIn_button.setGeometry(QtCore.QRect(150, 450, 500, 60))
        self.signIn_button.setObjectName("signInButton")
        self.signIn_button.clicked.connect(self.go_to_signin_page)
        self.signIn_button.setCursor(QtGui.QCursor(
            QtCore.Qt.CursorShape.PointingHandCursor))

        self.update_app_layout(self.stacked_layout.currentIndex())

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
        self.welcomeMessage.setFont(setup_font(28))

        self.newUserLabel = QLabel(parent=self.signin_widget)
        self.newUserLabel.setGeometry(QtCore.QRect(40, 80, 81, 20))
        self.newUserLabel.setFont(setup_font(14))
        self.newUserLabel.setText("New user?")

        self.signupLabel = QLabel(parent=self.signin_widget)
        self.signupLabel.setGeometry(QtCore.QRect(120, 80, 150, 20))
        self.signupLabel.setFont(setup_font(14))

        if self.current_theme == "dark":
            urlLink = '<a href="https://ralvie.minervaiotstaging.com/pages/verify-email" style="color: #A49DC8; text-decoration: none;">Sign up here</a>'
        else:
            urlLink = '<a href="https://ralvie.minervaiotstaging.com/pages/verify-email" style="color: #1D0B77; text-decoration: none;">Sign up here</a>'
        self.signupLabel.setText(urlLink)
        self.signupLabel.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.signupLabel.setOpenExternalLinks(True)

        self.emailField = QLineEdit(parent=self.signin_widget)
        self.emailField.setGeometry(QtCore.QRect(40, 120, 444, 60))
        self.emailField.setPlaceholderText("User name or Email")
        self.emailField.setFont(setup_font(16))

        self.passwordField = QLineEdit(self.signin_widget)
        self.passwordField.setGeometry(40, 200, 444, 60)
        self.passwordField.setPlaceholderText("Password")
        self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordField.setFont(setup_font(16))


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
        self.errorMessageLabel.setFont(setup_font(12))
        self.errorMessageLabel.setVisible(False)

        self.Forgot_password_Label = QLabel(parent=self.signin_widget)
        self.Forgot_password_Label.setGeometry(QtCore.QRect(360, 280, 200, 23))
        self.Forgot_password_Label.setFont(setup_font(14))
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
        self.sign_In_button.setFont(setup_font(14))

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

        self.CompanyMessage.setFont(setup_font(24))

        self.companySelect = QComboBox(self.company_widget)
        self.companySelect.setGeometry(QtCore.QRect(40, 100, 434, 60))

        self.companyErrorMessageLabel = QLabel(parent=self.company_widget)
        self.companyErrorMessageLabel.setGeometry(
            QtCore.QRect(42, 170, 334, 20))
        self.companyErrorMessageLabel.setFont(setup_font(12))
        self.companyErrorMessageLabel.setVisible(False)
        self.company_select_button = QPushButton(
            "Get started", parent=self.company_widget)
        self.company_select_button.setGeometry(QtCore.QRect(40, 200, 434, 50))
        self.company_select_button.clicked.connect(
            self.handle_company_selection)
        self.company_select_button.setFont(setup_font(14))

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

    def update_app_layout(self,page_index):
        """Update the background based on the current page index and theme."""
        current_palette = QtWidgets.QApplication.palette()
        print(page_index)
        # Determine if it's a light or dark theme based on the background color
        if current_palette.color(QtGui.QPalette.ColorRole.Window).lightness() > 128:
            background_image_path = os.path.join(lightTheme, "BackgroundImage.svg")
            if page_index == -1 or page_index == 0:  # Sign-in page
                pixmap = QtGui.QPixmap(background_image_path)
                self.homepage_background.setPixmap(pixmap)
                self.homepage_background.setScaledContents(True)
                homepage_SundialLogo = os.path.join(lightTheme, "description_logo.svg")
                homepage_pixmap = QPixmap(homepage_SundialLogo)
                self.homepage_Sundial_logo.setPixmap(homepage_pixmap)

                homepage_subtitle = os.path.join(lightTheme, "signin_subtitle.svg")
                homepage_subtitle_pixmap = QPixmap(homepage_subtitle)
                self.homepage_subtitle.setPixmap(homepage_subtitle_pixmap)
            elif page_index == 1:  # Homepage
                pixmap = QtGui.QPixmap(background_image_path)
                self.sign_in_background.setPixmap(pixmap)
                self.sign_in_background.setScaledContents(True)

                sign_in_SundialLogo = os.path.join(lightTheme, "signin_logo.svg")
                sign_in_pixmap = QPixmap(sign_in_SundialLogo)
                self.sign_in_Sundial_logo.setPixmap(sign_in_pixmap)
            elif page_index == 2:  # Company page
                pixmap = QtGui.QPixmap(background_image_path)
                self.sign_in_background.setPixmap(pixmap)
                self.sign_in_background.setScaledContents(True)
        else:
            background_image_path = os.path.join(darkTheme, "darkBackground.svg")
            if page_index == -1 or page_index == 0 :  # Sign-in page
                pixmap = QtGui.QPixmap(background_image_path)
                self.homepage_background.setPixmap(pixmap)
                self.homepage_background.setScaledContents(True)

                homepage_SundialLogo = os.path.join(darkTheme, "dark_des_logo.svg")
                homepage_pixmap = QPixmap(homepage_SundialLogo)
                self.homepage_Sundial_logo.setPixmap(homepage_pixmap)
                self.homepage_Sundial_logo.setStyleSheet("background: transparent;")

                homepage_subtitle = os.path.join(darkTheme, "signin_subtitle.svg")
                homepage_subtitle_pixmap = QPixmap(homepage_subtitle)
                self.homepage_subtitle.setPixmap(homepage_subtitle_pixmap)
                self.homepage_subtitle.setStyleSheet("background-color: none;")
            elif page_index == 1:  # Homepage
                pixmap = QtGui.QPixmap(background_image_path)
                self.sign_in_background.setPixmap(pixmap)
                self.sign_in_background.setScaledContents(True)

                sign_in_SundialLogo = os.path.join(darkTheme, "dark_signin_logo.svg")
                sign_in_pixmap = QPixmap(sign_in_SundialLogo)
                self.sign_in_Sundial_logo.setPixmap(sign_in_pixmap)
            elif page_index == 2:  # Company page
                pixmap = QtGui.QPixmap(background_image_path)
                self.company_background.setPixmap(pixmap)
                self.company_background.setScaledContents(True)


    def update_background_image(self):
        """Updates the background image based on the current theme."""
        current_palette = QtWidgets.QApplication.palette()

        # Determine if it's a light or dark theme based on the background color
        if current_palette.color(QtGui.QPalette.ColorRole.Window).lightness() > 128:
            # Light theme: set a light-themed background image
            light_background_path = os.path.join(lightTheme, "BackgroundImage.svg")
            pixmap = QtGui.QPixmap(light_background_path)

            SundialLogo = os.path.join(lightTheme, "SundialLogo.svg")
            SundialLogo_pixmap = QtGui.QPixmap(SundialLogo)  # Load the Sundial logo
            self.Sundial_logo.setPixmap(SundialLogo_pixmap)
            self.apply_light_theme()
            self.current_theme = "light"
        else:
            # Dark theme: set a dark-themed background image
            dark_background_path = os.path.join(darkTheme, "darkBackground.svg")
            pixmap = QtGui.QPixmap(dark_background_path)

            SundialLogo = os.path.join(darkTheme, "darkSundialLogo.svg")
            SundialLogo_pixmap = QtGui.QPixmap(SundialLogo)  # Load the Sundial logo
            self.Sundial_logo.setPixmap(SundialLogo_pixmap)
            self.apply_dark_theme()
            self.current_theme = "dark"

        # Check if the image was successfully loaded
        if pixmap.isNull():
            print("Failed to load the background image.")
        else:
            # Apply the pixmap to the background label
            self.background.setPixmap(pixmap)
            self.background.setScaledContents(True)  # Ensure the image scales properly



    def handle_palette_change(self):
        """Handle system theme change dynamically."""
        print("System theme changed!")
        self.update_background_image()
        self.update_app_layout(self.stacked_layout.currentIndex())
        self.onboard_page.toggle_theme()

    def redirect_to_login(self):
        creds = credentials()
        if creds and creds.get("Authenticated"):
            # self.update_settings()
            # Directly to the main UI if already authenticated
            self.onboarding_status.setValue("onboarding_complete", "j?KEgMKb:^kNMpX:Bx=7")
            self.app_layout.setCurrentIndex(3)
            # self.change_page(0)

    def initiate_login(self):
        print("Initiating login...")
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
        print("perform_login_request")
        payload = {"userName": email, "password": password,"companyId":self.companyid}
        try:
            response = requests.post(host + "/0/ralvie/login", json=payload,
                                     headers={'Content-Type': 'application/json'})
            if response.ok:
                # Emit signal with the response
                print("testing")
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
            if self.onboarding_status.value("onboarding_complete", False) == "j?KEgMKb:^ksdasNMpX:Bx=7":
                # If onboarding is complete, skip it and go to the sign-in or main page
                self.app_layout.setCurrentWidget(self.dashboard)
            else:
                # Show the onboarding screen only once
                self.app_layout.setCurrentWidget(self.onboard_page)
            # user_details()
            # self.clear_activities()
            # self.add_dynamic_blocks()
            # clear_credentials("SD_KEYS")
            # self.loader_.setVisible(False)
            # QCoreApplication.processEvents()
            # self.update_settings()
            # self.update_theme()
            #

        elif response_data["code"] == 'RCW00001':
            print(response_data)
            self.companies = response_data['data']['companies']

            if self.companies:
                print(self.companies)
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

    def populate_company_combobox(self):
        self.companySelect.clear()
        unique_company_names = {company['name'] for company in self.companies}
        self.companySelect.addItems(unique_company_names)

    def go_to_company_page(self):
        self.loader_.setVisible(False)
        self.stacked_layout.setCurrentIndex(2)

    def handle_company_selection(self):
        self.selected_company = self.companySelect.currentText()
        self.continue_with_selected_company()

    def continue_with_selected_company(self):
        print("Company_select")
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
            self.app_layout.setCurrentIndex(1)  # Show the sign-in page
            if creds and creds.get("Authenticated"):
                # self.update_settings()
                # Directly to the main UI if already authenticated
                if self.onboarding_status.value("onboarding_complete", False) == "j?KEgMKb:^kNMpX:Bx=7":
                    # If onboarding is complete, skip it and go to the sign-in or main page
                    self.app_layout.setCurrentWidget(self.dashboard)
                else:
                    # Show the onboarding screen only once
                    self.app_layout.setCurrentWidget(self.onboard_page)
            else:
                self.app_layout.setCurrentIndex(1)  # Show the sign-in page
        else:
            print("Waiting for the server to start...")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.app_authentication()
    sys.exit(app.exec())