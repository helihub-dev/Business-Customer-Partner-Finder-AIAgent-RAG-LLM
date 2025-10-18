"""Load and process AxleWave company documents."""
from pathlib import Path
from typing import List, Dict
from zipfile import ZipFile
import xml.etree.ElementTree as ET


def extract_docx_text(docx_path: Path) -> str:
    """Extract text from .docx file."""
    with ZipFile(docx_path) as docx:
        xml_content = docx.read('word/document.xml')
        tree = ET.XML(xml_content)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = []
        
        for paragraph in tree.findall('.//w:p', namespaces):
            texts = [node.text for node in paragraph.findall('.//w:t', namespaces) if node.text]
            if texts:
                paragraphs.append(''.join(texts))
        
        return '\n'.join(paragraphs)


def load_axlewave_documents(docs_dir: Path) -> List[Dict[str, str]]:
    """Load all AxleWave documents from directory."""
    documents = []
    
    for file_path in docs_dir.glob("*.docx"):
        try:
            content = extract_docx_text(file_path)
            documents.append({
                "filename": file_path.name,
                "content": content,
                "type": "docx"
            })
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
    
    return documents


def create_company_context(documents: List[Dict[str, str]]) -> str:
    """Create a consolidated context about AxleWave from all documents."""
    context_parts = []
    
    for doc in documents:
        context_parts.append(f"=== {doc['filename']} ===\n{doc['content']}\n")
    
    return "\n".join(context_parts)


class DocumentLoader:
    """Simple wrapper for document loading functions."""
    
    @staticmethod
    def load_documents(docs_dir: Path) -> List[Dict[str, str]]:
        return load_axlewave_documents(docs_dir)
    
    @staticmethod
    def create_context(documents: List[Dict[str, str]]) -> str:
        return create_company_context(documents)
