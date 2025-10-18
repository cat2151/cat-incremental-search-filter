# Usage Examples

## Example 1: Basic Server and Client Usage

### Terminal 1: Start the Server

```bash
python src/server.py --config-filename config.toml
```

Output:
```
Starting server on pipe: \\.\pipe\cat_incremental_search_filter
Press Ctrl+C to stop
Waiting for client connection...
```

### Terminal 2: Start the Test Client

```bash
python src/client.py --config-filename config.toml
```

The client window will open with:
- A search input field
- The window title shows the currently selected line from the client.py file

### Using the Client

1. Type in the search field to filter lines
   - Type "import" to see all import statements
   - Type "def" to see all function definitions
   - Type "class" to see all class definitions

2. The window title updates in real-time showing the first matching line

3. As you type more characters, the filter narrows down:
   - Type "i" → sees many matches
   - Type "im" → sees import-related lines
   - Type "imp" → sees import statements
   - Type "impor" → sees import statements
   - Type "import t" → sees "import tkinter"

## Example 2: Testing with Custom Data File

### Create a test data file

```bash
echo -e "apple\nbanana\ncherry\ndate\nelderberry" > fruits.txt
```

### Modify Client to Use Custom File

Edit the client.py temporarily (or create a custom client script):

```python
# Instead of:
source_filename = os.path.abspath(__file__)

# Use:
source_filename = os.path.abspath('fruits.txt')
```

Now when you type:
- "a" → shows "apple", "banana", "date"
- "ap" → shows "apple"
- "berry" → shows "elderberry"

## Example 3: Testing with the Example Data File

Start the client with example_data.txt:

```python
# Modify client.py to use example_data.txt
source_filename = os.path.abspath('example_data.txt')
```

Then search for:
- "test" → shows all test files
- "src" → shows all source files
- ".py" → shows all Python files
- "docs" → shows all documentation files

## Example 4: Case Sensitive Search

### Edit config.toml

```toml
[search]
case_sensitive = true
```

### Restart Server

```bash
python src/server.py --config-filename config.toml
```

Now searches are case-sensitive:
- "README" matches "README.md"
- "readme" doesn't match "README.md"

## Example 5: Custom Pipe Name

### Edit config.toml

```toml
[pipe]
name = "\\\\.\\pipe\\my_custom_filter"
```

### Restart Both Server and Client

The server and client will now communicate via the custom named pipe.

## Protocol Examples

### Sending Messages Manually (Advanced)

If you want to create your own client, here are the message formats:

#### Initialize with a file
```python
import json
message = json.dumps({"type": "init", "filename": "myfile.txt"})
# Send via pipe, receive response
```

#### Search for a pattern
```python
message = json.dumps({"type": "search", "pattern": "test"})
# Send via pipe, receive response with matched line
```

#### Move selection
```python
message = json.dumps({"type": "move", "delta": 1})  # Move down
# or
message = json.dumps({"type": "move", "delta": -1})  # Move up
# Send via pipe, receive response with new selected line
```

## Troubleshooting

### Server won't start
- Check if another instance is already running
- Verify the pipe name in config.toml is valid
- Make sure you have necessary permissions

### Client can't connect
- Ensure server is running first
- Verify both server and client use the same config.toml
- Check pipe name matches in both

### No results when searching
- Verify the input file exists and is readable
- Check encoding setting in config.toml
- Try with case_sensitive = false
