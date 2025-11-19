"""Clipboard utilities for Windows copy-paste support"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData


class Clipboard:
    """Wrapper for clipboard operations using PyQt5"""
    
    @staticmethod
    def get_clipboard():
        """Get QClipboard instance"""
        return QApplication.clipboard()
    
    @staticmethod
    def copy_text(text: str):
        """
        Copy text to clipboard
        
        Args:
            text: Text to copy
        """
        clipboard = Clipboard.get_clipboard()
        clipboard.setText(text)
    
    @staticmethod
    def paste_text() -> str:
        """
        Get text from clipboard
        
        Returns:
            Text from clipboard, empty string if no text available
        """
        clipboard = Clipboard.get_clipboard()
        return clipboard.text()
    
    @staticmethod
    def has_text() -> bool:
        """
        Check if clipboard contains text
        
        Returns:
            True if clipboard has text, False otherwise
        """
        clipboard = Clipboard.get_clipboard()
        mime_data = clipboard.mimeData()
        return mime_data.hasText()

