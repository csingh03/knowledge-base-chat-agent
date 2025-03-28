import os
import json
import time
from typing import List, Dict, Optional, Any

class DocumentRepository:
    """Class to manage document chunks from Google Drive files."""
    
    def __init__(self, storage_path: str = "document_storage.json"):
        """Initialize document repository with optional storage path."""
        self.storage_path = storage_path
        self.documents = self._load_storage()
    
    def _load_storage(self) -> Dict[str, Any]:
        """Load document storage from disk or create new if not exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading document storage: {e}")
                return {"files": {}, "last_updated": time.time()}
        else:
            return {"files": {}, "last_updated": time.time()}
    
    def _save_storage(self) -> None:
        """Save document storage to disk."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.documents, f)
    
    def add_document(self, file_id: str, file_name: str, chunks: List[str]) -> None:
        """Add or update document chunks for a file ID."""
        self.documents["files"][file_id] = {
            "name": file_name,
            "chunks": chunks,
            "added": time.time()
        }
        self.documents["last_updated"] = time.time()
        self._save_storage()
    
    def get_document_chunks(self, file_id: str) -> List[str]:
        """Get chunks for a specific document by file ID."""
        if file_id in self.documents["files"]:
            return self.documents["files"][file_id].get("chunks", [])
        return []
    
    def get_all_chunks(self) -> List[str]:
        """Get all document chunks from all files."""
        all_chunks = []
        for file_id, file_data in self.documents["files"].items():
            all_chunks.extend(file_data.get("chunks", []))
        return all_chunks
    
    def remove_document(self, file_id: str) -> bool:
        """Remove a document from the repository."""
        if file_id in self.documents["files"]:
            del self.documents["files"][file_id]
            self.documents["last_updated"] = time.time()
            self._save_storage()
            return True
        return False
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Get a list of all documents with metadata."""
        return [
            {
                "id": file_id,
                "name": file_data["name"],
                "added": file_data["added"],
                "chunk_count": len(file_data.get("chunks", []))
            }
            for file_id, file_data in self.documents["files"].items()
        ]
    
    def clear_all_documents(self) -> None:
        """Clear all documents from the repository."""
        self.documents = {"files": {}, "last_updated": time.time()}
        self._save_storage() 