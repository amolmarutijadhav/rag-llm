import os
from dotenv import load_dotenv
from src.cert_utils import CertificateManager

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with externalized API endpoints and certificate support"""
    
    # External API Endpoints - Complete URLs
    EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "https://api.openai.com/v1/embeddings")
    VECTOR_INSERT_API_URL = os.getenv("VECTOR_INSERT_API_URL", "https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points")
    VECTOR_SEARCH_API_URL = os.getenv("VECTOR_SEARCH_API_URL", "https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points/search")
    VECTOR_COLLECTION_URL = os.getenv("VECTOR_COLLECTION_URL", "https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents")
    LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    
    # API Authentication
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Certificate Configuration
    CERT_FILE_PATH = os.getenv("CERT_FILE_PATH")
    VERIFY_SSL = os.getenv("VERIFY_SSL", "True").lower() == "true"
    CERT_VERIFY_MODE = os.getenv("CERT_VERIFY_MODE", "auto")
    
    # Vector Database Configuration
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Document Processing
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS = [".pdf", ".txt", ".docx"]
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # HTTP Configuration
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def get_ssl_config(cls):
        """Get SSL configuration using CertificateManager"""
        ssl_config = CertificateManager.get_httpx_ssl_config(
            cert_path=cls.CERT_FILE_PATH,
            verify_ssl=cls.VERIFY_SSL
        )
        CertificateManager.log_ssl_config(
            cert_path=cls.CERT_FILE_PATH,
            verify_ssl=cls.VERIFY_SSL
        )
        return ssl_config 