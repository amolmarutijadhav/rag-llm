#!/usr/bin/env python3
"""
Simple script to run the RAG LLM API
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import uvicorn
from app.core.config import Config

def main():
    """Main function to start the RAG LLM API server"""
    print("🚀 Starting RAG LLM API...")
    print(f"📡 Server will be available at: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main() 