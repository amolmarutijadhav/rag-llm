#!/usr/bin/env python3
"""
Script to fix async/await issues in document upload tests.
This script removes @pytest.mark.asyncio decorators and async/await keywords.
"""

import re
import os

def fix_async_tests():
    """Fix async/await issues in test files."""
    test_file = "tests/integration/test_document_upload.py"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    # Read the file
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix patterns
    original_content = content
    
    # Remove @pytest.mark.asyncio decorators
    content = re.sub(r'@pytest\.mark\.asyncio\s*\n\s*async def', 'def', content)
    
    # Remove async keywords from function definitions
    content = re.sub(r'async def test_', 'def test_', content)
    
    # Remove await keywords from function calls
    content = re.sub(r'await async_client\.', 'async_client.', content)
    
    # Write back if changes were made
    if content != original_content:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed async/await issues in {test_file}")
    else:
        print(f"ℹ️  No changes needed in {test_file}")

if __name__ == "__main__":
    fix_async_tests() 