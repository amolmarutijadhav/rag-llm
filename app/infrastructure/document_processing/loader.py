import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from app.core.config import Config

class DocumentLoader:
    """Handles document loading and text extraction"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and process a document file"""
        
        # Validate file format
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in Config.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Load document based on format
        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension == ".txt":
            loader = TextLoader(file_path)
        elif file_extension == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extract text
        documents = loader.load()
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Convert to dictionary format
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "id": f"{os.path.basename(file_path)}_{i}",
                "content": chunk.page_content,
                "metadata": {
                    "source": file_path,
                    "page": chunk.metadata.get("page", 0),
                    "chunk_index": i
                }
            })
        
        return processed_chunks
    
    def load_text(self, text: str, source_name: str = "text_input") -> List[Dict[str, Any]]:
        """Load and process raw text"""
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Convert to dictionary format
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "id": f"{source_name}_{i}",
                "content": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_index": i
                }
            })
        
        return processed_chunks 