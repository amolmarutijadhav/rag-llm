import os
from dotenv import load_dotenv
from typing import Dict, Any
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
    
    # Security Configuration for Critical Endpoints
    CLEAR_ENDPOINT_API_KEY = os.getenv("CLEAR_ENDPOINT_API_KEY", "admin-secret-key-change-me")
    CLEAR_ENDPOINT_CONFIRMATION_TOKEN = os.getenv("CLEAR_ENDPOINT_CONFIRMATION_TOKEN", "CONFIRM_DELETE_ALL_DATA")
    CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR = int(os.getenv("CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR", "5"))
    ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING = os.getenv("ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING", "True").lower() == "true"
    
    # Provider Configuration - New plugin architecture support
    PROVIDER_EMBEDDING_TYPE = os.getenv("PROVIDER_EMBEDDING_TYPE", "openai")
    PROVIDER_LLM_TYPE = os.getenv("PROVIDER_LLM_TYPE", "openai")
    PROVIDER_VECTOR_STORE_TYPE = os.getenv("PROVIDER_VECTOR_STORE_TYPE", "qdrant")
    
    # In-house Provider Configuration
    INHOUSE_EMBEDDING_API_URL = os.getenv("INHOUSE_EMBEDDING_API_URL")
    INHOUSE_LLM_API_URL = os.getenv("INHOUSE_LLM_API_URL")
    INHOUSE_VECTOR_STORE_URL = os.getenv("INHOUSE_VECTOR_STORE_URL")
    INHOUSE_API_KEY = os.getenv("INHOUSE_API_KEY")
    
    # Enhanced In-house LLM Configuration
    INHOUSE_LLM_API_KEY = os.getenv("INHOUSE_LLM_API_KEY", INHOUSE_API_KEY)
    INHOUSE_LLM_MODEL = os.getenv("INHOUSE_LLM_MODEL", "inhouse-llm-model")
    INHOUSE_LLM_TEMPERATURE = float(os.getenv("INHOUSE_LLM_TEMPERATURE", "0.1"))
    INHOUSE_LLM_MAX_TOKENS = int(os.getenv("INHOUSE_LLM_MAX_TOKENS", "1000"))
    INHOUSE_LLM_AUTH_SCHEME = os.getenv("INHOUSE_LLM_AUTH_SCHEME", "bearer")
    
    # In-house Embedding Configuration
    INHOUSE_EMBEDDING_API_KEY = os.getenv("INHOUSE_EMBEDDING_API_KEY", INHOUSE_API_KEY)
    INHOUSE_EMBEDDING_MODEL = os.getenv("INHOUSE_EMBEDDING_MODEL", "inhouse-embedding-model")
    INHOUSE_EMBEDDING_AUTH_SCHEME = os.getenv("INHOUSE_EMBEDDING_AUTH_SCHEME", "bearer")
    
    # In-house Vector Store Configuration
    INHOUSE_VECTOR_STORE_API_KEY = os.getenv("INHOUSE_VECTOR_STORE_API_KEY", INHOUSE_API_KEY)
    INHOUSE_VECTOR_STORE_AUTH_SCHEME = os.getenv("INHOUSE_VECTOR_STORE_AUTH_SCHEME", "api_key")
    
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
    
    @classmethod
    def get_embedding_provider_config(cls) -> Dict[str, Any]:
        """
        Get configuration for embedding provider.
        
        Returns:
            Configuration dictionary for embedding provider
        """
        if cls.PROVIDER_EMBEDDING_TYPE == "inhouse":
            return {
                "type": cls.PROVIDER_EMBEDDING_TYPE,
                "api_url": cls.INHOUSE_EMBEDDING_API_URL,
                "api_key": cls.INHOUSE_EMBEDDING_API_KEY,
                "model": cls.INHOUSE_EMBEDDING_MODEL,
                "auth_scheme": cls.INHOUSE_EMBEDDING_AUTH_SCHEME,
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES
            }
        else:
            return {
                "type": cls.PROVIDER_EMBEDDING_TYPE,
                "api_url": cls.EMBEDDING_API_URL,
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.EMBEDDING_MODEL,
                "auth_scheme": "bearer",
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES
            }
    
    @classmethod
    def get_llm_provider_config(cls) -> Dict[str, Any]:
        """
        Get configuration for LLM provider.
        
        Returns:
            Configuration dictionary for LLM provider
        """
        if cls.PROVIDER_LLM_TYPE == "inhouse":
            # Get static fields for in-house LLM
            static_fields = cls._get_inhouse_llm_static_fields()
            
            return {
                "type": cls.PROVIDER_LLM_TYPE,
                "api_url": cls.INHOUSE_LLM_API_URL,
                "api_key": cls.INHOUSE_LLM_API_KEY,
                "default_model": cls.INHOUSE_LLM_MODEL,
                "default_temperature": cls.INHOUSE_LLM_TEMPERATURE,
                "default_max_tokens": cls.INHOUSE_LLM_MAX_TOKENS,
                "auth_scheme": cls.INHOUSE_LLM_AUTH_SCHEME,
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "static_fields": static_fields
            }
        else:
            return {
                "type": cls.PROVIDER_LLM_TYPE,
                "api_url": cls.LLM_API_URL,
                "api_key": cls.OPENAI_API_KEY,
                "default_model": cls.LLM_MODEL,
                "default_temperature": cls.LLM_TEMPERATURE,
                "default_max_tokens": cls.LLM_MAX_TOKENS,
                "auth_scheme": "bearer",
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES
            }
    
    @classmethod
    def _get_inhouse_llm_static_fields(cls) -> Dict[str, Any]:
        """
        Get static fields configuration for in-house LLM provider.
        
        Returns:
            Dictionary of static fields for authentication/identification
        """
        static_fields = {}
        
        # Add static fields if they are configured
        if os.getenv("INHOUSE_LLM_CLIENT_ID"):
            static_fields["client_id"] = os.getenv("INHOUSE_LLM_CLIENT_ID")
        if os.getenv("INHOUSE_LLM_VERSION"):
            static_fields["version"] = os.getenv("INHOUSE_LLM_VERSION")
        if os.getenv("INHOUSE_LLM_ENVIRONMENT"):
            static_fields["environment"] = os.getenv("INHOUSE_LLM_ENVIRONMENT")
        if os.getenv("INHOUSE_LLM_REQUEST_SOURCE"):
            static_fields["request_source"] = os.getenv("INHOUSE_LLM_REQUEST_SOURCE")
        if os.getenv("INHOUSE_LLM_AUTH_TOKEN"):
            static_fields["auth_token"] = os.getenv("INHOUSE_LLM_AUTH_TOKEN")
        if os.getenv("INHOUSE_LLM_ORGANIZATION_ID"):
            static_fields["organization_id"] = os.getenv("INHOUSE_LLM_ORGANIZATION_ID")
        if os.getenv("INHOUSE_LLM_PROJECT_ID"):
            static_fields["project_id"] = os.getenv("INHOUSE_LLM_PROJECT_ID")
        
        return static_fields
    
    @classmethod
    def get_vector_store_provider_config(cls) -> Dict[str, Any]:
        """
        Get configuration for vector store provider.
        
        Returns:
            Configuration dictionary for vector store provider
        """
        if cls.PROVIDER_VECTOR_STORE_TYPE == "inhouse":
            return {
                "type": cls.PROVIDER_VECTOR_STORE_TYPE,
                "base_url": cls.INHOUSE_VECTOR_STORE_URL,
                "api_key": cls.INHOUSE_VECTOR_STORE_API_KEY,
                "auth_scheme": cls.INHOUSE_VECTOR_STORE_AUTH_SCHEME,
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "collection_name": cls.QDRANT_COLLECTION_NAME,
                "vector_size": cls.VECTOR_SIZE,
                "distance_metric": cls.VECTOR_DISTANCE_METRIC
            }
        else:
            # Extract base URL from collection URL for Qdrant
            base_url = cls.VECTOR_COLLECTION_URL.replace(f"/collections/{cls.QDRANT_COLLECTION_NAME}", "")
            
            return {
                "type": cls.PROVIDER_VECTOR_STORE_TYPE,
                "base_url": base_url,
                "api_key": cls.QDRANT_API_KEY,
                "auth_scheme": "api_key",
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "collection_name": cls.QDRANT_COLLECTION_NAME,
                "vector_size": cls.VECTOR_SIZE,
                "distance_metric": cls.VECTOR_DISTANCE_METRIC
            } 