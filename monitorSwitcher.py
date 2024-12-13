import os
import platform
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, 
    QFileDialog, QHBoxLayout, QSystemTrayIcon, QMenu, QAction, QWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import keyboard
import json

PROFILES_DIR = "monitor_profiles"
MULTIMONITOR_TOOL = "MultiMonitorTool.exe"

if not os.path.exists(PROFILES_DIR):
    os.makedirs(PROFILES_DIR)

class MonitorManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.hotkeys = self.load_hotkeys()

    def init_ui(self):
        self.setWindowTitle("Monitor Profile Manager")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Ready", self)
        layout.addWidget(self.status_label)
        
        save_layout = QHBoxLayout()
        self.profile_name_input = QLineEdit(self)
        self.profile_name_input.setPlaceholderText("Enter profile name")
        save_button = QPushButton("Save Profile", self)
        save_button.clicked.connect(self.save_profile)
        save_layout.addWidget(self.profile_name_input)
        save_layout.addWidget(save_button)
        layout.addLayout(save_layout)

        load_button = QPushButton("Load Profile", self)
        load_button.clicked.connect(self.load_profile)
        layout.addWidget(load_button)

        delete_button = QPushButton("Delete Profile", self)
        delete_button.clicked.connect(self.delete_profile)
        layout.addWidget(delete_button)

        hotkey_button = QPushButton("Set Hotkey", self)
        hotkey_button.clicked.connect(self.set_hotkey)
        layout.addWidget(hotkey_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        tray_menu = QMenu(self)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def save_profile(self):
        profile_name = self.profile_name_input.text().strip()
        if not profile_name:
            self.status_label.setText("Status: Enter a profile name.")
            return
        profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.dat")
        command = f"{MULTIMONITOR_TOOL} /SaveConfig \"{profile_path}\""
        if platform.system() == "Windows" and os.path.exists(MULTIMONITOR_TOOL):
            subprocess.run(command, shell=True)
            self.status_label.setText(f"Status: Profile '{profile_name}' saved.")
        else:
            self.status_label.setText("Status: MultiMonitorTool not found.")

    def load_profile(self):
        profile_path, _ = QFileDialog.getOpenFileName(self, "Load Profile", PROFILES_DIR, "Profiles (*.dat)")
        if profile_path:
            command = f"{MULTIMONITOR_TOOL} /LoadConfig \"{profile_path}\""
            print(f"Executing command: {command}")

            if platform.system() == "Windows" and os.path.exists(MULTIMONITOR_TOOL):
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error: {result.stderr}")
                    self.status_label.setText(f"Error loading profile from '{profile_path}'.")
                else:
                    self.status_label.setText(f"Status: Profile loaded from '{profile_path}'.")
            else:
                self.status_label.setText("Status: MultiMonitorTool not found.")

    def delete_profile(self):
        profile_path, _ = QFileDialog.getOpenFileName(self, "Delete Profile", PROFILES_DIR, "Profiles (*.dat)")
        if profile_path and os.path.exists(profile_path):
            os.remove(profile_path)
            self.status_label.setText(f"Status: Profile '{os.path.basename(profile_path)}' deleted.")

    def set_hotkey(self):
        profile_path, _ = QFileDialog.getOpenFileName(self, "Set Hotkey", PROFILES_DIR, "Profiles (*.dat)")
        if not profile_path:
            return
        hotkey = QLineEdit(self)
        hotkey.setPlaceholderText("Press a key combination")
        hotkey_dialog = QVBoxLayout()
        hotkey_dialog.addWidget(hotkey)
        
        def save_hotkey():
            key_combo = hotkey.text()
            if key_combo:
                self.hotkeys[key_combo] = profile_path
                self.save_hotkeys()
                keyboard.add_hotkey(key_combo, lambda: self.load_profile_by_path(profile_path))
                self.status_label.setText(f"Hotkey '{key_combo}' set for profile '{os.path.basename(profile_path)}'.")
        
        hotkey.returnPressed.connect(save_hotkey)

    def load_profile_by_path(self, profile_path):
        if platform.system() == "Windows" and os.path.exists(MULTIMONITOR_TOOL):
            command = f"{MULTIMONITOR_TOOL} /LoadConfig \"{profile_path}\""
            subprocess.run(command, shell=True)
            self.status_label.setText(f"Status: Profile loaded from '{profile_path}'.")
        else:
            self.status_label.setText("Status: MultiMonitorTool not found.")

    def load_hotkeys(self):
        try:
            with open("hotkeys.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_hotkeys(self):
        with open("hotkeys.json", "w") as file:
            json.dump(self.hotkeys, file)

    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = MonitorManager()
    window.show()
    app.exec_()
