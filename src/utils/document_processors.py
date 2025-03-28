import pandas as pd
import pypdf
import csv
import os
from typing import List, Dict, Any, Optional

def process_pdf(file_path: str) -> str:
    """Extract text content from PDF files."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf = pypdf.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"
    return text

def process_csv(file_path: str) -> str:
    """Extract content from CSV files and format as readable text."""
    text = ""
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        text += "Headers: " + ", ".join(headers) + "\n\n"
        
        for row_num, row in enumerate(csv_reader, 1):
            text += f"Row {row_num}: " + ", ".join(row) + "\n"
    return text

def process_excel(file_path: str) -> str:
    """Extract content from Excel files and format as readable text."""
    text = ""
    excel_file = pd.ExcelFile(file_path)
    
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        text += f"\n\nSheet: {sheet_name}\n"
        text += df.to_string(index=False) + "\n\n"
    
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for processing."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk) < 50:  # Skip very small chunks
            continue
        chunks.append(chunk)
    return chunks

def process_document(file_path: str) -> List[str]:
    """Process document based on its extension and return chunked text."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        text = process_pdf(file_path)
    elif ext == '.csv':
        text = process_csv(file_path)
    elif ext in ['.xlsx', '.xls']:
        text = process_excel(file_path)
    else:
        # For text files or other formats
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
    
    return chunk_text(text) 