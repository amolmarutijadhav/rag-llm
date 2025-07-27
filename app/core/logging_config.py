"""
Production-ready logging configuration optimized for SRE and DevOps teams.
"""

import logging
import json
import uuid
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from dataclasses import dataclass, asdict
from enum import Enum

# Global correlation ID for request tracing
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')
request_start_time: ContextVar[float] = ContextVar('request_start_time', default=0.0)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class ExternalAPICall:
    """Structured log for external API calls with debugging info"""
    correlation_id: str
    provider: str
    endpoint: str
    method: str
    request_size_bytes: int
    response_size_bytes: int
    status_code: Optional[int]
    duration_ms: float
    success: bool
    error_type: Optional[str]
    error_message: Optional[str]
    timestamp: str
    curl_command: Optional[str]
    retry_count: int = 0

class StructuredJSONFormatter(logging.Formatter):
    """Production-optimized JSON formatter with correlation IDs"""
    
    def format(self, record):
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "pid": os.getpid(),
            "thread_id": record.thread
        }
        
        # Add request duration if available
        if request_start_time.get() > 0:
            log_entry["request_duration_ms"] = (time.time() - request_start_time.get()) * 1000
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, default=str)

class ProductionLoggingConfig:
    """SRE-optimized logging configuration"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.enable_structured_logging = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
        self.enable_external_api_logging = os.getenv("ENABLE_EXTERNAL_API_LOGGING", "true").lower() == "true"
        self.enable_curl_debugging = os.getenv("ENABLE_CURL_DEBUGGING", "true").lower() == "true"
        self.log_file_path = os.getenv("LOG_FILE_PATH")
        self.max_log_file_size = int(os.getenv("MAX_LOG_FILE_SIZE_MB", "100")) * 1024 * 1024
        self.log_file_backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))
        
        # Security settings
        self.redact_sensitive_headers = {'authorization', 'api-key', 'x-api-key', 'cookie', 'x-csrf-token'}
        self.redact_sensitive_fields = {'api_key', 'password', 'token', 'secret', 'key'}
    
    def setup_logging(self):
        """Configure production-ready logging"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        root_logger.handlers.clear()
        
        # Console handler for development/staging
        if self.environment in ["development", "staging"]:
            console_handler = logging.StreamHandler()
            if self.enable_structured_logging:
                console_handler.setFormatter(StructuredJSONFormatter())
            else:
                console_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] %(message)s'
                ))
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.log_file_path:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.log_file_path,
                maxBytes=self.max_log_file_size,
                backupCount=self.log_file_backup_count
            )
            file_handler.setFormatter(StructuredJSONFormatter())
            root_logger.addHandler(file_handler)
        
        # Suppress noisy third-party loggers
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        
        return root_logger

# Global instances
logging_config = ProductionLoggingConfig()

def get_logger(name: str) -> logging.Logger:
    """Get logger with correlation ID support"""
    return logging.getLogger(name)

def set_correlation_id(corr_id: str):
    """Set correlation ID for request context"""
    correlation_id.set(corr_id)

def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id.get()

def generate_correlation_id() -> str:
    """Generate unique correlation ID"""
    return str(uuid.uuid4())

def set_request_start_time():
    """Set request start time for duration tracking"""
    request_start_time.set(time.time())

def sanitize_for_logging(data: Any, sensitive_keys: set = None) -> Any:
    """Sanitize data for logging by removing sensitive information"""
    if sensitive_keys is None:
        sensitive_keys = logging_config.redact_sensitive_fields
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_for_logging(value, sensitive_keys)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item, sensitive_keys) for item in data]
    else:
        return data

class APILogger:
    """Specialized logger for external API calls with curl command generation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_api_call(self, api_call: ExternalAPICall):
        """Log external API call with full details"""
        log_data = asdict(api_call)
        
        if api_call.success:
            self.logger.info("External API call successful", extra={
                'extra_fields': {
                    'api_call': log_data,
                    'event_type': 'external_api_success'
                }
            })
        else:
            self.logger.error("External API call failed", extra={
                'extra_fields': {
                    'api_call': log_data,
                    'event_type': 'external_api_failure'
                }
            })
    
    def generate_curl_command(self, method: str, url: str, headers: Dict[str, str], 
                            body: Optional[Dict[str, Any]] = None) -> str:
        """Generate curl command for debugging external API calls"""
        if not logging_config.enable_curl_debugging:
            return None
            
        curl_parts = [f"curl -X {method.upper()} '{url}'"]
        
        # Add headers (excluding sensitive ones)
        for key, value in headers.items():
            if key.lower() in logging_config.redact_sensitive_headers:
                curl_parts.append(f"  -H '{key}: [REDACTED]'")
            else:
                curl_parts.append(f"  -H '{key}: {value}'")
        
        # Add body if present
        if body:
            sanitized_body = sanitize_for_logging(body)
            curl_parts.append(f"  -d '{json.dumps(sanitized_body)}'")
        
        return " \\\n".join(curl_parts)

# Global API logger instance
api_logger = APILogger(logging.getLogger("api_calls")) 