#!/usr/bin/env python3
"""
Script to fix API endpoint test issues.
This script fixes import paths, endpoint paths, and status expectations.
"""

import re
import os

def fix_api_tests():
    """Fix API endpoint test issues."""
    test_files = [
        "tests/integration/test_api_endpoints_sync.py",
        "tests/integration/test_api_endpoints.py"
    ]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"Test file not found: {test_file}")
            continue
        
        # Read the file
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix import paths: src.main -> app.api.routes.questions
        content = re.sub(r'src\.main\.rag_service', 'app.api.routes.questions.rag_service', content)
        
        # Fix import paths: app.main.rag_service -> app.api.routes.questions.rag_service
        content = re.sub(r'app\.main\.rag_service', 'app.api.routes.questions.rag_service', content)
        
        # Fix endpoint paths: /ask -> /questions/ask
        content = re.sub(r'"/ask"', '"/questions/ask"', content)
        
        # Fix endpoint paths: /upload -> /documents/upload
        content = re.sub(r'"/upload"', '"/documents/upload"', content)
        
        # Fix endpoint paths: /add-text -> /documents/add-text
        content = re.sub(r'"/add-text"', '"/documents/add-text"', content)
        
        # Fix endpoint paths: /clear -> /documents/clear
        content = re.sub(r'"/clear"', '"/documents/clear"', content)
        
        # Fix endpoint paths: /stats -> /questions/stats
        content = re.sub(r'"/stats"', '"/questions/stats"', content)
        
        # Fix status expectations for root endpoint
        content = re.sub(r'assert data\["status"\] == "running"', 'assert data["status"] == "healthy"', content)
        
        # Write back if changes were made
        if content != original_content:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed API endpoint test issues in {test_file}")
        else:
            print(f"ℹ️  No changes needed in {test_file}")

if __name__ == "__main__":
    fix_api_tests() 