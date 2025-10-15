# Architecture

## Overview

This project implements a client-server architecture using Windows named pipes for incremental search filtering.

```
┌─────────────────┐                    ┌─────────────────┐
│                 │                    │                 │
│  Test Client    │◄──Named Pipe──────►│    Server       │
│  (client.py)    │                    │  (server.py)    │
│                 │                    │                 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │                                      │
    ┌────▼─────┐                           ┌───▼────┐
    │          │                           │        │
    │ tkinter  │                           │ Search │
    │    UI    │                           │ Filter │
    │          │                           │ Logic  │
    └──────────┘                           └────────┘
                                                │
                                           ┌────▼────┐
                                           │         │
                                           │  Input  │
                                           │  File   │
                                           │         │
                                           └─────────┘
```

## Components

### 1. Server (server.py)

**Responsibilities:**
- Listen on Windows named pipe
- Accept client connections
- Load input files
- Perform incremental search filtering
- Send filtered results back to clients

**Key Features:**
- Stateful: maintains current filter state per connection
- Handles multiple message types: init, search, move
- Configurable via TOML

**Message Flow:**
1. Client connects to pipe
2. Client sends init message with filename
3. Server loads file and returns first line
4. Client sends search messages as user types
5. Server filters and returns selected line
6. Connection closes when client exits

### 2. Test Client (client.py)

**Responsibilities:**
- Connect to server via named pipe
- Send input filename (itself by default)
- Provide UI for search input
- Display filtered results

**Key Features:**
- Minimal tkinter UI
- Real-time search as user types
- Displays selected line in window title
- Sends search patterns to server
- Receives and displays results

### 3. Search Filter Logic (search_filter.py)

**Responsibilities:**
- Manage line filtering
- Handle pattern matching
- Track selection state
- Support case-sensitive/insensitive search

**Key Features:**
- Platform-independent
- Unit tested
- Efficient incremental filtering
- Selection management with bounds checking

## Communication Protocol

### JSON Message Format

All messages are JSON objects sent as newline-terminated strings.

#### Message Types

**1. Initialize**
```json
{
  "type": "init",
  "filename": "/path/to/file.txt"
}
```
Response:
```json
{
  "status": "ok",
  "line": "first line of file"
}
```

**2. Search**
```json
{
  "type": "search",
  "pattern": "search text"
}
```
Response:
```json
{
  "status": "ok",
  "line": "matching line"
}
```

**3. Move Selection**
```json
{
  "type": "move",
  "delta": 1  // positive = down, negative = up
}
```
Response:
```json
{
  "status": "ok",
  "line": "newly selected line"
}
```

**Error Response**
```json
{
  "status": "error",
  "message": "error description"
}
```

## Configuration

Configuration is stored in TOML format:

```toml
[pipe]
name = "\\\\.\\pipe\\cat_incremental_search_filter"

[encoding]
default = "utf-8"

[search]
case_sensitive = false
```

## Data Flow

### Initialization Sequence

```
Client                          Server
  |                              |
  |------- Connect to pipe ----->|
  |                              |
  |-- {"type":"init","file":...}>|
  |                              |-- Load file
  |                              |-- Create filter
  |                              |
  |<-- {"status":"ok","line":...}-|
  |                              |
  |-- Display in UI              |
```

### Search Sequence

```
Client                          Server
  |                              |
  | User types 'a'               |
  |-- {"type":"search","pat":"a"}>|
  |                              |-- Filter lines
  |                              |-- Get selected
  |                              |
  |<-- {"status":"ok","line":...}-|
  |                              |
  |-- Update window title        |
  |                              |
  | User types 'p' ('ap' total)  |
  |-- {"type":"search","pat":"ap"}>|
  |                              |-- Filter lines
  |                              |-- Get selected
  |                              |
  |<-- {"status":"ok","line":...}-|
  |                              |
  |-- Update window title        |
```

## Windows Named Pipes

### Pipe Naming Convention

Windows named pipes use the format: `\\.\pipe\<name>`

- `\\.` refers to the local computer
- `pipe` is the named pipe namespace
- `<name>` is the pipe identifier

### Example

Default pipe name: `\\.\pipe\cat_incremental_search_filter`

### Characteristics

- **Local only**: Named pipes in this implementation are local to the machine
- **Duplex**: Two-way communication
- **Message mode**: Messages are discrete units
- **Synchronous**: Server waits for client connections

## Threading Model

### Server

- Single-threaded
- Handles one client at a time
- Blocks waiting for connections
- Synchronous message handling

### Client

- Main thread: UI event loop (tkinter)
- Background thread: Initial server communication
- UI updates queued to main thread via `root.after()`

## Error Handling

### Server-side

- File loading errors → error response to client
- Invalid JSON → error response
- Pipe errors → log to stderr, continue
- Keyboard interrupt → graceful shutdown

### Client-side

- Connection failure → error message, exit
- Communication error → log to stderr
- Window close → cleanup, close pipe

## Testing

### Unit Tests (test_search.py)

Tests the core search filter logic:
- Case-sensitive/insensitive search
- Incremental filtering
- Selection movement
- Boundary conditions
- Empty input handling

### Manual Testing

1. Start server
2. Start client
3. Type in search field
4. Verify window title updates
5. Test with different files
6. Test edge cases

## Extension Points

### Custom Clients

You can create custom clients by:
1. Connecting to the named pipe
2. Sending JSON messages
3. Processing responses
4. Implementing your own UI

### Custom Search Logic

Extend `IncrementalSearchFilter`:
- Add regex support
- Add fuzzy matching
- Add multi-pattern AND/OR
- Add highlighting

### Multiple Clients

Modify server to:
- Accept multiple connections
- Use threading or async I/O
- Maintain separate state per client

## Performance Considerations

### File Size

- Current implementation loads entire file into memory
- Suitable for files up to several MB
- For larger files, consider pagination

### Search Speed

- O(n) search where n = number of lines
- Fast enough for files with thousands of lines
- For millions of lines, consider indexing

### Pipe Throughput

- Message-based communication
- One request → one response
- Minimal latency for typical use cases
- No batching currently implemented
