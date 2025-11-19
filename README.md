# PyWinSSH

Python SSH client for Windows - A GUI-based SSH client built with PyQt5 and Paramiko.

## Features

- **GUI-based Interface**: Modern, user-friendly graphical interface built with PyQt5
- **Interactive Terminal Sessions**: Full PTY support for interactive shell sessions
- **Windows Copy-Paste Support**: Native Windows clipboard integration (Ctrl+C, Ctrl+V, right-click menu)
- **Multiple Authentication Methods**: Support for password and private key authentication
- **ANSI Color Support**: Basic ANSI color code rendering in terminal
- **Non-blocking I/O**: Threaded SSH communication prevents GUI freezing
- **Connection Management**: Easy connection dialog with validation
- **Standalone Application**: Self-contained Windows application

## Requirements

- Python 3.7 or higher
- Windows 10/11
- PyQt5
- Paramiko

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd pywinssh
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Run the application from the project root:

```bash
python -m src.main
```

Or if you have a proper package installation:

```bash
python src/main.py
```

### Connecting to an SSH Server

1. Click the **"Connect"** button in the toolbar or go to **File > Connect**
2. Fill in the connection dialog:
   - **Hostname**: Server hostname or IP address (e.g., `example.com` or `192.168.1.100`)
   - **Port**: SSH port (default: 22)
   - **Username**: Your SSH username
   - **Password**: Your SSH password (or leave empty if using private key)
   - **Private Key**: Optional path to private key file (for key-based authentication)
3. Click **OK** to connect

### Using the Terminal

- **Type commands**: Simply type in the terminal and press Enter
- **Copy text**: Select text and press Ctrl+C, or right-click and select "Copy"
- **Paste text**: Press Ctrl+V, or right-click and select "Paste"
- **Clear terminal**: Press Ctrl+L or go to Edit > Clear Terminal
- **Disconnect**: Click "Disconnect" button or go to File > Disconnect

### Keyboard Shortcuts

- `Ctrl+N` or `Ctrl+O`: Connect to SSH server
- `Ctrl+D`: Disconnect from SSH server
- `Ctrl+C`: Copy selected text
- `Ctrl+V`: Paste from clipboard
- `Ctrl+L`: Clear terminal
- `Alt+F4` or `Ctrl+Q`: Exit application

## Project Structure

```
pywinssh/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py     # Main application window
│   │   ├── connection_dialog.py # Connection settings dialog
│   │   └── terminal_widget.py  # Terminal emulator widget
│   ├── ssh/
│   │   ├── __init__.py
│   │   ├── client.py          # Paramiko SSH client wrapper
│   │   └── session.py         # SSH session management
│   └── utils/
│       ├── __init__.py
│       └── clipboard.py       # Windows clipboard utilities
├── requirements.txt
├── README.md
└── LICENSE
```

## Technical Details

### Architecture

- **GUI Framework**: PyQt5 for cross-platform GUI with native Windows look and feel
- **SSH Library**: Paramiko for SSH protocol implementation
- **Threading**: Separate threads for SSH I/O to prevent GUI blocking
- **Signals/Slots**: PyQt5 signals for thread-safe GUI updates

### Components

- **SSHClient**: Wrapper around Paramiko's SSHClient with simplified API
- **SSHSession**: Manages SSH channel lifecycle with threaded I/O
- **TerminalWidget**: Custom QPlainTextEdit with ANSI color support and keyboard handling
- **ConnectionDialog**: Modal dialog for SSH connection parameters
- **MainWindow**: Main application window with menus, toolbar, and terminal integration

## Limitations

- Basic ANSI color support (not all ANSI codes are fully supported)
- Terminal resizing not yet implemented
- No session history or saved connections (planned for future versions)
- No SFTP file transfer (terminal sessions only)

## Troubleshooting

### Connection Issues

- **Authentication failed**: Verify your username and password/key file are correct
- **Connection timeout**: Check if the hostname/IP and port are correct, and ensure the server is reachable
- **Host key verification**: The application uses AutoAddPolicy for host keys (less secure but convenient)

### Application Issues

- **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
- **GUI not displaying**: Check that PyQt5 is properly installed
- **Terminal not responding**: Check the status bar for connection status

## Development

### Running from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.main
```

### Building Standalone Executable

To create a standalone Windows executable, you can use PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name pywinssh src/main.py
```

## License

Apache License 2.0 - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- Built with [Paramiko](https://www.paramiko.org/) - Python SSH library
- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Python bindings for Qt
