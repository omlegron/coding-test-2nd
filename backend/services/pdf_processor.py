import os
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        # TODO: Initialize text splitter with chunk size and overlap settings
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )

    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF and return page-wise content"""
        # TODO: Implement PDF text extraction
        # - Use pdfplumber or PyPDF2 to extract text from each page
        # - Return list of dictionaries with page content and metadata
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page": i + 1,
                            "text": text.strip()
                        })
        except Exception as e:
            logger.exception(f"❌ Failed to extract text from PDF: {e}")
            raise e

        return pages
    
    def split_into_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Document]:
        """Split page content into chunks"""
        # TODO: Implement text chunking
        # - Split each page content into smaller chunks
        # - Create Document objects with proper metadata
        # - Return list of Document objects
        documents = []

        for page in pages_content:
            page_text = page["text"]
            page_number = page["page"]

            chunks = self.splitter.split_text(page_text)
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={"page": page_number, "chunk": i + 1}
                ))

        return documents
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF file and return list of Document objects"""
        # TODO: Implement complete PDF processing pipeline
        # 1. Extract text from PDF
        # 2. Split text into chunks
        # 3. Return processed documents
        logger.info(f"📄 Processing PDF: {file_path}")
        pages = self.extract_text_from_pdf(file_path)
        if not pages:
            raise ValueError("No text found in PDF.")

        documents = self.split_into_chunks(pages)
        logger.info(f"✅ Extracted {len(documents)} chunks from {len(pages)} pages.")
        return documents
 