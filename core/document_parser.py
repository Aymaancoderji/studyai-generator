import os
from pathlib import Path
from typing import Tuple
import PyPDF2
from docx import Document

class DocumentParser:
    """Parse various document formats to extract text."""
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, str]:
        """
        Parse a file and extract its text content.
        
        Returns:
            Tuple of (content, file_type)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return DocumentParser.parse_pdf(file_path), 'pdf'
        elif extension == '.txt':
            return DocumentParser.parse_txt(file_path), 'txt'
        elif extension == '.docx':
            return DocumentParser.parse_docx(file_path), 'docx'
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    @staticmethod
    def parse_pdf(file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
    
    @staticmethod
    def parse_docx(file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            
            return '\n'.join(text)
        
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def validate_content(content: str, min_length: int = 50) -> bool:
        """Validate that extracted content is usable."""
        if not content or len(content.strip()) < min_length:
            return False
        return True
    
    @staticmethod
    def get_content_stats(content: str) -> dict:
        """Get basic statistics about the content."""
        words = content.split()
        sentences = content.split('.')
        
        return {
            'character_count': len(content),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
