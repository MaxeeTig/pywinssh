"""Settings management using QSettings"""

from PyQt5.QtCore import QSettings
from typing import Optional, Dict


class SettingsManager:
    """Manages application settings using QSettings"""
    
    def __init__(self):
        """Initialize settings manager"""
        self.settings = QSettings()
    
    def save_connection_settings(
        self,
        hostname: str,
        port: int,
        username: str,
        key_filename: Optional[str] = None
    ) -> None:
        """
        Save connection settings
        
        Args:
            hostname: Server hostname or IP address
            port: SSH port
            username: Username for authentication
            key_filename: Optional path to private key file
        """
        self.settings.beginGroup("connection")
        self.settings.setValue("hostname", hostname)
        self.settings.setValue("port", port)
        self.settings.setValue("username", username)
        if key_filename:
            self.settings.setValue("key_filename", key_filename)
        else:
            self.settings.remove("key_filename")
        self.settings.endGroup()
        self.settings.sync()
    
    def load_connection_settings(self) -> Optional[Dict[str, any]]:
        """
        Load saved connection settings
        
        Returns:
            Dictionary with connection settings if found, None otherwise
        """
        self.settings.beginGroup("connection")
        
        hostname = self.settings.value("hostname")
        if not hostname:
            self.settings.endGroup()
            return None
        
        port = self.settings.value("port", 22, type=int)
        username = self.settings.value("username")
        key_filename = self.settings.value("key_filename")
        
        self.settings.endGroup()
        
        return {
            "hostname": hostname,
            "port": port,
            "username": username,
            "key_filename": key_filename if key_filename else None
        }
    
    def clear_connection_settings(self) -> None:
        """Clear all saved connection settings"""
        self.settings.beginGroup("connection")
        self.settings.remove("hostname")
        self.settings.remove("port")
        self.settings.remove("username")
        self.settings.remove("key_filename")
        self.settings.endGroup()
        self.settings.sync()

