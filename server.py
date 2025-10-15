#!/usr/bin/env python3
"""
Incremental search filter server using Windows named pipes.
Receives input filename via pipe, performs incremental search, and sends back selected line.
"""
import argparse
import sys
import win32pipe
import win32file
import pywintypes
import tomli
import os
import json


class IncrementalSearchFilter:
    """Manages the incremental search filtering logic."""
    
    def __init__(self, lines, case_sensitive=False):
        self.original_lines = lines
        self.filtered_lines = lines[:]
        self.selected_index = 0
        self.case_sensitive = case_sensitive
        self.current_pattern = ""
    
    def update_filter(self, pattern):
        """Update the filter pattern and return the currently selected line."""
        self.current_pattern = pattern
        
        if not pattern:
            self.filtered_lines = self.original_lines[:]
            self.selected_index = 0
        else:
            # Perform incremental search
            self.filtered_lines = []
            search_pattern = pattern if self.case_sensitive else pattern.lower()
            
            for line in self.original_lines:
                search_line = line if self.case_sensitive else line.lower()
                if search_pattern in search_line:
                    self.filtered_lines.append(line)
            
            # Reset selection if out of bounds
            if self.selected_index >= len(self.filtered_lines):
                self.selected_index = 0
        
        return self.get_selected_line()
    
    def get_selected_line(self):
        """Get the currently selected line."""
        if self.filtered_lines and 0 <= self.selected_index < len(self.filtered_lines):
            return self.filtered_lines[self.selected_index]
        return ""
    
    def move_selection(self, delta):
        """Move selection up or down."""
        if not self.filtered_lines:
            return self.get_selected_line()
        
        self.selected_index = max(0, min(len(self.filtered_lines) - 1, self.selected_index + delta))
        return self.get_selected_line()


class PipeServer:
    """Windows named pipe server for incremental search."""
    
    def __init__(self, pipe_name, encoding='utf-8', case_sensitive=False):
        self.pipe_name = pipe_name
        self.encoding = encoding
        self.case_sensitive = case_sensitive
        self.filter = None
    
    def load_file(self, filename):
        """Load input file for filtering."""
        try:
            with open(filename, 'r', encoding=self.encoding) as f:
                lines = f.read().splitlines()
            self.filter = IncrementalSearchFilter(lines, self.case_sensitive)
            return True
        except Exception as e:
            print(f"Error loading file {filename}: {e}", file=sys.stderr)
            return False
    
    def handle_client(self, pipe_handle):
        """Handle a single client connection."""
        try:
            # Read input filename
            data = b""
            while True:
                try:
                    result, chunk = win32file.ReadFile(pipe_handle, 4096)
                    data += chunk
                    if result == 0 and len(chunk) < 4096:
                        break
                except pywintypes.error as e:
                    if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                        break
                    raise
            
            if not data:
                return
            
            message = data.decode(self.encoding).strip()
            
            # Parse message
            try:
                msg_obj = json.loads(message)
                msg_type = msg_obj.get('type')
                
                if msg_type == 'init':
                    # Initialize with input filename
                    filename = msg_obj.get('filename')
                    if self.load_file(filename):
                        response = json.dumps({'status': 'ok', 'line': self.filter.get_selected_line()})
                        win32file.WriteFile(pipe_handle, (response + '\n').encode(self.encoding))
                    else:
                        response = json.dumps({'status': 'error', 'message': 'Failed to load file'})
                        win32file.WriteFile(pipe_handle, (response + '\n').encode(self.encoding))
                
                elif msg_type == 'search':
                    # Update search pattern
                    if self.filter:
                        pattern = msg_obj.get('pattern', '')
                        line = self.filter.update_filter(pattern)
                        response = json.dumps({'status': 'ok', 'line': line})
                        win32file.WriteFile(pipe_handle, (response + '\n').encode(self.encoding))
                
                elif msg_type == 'move':
                    # Move selection
                    if self.filter:
                        delta = msg_obj.get('delta', 0)
                        line = self.filter.move_selection(delta)
                        response = json.dumps({'status': 'ok', 'line': line})
                        win32file.WriteFile(pipe_handle, (response + '\n').encode(self.encoding))
                
            except (json.JSONDecodeError, KeyError) as e:
                response = json.dumps({'status': 'error', 'message': f'Invalid message format: {e}'})
                win32file.WriteFile(pipe_handle, (response + '\n').encode(self.encoding))
        
        except Exception as e:
            print(f"Error handling client: {e}", file=sys.stderr)
        finally:
            win32file.CloseHandle(pipe_handle)
    
    def run(self):
        """Run the pipe server."""
        print(f"Starting server on pipe: {self.pipe_name}")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Create named pipe
                pipe_handle = win32pipe.CreateNamedPipe(
                    self.pipe_name,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,  # Max instances
                    65536,  # Out buffer size
                    65536,  # In buffer size
                    0,  # Default timeout
                    None
                )
                
                print(f"Waiting for client connection...")
                
                # Wait for client
                win32pipe.ConnectNamedPipe(pipe_handle, None)
                print("Client connected")
                
                # Handle client
                self.handle_client(pipe_handle)
                print("Client disconnected")
                
            except KeyboardInterrupt:
                print("\nShutting down server...")
                break
            except Exception as e:
                print(f"Server error: {e}", file=sys.stderr)


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
        description="Incremental search filter server using Windows named pipes"
    )
    parser.add_argument(
        '--config-filename',
        required=True,
        help='Path to TOML configuration file'
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config_filename)
    
    pipe_name = config.get('pipe', {}).get('name', '\\\\.\\pipe\\cat_incremental_search_filter')
    encoding = config.get('encoding', {}).get('default', 'utf-8')
    case_sensitive = config.get('search', {}).get('case_sensitive', False)
    
    # Start server
    server = PipeServer(pipe_name, encoding, case_sensitive)
    server.run()


if __name__ == '__main__':
    main()
