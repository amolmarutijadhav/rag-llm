#!/usr/bin/env python3
"""
Test certificate configuration
"""

import pytest
from app.core.config import Config
from app.utils.cert_utils import CertificateManager

def test_cert_config():
    """Test certificate configuration"""
    print("🔐 Testing Certificate Configuration")
    print("=" * 50)
    
    # Test SSL config
    ssl_config = Config.get_ssl_config()
    print(f"SSL Config: {ssl_config}")
    assert isinstance(ssl_config, dict)
    
    # Test certificate validation
    if Config.CERT_FILE_PATH:
        is_valid = CertificateManager.validate_certificate_path(Config.CERT_FILE_PATH)
        print(f"Certificate valid: {is_valid}")
        assert isinstance(is_valid, bool)
    
    # Test httpx client creation
    from app.infrastructure.external.external_api_service import ExternalAPIService
    api_service = ExternalAPIService()
    print(f"API Service SSL Config: {api_service.ssl_config}")
    assert hasattr(api_service, 'ssl_config')

if __name__ == "__main__":
    test_cert_config() 