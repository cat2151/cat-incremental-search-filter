# Getting Started

This guide will help you get up and running with cat-incremental-search-filter in 5 minutes.

## Prerequisites

- Windows operating system
- Python 3.7 or higher
- pip (Python package installer)

## Step 1: Install Dependencies

Open Command Prompt or PowerShell and run:

```bash
pip install -r requirements.txt
```

This installs:
- `pywin32` - Windows API support for named pipes
- `tomli` - TOML configuration file parser

## Step 2: Verify Installation

Check that the server can start:

```bash
python src/server.py --config-filename config.toml
```

You should see:
```
Starting server on pipe: \\.\pipe\cat_incremental_search_filter
Press Ctrl+C to stop
Waiting for client connection...
```

Press `Ctrl+C` to stop the server.

## Step 3: Start the System

### Option A: Using Batch Files (Recommended)

1. Double-click `start_server.bat`
   - A command window opens showing "Waiting for client connection..."

2. Double-click `start_client.bat`
   - A tkinter window opens with a search input field
   - The server window shows "Client connected"

### Option B: Using Command Line

**Terminal 1 (Server):**
```bash
python src/server.py --config-filename config.toml
```

**Terminal 2 (Client):**
```bash
python src/client.py --config-filename config.toml
```

## Step 4: Try It Out

1. In the client window, you'll see:
   - A search input box
   - The window title showing the first line of client.py

2. Type in the search box:
   - Type `import` → See import statements
   - Type `def` → See function definitions
   - Type `class` → See class definitions

3. The window title updates in real-time showing the first matching line!

## Example Session

```
1. Start server
   → Server: "Waiting for client connection..."

2. Start client
   → Server: "Client connected"
   → Client window opens
   → Title: "Test Client - #!/usr/bin/env python3"

3. Type "import" in search box
   → Title updates: "Test Client - import argparse"

4. Type "import tk" in search box
   → Title updates: "Test Client - import tkinter as tk"

5. Clear search box
   → Title updates: "Test Client - #!/usr/bin/env python3"

6. Close client window
   → Server: "Client disconnected"
   → Server: "Waiting for client connection..."
```

## Common Issues

### Issue: "No module named 'win32pipe'"

**Solution:** Install pywin32
```bash
pip install pywin32
```

### Issue: "FileNotFoundError: config.toml"

**Solution:** Make sure you're in the correct directory
```bash
cd path\to\cat-incremental-search-filter
```

### Issue: Client can't connect

**Solution:** Make sure server is running first
1. Start the server
2. Wait for "Waiting for client connection..."
3. Then start the client

### Issue: "Access denied" when starting server

**Solution:** The pipe might be in use
1. Close any running instances
2. Wait a few seconds
3. Try again

## Next Steps

### Customize Configuration

Edit `config.toml`:

```toml
[pipe]
# Change pipe name
name = "\\\\.\\pipe\\my_custom_filter"

[encoding]
# Change file encoding
default = "utf-8"  # or "cp932", "shift_jis", etc.

[search]
# Enable case-sensitive search
case_sensitive = true  # default: false
```

### Test with Your Own Files

Modify `client.py` to use a different file:

```python
# Around line 175, change:
source_filename = os.path.abspath(__file__)

# To:
source_filename = os.path.abspath('your_file.txt')
```

Or try with the example data:

```python
source_filename = os.path.abspath('example_data.txt')
```

### Run Tests

Verify everything works:

```bash
python test_search.py -v
```

You should see:
```
test_case_insensitive_search ... ok
test_case_sensitive_search ... ok
...
----------------------------------------------------------------------
Ran 11 tests in 0.001s

OK
```

## Learn More

- **README.md** - Full documentation
- **ARCHITECTURE.md** - How it works
- **EXAMPLES.md** - More usage examples
- **QUICKREF.md** - Quick reference
- **VISUAL.md** - Visual diagrams

## Getting Help

If you encounter issues:

1. Check the documentation files
2. Verify Python version: `python --version` (should be 3.7+)
3. Verify dependencies: `pip list | findstr "pywin32 tomli"`
4. Check the error messages carefully

## What's Next?

Once you're comfortable with the basics:

1. Try different search patterns
2. Test with larger files
3. Experiment with case-sensitive search
4. Create your own client implementation
5. Extend the search logic with regex support

Happy searching! 🔍
