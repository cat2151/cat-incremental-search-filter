# Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Start Server

Windows batch file:
```cmd
start_server.bat
```

Or manually:
```bash
python src/server.py --config-filename config.toml
```

## Start Test Client

Windows batch file:
```cmd
start_client.bat
```

Or manually:
```bash
python src/client.py --config-filename config.toml
```

## Run Tests

```bash
python tests/test_search.py
```

Or with verbose output:
```bash
python tests/test_search.py -v
```

## Configuration File

Default location: `config.toml`

```toml
[pipe]
name = "\\\\.\\pipe\\cat_incremental_search_filter"

[encoding]
default = "utf-8"

[search]
case_sensitive = false
```

## Key Files

| File | Purpose |
|------|---------|
| `src/server.py` | Named pipe server for incremental search |
| `src/client.py` | Test client with tkinter UI |
| `src/search_filter.py` | Core search filter logic (platform-independent) |
| `tests/test_search.py` | Unit tests for search logic |
| `config.toml` | Configuration file |
| `requirements.txt` | Python dependencies |
| `README.md` | Main documentation |
| `ARCHITECTURE.md` | Architecture and design documentation |
| `EXAMPLES.md` | Usage examples |
| `example_data.txt` | Sample data for testing |

## Common Tasks

### Change Pipe Name

Edit `config.toml`:
```toml
[pipe]
name = "\\\\.\\pipe\\my_custom_name"
```

Restart both server and client.

### Enable Case-Sensitive Search

Edit `config.toml`:
```toml
[search]
case_sensitive = true
```

Restart server.

### Test with Custom File

Modify `src/client.py` line that sets `source_filename`:
```python
# Change from:
source_filename = os.path.abspath(__file__)

# To:
source_filename = os.path.abspath('your_file.txt')
```

### Change Encoding

Edit `config.toml`:
```toml
[encoding]
default = "cp932"  # or "shift_jis", "iso-8859-1", etc.
```

Restart server.

## Troubleshooting

### Server won't start

- Check if another instance is running
- Verify pipe name in config.toml
- Check permissions

### Client can't connect

- Ensure server is running first
- Verify same config.toml for both
- Check pipe name matches

### No search results

- Verify input file exists
- Check file encoding
- Try case_sensitive = false

### Import errors

```bash
pip install -r requirements.txt
```

## Development

### Run Tests

```bash
python tests/test_search.py -v
```

### Check Syntax

```bash
python -m py_compile src/server.py
python -m py_compile src/client.py
python -m py_compile src/search_filter.py
```

### Add New Test

Edit `tests/test_search.py` and add a new test method:
```python
def test_my_feature(self):
    """Test description."""
    filter = IncrementalSearchFilter(["line1", "line2"])
    result = filter.update_filter("line")
    self.assertEqual(result, "line1")
```

## API Reference

### IncrementalSearchFilter Class

```python
from src.search_filter import IncrementalSearchFilter

# Create filter
filter = IncrementalSearchFilter(
    lines=["line1", "line2", "line3"],
    case_sensitive=False
)

# Update filter pattern
selected_line = filter.update_filter("pattern")

# Get current selection
current = filter.get_selected_line()

# Move selection
new_selection = filter.move_selection(delta=1)  # +1 down, -1 up
```

### Message Protocol

All messages are JSON:

```python
import json

# Initialize
msg = json.dumps({"type": "init", "filename": "file.txt"})

# Search
msg = json.dumps({"type": "search", "pattern": "text"})

# Move
msg = json.dumps({"type": "move", "delta": 1})
```

## Performance Notes

- Loads entire file into memory
- O(n) search complexity per keystroke
- Suitable for files up to several thousand lines
- Single client per server instance

## Platform Requirements

- Windows only (uses Windows named pipes)
- Python 3.7+
- pywin32 library
- tkinter (usually included with Python)
