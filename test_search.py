#!/usr/bin/env python3
"""
Unit tests for the incremental search filter logic.
These tests verify the search functionality without requiring Windows named pipes.
"""
import unittest
import sys
import os

# Add parent directory to path to import search_filter module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_filter import IncrementalSearchFilter


class TestIncrementalSearchFilter(unittest.TestCase):
    """Test cases for IncrementalSearchFilter class."""
    
    def setUp(self):
        """Set up test data."""
        self.test_lines = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elderberry",
            "fig",
            "grape",
            "Apple Pie",
            "BANANA SPLIT",
        ]
    
    def test_initial_state(self):
        """Test initial state without any filter."""
        filter = IncrementalSearchFilter(self.test_lines)
        self.assertEqual(filter.get_selected_line(), "apple")
        self.assertEqual(len(filter.filtered_lines), 9)
    
    def test_case_insensitive_search(self):
        """Test case-insensitive search (default)."""
        filter = IncrementalSearchFilter(self.test_lines, case_sensitive=False)
        
        # Search for "apple" should match "apple" and "Apple Pie"
        result = filter.update_filter("apple")
        self.assertIn(result, ["apple", "Apple Pie"])
        self.assertEqual(len(filter.filtered_lines), 2)
        self.assertIn("apple", filter.filtered_lines)
        self.assertIn("Apple Pie", filter.filtered_lines)
    
    def test_case_sensitive_search(self):
        """Test case-sensitive search."""
        filter = IncrementalSearchFilter(self.test_lines, case_sensitive=True)
        
        # Search for "apple" should only match "apple"
        result = filter.update_filter("apple")
        self.assertEqual(result, "apple")
        self.assertEqual(len(filter.filtered_lines), 1)
        self.assertEqual(filter.filtered_lines[0], "apple")
        
        # Search for "Apple" should only match "Apple Pie"
        result = filter.update_filter("Apple")
        self.assertEqual(result, "Apple Pie")
        self.assertEqual(len(filter.filtered_lines), 1)
        self.assertEqual(filter.filtered_lines[0], "Apple Pie")
    
    def test_incremental_filtering(self):
        """Test incremental filtering as user types."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Type "a"
        result = filter.update_filter("a")
        self.assertIn(result, ["apple", "banana", "date", "grape", "Apple Pie", "BANANA SPLIT"])
        self.assertEqual(len(filter.filtered_lines), 6)
        
        # Type "ap"
        result = filter.update_filter("ap")
        self.assertIn(result, ["apple", "grape", "Apple Pie"])
        self.assertEqual(len(filter.filtered_lines), 3)
        
        # Type "app"
        result = filter.update_filter("app")
        self.assertIn(result, ["apple", "Apple Pie"])
        self.assertEqual(len(filter.filtered_lines), 2)
    
    def test_empty_pattern(self):
        """Test that empty pattern shows all lines."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Filter then clear
        filter.update_filter("app")
        result = filter.update_filter("")
        
        self.assertEqual(result, "apple")
        self.assertEqual(len(filter.filtered_lines), 9)
    
    def test_no_matches(self):
        """Test behavior when no matches are found."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        result = filter.update_filter("xyz")
        self.assertEqual(result, "")
        self.assertEqual(len(filter.filtered_lines), 0)
    
    def test_move_selection_down(self):
        """Test moving selection down."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Start at index 0
        self.assertEqual(filter.get_selected_line(), "apple")
        
        # Move down
        result = filter.move_selection(1)
        self.assertEqual(result, "banana")
        self.assertEqual(filter.selected_index, 1)
        
        # Move down again
        result = filter.move_selection(1)
        self.assertEqual(result, "cherry")
        self.assertEqual(filter.selected_index, 2)
    
    def test_move_selection_up(self):
        """Test moving selection up."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Move to index 2
        filter.move_selection(2)
        self.assertEqual(filter.get_selected_line(), "cherry")
        
        # Move up
        result = filter.move_selection(-1)
        self.assertEqual(result, "banana")
        self.assertEqual(filter.selected_index, 1)
        
        # Move up again
        result = filter.move_selection(-1)
        self.assertEqual(result, "apple")
        self.assertEqual(filter.selected_index, 0)
    
    def test_move_selection_bounds(self):
        """Test that selection stays within bounds."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Try to move beyond start
        result = filter.move_selection(-10)
        self.assertEqual(result, "apple")
        self.assertEqual(filter.selected_index, 0)
        
        # Try to move beyond end
        result = filter.move_selection(100)
        self.assertEqual(result, "BANANA SPLIT")
        self.assertEqual(filter.selected_index, 8)
    
    def test_selection_reset_on_filter(self):
        """Test that selection resets when filtered list becomes smaller."""
        filter = IncrementalSearchFilter(self.test_lines)
        
        # Move to a later item
        filter.move_selection(5)
        self.assertEqual(filter.selected_index, 5)
        
        # Apply filter that has fewer items
        filter.update_filter("apple")
        # Selection should be reset to 0 since filtered list only has 2 items
        self.assertEqual(filter.selected_index, 0)
    
    def test_empty_lines(self):
        """Test behavior with empty line list."""
        filter = IncrementalSearchFilter([])
        
        self.assertEqual(filter.get_selected_line(), "")
        result = filter.update_filter("test")
        self.assertEqual(result, "")
        result = filter.move_selection(1)
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
