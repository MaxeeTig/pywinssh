"""Terminal emulator widget for SSH sessions"""

import re
from PyQt5.QtWidgets import QPlainTextEdit, QMenu
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QKeyEvent
from ..utils.clipboard import Clipboard


class TerminalWidget(QPlainTextEdit):
    """Terminal emulator widget with ANSI color support"""
    
    # Signal emitted when user types (for forwarding to SSH)
    data_to_send = pyqtSignal(bytes)
    
    # ANSI color codes mapping
    ANSI_COLORS = {
        '30': QColor(0, 0, 0),      # Black
        '31': QColor(205, 0, 0),    # Red
        '32': QColor(0, 205, 0),    # Green
        '33': QColor(205, 205, 0),  # Yellow
        '34': QColor(0, 0, 238),    # Blue
        '35': QColor(205, 0, 205),  # Magenta
        '36': QColor(0, 205, 205),  # Cyan
        '37': QColor(229, 229, 229), # White
        '90': QColor(127, 127, 127), # Bright Black
        '91': QColor(255, 0, 0),    # Bright Red
        '92': QColor(0, 255, 0),    # Bright Green
        '93': QColor(255, 255, 0),  # Bright Yellow
        '94': QColor(92, 92, 255),  # Bright Blue
        '95': QColor(255, 0, 255),  # Bright Magenta
        '96': QColor(0, 255, 255),  # Bright Cyan
        '97': QColor(255, 255, 255), # Bright White
    }
    
    def __init__(self, parent=None):
        """Initialize terminal widget"""
        super().__init__(parent)
        
        # Set monospace font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        
        # Configure widget
        self.setReadOnly(False)  # Allow input
        self.setUndoRedoEnabled(False)
        self.setMaximumBlockCount(10000)  # Limit history
        
        # Set black background for terminal look
        self.setStyleSheet("QPlainTextEdit { background-color: #000000; color: #e5e5e5; }")
        
        # Terminal state
        self._current_format = QTextCharFormat()
        self._current_format.setForeground(QColor(229, 229, 229))  # Default white text
        self._current_format.setBackground(QColor(0, 0, 0))  # Black background
        
        # Track cursor position for input
        self._input_start_pos = 0
        
    def append_text(self, text: str):
        """
        Append text to terminal with ANSI color support
        
        Args:
            text: Text to append
        """
        # Parse ANSI codes and append formatted text
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        
        # Update input start position (for backspace handling)
        self._input_start_pos = cursor.position()
        
        # Simple ANSI code parser
        parts = self._parse_ansi(text)
        
        for part in parts:
            if isinstance(part, dict):
                # Formatting instruction
                if 'fg' in part:
                    self._current_format.setForeground(part['fg'])
                if 'bg' in part:
                    self._current_format.setBackground(part['bg'])
                if 'reset' in part:
                    self._current_format.setForeground(QColor(229, 229, 229))
                    self._current_format.setBackground(QColor(0, 0, 0))
            else:
                # Text to insert
                cursor.setCharFormat(self._current_format)
                cursor.insertText(part)
                # Update input start position after inserting text
                self._input_start_pos = cursor.position()
        
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def _parse_ansi(self, text: str):
        """
        Parse ANSI escape codes from text
        
        Args:
            text: Text with ANSI codes
            
        Returns:
            List of text parts and formatting instructions
        """
        parts = []
        i = 0
        
        while i < len(text):
            # Check for ANSI escape sequence (\x1b[)
            if text[i] == '\x1b' and i + 1 < len(text) and text[i + 1] == '[':
                # Found ANSI escape sequence
                j = i + 2
                # Find the end of the escape sequence (command character)
                # Common ANSI command characters: m (formatting), H (cursor position), 
                # K (erase), J (erase), A-D (cursor movement), etc.
                while j < len(text) and text[j] not in 'HfABCDEFGHJKSTm@':
                    j += 1
                
                if j < len(text):
                    command = text[j]
                    code_str = text[i + 2:j]
                    
                    if command == 'm':
                        # Color/formatting code
                        codes = code_str.split(';')
                        
                        for code in codes:
                            if code == '0' or code == '':
                                parts.append({'reset': True})
                            elif code in self.ANSI_COLORS:
                                parts.append({'fg': self.ANSI_COLORS[code]})
                            elif code.startswith('3') and len(code) == 2:
                                # Foreground color
                                color_code = code[1]
                                if color_code in self.ANSI_COLORS:
                                    parts.append({'fg': self.ANSI_COLORS[color_code]})
                            elif code.startswith('4') and len(code) == 2:
                                # Background color
                                color_code = code[1]
                                if color_code in self.ANSI_COLORS:
                                    parts.append({'bg': self.ANSI_COLORS[color_code]})
                    # For other ANSI sequences (cursor positioning, clearing, etc.), skip them
                    # They don't produce visible output but are control sequences
                    
                    i = j + 1
                else:
                    # Incomplete escape sequence, skip it
                    i += 1
            # Check for other control characters that shouldn't be displayed
            elif ord(text[i]) < 32 and text[i] not in '\n\r\t':
                # Skip control characters except newline, carriage return, and tab
                i += 1
            else:
                # Regular text
                start = i
                while i < len(text):
                    # Stop at ANSI escape sequence start
                    if text[i] == '\x1b' and i + 1 < len(text) and text[i + 1] == '[':
                        break
                    # Stop at control characters (except newline, carriage return, tab)
                    if ord(text[i]) < 32 and text[i] not in '\n\r\t':
                        break
                    i += 1
                if start < i:
                    parts.append(text[start:i])
                if i < len(text) and ord(text[i]) < 32 and text[i] not in '\n\r\t':
                    # Skip control character
                    i += 1
        
        return parts
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input"""
        # Handle copy-paste shortcuts
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_C:
                # Copy selected text
                self.copy()
                return
            elif event.key() == Qt.Key_V:
                # Paste from clipboard
                self._paste_text()
                return
        
        # Handle Enter key
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Send newline to SSH - server will echo it back
            self.data_to_send.emit(b'\r\n')
            return
        
        # Handle Backspace
        if event.key() == Qt.Key_Backspace:
            # Send backspace to SSH - server will handle the deletion
            self.data_to_send.emit(b'\x08')  # Backspace character
            return
        
        # Handle other special keys
        if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right,
                          Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown):
            # Allow navigation
            super().keyPressEvent(event)
            return
        
        # Send printable characters to SSH
        # Don't insert locally - let the SSH server echo it back
        if event.text():
            # Send to SSH - server will echo it back
            self.data_to_send.emit(event.text().encode('utf-8'))
            return
        
        # Default handling
        super().keyPressEvent(event)
    
    def _paste_text(self):
        """Paste text from clipboard"""
        if Clipboard.has_text():
            text = Clipboard.paste_text()
            # Send to SSH - server will echo it back
            self.data_to_send.emit(text.encode('utf-8'))
    
    def contextMenuEvent(self, event):
        """Show context menu with copy/paste"""
        menu = QMenu(self)
        
        copy_action = menu.addAction("Copy")
        copy_action.setEnabled(self.textCursor().hasSelection())
        copy_action.triggered.connect(self.copy)
        
        paste_action = menu.addAction("Paste")
        paste_action.setEnabled(Clipboard.has_text())
        paste_action.triggered.connect(self._paste_text)
        
        menu.exec_(event.globalPos())
    
    def clear_terminal(self):
        """Clear terminal content"""
        self.clear()
        self._input_start_pos = 0

