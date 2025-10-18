#!/usr/bin/env python3
"""
Test client for incremental search filter server.
Connects to server via named pipe and displays filtered results in tkinter window.
"""
import argparse
import sys
import tkinter as tk
import win32file
import win32pipe
import pywintypes
import tomli
import json
import os
import threading


class TestClient:
    """Test client with minimal tkinter UI."""
    
    def __init__(self, pipe_name, source_filename, encoding='utf-8'):
        self.pipe_name = pipe_name
        self.source_filename = source_filename
        self.encoding = encoding
        self.pipe_handle = None
        self.root = None
        self.entry = None
        self.current_line = ""
        
    def connect(self):
        """Connect to the named pipe server."""
        try:
            print(f"Connecting to pipe: {self.pipe_name}")
            self.pipe_handle = win32file.CreateFile(
                self.pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            
            # Set pipe to message mode
            win32pipe.SetNamedPipeHandleState(
                self.pipe_handle,
                win32pipe.PIPE_READMODE_MESSAGE,
                None,
                None
            )
            
            print("Connected to server")
            return True
        except pywintypes.error as e:
            print(f"Failed to connect to server: {e}", file=sys.stderr)
            return False
    
    def send_message(self, msg_obj):
        """Send a message to the server and receive response."""
        try:
            message = json.dumps(msg_obj) + '\n'
            win32file.WriteFile(self.pipe_handle, message.encode(self.encoding))
            
            # Read response
            result, data = win32file.ReadFile(self.pipe_handle, 65536)
            response = json.loads(data.decode(self.encoding).strip())
            return response
        except Exception as e:
            print(f"Error communicating with server: {e}", file=sys.stderr)
            return None
    
    def init_server(self):
        """Initialize server with source filename."""
        response = self.send_message({
            'type': 'init',
            'filename': self.source_filename
        })
        if response and response.get('status') == 'ok':
            self.current_line = response.get('line', '')
            return True
        return False
    
    def on_search_change(self, event=None):
        """Handle search input changes."""
        pattern = self.entry.get()
        response = self.send_message({
            'type': 'search',
            'pattern': pattern
        })
        if response and response.get('status') == 'ok':
            self.current_line = response.get('line', '')
            self.update_title()
    
    def update_title(self):
        """Update window title with current line."""
        if self.root:
            self.root.title(f"Test Client - {self.current_line}")
    
    def run(self):
        """Run the test client UI."""
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.title("Test Client - Connecting...")
        self.root.geometry("400x100")
        
        # Create UI elements
        tk.Label(self.root, text="Search:").pack(pady=10)
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)
        self.entry.focus_set()
        
        # Bind search event
        self.entry.bind('<KeyRelease>', self.on_search_change)
        
        # Initialize server in background thread
        def init_thread():
            if self.init_server():
                self.root.after(0, self.update_title)
            else:
                self.root.after(0, lambda: self.root.title("Test Client - Connection Failed"))
        
        threading.Thread(target=init_thread, daemon=True).start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Run UI
        self.root.mainloop()
    
    def on_close(self):
        """Clean up on window close."""
        if self.pipe_handle:
            try:
                win32file.CloseHandle(self.pipe_handle)
            except:
                pass
        if self.root:
            self.root.destroy()


def load_config(config_filename):
    """Load configuration from TOML file."""
    try:
        with open(config_filename, 'rb') as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Test client for incremental search filter server"
    )
    parser.add_argument(
        '--config-filename',
        default='config.toml',
        help='Path to TOML configuration file'
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config_filename)
    
    pipe_name = config.get('pipe', {}).get('name', '\\\\.\\pipe\\cat_incremental_search_filter')
    encoding = config.get('encoding', {}).get('default', 'utf-8')
    
    # Get source filename (this client's source file)
    source_filename = os.path.abspath(__file__)
    
    # Create and run client
    client = TestClient(pipe_name, source_filename, encoding)
    
    if not client.connect():
        print("Failed to connect to server. Make sure the server is running.", file=sys.stderr)
        sys.exit(1)
    
    client.run()


if __name__ == '__main__':
    main()
