# Visual Overview

## System Workflow

```
┌───────────────────────────────────────────────────────────────────┐
│                         USER STARTS SYSTEM                        │
└───────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │  Terminal 1          │    │  Terminal 2          │
        │  Start Server        │    │  Start Client        │
        │                      │    │                      │
        │  start_server.bat    │    │  start_client.bat    │
        │  or                  │    │  or                  │
        │  python server.py    │    │  python client.py    │
        └──────────┬───────────┘    └──────────┬───────────┘
                   │                           │
                   │                           │
                   ▼                           ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │  Load config.toml    │    │  Load config.toml    │
        │  - pipe name         │    │  - pipe name         │
        │  - encoding          │    │  - encoding          │
        │  - search settings   │    │  - search settings   │
        └──────────┬───────────┘    └──────────┬───────────┘
                   │                           │
                   │                           │
                   ▼                           ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │  Create Named Pipe   │    │  Open tkinter UI     │
        │  Listen on:          │    │  - Search input      │
        │  \\.\pipe\           │    │  - Window title      │
        │   cat_incremental... │    │                      │
        └──────────┬───────────┘    └──────────┬───────────┘
                   │                           │
                   │◄──────────────────────────┤
                   │    Connect to pipe        │
                   │                           │
                   ├──────────────────────────►│
                   │   Connection established  │
                   │                           │
                   │◄──────────────────────────┤
                   │   {"type":"init",         │
                   │    "filename":"client.py"}│
                   │                           │
                   ▼                           │
        ┌──────────────────────┐              │
        │  Load client.py      │              │
        │  Create SearchFilter │              │
        │  - Read all lines    │              │
        │  - Initialize state  │              │
        └──────────┬───────────┘              │
                   │                           │
                   ├──────────────────────────►│
                   │   {"status":"ok",         │
                   │    "line":"#!/usr/bin..."}│
                   │                           │
                   │                           ▼
                   │              ┌──────────────────────┐
                   │              │  Update window title │
                   │              │  "Test Client -      │
                   │              │   #!/usr/bin/env..." │
                   │              └──────────┬───────────┘
                   │                         │
                   │                         │ User types "import"
                   │                         │
                   │◄────────────────────────┤
                   │   {"type":"search",     │
                   │    "pattern":"import"}  │
                   │                         │
                   ▼                         │
        ┌──────────────────────┐            │
        │  Filter lines with   │            │
        │  pattern "import"    │            │
        │  - Search all lines  │            │
        │  - Find matches      │            │
        │  - Return first one  │            │
        └──────────┬───────────┘            │
                   │                         │
                   ├────────────────────────►│
                   │   {"status":"ok",       │
                   │    "line":"import..."}  │
                   │                         │
                   │                         ▼
                   │              ┌──────────────────────┐
                   │              │  Update window title │
                   │              │  "Test Client -      │
                   │              │   import argparse"   │
                   │              └──────────┬───────────┘
                   │                         │
                   │                         │ User types more...
                   │                         │
                   │          (repeat for each keystroke)
                   │                         │
                   │                         │ User closes window
                   │                         │
                   │◄────────────────────────┤
                   │   Disconnect            │
                   │                         │
                   ▼                         ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │  Close connection    │  │  Cleanup and exit    │
        │  Wait for next       │  │                      │
        │  client...           │  └──────────────────────┘
        └──────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT SIDE                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      client.py                            │  │
│  │                                                           │  │
│  │  ┌──────────────┐         ┌──────────────────────────┐   │  │
│  │  │              │         │                          │   │  │
│  │  │   tkinter    │◄────────┤   TestClient Class       │   │  │
│  │  │   Window     │         │   - pipe_handle          │   │  │
│  │  │              │         │   - send_message()       │   │  │
│  │  │  - Entry     │         │   - on_search_change()   │   │  │
│  │  │  - Title     │         │   - update_title()       │   │  │
│  │  │              │         │                          │   │  │
│  │  └──────┬───────┘         └──────────┬───────────────┘   │  │
│  │         │                            │                   │  │
│  │         │ User types                 │ Send JSON         │  │
│  │         │                            │                   │  │
│  └─────────┼────────────────────────────┼───────────────────┘  │
│            │                            │                      │
└────────────┼────────────────────────────┼──────────────────────┘
             │                            │
             │                            │
        User input                   Named Pipe
                                    \\.\pipe\...
             │                            │
             │                            │
┌────────────┼────────────────────────────┼──────────────────────┐
│            │                            │                      │
│  ┌─────────┼────────────────────────────┼───────────────────┐  │
│  │         │                            │                   │  │
│  │         │                            ▼                   │  │
│  │    ┌────▼─────────┐         ┌────────────────┐          │  │
│  │    │  Display     │         │   PipeServer   │          │  │
│  │    │  Results     │◄────────┤   - listen()   │          │  │
│  │    │              │  JSON   │   - handle()   │          │  │
│  │    └──────────────┘         └───────┬────────┘          │  │
│  │                                     │                   │  │
│  │                                     │                   │  │
│  │                                     ▼                   │  │
│  │                         ┌──────────────────────┐        │  │
│  │                         │ IncrementalSearch    │        │  │
│  │                         │ Filter               │        │  │
│  │                         │ - original_lines     │        │  │
│  │                         │ - filtered_lines     │        │  │
│  │                         │ - selected_index     │        │  │
│  │                         │ - update_filter()    │        │  │
│  │                         │ - move_selection()   │        │  │
│  │                         └──────────┬───────────┘        │  │
│  │                                    │                    │  │
│  │                server.py           │ search_filter.py   │  │
│  └────────────────────────────────────┼────────────────────┘  │
│                                       │                       │
│                         SERVER SIDE   │                       │
└───────────────────────────────────────┼───────────────────────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Input File   │
                                │  (e.g.,       │
                                │   client.py)  │
                                └───────────────┘
```

