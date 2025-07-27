import os
import tempfile
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from app.core.config import Config

# Image processing imports
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    from docx import Document
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("Warning: Image processing dependencies not available. Images will be ignored.")

class DocumentLoader:
    """Handles document loading and text extraction with image OCR support"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
        self.image_processing_enabled = IMAGE_PROCESSING_AVAILABLE
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR"""
        if not self.image_processing_enabled:
            return ""
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"OCR failed for image {image_path}: {e}")
            return ""
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract images from PDF and return list of image paths"""
        if not self.image_processing_enabled:
            return []
        
        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(pdf_path)
            image_paths = []
            
            for i, image in enumerate(images):
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name, 'PNG')
                    image_paths.append(temp_file.name)
            
            return image_paths
        except Exception as e:
            print(f"Failed to extract images from PDF {pdf_path}: {e}")
            return []
    
    def extract_images_from_docx(self, docx_path: str) -> List[str]:
        """Extract images from DOCX and return list of image paths"""
        if not self.image_processing_enabled:
            return []
        
        try:
            doc = Document(docx_path)
            image_paths = []
            
            for i, rel in enumerate(doc.part.rels.values()):
                if "image" in rel.target_ref:
                    # Extract image data
                    image_data = rel.target_part.blob
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_file.write(image_data)
                        image_paths.append(temp_file.name)
            
            return image_paths
        except Exception as e:
            print(f"Failed to extract images from DOCX {docx_path}: {e}")
            return []
    
    def process_images_in_document(self, file_path: str) -> str:
        """Process images in a document and return extracted text"""
        if not self.image_processing_enabled:
            return ""
        
        file_extension = os.path.splitext(file_path)[1].lower()
        image_texts = []
        
        try:
            if file_extension == ".pdf":
                image_paths = self.extract_images_from_pdf(file_path)
            elif file_extension == ".docx":
                image_paths = self.extract_images_from_docx(file_path)
            else:
                return ""
            
            # Extract text from each image
            for image_path in image_paths:
                text = self.extract_text_from_image(image_path)
                if text:
                    image_texts.append(f"[Image Content: {text}]")
                
                # Clean up temporary image file
                try:
                    os.unlink(image_path)
                except:
                    pass
            
            return "\n".join(image_texts)
            
        except Exception as e:
            print(f"Failed to process images in {file_path}: {e}")
            return ""
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and process a document file with image OCR support"""
        
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
        
        # Extract text from document
        documents = loader.load()
        
        # Process images if supported formats
        image_text = ""
        if file_extension in [".pdf", ".docx"]:
            image_text = self.process_images_in_document(file_path)
        
        # Combine document text with image text
        combined_text = ""
        for doc in documents:
            combined_text += doc.page_content + "\n"
        
        if image_text:
            combined_text += f"\n{image_text}\n"
        
        # Create a single document with combined content
        from langchain.schema import Document
        combined_document = Document(
            page_content=combined_text,
            metadata={"source": file_path, "page": 0}
        )
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([combined_document])
        
        # Convert to dictionary format
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "id": f"{os.path.basename(file_path)}{Config.CHUNK_ID_SEPARATOR}{i}",
                "content": chunk.page_content,
                "metadata": {
                    "source": file_path,
                    "page": chunk.metadata.get("page", 0),
                    "chunk_index": i,
                    "has_images": bool(image_text)
                }
            })
        
        return processed_chunks
    
    def load_text(self, text: str, source_name: str = None) -> List[Dict[str, Any]]:
        """Load and process raw text"""
        
        # Use default source name from config if not provided
        if source_name is None:
            source_name = Config.DEFAULT_SOURCE_NAME
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Convert to dictionary format
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "id": f"{source_name}{Config.CHUNK_ID_SEPARATOR}{i}",
                "content": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_index": i
                }
            })
        
        return processed_chunks 