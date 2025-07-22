import os
from dotenv import load_dotenv
from app.utils.cert_utils import CertificateManager

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
    
    # Document Processing Configuration
    CHUNK_ID_SEPARATOR = os.getenv("CHUNK_ID_SEPARATOR", "_")
    DEFAULT_SOURCE_NAME = os.getenv("DEFAULT_SOURCE_NAME", "text_input")
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # RAG Prompt Templates
    RAG_PROMPT_TEMPLATE = os.getenv("RAG_PROMPT_TEMPLATE", """You are a helpful AI assistant that answers questions based on the provided context. 
        Use only the information from the context to answer the question. If the context doesn't contain 
        enough information to answer the question, say "I don't have enough information to answer this question."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:""")
    
    # RAG Display Configuration
    CONTENT_PREVIEW_LENGTH = int(os.getenv("CONTENT_PREVIEW_LENGTH", "200"))
    DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))
    
    # AI Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1536"))
    VECTOR_DISTANCE_METRIC = os.getenv("VECTOR_DISTANCE_METRIC", "Cosine")
    
    # LLM Parameters
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    
    # FastAPI Application Configuration
    API_TITLE = os.getenv("API_TITLE", "RAG LLM API")
    API_DESCRIPTION = os.getenv("API_DESCRIPTION", "A simple RAG (Retrieval-Augmented Generation) API for document Q&A")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    
    # CORS Configuration
    CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
    CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
    
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