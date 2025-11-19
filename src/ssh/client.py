"""SSH Client wrapper using Paramiko"""

import paramiko
import socket
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SSHClient:
    """Wrapper around Paramiko SSHClient for easier usage"""
    
    def __init__(self):
        """Initialize SSH client"""
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connected = False
        self._hostname = None
        self._port = 22
        self._username = None
    
    def connect(
        self,
        hostname: str,
        port: int = 22,
        username: str = None,
        password: str = None,
        key_filename: Optional[str] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        Connect to SSH server
        
        Args:
            hostname: Server hostname or IP address
            port: SSH port (default: 22)
            username: Username for authentication
            password: Password for authentication (if using password auth)
            key_filename: Path to private key file (if using key auth)
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            connect_params = {
                'hostname': hostname,
                'port': port,
                'timeout': timeout,
            }
            
            if username:
                connect_params['username'] = username
            
            if password:
                connect_params['password'] = password
            
            if key_filename:
                connect_params['key_filename'] = key_filename
                connect_params['look_for_keys'] = False
                connect_params['allow_agent'] = False
            
            self.client.connect(**connect_params)
            
            self._connected = True
            self._hostname = hostname
            self._port = port
            self._username = username
            
            logger.info(f"Connected to {hostname}:{port} as {username}")
            return True
            
        except paramiko.AuthenticationException as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except paramiko.SSHException as e:
            logger.error(f"SSH error: {e}")
            raise
        except socket.error as e:
            logger.error(f"Socket error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def invoke_shell(
        self,
        term: str = 'xterm',
        width: int = 80,
        height: int = 24
    ) -> paramiko.Channel:
        """
        Invoke an interactive shell session with PTY
        
        Args:
            term: Terminal type (default: 'xterm')
            width: Terminal width in characters
            height: Terminal height in characters
            
        Returns:
            SSH channel for the shell session
        """
        if not self._connected:
            raise RuntimeError("Not connected to SSH server")
        
        try:
            channel = self.client.invoke_shell(term=term, width=width, height=height)
            logger.info(f"Shell session started: {term} {width}x{height}")
            return channel
        except Exception as e:
            logger.error(f"Failed to invoke shell: {e}")
            raise
    
    def exec_command(self, command: str) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        """
        Execute a command on the remote server
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (stdin, stdout, stderr) file-like objects
        """
        if not self._connected:
            raise RuntimeError("Not connected to SSH server")
        
        return self.client.exec_command(command)
    
    def resize_terminal(self, channel: paramiko.Channel, width: int, height: int):
        """
        Resize terminal window
        
        Args:
            channel: SSH channel
            width: New width in characters
            height: New height in characters
        """
        try:
            channel.resize_pty(width=width, height=height)
            logger.debug(f"Terminal resized to {width}x{height}")
        except Exception as e:
            logger.warning(f"Failed to resize terminal: {e}")
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    def get_transport(self) -> Optional[paramiko.Transport]:
        """Get the underlying transport object"""
        if self._connected:
            return self.client.get_transport()
        return None
    
    def close(self):
        """Close SSH connection"""
        if self._connected:
            try:
                self.client.close()
                logger.info("SSH connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connected = False
                self._hostname = None
                self._username = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