## Data Flow

```
User Types: "im"
     │
     ▼
┌─────────────────┐
│ tkinter Entry   │
│ on_search_change│
└────────┬────────┘
         │
         ▼
┌────────────────────────────┐
│ TestClient                 │
│ send_message({             │
│   "type": "search",        │
│   "pattern": "im"          │
│ })                         │
└────────┬───────────────────┘
         │
         ▼  Named Pipe
┌────────────────────────────┐
│ PipeServer                 │
│ handle_client()            │
│ - Parse JSON               │
│ - Extract pattern          │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ IncrementalSearchFilter    │
│ update_filter("im")        │
│                            │
│ For each line:             │
│   if "im" in line.lower(): │
│     add to filtered        │
│                            │
│ return filtered[0]         │
└────────┬───────────────────┘
         │
         ▼  "import argparse"
┌────────────────────────────┐
│ PipeServer                 │
│ Return JSON response:      │
│ {                          │
│   "status": "ok",          │
│   "line": "import ..."     │
│ }                          │
└────────┬───────────────────┘
         │
         ▼  Named Pipe
┌────────────────────────────┐
│ TestClient                 │
│ - Receive response         │
│ - Parse JSON               │
│ - Extract line             │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Update window title:       │
│ "Test Client - import ..." │
└────────────────────────────┘
         │
         ▼
    User sees result!
```

## File Dependencies

```
config.toml
    │
    ├─► server.py
    │       │
    │       ├─► search_filter.py
    │       │
    │       └─► win32pipe, win32file
    │           (Windows named pipes)
    │
    └─► client.py
            │
            ├─► tkinter
            │   (GUI)
            │
            └─► win32pipe, win32file
                (Windows named pipes)

test_search.py
    │
    └─► search_filter.py
        (Unit tests)
```

## State Management

```
Server State per Connection:
┌─────────────────────────────┐
│ PipeServer                  │
│  └─► IncrementalSearchFilter│
│       ├─► original_lines []  │ Loaded from file, never changes
│       ├─► filtered_lines []  │ Changes with each search
│       ├─► selected_index: 0  │ Current selection position
│       ├─► case_sensitive     │ Configuration setting
│       └─► current_pattern    │ Last search pattern
└─────────────────────────────┘

Client State:
┌─────────────────────────────┐
│ TestClient                  │
│  ├─► pipe_handle            │ Connection to server
│  ├─► current_line           │ Last received line
│  ├─► root                   │ tkinter window
│  └─► entry                  │ Search input widget
└─────────────────────────────┘
```

## Execution Flow

```
1. Start Server
   ├─► Parse arguments (--config-filename)
   ├─► Load config.toml
   ├─► Create named pipe
   └─► Listen for connections

2. Start Client
   ├─► Parse arguments (--config-filename)
   ├─► Load config.toml
   ├─► Connect to server
   ├─► Send init message
   └─► Show tkinter window

3. User Interaction
   ├─► User types in search box
   ├─► Client sends search message
   ├─► Server filters lines
   ├─► Server returns selected line
   └─► Client updates window title

4. Shutdown
   ├─► User closes client window
   ├─► Client closes pipe
   └─► Server waits for next connection
```
