import os
import json
import pickle
import gradio as gr
from dotenv import load_dotenv
import tempfile
from typing import List, Dict, Any, Tuple

# Load environment variables
load_dotenv()

# Import local modules
from models import DocumentRepository
from services import create_oauth_flow, get_drive_service, list_files, download_file, query_documents
from utils import process_document

# Initialize document repository
doc_repo = DocumentRepository()

# Store user credentials (in memory for demo purposes, use proper secure storage in production)
user_credentials = {}

def authenticate() -> Tuple[str, str]:
    """Start the Google authentication flow and return the auth URL."""
    flow = create_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url, "Please click the link above to authorize access to your Google Drive."

def handle_oauth_callback(code: str) -> str:
    """Handle the OAuth callback and store user credentials."""
    try:
        flow = create_oauth_flow()
        flow.fetch_token(code=code)
        
        # Extract credentials
        credentials = flow.credentials
        credentials_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Store credentials (securely in a real application)
        global user_credentials
        user_credentials = credentials_dict
        
        return "Authentication successful! You can now browse your Google Drive files."
    except Exception as e:
        return f"Authentication failed: {str(e)}"

def list_drive_files() -> List[Dict[str, Any]]:
    """List files from the user's Google Drive."""
    if not user_credentials:
        return []
    
    try:
        drive_service = get_drive_service(user_credentials)
        return list_files(drive_service)
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def process_selected_files(file_ids: List[str]) -> str:
    """Process selected files from Google Drive and add to repository."""
    if not user_credentials or not file_ids:
        return "No files selected or authentication required."
    
    try:
        drive_service = get_drive_service(user_credentials)
        
        for file_id in file_ids:
            # Get file metadata
            file_metadata = drive_service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'unknown')
            
            # Download file
            local_path = download_file(drive_service, file_id)
            
            # Process document into chunks
            chunks = process_document(local_path)
            
            # Add to document repository
            doc_repo.add_document(file_id, file_name, chunks)
            
            # Clean up temp file
            if os.path.exists(local_path):
                os.remove(local_path)
        
        return f"Successfully processed {len(file_ids)} files. Total documents in repository: {len(doc_repo.get_document_list())}"
    except Exception as e:
        return f"Error processing files: {str(e)}"

def query_knowledge_base(query: str) -> str:
    """Query the knowledge base using the Model Context Protocol approach."""
    if not query.strip():
        return "Please enter a question."
    
    all_chunks = doc_repo.get_all_chunks()
    
    if not all_chunks:
        return "No documents have been loaded into the knowledge base. Please add some files first."
    
    try:
        # Use the Model Context Protocol to generate an answer
        answer = query_documents(query, all_chunks)
        return answer
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def list_repository_files() -> str:
    """List all files in the document repository."""
    doc_list = doc_repo.get_document_list()
    
    if not doc_list:
        return "No documents in the repository."
    
    file_info = "\n".join([
        f"{i+1}. {doc['name']} (chunks: {doc['chunk_count']})"
        for i, doc in enumerate(doc_list)
    ])
    
    return f"Documents in repository ({len(doc_list)}):\n\n{file_info}"

def clear_repository() -> str:
    """Clear all documents from the repository."""
    doc_repo.clear_all_documents()
    return "Document repository cleared."

# Create Gradio interface
with gr.Blocks(title="Knowledge Base Chat Agent") as app:
    gr.Markdown("# Internal Knowledge Chat Agent (MCP)")
    gr.Markdown("Connect to your Google Drive and ask questions based on your documents.")
    
    with gr.Tab("Authentication"):
        auth_button = gr.Button("Start Google Authentication")
        auth_output = gr.Textbox(label="Authentication URL")
        auth_message = gr.Textbox(label="Message")
        
        auth_button.click(authenticate, outputs=[auth_output, auth_message])
        
        gr.Markdown("### Complete Authentication")
        callback_code = gr.Textbox(label="Enter the authorization code")
        submit_code = gr.Button("Submit Code")
        auth_result = gr.Textbox(label="Authentication Result")
        
        submit_code.click(handle_oauth_callback, inputs=callback_code, outputs=auth_result)
    
    with gr.Tab("Document Management"):
        refresh_button = gr.Button("Refresh Google Drive Files")
        file_list = gr.Dataframe(
            headers=["ID", "Name", "Type"],
            datatype=["str", "str", "str"],
            label="Google Drive Files"
        )
        
        refresh_button.click(
            lambda: [[f["id"], f["name"], f["mimeType"]] for f in list_drive_files()],
            outputs=file_list
        )
        
        selected_files = gr.Textbox(label="Enter file IDs (comma-separated)")
        process_button = gr.Button("Process Selected Files")
        process_result = gr.Textbox(label="Processing Result")
        
        process_button.click(
            lambda ids: process_selected_files(ids.split(",")),
            inputs=selected_files,
            outputs=process_result
        )
        
        list_repo_button = gr.Button("List Repository Files")
        repo_files = gr.Textbox(label="Repository Files")
        
        list_repo_button.click(list_repository_files, outputs=repo_files)
        
        clear_button = gr.Button("Clear Repository")
        clear_result = gr.Textbox(label="Clear Result")
        
        clear_button.click(clear_repository, outputs=clear_result)
    
    with gr.Tab("Chat"):
        gr.Markdown("### Ask questions about your documents")
        
        query_input = gr.Textbox(label="Your Question", placeholder="Ask something about your documents...")
        query_button = gr.Button("Ask")
        answer_output = gr.Textbox(label="Answer")
        
        query_button.click(query_knowledge_base, inputs=query_input, outputs=answer_output)

if __name__ == "__main__":
    app.launch(share=True) 