"""Main application window"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QMenu,
    QToolBar, QAction, QStatusBar, QMessageBox, QApplication, QDialog
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from .terminal_widget import TerminalWidget
from .connection_dialog import ConnectionDialog
from ..ssh.client import SSHClient
from ..ssh.session import SSHSession

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, parent=None):
        """Initialize main window"""
        super().__init__(parent)
        self.setWindowTitle("PyWinSSH - SSH Client")
        self.resize(800, 600)
        
        # SSH components
        self.ssh_client = None
        self.ssh_session = None
        
        # UI components
        self.terminal_widget = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
    
    def _setup_ui(self):
        """Setup main UI"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create terminal widget
        self.terminal_widget = TerminalWidget()
        self.terminal_widget.data_to_send.connect(self._on_terminal_data)
        layout.addWidget(self.terminal_widget)
        
        # Show welcome message
        self.terminal_widget.append_text("PyWinSSH - SSH Client for Windows\n")
        self.terminal_widget.append_text("Click 'Connect' to start a new SSH session.\n\n")
    
    def _setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        connect_action = QAction("&Connect...", self)
        connect_action.setShortcut(QKeySequence.New)
        connect_action.triggered.connect(self._connect_ssh)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.setShortcut(QKeySequence("Ctrl+D"))
        disconnect_action.triggered.connect(self._disconnect_ssh)
        disconnect_action.setEnabled(False)
        self.disconnect_action = disconnect_action
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("&Clear Terminal", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self._clear_terminal)
        edit_menu.addAction(clear_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        connect_action = QAction("Connect", self)
        connect_action.setToolTip("Connect to SSH server")
        connect_action.triggered.connect(self._connect_ssh)
        toolbar.addAction(connect_action)
        self.toolbar_connect_action = connect_action
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.setToolTip("Disconnect from SSH server")
        disconnect_action.triggered.connect(self._disconnect_ssh)
        disconnect_action.setEnabled(False)
        toolbar.addAction(disconnect_action)
        self.toolbar_disconnect_action = disconnect_action
    
    def _setup_statusbar(self):
        """Setup status bar"""
        self.statusBar().showMessage("Ready - Not connected")
    
    @pyqtSlot()
    def _connect_ssh(self):
        """Open connection dialog and connect to SSH server"""
        dialog = ConnectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._establish_connection(dialog.get_connection_params())
    
    def _establish_connection(self, params: dict):
        """Establish SSH connection"""
        try:
            self.statusBar().showMessage("Connecting...")
            QApplication.processEvents()
            
            # Create SSH client
            self.ssh_client = SSHClient()
            
            # Connect
            self.ssh_client.connect(**params)
            
            # Create session
            self.ssh_session = SSHSession(self.ssh_client, self)
            self.ssh_session.data_received.connect(self._on_ssh_data)
            self.ssh_session.session_closed.connect(self._on_session_closed)
            self.ssh_session.error_occurred.connect(self._on_ssh_error)
            
            # Start session
            self.ssh_session.start_session()
            
            # Update UI
            self.disconnect_action.setEnabled(True)
            self.toolbar_disconnect_action.setEnabled(True)
            self.toolbar_connect_action.setEnabled(False)
            
            self.statusBar().showMessage(
                f"Connected to {params['hostname']}:{params['port']} as {params['username']}"
            )
            
            # Clear terminal and show connection message
            self.terminal_widget.clear_terminal()
            self.terminal_widget.append_text(
                f"Connected to {params['hostname']}:{params['port']}\n"
            )
            self.terminal_widget.append_text("=" * 50 + "\n\n")
            
            logger.info(f"Successfully connected to {params['hostname']}")
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Connection Error", error_msg)
            self.statusBar().showMessage("Connection failed")
            
            # Cleanup
            if self.ssh_session:
                self.ssh_session.close()
                self.ssh_session = None
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
    
    @pyqtSlot()
    def _disconnect_ssh(self):
        """Disconnect from SSH server"""
        if self.ssh_session:
            self.ssh_session.close()
            self.ssh_session = None
        
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        
        # Update UI
        self.disconnect_action.setEnabled(False)
        self.toolbar_disconnect_action.setEnabled(False)
        self.toolbar_connect_action.setEnabled(True)
        
        self.statusBar().showMessage("Disconnected")
        
        # Show disconnect message
        self.terminal_widget.append_text("\n" + "=" * 50 + "\n")
        self.terminal_widget.append_text("Disconnected from SSH server\n\n")
    
    @pyqtSlot(str)
    def _on_ssh_data(self, data: str):
        """Handle data received from SSH"""
        self.terminal_widget.append_text(data)
    
    @pyqtSlot(int)
    def _on_session_closed(self, exit_code: int):
        """Handle SSH session closure"""
        self.terminal_widget.append_text(f"\n\nSession closed with exit code: {exit_code}\n")
        self._disconnect_ssh()
    
    @pyqtSlot(str)
    def _on_ssh_error(self, error: str):
        """Handle SSH error"""
        QMessageBox.warning(self, "SSH Error", f"SSH error occurred: {error}")
        self._disconnect_ssh()
    
    @pyqtSlot(bytes)
    def _on_terminal_data(self, data: bytes):
        """Handle data to send to SSH"""
        if self.ssh_session and self.ssh_session.is_running():
            self.ssh_session.send_data(data)
    
    @pyqtSlot()
    def _clear_terminal(self):
        """Clear terminal content"""
        self.terminal_widget.clear_terminal()
    
    @pyqtSlot()
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About PyWinSSH",
            "PyWinSSH - Python SSH Client for Windows\n\n"
            "A GUI-based SSH client built with PyQt5 and Paramiko.\n\n"
            "Version 0.1.0"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.ssh_session or self.ssh_client:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "You have an active SSH connection. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._disconnect_ssh()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

