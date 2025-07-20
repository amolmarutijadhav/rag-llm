#!/usr/bin/env python3
"""
Test certificate configuration
"""

import asyncio
from src.config import Config
from src.cert_utils import CertificateManager

async def test_cert_config():
    """Test certificate configuration"""
    print("🔐 Testing Certificate Configuration")
    print("=" * 50)
    
    # Test SSL config
    ssl_config = Config.get_ssl_config()
    print(f"SSL Config: {ssl_config}")
    
    # Test certificate validation
    if Config.CERT_FILE_PATH:
        is_valid = CertificateManager.validate_certificate_path(Config.CERT_FILE_PATH)
        print(f"Certificate valid: {is_valid}")
    
    # Test httpx client creation
    from src.external_api_service import ExternalAPIService
    api_service = ExternalAPIService()
    print(f"API Service SSL Config: {api_service.ssl_config}")

if __name__ == "__main__":
    asyncio.run(test_cert_config()) 