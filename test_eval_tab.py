#!/usr/bin/env python3
"""Test script to verify evaluation tab functionality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from main_window import MainWindow

def test_eval_tab():
    """Test the evaluation tab"""
    print("[TEST] Starting application...")
    app = QApplication(sys.argv)
    
    print("[TEST] Creating main window...")
    window = MainWindow()
    
    print("[TEST] Getting evaluation tab...")
    eval_tab = window.evaluation_tab
    
    print("[TEST] Testing _get_hierarchical_categories()...")
    # Create a test by accessing the database
    from database import Database
    db = Database()
    
    # Get all projects
    projects = db.get_all_projects()
    print(f"[TEST] Found {len(projects)} projects")
    
    if projects:
        project_id = projects[0][0]
        print(f"[TEST] Testing with project {project_id}...")
        
        # Get hierarchical categories
        categories = eval_tab._get_hierarchical_categories(project_id)
        print(f"[TEST] Hierarchical categories for project {project_id}:")
        
        level2_count = sum(1 for c in categories if c[3] == 2)
        level3_count = sum(1 for c in categories if c[3] == 3)
        print(f"  - Level 2 (parents): {level2_count}")
        print(f"  - Level 3 (children): {level3_count}")
        
        # Verify structure
        assert all(len(c) == 5 for c in categories), "Each category should have 5 elements"
        assert all(c[3] in (2, 3) for c in categories), "Only levels 2 and 3 expected"
        
        # Print sample categories
        if categories:
            print(f"\n[TEST] Sample categories:")
            for cat in categories[:3]:
                cat_id, name, points, level, parent_id = cat
                print(f"  - L{level}: {name} (id={cat_id}, points={points}, parent={parent_id})")
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_eval_tab()
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
