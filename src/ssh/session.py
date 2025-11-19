"""SSH Session management with threading for non-blocking I/O"""

import threading
import queue
import logging
from typing import Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal
from .client import SSHClient

logger = logging.getLogger(__name__)


class SSHSession(QObject):
    """Manages SSH session with non-blocking I/O using threading"""
    
    # Signals for GUI thread communication
    data_received = pyqtSignal(str)  # Emitted when data is received from SSH
    session_closed = pyqtSignal(int)  # Emitted when session closes (exit code)
    error_occurred = pyqtSignal(str)  # Emitted when an error occurs
    
    def __init__(self, ssh_client: SSHClient, parent=None):
        """
        Initialize SSH session
        
        Args:
            ssh_client: Connected SSHClient instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self.ssh_client = ssh_client
        self.channel = None
        self._running = False
        self._receive_thread = None
        self._send_queue = queue.Queue()
        self._send_thread = None
        
    def start_session(self, term: str = 'xterm', width: int = 80, height: int = 24):
        """
        Start interactive SSH session
        
        Args:
            term: Terminal type
            width: Terminal width
            height: Terminal height
        """
        if self._running:
            logger.warning("Session already running")
            return
        
        try:
            self.channel = self.ssh_client.invoke_shell(term=term, width=width, height=height)
            self.channel.settimeout(0.1)  # Non-blocking with short timeout
            
            self._running = True
            
            # Start receive thread
            self._receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._receive_thread.start()
            
            # Start send thread
            self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self._send_thread.start()
            
            logger.info("SSH session started")
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            self.error_occurred.emit(str(e))
            raise
    
    def send_data(self, data: bytes):
        """
        Send data to SSH session (thread-safe)
        
        Args:
            data: Data to send (bytes)
        """
        if self._running and self.channel:
            self._send_queue.put(data)
    
    def send_text(self, text: str, encoding: str = 'utf-8'):
        """
        Send text to SSH session
        
        Args:
            text: Text to send
            encoding: Text encoding (default: utf-8)
        """
        self.send_data(text.encode(encoding))
    
    def _receive_loop(self):
        """Receive data from SSH channel in background thread"""
        try:
            while self._running and self.channel:
                if self.channel.recv_ready():
                    try:
                        data = self.channel.recv(4096)
                        if data:
                            # Decode and emit signal (will be handled in GUI thread)
                            text = data.decode('utf-8', errors='replace')
                            self.data_received.emit(text)
                    except Exception as e:
                        logger.warning(f"Error receiving data: {e}")
                        break
                
                # Check if channel is closed
                if self.channel.exit_status_ready():
                    exit_code = self.channel.recv_exit_status()
                    logger.info(f"Session closed with exit code: {exit_code}")
                    self.session_closed.emit(exit_code)
                    break
                    
        except Exception as e:
            logger.error(f"Receive loop error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self._running = False
    
    def _send_loop(self):
        """Send data to SSH channel in background thread"""
        try:
            while self._running and self.channel:
                try:
                    # Get data from queue with timeout
                    data = self._send_queue.get(timeout=0.1)
                    if data and self.channel:
                        self.channel.send(data)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.warning(f"Error sending data: {e}")
                    break
        except Exception as e:
            logger.error(f"Send loop error: {e}")
            self.error_occurred.emit(str(e))
    
    def resize_terminal(self, width: int, height: int):
        """
        Resize terminal window
        
        Args:
            width: New width in characters
            height: New height in characters
        """
        if self.channel and self._running:
            try:
                self.ssh_client.resize_terminal(self.channel, width, height)
            except Exception as e:
                logger.warning(f"Failed to resize terminal: {e}")
    
    def close(self):
        """Close SSH session"""
        self._running = False
        
        # Wait for threads to finish
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=1.0)
        
        if self._send_thread and self._send_thread.is_alive():
            # Put sentinel to wake up send thread
            self._send_queue.put(None)
            self._send_thread.join(timeout=1.0)
        
        # Close channel
        if self.channel:
            try:
                self.channel.close()
            except Exception as e:
                logger.warning(f"Error closing channel: {e}")
        
        logger.info("SSH session closed")
    
    def is_running(self) -> bool:
        """Check if session is running"""
        return self._running

