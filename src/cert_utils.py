import os
import ssl
from typing import Optional, Dict, Any
from pathlib import Path

class CertificateManager:
    """Manages certificate configuration for secure API calls"""
    
    @staticmethod
    def validate_certificate_path(cert_path: str) -> bool:
        """Validate if certificate file exists and is readable"""
        if not cert_path:
            return False
        
        cert_file = Path(cert_path)
        return cert_file.exists() and cert_file.is_file() and os.access(cert_file, os.R_OK)
    
    @staticmethod
    def get_ssl_context(cert_path: Optional[str] = None, verify_ssl: bool = True) -> ssl.SSLContext:
        """Create SSL context with certificate if provided"""
        if cert_path and CertificateManager.validate_certificate_path(cert_path):
            # Create SSL context with custom certificate
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cert_path)
            return ssl_context
        elif not verify_ssl:
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        else:
            # Use default SSL context
            return ssl.create_default_context()
    
    @staticmethod
    def get_httpx_ssl_config(cert_path: Optional[str] = None, verify_ssl: bool = True) -> Dict[str, Any]:
        """Get httpx-compatible SSL configuration"""
        if cert_path and CertificateManager.validate_certificate_path(cert_path):
            return {"verify": cert_path}
        elif not verify_ssl:
            return {"verify": False}
        else:
            return {"verify": True}
    
    @staticmethod
    def log_ssl_config(cert_path: Optional[str] = None, verify_ssl: bool = True):
        """Log SSL configuration for debugging"""
        if cert_path and CertificateManager.validate_certificate_path(cert_path):
            print(f"🔐 Using certificate file: {cert_path}")
        elif not verify_ssl:
            print("⚠️ SSL verification disabled")
        else:
            print("🔒 Using default SSL verification") 