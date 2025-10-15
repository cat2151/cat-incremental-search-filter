# cat-incremental-search-filter

Windows named pipe based incremental search filter server and client.

## Features

- **Server**: Resident process that provides incremental search filtering via Windows named pipes
- **Client**: Test client with minimal tkinter UI for testing the server
- **Configuration**: TOML-based configuration for pipe name and encoding settings

## Requirements

- Python 3.7+
- Windows (uses Windows named pipes)
- Dependencies listed in `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.toml` to configure the server:

```toml
[pipe]
name = "\\\\.\\pipe\\cat_incremental_search_filter"

[encoding]
default = "utf-8"

[search]
case_sensitive = false
```

## Usage

### Server

Start the server:

```bash
python server.py --config-filename config.toml
```

The server will:
1. Listen on the configured named pipe
2. Accept connections from clients
3. Receive an input filename
4. Perform incremental search filtering as the user types
5. Send back the currently selected line after each keystroke

### Test Client

Start the test client (in a separate terminal):

```bash
python client.py --config-filename config.toml
```

The client will:
1. Connect to the server via named pipe
2. Send its own source filename to the server
3. Display a search input field
4. Update the window title with the currently selected line as you type

## Protocol

The server and client communicate via JSON messages:

### Initialize
```json
{"type": "init", "filename": "path/to/file.txt"}
```
Response:
```json
{"status": "ok", "line": "first line"}
```

### Search
```json
{"type": "search", "pattern": "search text"}
```
Response:
```json
{"status": "ok", "line": "matched line"}
```

### Move Selection
```json
{"type": "move", "delta": 1}
```
Response:
```json
{"status": "ok", "line": "new selected line"}
```

## License

MIT License - See LICENSE file for details