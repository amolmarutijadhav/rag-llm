#!/usr/bin/env python3
"""
Simple script to run the RAG LLM API
"""

import uvicorn
from src.config import Config

if __name__ == "__main__":
    print("🚀 Starting RAG LLM API...")
    print(f"📡 Server will be available at: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    
    uvicorn.run(
        "src.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    ) 