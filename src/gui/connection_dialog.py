"""Connection dialog for SSH settings"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QCheckBox,
    QLabel, QFileDialog, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from ..utils.settings import SettingsManager


class ConnectionDialog(QDialog):
    """Dialog for SSH connection settings"""
    
    def __init__(self, parent=None):
        """Initialize connection dialog"""
        super().__init__(parent)
        self.setWindowTitle("SSH Connection")
        self.setModal(True)
        self.resize(400, 250)
        
        # Connection parameters
        self.hostname = None
        self.port = 22
        self.username = None
        self.password = None
        self.key_filename = None
        self.save_settings = False
        
        # Settings manager
        self.settings_manager = SettingsManager()
        
        self._setup_ui()
        self._load_saved_settings()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        
        # Hostname
        self.hostname_edit = QLineEdit()
        self.hostname_edit.setPlaceholderText("example.com or 192.168.1.100")
        form_layout.addRow("Hostname:", self.hostname_edit)
        
        # Port
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setMinimum(1)
        self.port_spinbox.setMaximum(65535)
        self.port_spinbox.setValue(22)
        form_layout.addRow("Port:", self.port_spinbox)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("username")
        form_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("password")
        form_layout.addRow("Password:", self.password_edit)
        
        # Private key file
        key_layout = QHBoxLayout()
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Optional: path to private key file")
        self.key_edit.setReadOnly(True)
        key_browse_btn = QPushButton("Browse...")
        key_browse_btn.clicked.connect(self._browse_key_file)
        key_layout.addWidget(self.key_edit)
        key_layout.addWidget(key_browse_btn)
        form_layout.addRow("Private Key:", key_layout)
        
        # Save settings checkbox
        self.save_checkbox = QCheckBox("Save connection settings")
        form_layout.addRow("", self.save_checkbox)
        
        layout.addLayout(form_layout)
        
        # Info label
        info_label = QLabel("Note: Either password or private key is required")
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _browse_key_file(self):
        """Browse for private key file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Private Key File",
            "",
            "All Files (*);;RSA Key (*);;Ed25519 Key (*)"
        )
        if filename:
            self.key_edit.setText(filename)
    
    def _load_saved_settings(self):
        """Load saved connection settings and populate form fields"""
        saved_settings = self.settings_manager.load_connection_settings()
        if saved_settings:
            self.hostname_edit.setText(saved_settings.get("hostname", ""))
            self.port_spinbox.setValue(saved_settings.get("port", 22))
            self.username_edit.setText(saved_settings.get("username", ""))
            key_filename = saved_settings.get("key_filename")
            if key_filename:
                self.key_edit.setText(key_filename)
            # Check the save checkbox if settings were loaded
            self.save_checkbox.setChecked(True)
    
    def _validate_and_accept(self):
        """Validate inputs and accept dialog"""
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        key_filename = self.key_edit.text().strip()
        
        # Validation
        if not hostname:
            QMessageBox.warning(self, "Validation Error", "Hostname is required")
            return
        
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return
        
        if not password and not key_filename:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Either password or private key file is required"
            )
            return
        
        # Store values
        self.hostname = hostname
        self.port = self.port_spinbox.value()
        self.username = username
        self.password = password if password else None
        self.key_filename = key_filename if key_filename else None
        self.save_settings = self.save_checkbox.isChecked()
        
        # Save or clear settings based on checkbox state
        if self.save_settings:
            self.settings_manager.save_connection_settings(
                hostname=hostname,
                port=self.port,
                username=username,
                key_filename=key_filename if key_filename else None
            )
        else:
            self.settings_manager.clear_connection_settings()
        
        self.accept()
    
    def get_connection_params(self):
        """
        Get connection parameters as dictionary
        
        Returns:
            Dictionary with connection parameters
        """
        return {
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'key_filename': self.key_filename,
        }

