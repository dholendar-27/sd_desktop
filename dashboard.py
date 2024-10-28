import os
import threading
from datetime import datetime, timedelta
import sys

import pytz
import requests
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QHBoxLayout, QApplication, \
    QGraphicsDropShadowEffect, QTimeEdit, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QSize, QRect, QTimer, QPropertyAnimation
from PySide6.QtGui import QCursor, QPixmap, QFont, QPalette, QColor
from deepdiff import DeepDiff
from qt_material import apply_stylesheet

from sd_core.cache import cache_user_credentials
from sd_qt.sd_desktop.checkBox import CustomCheckBox
from sd_qt.sd_desktop.theme_manager import ThemeManager
from sd_qt.sd_desktop.toggleSwitch import SwitchControl
from sd_qt.sd_desktop.util import credentials, add_settings, retrieve_settings

host = "http://localhost:7600/api"

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

cached_credentials = None
class EventManager:


    def __init__(self):
        self.scrollAreaWidgetContents = None
        self.current_color_index = 0
        self.theme_manager = ThemeManager.get_instance()

        # Connect to the theme change signal
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        QApplication.instance().paletteChanged.connect(self.handle_palette_change)
        self.theme_manager.set_theme_based_on_system(QApplication.instance().activeWindow())

    def on_theme_changed(self, theme_name):
        """Reapply styles when the theme changes."""
        self.update_events_style()

    def truncate_text(self, text, max_words):
        return text[:max_words] + "..." if len(text) > max_words else text


    def listView(self, events):
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


    def update_events_style(self):
        # Clear previous widgets to avoid duplicates (optional)
        while self.scrollAreaWidgetContents.layout().count():
            item = self.scrollAreaWidgetContents.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Loop through each child widget (each event)
        for event_widget in self.scrollAreaWidgetContents.findChildren(QWidget):
            # Create an outer container for each event_widget to apply margin
            outer_container = QWidget(parent=self.scrollAreaWidgetContents)
            outer_layout = QHBoxLayout(outer_container)

            # Set left and right margins (e.g., 20px)
            outer_layout.setContentsMargins(20, 0, 20, 0)

            # Set distinct background colors and border to visualize the margin effect
            outer_container.setStyleSheet("background-color: lightgrey; border: 1px solid black;")
            event_widget.setStyleSheet("background-color: white; border: 1px solid blue;")

            # Add the event_widget to the outer container layout
            outer_layout.addWidget(event_widget)

            # Set the layout of scrollAreaWidgetContents if it’s not set
            if not self.scrollAreaWidgetContents.layout():
                self.scrollAreaWidgetContents.setLayout(QVBoxLayout())

            # Add the outer_container to the scroll area layout
            self.scrollAreaWidgetContents.layout().addWidget(outer_container)

            # Apply the dynamic stylesheet if available
            light_color = event_widget.property('light_color')
            dark_color = event_widget.property('dark_color')

            if light_color and dark_color:
                stylesheet = self.get_dynamic_block_stylesheet(light_color, dark_color)
                event_widget.setStyleSheet(stylesheet)

                # Apply additional styles to labels inside the event_widget
                for label_name in ["application_name", "time_label"]:
                    label = event_widget.findChild(QLabel, label_name)
                    if label:
                        label.setStyleSheet("background:transparent;")

    def get_dynamic_block_stylesheet(self, light_color, dark_color):
        """Generate a dynamic stylesheet based on the current theme."""
        if self.theme_manager.current_theme == "light":
            # Light theme settings
            color = light_color
            border_color = light_colors_border.get(light_color, "#000000")  # Default to black if not found
            text_color = "black"
        else:
            # Dark theme settings
            color = dark_color
            border_color = dark_colors_border.get(dark_color, "#000000")  # Default to black if not found
            text_color = "white"

        # Return the generated stylesheet string
        return (
            ".QWidget {"
            f"background-color: {color};"
            f"color: {text_color};"
            f"border-radius: 5px;"
            f"margin: 5px 20px 5px 0;"
            f"opacity: 0.9;"
            f"border-left: 3px solid {border_color};"
            "}"
        )

    def get_next_color(self):
        """Get the next color in the light and dark color arrays."""
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
            "light_color": light_colors[self.current_color_index % len(light_colors)],
            "dark_color": dark_colors[self.current_color_index % len(dark_colors)]
        }

        # Update the index for the next call
        self.current_color_index += 1
        self.current_color_index %= len(light_colors)  # Ensure it cycles correctly

        return colors

    def add_dynamic_blocks(self):
        start_time_utc, end_time_utc = self.get_schedule_times()
        start_time = start_time_utc.strftime('%Y-%m-%d %H:%M:%S')
        end_time = end_time_utc.strftime('%Y-%m-%d %H:%M:%S')

        creds = credentials()
        if not creds:
            print("No credentials found")
            return

        try:
            response = requests.get(
                f"{host}/0/dashboard/events?start={start_time}&end={end_time}",
                headers={"Authorization": creds['token']}
            )
            event_data = response.json().get('events', [])

            event_data = self.listView(event_data)

            if event_data:
                while self.layout.count():
                    widget = self.layout.takeAt(0).widget()
                    if widget:
                        widget.deleteLater()

                self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                for event in event_data:
                    event_widget = self.create_event_widget(event)
                    self.layout.addWidget(event_widget)
                self.layout.update()
            else:
                print("No events found")

        except Exception as e:
            print(f"Error retrieving or processing events: {e}")

    def create_event_widget(self, event):
        color = self.get_next_color()

        # Create an outer container widget to handle equal margins around event_widget
        outer_container = QtWidgets.QWidget(parent=self.scrollAreaWidgetContents)
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(10, 5, 0, 0)  # Equal margins on all sides

        # Create the main event widget with an inner layout
        event_widget = QtWidgets.QWidget(parent=outer_container)
        event_widget.setFixedSize(530, 60)  # Adjusted size for internal padding

        # Set theme color
        is_light_theme = self.theme_manager.current_theme == "light"
        event_widget.setStyleSheet(f"""
            background-color: {color['light_color'] if is_light_theme else color['dark_color']};
            border-radius: 10px;
        """)

        # Inner layout for event details
        event_widget_layout = QVBoxLayout(event_widget)
        event_widget_layout.setContentsMargins(5, 5, 5, 5)  # Additional internal padding

        # Horizontal layout for application name and time
        hbox_layout = QHBoxLayout()
        hbox_layout.setContentsMargins(10, 0, 10, 0)  # No extra margin for internal widgets

        # Create and style application name label
        application_name_label = QtWidgets.QLabel(parent=event_widget)
        application_name_label.setObjectName("application_name")
        application_name_label.setFont(self.get_font(12 if sys.platform == "darwin" else 9))
        application_name_label.setText(self.truncate_text(event['app'], 50))
        if len(event['app']) > 50:
            application_name_label.setToolTip(event['app'])
        application_name_label.setStyleSheet("background:transparent;")

        # Create and style time label
        time_label = QtWidgets.QLabel(parent=event_widget)
        time_label.setObjectName("time_label")
        time_label.setFont(self.get_font(12 if sys.platform == "darwin" else 9))
        time_label.setText(event['time'])
        time_label.setStyleSheet("background:transparent;")

        # Add labels to horizontal layout
        hbox_layout.addWidget(application_name_label)
        hbox_layout.addWidget(time_label, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # Add horizontal layout to event widget layout
        event_widget_layout.addLayout(hbox_layout)

        # Add event widget to outer container layout
        outer_layout.addWidget(event_widget)

        # Return outer container for adding to main layout
        return outer_container

    def get_font(self, size):
        font = QtGui.QFont()
        font.setPointSize(size)
        return font

    def get_schedule_times(self):
        current_utc_date = datetime.utcnow().date()
        start_time_utc = datetime(current_utc_date.year, current_utc_date.month, current_utc_date.day)
        end_time_utc = start_time_utc + timedelta(days=1) - timedelta(seconds=1)
        return start_time_utc, end_time_utc

    def handle_palette_change(self):
        """Handle system theme change dynamically."""
        print("System theme changed!")
        self.add_dynamic_blocks()


class Dashboard(QWidget):
    def __init__(self,main_reference,settings,darkTheme,LightTheme,parent=None):
        super().__init__(parent)
        self.To_time = QTimeEdit()
        self.From_time = QTimeEdit()
        self.darkTheme = darkTheme
        self.lightTheme = LightTheme
        self.main_reference = main_reference

        self.settings = settings
        self.selected_button = None
        self.user_override_theme = False
        self.last_date = None
        self.week_schedule = {
            'Monday': True, 'Tuesday': True, 'Wednesday': True, 'Thursday': True,
            'Friday': True, 'Saturday': True, 'Sunday': True,
            'starttime': '00:00', 'endtime': '23:59'
        }
        self.default_week_schedule = self.week_schedule.copy()

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.theme_manager = ThemeManager.get_instance()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.theme_manager.set_theme_based_on_system(self)


        self.setupSidebar(darkTheme)
        self.horizontalLayout.addWidget(self.sidebar)

        self.setupStack()
        self.horizontalLayout.addWidget(self.stackedWidget)

        self.setWindowTitle("Dashboard")
        self.setFixedSize(800, 600)

        self.activities_timer = QTimer(self)
        self.activities_timer.setInterval(60000)
        self.activities_timer.timeout.connect(self.refresh_activities)



    def on_theme_changed(self, theme):
        """Handle theme change and update styles."""
        print(f"Theme changed to: {theme}")  # Debug print to confirm the slot is executed
        self.update_app_layout()
        self.refresh_widget_styles()
        self.repaint()

    def refresh_widget_styles(self):
        """Refresh styles for widgets after a theme change."""
        self.setAutoFillBackground(True)
        self.update()

    def refresh_activities(self):
        if self.stackedWidget.currentIndex() == 0:
            self.event_manager.add_dynamic_blocks()

    def handle_palette_change(self):
        """Handle system theme change dynamically."""
        self.theme_manager.set_theme_based_on_system(self)
        self.update_app_layout()

    def createButton(self, text, icon_path, top_position, folder_path):
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setFont(self.getFont())

        if icon_path:
            icon_label = QLabel(parent=button)
            icon_label.setGeometry(QRect(20, 10, 21, 21))
            icon_label.setPixmap(QPixmap(folder_path + icon_path))

        button.setStyleSheet("""
            QPushButton {
                border: none;
                padding-left: 10px;
            }
            QPushButton:hover, QPushButton:checked {
                background-color: #E0E0E0;
                color: black;
            }
        """)

        return button

    def setupSidebar(self, folder_path):
        self.sidebar = QWidget(parent=self)
        self.sidebar.setMinimumSize(QSize(200, 570))
        self.sidebar.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.sidebar)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.AppLogo = QWidget(parent=self.sidebar)
        self.AppLogo.setMinimumSize(QSize(0, 40))
        self.AppLogo.setMaximumSize(QSize(200, 40))
        self.label = QLabel(parent=self.AppLogo)
        self.label.setGeometry(QRect(10, 0, 150, 40))
        self.label.setText("App Logo")
        self.verticalLayout_2.addWidget(self.AppLogo)

        self.widget_6 = QWidget(parent=self.sidebar)
        self.widget_6.setMinimumSize(QSize(0, 420))
        self.verticalLayout_2.addWidget(self.widget_6)

        self.createSidebarButton("Activities", "/Activity.svg", QRect(2, 10, 190, 40), 0, folder_path)
        self.createSidebarButton("General settings", "/generalSettings.svg", QRect(2, 55, 190, 40), 1, folder_path)
        self.createSidebarButton("Schedule", "/schedule.svg", QRect(2, 100, 190, 40), 2, folder_path)

        self.widget = QWidget(parent=self.sidebar)
        widget_layout = QVBoxLayout(self.widget)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        button_height = 40
        button_spacing = 10

        self.username_widget = self.createSidebarButton("Profile settings", "/open_arrow.svg", QRect(2, 0, 190, 40), 3, folder_path)
        widget_layout.addWidget(self.username_widget)
        self.Signout = self.createSidebarButton("Sign out", "/signout.svg", QRect(2, button_height + button_spacing, 190, 40), -1, folder_path)
        widget_layout.addWidget(self.Signout)
        self.theme = self.createButton("Change Theme", "", QRect(2, 2 * (button_height + button_spacing), 190, 40), -1)
        widget_layout.addWidget(self.theme)
        self.verticalLayout_2.addWidget(self.widget)

    def createSidebarButton(self, text, icon_path, geometry, page_index, folder_path):
        button = QPushButton(text, self.widget_6)
        button.setGeometry(geometry)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setFont(self.getFont())

        if icon_path:
            icon_label = QLabel(parent=button)
            icon_label.setGeometry(QRect(20, 10, 21, 21))
            icon_label.setPixmap(QPixmap(folder_path + icon_path))

        button.setStyleSheet("""
            QPushButton {
                border: none;
                padding-left: 10px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:checked {
                background-color: #B0C4DE;
                color: black;
            }
        """)

        button.setCheckable(True)
        button.clicked.connect(lambda: self.onButtonClicked(button, page_index))
        return button

    def onButtonClicked(self, button, page_index):
        if self.selected_button and self.selected_button != button:
            self.selected_button.setChecked(False)

        button.setChecked(True)
        self.selected_button = button
        self.stackedWidget.setCurrentIndex(page_index)

        if page_index == 0:
            self.activities_timer.start()
        else:
            self.activities_timer.stop()

    def getFont(self):
        font = QFont()
        font.setPointSize(10)
        return font

    def setupStack(self):
        self.stackedWidget = QStackedWidget(parent=self)
        self.stackedWidget.setContentsMargins(0, 0, 0, 0)

        self.Activities = self.setupActivitiesPage()
        self.GeneralSettings = self.GeneralSettingsPage()
        self.Schedule = self.setupSchedulePage()
        self.userProfile_widget = self.setupUserDrawer()

        self.stackedWidget.addWidget(self.Activities)
        self.stackedWidget.addWidget(self.GeneralSettings)
        self.stackedWidget.addWidget(self.Schedule)
        self.stackedWidget.addWidget(self.userProfile_widget)

        # Connect a signal to handle changes in the stacked widget
        self.stackedWidget.currentChanged.connect(self.update_app_layout)

    def addPageContent(self, page_widget, text):
        layout = QVBoxLayout(page_widget)
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

    def setupActivitiesPage(self):
        # Initialize the main widget
        self.Activities = QtWidgets.QWidget()
        self.displayed_events = set()

        # Header setup
        self.Activities_header = QtWidgets.QLabel(parent=self.Activities)
        self.Activities_header.setGeometry(QtCore.QRect(10, 15, 191, 40))
        self.Activities_header.setText("Activities")

        header_font = QtGui.QFont()
        header_font.setPointSize(20 if sys.platform == "darwin" else 16)
        header_font.setWeight(QtGui.QFont.Weight.Bold)
        self.Activities_header.setFont(header_font)

        # Date display setup
        self.Date_display = QtWidgets.QWidget(parent=self.Activities)
        self.Date_display.setGeometry(QtCore.QRect(10, 70, 560, 51))

        self.Day = QtWidgets.QLabel(parent=self.Date_display)
        self.Day.setGeometry(QtCore.QRect(22, 15, 58, 20))
        date_font = QtGui.QFont()
        date_font.setPointSize(14 if sys.platform == "darwin" else 10)
        date_font.setWeight(QtGui.QFont.Weight.Bold)
        self.Day.setText("Today")
        self.Day.setFont(date_font)

        self.event_manager = EventManager()
        self.event_manager.scrollAreaWidgetContents = QWidget()
        self.event_manager.layout = QVBoxLayout(self.event_manager.scrollAreaWidgetContents)
        self.event_manager.layout.setContentsMargins(0, 0, 10, 10)
        self.event_manager.layout.setSpacing(10)

        self.scrollArea = QtWidgets.QScrollArea(self.Activities)
        self.scrollArea.setGeometry(QtCore.QRect(10, 120, 560, 460))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.event_manager.scrollAreaWidgetContents)
        self.event_manager.add_dynamic_blocks()
        self.update_app_layout()
        return self.Activities

    def GeneralSettingsPage(self):
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

        self.load_settings()

        return self.GeneralSettings

        # Retrieve and set initial settings


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

        # Update description
        font.setPointSize(14 if sys.platform == "darwin" else 8)
        self.update_description = QLabel(parent=self.Version_2)
        self.update_description.setGeometry(QRect(20, 50, 311, 16))
        self.update_description.setFont(font)
        self.update_description.setText("Your Sundial application is up to date")

        # Display current version
        self.current_version = QLabel(parent=self.Version_2)
        self.current_version.setGeometry(QRect(20, 80, 311, 20))
        self.current_version.setFont(font)
        # self.update_version_display()

        # Toast message setup
        self.startup_toast_message = QWidget(parent=self.GeneralSettings)
        self.startup_toast_message.setGeometry(QRect(830, 520, 350, 60))
        self.startup_toast_label = QLabel(self.startup_toast_message)
        self.startup_toast_label.setGeometry(QRect(20, 10, 330, 40))
        font.setPointSize(14 if sys.platform == "darwin" else 12)
        self.startup_toast_label.setFont(font)
        self.startup_toast_message.setStyleSheet("border-radius: 10px; background-color:#BFF6C3")

        # Initially hide the toast
        self.startup_toast_message.setVisible(False)

        # Animation setup for sliding in the toast message
        self.toast_animation = QPropertyAnimation(self.startup_toast_message, b"geometry")
        self.toast_animation.setDuration(500)
        self.toast_animation.setStartValue(QRect(830, 520, 350, 60))
        self.toast_animation.setEndValue(QRect(220, 520, 350, 60))
        self.toast_animation.setEasingCurve(QtCore.QEasingCurve.OutBounce)

    def show_toast_message(self, message):
        self.startup_toast_label.setText(message)
        self.startup_toast_message.setVisible(True)
        self.toast_animation.start()
        QtCore.QTimer.singleShot(3000, self.hide_toast_message)

    def hide_toast_message(self):
        self.startup_toast_message.setVisible(False)

    def load_settings(self):
        settings = retrieve_settings()
        self.startup_checkbox.setChecked(settings.get('launch', False))
        self.idletime_checkbox.setChecked(settings.get('idle_time', False))


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


    #
    # def version(self):
    #     settings = retrieve_settings()
    #     version = settings.get("version", "Unknown")
    #     return version
    #
    # def update_version_display(self):
    #     new_version = self.version()
    #     if not hasattr(self, 'is_dark_mode'):
    #         self.is_dark_mode = self.detect_system_theme()
    #
    #     color, bg_color = ("rgba(248, 248, 248, 0.5)", "white") if self.is_dark_mode else (
    #     "rgba(71, 75, 79, 1)", "black")
    #     self.current_version.setText(
    #         f'<span style="color: {color};">Current app version: </span>'
    #         f'<span style="color: {bg_color}; background:transparent;">2.0.0_<span style="font-size=10px">beta</span></span>'
    #     )
    #     self.current_version.update()
    #
    # def check_for_updates(self):
    #     def fetch_version():
    #         new_version = self.get_version_from_server()  # Implement this
    #         settings = retrieve_settings()
    #         settings['version'] = new_version
    #         save_settings(settings)
    #         self.update_version_display()
    #
    #     threading.Thread(target=fetch_version).start()
    #
    # def startup_status(self):
    #     status = "start" if self.startup_checkbox.isChecked() else "stop"
    #     self.launch_on_start(status)
    #
    # def idletime_status(self):
    #     status = "start" if self.idletime_checkbox.isChecked() else "stop"
    #     self.enable_idletime(status)


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
        # self.From_time.timeChanged.connect(self.update_to_time_min)
        # self.To_time.timeChanged.connect(self.update_from_time_max)

        self.result_label = QLabel(self.day_widget)
        self.result_label.setGeometry(QtCore.QRect(20, 230, 450, 30))

        # self.To_time.timeChanged.connect(self.compare_times)
        # self.From_time.timeChanged.connect(self.compare_times)

        self.Reset = QPushButton(parent=self.day_widget)
        self.Reset.setGeometry(QtCore.QRect(315, 235, 100, 50))
        self.Reset.clicked.connect(self.resetSchedule)
        #
        self.From_time.timeChanged.connect(self.update_save_button_state)
        self.To_time.timeChanged.connect(self.update_save_button_state)

        self.Save = QPushButton(parent=self.day_widget)
        self.Save.setGeometry(QtCore.QRect(435, 235, 100, 50))
        self.Save.clicked.connect(self.saveSchedule)
        self.Reset.setText("Reset")
        self.Save.setText("Save")

        self.schedule_settings()

        self.Schedule_enabler_checkbox.stateChanged.connect(
            self.toggle_schedule_visibility)
        self.Schedule.installEventFilter(self)

        return self.Schedule

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

    def resetSchedule(self):
        global week_schedule
        threading.Thread(target=self.save_schedule,
                         args=(self.default_week_schedule,)).start()
        self.updateCheckboxStates(self.default_week_schedule)
        self.update_save_button_state()

    def show_message(self):
        # Toggle the visibility of the info_message widget
        if self.info_message.isVisible():
            self.info_message.setVisible(False)
        else:
            self.info_message.setVisible(True)
            self.info_message.raise_()

    def setupScheduleCheckboxes(self):
        # Days of the week for creating checkboxes and labels dynamically
        days = [
            {"name": "Monday", "x": 20, "y": 58},
            {"name": "Tuesday", "x": 160, "y": 58},
            {"name": "Wednesday", "x": 300, "y": 58},
            {"name": "Thursday", "x": 440, "y": 58},
            {"name": "Friday", "x": 20, "y": 98},
            {"name": "Saturday", "x": 160, "y": 98},
            {"name": "Sunday", "x": 300, "y": 98}
        ]

        # Common font settings
        font = QtGui.QFont()
        font.setPointSize(14 if sys.platform == "darwin" else 10)
        current_palette = QApplication.palette()
        # Determine theme path based on current theme
        theme_path = (
            "/Users/pothireddy/Documents/Sundial/v2.0.0/activitywatch/sd-qt/sd_qt/sd_desktop/resources/DarkTheme"
            if current_palette.color(QtGui.QPalette.ColorRole.Window).lightness() > 128
            else "/Users/pothireddy/Documents/Sundial/v2.0.0/activitywatch/sd-qt/sd_qt/sd_desktop/resources/LightTheme"
        )

        # Loop through each day to create checkbox and label
        for day in days:
            # Checkbox for each day
            checkbox = CustomCheckBox(parent=self.day_widget)
            checkbox.setGeometry(QtCore.QRect(day["x"], day["y"], 40, 40))
            checkbox.setStyleSheet(".QCheckBox::indicator { width: 40px; height: 40px; }")

            # Set images based on theme path
            checkbox.setTickImage(os.path.join(theme_path, 'checkedbox.svg'))
            checkbox.setUncheckedImage(os.path.join(theme_path, 'checkbox.svg'))

            # Label for each checkbox
            label = QLabel(day["name"], parent=self.day_widget)
            label.setGeometry(QtCore.QRect(day["x"] + 30, day["y"] - 8, 110, 40))
            label.setFont(font)

            # Set attributes for day checkboxes as instance variables for easy access
            day_name_lower = day['name'].lower()
            setattr(self, f"{day_name_lower}_checkbox", checkbox)
            setattr(self, f"{day_name_lower}_label", label)

            # Connect state change to update the save button
            checkbox.stateChanged.connect(self.update_save_button_state)

        # Initial checkbox state setup
        self.updateCheckboxStates(self.settings.get('weekdays_schedule', {}))

    def updateCheckboxStates(self, weekdays):
        # Update each checkbox based on the weekdays dictionary
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            checkbox = getattr(self, f"{day}_checkbox", None)
            if checkbox:
                checkbox.setChecked(weekdays.get(day.capitalize(), False))

        # Set start and end times if present
        if hasattr(self, 'From_time') and hasattr(self, 'To_time'):
            self.From_time.setTime(QtCore.QTime.fromString(
                weekdays.get('starttime', "09:30"), "HH:mm"))
            self.To_time.setTime(QtCore.QTime.fromString(
                weekdays.get('endtime', "18:30"), "HH:mm"))

        self.Schedule_label.setText("Schedule")
        self.Schedule_enabler_label.setText(
            "Record data only during my scheduled work hours.")
        self.Working_days_label.setText("Working days")

    def get_current_schedule(self):
        return {
            day.capitalize(): getattr(self, f"{day}_checkbox").isChecked()
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        } | {
            'starttime': self.From_time.time().toString("HH:mm"),
            'endtime': self.To_time.time().toString("HH:mm")
        }

    def update_save_button_state(self):
        current_schedule = self.get_current_schedule()
        # Compare schedule and check if all checkboxes are unchecked
        previous_schedule = self.settings.get('weekdays_schedule', {})
        if not DeepDiff(current_schedule, previous_schedule) or self.check_all_days_false():
            self.Save.setEnabled(False)
            self.Reset.setEnabled(True)

            # Detect and set dark mode if not already set


            # Styles based on theme
            reset_style = "color:#6A5FA2; border: 1px solid #6A5FA2; border-radius: 5px;"
            save_style = """
                background: qlineargradient(
                    spread: pad, x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(45, 35, 100, 76),
                    stop: 1 rgba(90, 80, 130, 76)
                );
                border-radius: 5px;
                color: rgba(255, 255, 255, 0.3);
            """
            # Apply styles
            self.Reset.setStyleSheet(reset_style)
            self.Save.setStyleSheet(save_style)

            # Apply opacity effect to buttons
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.1)
            self.Save.setGraphicsEffect(opacity_effect)
            self.Reset.setGraphicsEffect(opacity_effect)
        else:
            # Enable both Save and Reset buttons with active styles
            self.Save.setEnabled(True)
            self.Reset.setEnabled(True)



    def check_all_days_false(self):
        # Check if all day checkboxes are unchecked
        return not any(
            getattr(self, f"{day}_checkbox").isChecked()
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        )

    def save_schedule(self, schedule):
        add_settings('weekdays_schedule', schedule)
        self.update_save_button_state()

    def saveSchedule(self):
        if self.check_all_days_false():
            return  # Avoid saving if all checkboxes are unchecked

        week_schedule = self.get_current_schedule()
        save_thread = threading.Thread(target=self.save_schedule, args=(week_schedule,))
        save_thread.start()
        save_thread.join()  # Ensure completion before UI update



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

        return self.userProfile_widget

    def ellipsis(self, value, length):
        if len(value) > length:
            return value[:length] + "..."
        else:
            return value


    def load_user_details(self):
        """Load and display the logged-in user's details."""
        # Fetch user details from the storage or API (you can adjust this as needed)
        user_details = credentials()

        if not user_details:
            # If user details are not available, clear the fields
            self.clear_user_detail_fields()
            return

        # Helper function to update text and tooltip
        def update_field(widget, text, max_length=30):
            if len(text) > max_length:
                widget.setText(self.ellipsis(text, max_length))
                widget.setToolTip(text)
            else:
                widget.setText(text)
                widget.setToolTip("")  # Clear tooltip if not needed

        # Update the UI components with the fetched user details
        update_field(self.first_name_value, user_details.get('firstname', ''))
        update_field(self.email_value, user_details.get('email', ''))
        update_field(self.company_value, user_details.get('companyName', ''))

        # Update phone number separately as it does not have a tooltip logic
        self.mobile_value.setText(user_details.get('phone', ''))

        # Trigger an update for all fields to ensure the UI refreshes
        self.first_name_value.update()
        self.email_value.update()
        self.mobile_value.update()
        self.company_value.update()

    def clear_user_detail_fields(self):
        """Clear user detail fields in the UI."""
        self.first_name_value.setText("")
        self.first_name_value.setToolTip("")
        self.email_value.setText("")
        self.email_value.setToolTip("")
        self.mobile_value.setText("")
        self.company_value.setText("")
        self.company_value.setToolTip("")


    def schedule_settings(self):
        settings = retrieve_settings()
        self.updateCheckboxStates(settings.get('weekdays_schedule', {}))
        self.Schedule_enabler_checkbox.setChecked(
            settings.get('schedule', False))
        if settings.get('schedule'):
            self.day_widget.show()
        else:
            self.day_widget.hide()

    def update_app_layout(self):
        """Update the background based on the current page index and theme."""
        page_index = self.stackedWidget.currentIndex()  # Get the current page index
        print(f"Current page index: {page_index}")

        # Determine if it's a light or dark theme based on the current theme in ThemeManager
        is_light_theme = self.theme_manager.current_theme == "light"

        # Define styles based on the theme
        if is_light_theme:
            # Light theme styles
            print("Hello")
            self.apply_styles_for_page(page_index, "#EFEFEF", "#F9F9F9", "black", "#FFFFFF")
        else:
            print("world")
            # Dark theme styles
            self.apply_styles_for_page(page_index, "#171717", "#101010", "white", "#010101")

        # Force a repaint to make sure all changes are visible
        self.repaint()

    def apply_styles_for_page(self, page_index, date_background, scroll_background, version_text_color, checkbox_color):
        """Apply styles based on the current page index and theme colors."""
        # Apply new styles
        if page_index == 0 or page_index == -1:
            self.Date_display.setStyleSheet("")
            self.scrollArea.setStyleSheet("")
            self.Day.setStyleSheet("")

            self.Date_display.setStyleSheet(f"""
                background-color: {date_background};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            """)
            self.scrollArea.setStyleSheet(f"""
                border: None;
                background-color: {scroll_background};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            """)
            self.Day.setStyleSheet("background: transparent;")
            self.scrollArea.verticalScrollBar().setStyleSheet(f"""
                QScrollBar:vertical {{
                    background: {scroll_background};
                    width: 5px;
                    margin: 0px 0px 0px 0px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background: #B0B0B0;
                    min-height: 20px;
                    border-radius: 5px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                    width: 0px;
                }}
                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                    background: none;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
        elif page_index == 1:
            self.GeneralSettings_header.setStyleSheet("")
            self.startup.setStyleSheet("")
            self.idletime.setStyleSheet("")
            self.Version_2.setStyleSheet("")

            self.GeneralSettings_header.setStyleSheet(f"background-color: {checkbox_color};")
            self.startup_checkbox.set_circle_color(checkbox_color)
            self.idletime_checkbox.set_circle_color(checkbox_color)
            self.startup.setStyleSheet(f"border-radius: 10px; background-color: {scroll_background};")
            self.idletime.setStyleSheet(f"border-radius: 10px; background-color: {scroll_background};")
            self.Version_2.setStyleSheet(f"border-radius: 10px; background-color: {scroll_background};")
            self.current_version.setText(
                f'<span style="color: rgba(71, 75, 79, 1);">Current app version: </span>'
                f'<span style="color: {version_text_color}; background:transparent;">2.0.0_beta</span>'
            )
        elif page_index == 2:

            self.Schedule_enabler.setStyleSheet("")
            self.day_widget.setStyleSheet("")


            self.Schedule_enabler.setStyleSheet(f"""
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                background-color: {scroll_background};
            """)
            self.day_widget.setStyleSheet(f"""
                .QWidget {{
                    border-top-left-radius: 0px;
                    border-top-right-radius: 0px;
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                    background-color: {scroll_background};
                }}
            """)
        elif page_index == 3:
            self.profile_container.setStyleSheet("")
            self.profile_image.setStyleSheet("")


            self.profile_container.setStyleSheet(f"border-radius: 10px; background-color: {scroll_background};")
            self.profile_image.setFixedSize(100, 100)
            self.profile_image.setStyleSheet(f"""
                border-radius: 50%;
                background-color: {scroll_background};
                background-position: center;
                background-repeat: no-repeat;
            """)



