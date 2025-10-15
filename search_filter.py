"""
Core incremental search filter logic (platform-independent).
"""


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
