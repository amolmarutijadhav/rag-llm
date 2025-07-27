import os
import tempfile
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from app.core.config import Config
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

# Image processing imports
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    from docx import Document
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logger.warning("Image processing dependencies not available. Images will be ignored.", extra={
        'extra_fields': {
            'event_type': 'document_loader_image_processing_unavailable',
            'missing_dependencies': ['pytesseract', 'PIL', 'pdf2image', 'docx']
        }
    })

class DocumentLoader:
    """Handles document loading and text extraction with image OCR support and enhanced logging"""
    
    def __init__(self):
        logger.info("Initializing document loader", extra={
            'extra_fields': {
                'event_type': 'document_loader_initialization_start',
                'chunk_size': Config.CHUNK_SIZE,
                'chunk_overlap': Config.CHUNK_OVERLAP,
                'image_processing_enabled': IMAGE_PROCESSING_AVAILABLE
            }
        })
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
        self.image_processing_enabled = IMAGE_PROCESSING_AVAILABLE
        
        logger.info("Document loader initialized successfully", extra={
            'extra_fields': {
                'event_type': 'document_loader_initialization_complete',
                'text_splitter_configured': True,
                'image_processing_enabled': self.image_processing_enabled
            }
        })
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if not self.image_processing_enabled:
            logger.debug("Image processing disabled, skipping OCR", extra={
                'extra_fields': {
                    'event_type': 'document_loader_ocr_skipped',
                    'image_path': image_path,
                    'reason': 'image_processing_disabled',
                    'correlation_id': correlation_id
                }
            })
            return ""
        
        logger.debug("Starting OCR text extraction", extra={
            'extra_fields': {
                'event_type': 'document_loader_ocr_start',
                'image_path': image_path,
                'correlation_id': correlation_id
            }
        })
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            extracted_text = text.strip()
            
            logger.info("OCR text extraction completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_ocr_success',
                    'image_path': image_path,
                    'extracted_text_length': len(extracted_text),
                    'correlation_id': correlation_id
                }
            })
            
            return extracted_text
            
        except Exception as e:
            logger.error("OCR text extraction failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_ocr_failure',
                    'image_path': image_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return ""
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract images from PDF and return list of image paths with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if not self.image_processing_enabled:
            logger.debug("Image processing disabled, skipping PDF image extraction", extra={
                'extra_fields': {
                    'event_type': 'document_loader_pdf_image_extraction_skipped',
                    'pdf_path': pdf_path,
                    'reason': 'image_processing_disabled',
                    'correlation_id': correlation_id
                }
            })
            return []
        
        logger.debug("Starting PDF image extraction", extra={
            'extra_fields': {
                'event_type': 'document_loader_pdf_image_extraction_start',
                'pdf_path': pdf_path,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(pdf_path)
            image_paths = []
            
            logger.debug("Converting PDF pages to images", extra={
                'extra_fields': {
                    'event_type': 'document_loader_pdf_conversion_progress',
                    'pdf_path': pdf_path,
                    'total_pages': len(images),
                    'correlation_id': correlation_id
                }
            })
            
            for i, image in enumerate(images):
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name, 'PNG')
                    image_paths.append(temp_file.name)
            
            logger.info("PDF image extraction completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_pdf_image_extraction_success',
                    'pdf_path': pdf_path,
                    'images_extracted': len(image_paths),
                    'correlation_id': correlation_id
                }
            })
            
            return image_paths
            
        except Exception as e:
            logger.error("PDF image extraction failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_pdf_image_extraction_failure',
                    'pdf_path': pdf_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return []
    
    def extract_images_from_docx(self, docx_path: str) -> List[str]:
        """Extract images from DOCX and return list of image paths with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if not self.image_processing_enabled:
            logger.debug("Image processing disabled, skipping DOCX image extraction", extra={
                'extra_fields': {
                    'event_type': 'document_loader_docx_image_extraction_skipped',
                    'docx_path': docx_path,
                    'reason': 'image_processing_disabled',
                    'correlation_id': correlation_id
                }
            })
            return []
        
        logger.debug("Starting DOCX image extraction", extra={
            'extra_fields': {
                'event_type': 'document_loader_docx_image_extraction_start',
                'docx_path': docx_path,
                'correlation_id': correlation_id
            }
        })
        
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
            
            logger.info("DOCX image extraction completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_docx_image_extraction_success',
                    'docx_path': docx_path,
                    'images_extracted': len(image_paths),
                    'correlation_id': correlation_id
                }
            })
            
            return image_paths
            
        except Exception as e:
            logger.error("DOCX image extraction failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_docx_image_extraction_failure',
                    'docx_path': docx_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return []
    
    def process_images_in_document(self, file_path: str) -> str:
        """Process images in a document and return extracted text with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if not self.image_processing_enabled:
            logger.debug("Image processing disabled, skipping image processing", extra={
                'extra_fields': {
                    'event_type': 'document_loader_image_processing_skipped',
                    'file_path': file_path,
                    'reason': 'image_processing_disabled',
                    'correlation_id': correlation_id
                }
            })
            return ""
        
        file_extension = os.path.splitext(file_path)[1].lower()
        image_texts = []
        
        logger.debug("Starting image processing in document", extra={
            'extra_fields': {
                'event_type': 'document_loader_image_processing_start',
                'file_path': file_path,
                'file_extension': file_extension,
                'correlation_id': correlation_id
            }
        })
        
        try:
            if file_extension == ".pdf":
                image_paths = self.extract_images_from_pdf(file_path)
            elif file_extension == ".docx":
                image_paths = self.extract_images_from_docx(file_path)
            else:
                logger.debug("No image processing for file type", extra={
                    'extra_fields': {
                        'event_type': 'document_loader_image_processing_unsupported',
                        'file_path': file_path,
                        'file_extension': file_extension,
                        'correlation_id': correlation_id
                    }
                })
                return ""
            
            # Process each extracted image
            for image_path in image_paths:
                try:
                    image_text = self.extract_text_from_image(image_path)
                    if image_text:
                        image_texts.append(image_text)
                    
                    # Clean up temporary image file
                    os.unlink(image_path)
                    
                except Exception as e:
                    logger.warning("Failed to process individual image", extra={
                        'extra_fields': {
                            'event_type': 'document_loader_individual_image_processing_failure',
                            'image_path': image_path,
                            'error': str(e),
                            'correlation_id': correlation_id
                        }
                    })
                    # Clean up temporary image file even if processing failed
                    try:
                        os.unlink(image_path)
                    except:
                        pass
            
            combined_text = "\n\n".join(image_texts)
            
            logger.info("Image processing completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_image_processing_success',
                    'file_path': file_path,
                    'images_processed': len(image_paths),
                    'images_with_text': len(image_texts),
                    'total_extracted_text_length': len(combined_text),
                    'correlation_id': correlation_id
                }
            })
            
            return combined_text
            
        except Exception as e:
            logger.error("Image processing failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_image_processing_failure',
                    'file_path': file_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return ""
    
    def load_document(self, file_path: str) -> tuple[List[Dict[str, Any]], str]:
        """Load and process a document with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting document loading", extra={
            'extra_fields': {
                'event_type': 'document_loader_load_start',
                'file_path': file_path,
                'file_size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'correlation_id': correlation_id
            }
        })
        
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Load document based on file type
            logger.debug("Loading document based on file type", extra={
                'extra_fields': {
                    'event_type': 'document_loader_type_detection',
                    'file_path': file_path,
                    'file_extension': file_extension,
                    'correlation_id': correlation_id
                }
            })
            
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension == ".txt":
                loader = TextLoader(file_path)
            elif file_extension == ".docx":
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Load documents
            documents = loader.load()
            
            logger.info("Document loaded successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_load_success',
                    'file_path': file_path,
                    'file_extension': file_extension,
                    'documents_loaded': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            # Process images in the document
            logger.debug("Processing images in document", extra={
                'extra_fields': {
                    'event_type': 'document_loader_image_processing_start',
                    'file_path': file_path,
                    'correlation_id': correlation_id
                }
            })
            
            ocr_text = self.process_images_in_document(file_path)
            
            # Combine document text with OCR text
            all_text = ""
            for doc in documents:
                all_text += doc.page_content + "\n\n"
            
            if ocr_text:
                all_text += f"Extracted from images:\n{ocr_text}\n\n"
            
            # Split text into chunks
            logger.debug("Splitting text into chunks", extra={
                'extra_fields': {
                    'event_type': 'document_loader_chunking_start',
                    'file_path': file_path,
                    'total_text_length': len(all_text),
                    'chunk_size': Config.CHUNK_SIZE,
                    'chunk_overlap': Config.CHUNK_OVERLAP,
                    'correlation_id': correlation_id
                }
            })
            
            chunks = self.text_splitter.split_text(all_text)
            
            # Convert chunks to document format
            processed_documents = []
            for i, chunk in enumerate(chunks):
                processed_documents.append({
                    "id": f"{os.path.basename(file_path)}_{i}",
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })
            
            logger.info("Document processing completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_processing_complete',
                    'file_path': file_path,
                    'original_documents': len(documents),
                    'processed_chunks': len(processed_documents),
                    'ocr_text_extracted': bool(ocr_text),
                    'ocr_text_length': len(ocr_text) if ocr_text else 0,
                    'correlation_id': correlation_id
                }
            })
            
            return processed_documents, ocr_text
            
        except Exception as e:
            logger.error("Document loading failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_load_failure',
                    'file_path': file_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            raise
    
    def load_text(self, text: str, source_name: str = None) -> List[Dict[str, Any]]:
        """Load and process raw text with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if source_name is None:
            source_name = "text_input"
        
        logger.info("Starting text loading", extra={
            'extra_fields': {
                'event_type': 'document_loader_text_load_start',
                'source_name': source_name,
                'text_length': len(text),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Split text into chunks
            logger.debug("Splitting text into chunks", extra={
                'extra_fields': {
                    'event_type': 'document_loader_text_chunking_start',
                    'source_name': source_name,
                    'text_length': len(text),
                    'chunk_size': Config.CHUNK_SIZE,
                    'chunk_overlap': Config.CHUNK_OVERLAP,
                    'correlation_id': correlation_id
                }
            })
            
            chunks = self.text_splitter.split_text(text)
            
            # Convert chunks to document format
            processed_documents = []
            for i, chunk in enumerate(chunks):
                processed_documents.append({
                    "id": f"{source_name}_{i}",
                    "content": chunk,
                    "metadata": {
                        "source": source_name,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })
            
            logger.info("Text processing completed successfully", extra={
                'extra_fields': {
                    'event_type': 'document_loader_text_processing_complete',
                    'source_name': source_name,
                    'original_text_length': len(text),
                    'processed_chunks': len(processed_documents),
                    'correlation_id': correlation_id
                }
            })
            
            return processed_documents
            
        except Exception as e:
            logger.error("Text loading failed", extra={
                'extra_fields': {
                    'event_type': 'document_loader_text_load_failure',
                    'source_name': source_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            raise 