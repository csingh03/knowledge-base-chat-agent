# Internal Knowledge Chat Agent (MCP)

A proof of concept for an internal knowledge base chat agent that uses the Model Context Protocol (MCP) approach to answer questions based on document content without creating embeddings.

## Overview

This application enables users to:

1. Connect to their Google Drive account
2. Select documents (PDF, CSV, Excel files) for processing
3. Ask questions about these documents
4. Get answers directly derived from document content

The system uses a direct context insertion approach rather than vector embeddings, implementing the Model Context Protocol concept.

## Technical Architecture

The application consists of:

- **Google Drive Integration**: Authentication and document retrieval
- **Document Processing**: Extracting and chunking text from various file formats
- **Document Repository**: Managing and storing document chunks
- **Query Processing**: Using Model Context Protocol to match queries to relevant content
- **Claude 3.5 Sonnet Integration**: Generating answers based on relevant document context
- **Gradio Interface**: Simple user interface for interaction

## Setup Instructions

### Prerequisites

- Python 3.9+
- Google Cloud Platform account with OAuth credentials
- Anthropic API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/knowledge-base-chat.git
   cd knowledge-base-chat
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:7860/oauth2callback
   ```

### Google Cloud Setup

1. Create a project in Google Cloud Console
2. Enable the Google Drive API
3. Create OAuth 2.0 credentials
4. Add the redirect URI: `http://localhost:7860/oauth2callback`

### Running the Application

Start the application:
```
python src/index.py
```

The Gradio interface will be accessible at: `http://localhost:7860`

## Usage

1. Go to the "Authentication" tab and connect your Google Drive
2. In the "Document Management" tab, refresh and view your Google Drive files
3. Select files to process by entering comma-separated file IDs
4. Switch to the "Chat" tab to ask questions about your documents

## Model Context Protocol (MCP)

Unlike typical RAG systems that use vector embeddings, this application:

1. Chunks documents into manageable pieces
2. Uses a simple keyword-based relevance approach to find related content
3. Directly inserts relevant chunks into the LLM's context window
4. Instructs the LLM to answer based solely on the provided context

This approach eliminates the need for embedding models and vector databases while still providing focused, document-based responses.

## Limitations

This proof of concept has several limitations:

- Simple keyword-based relevance detection (not semantic matching)
- Limited to text and simple tabular data in PDFs, CSVs, and Excel files
- Credentials stored in memory (not persistent)
- Basic error handling
- No chat history or session management

## Future Improvements

- Improved chunk relevance scoring with BM25 or TF-IDF
- Support for more file types
- Secure credential storage
- Multi-user support
- Chat history and conversation management
- Source attribution for answers
- Performance optimizations for larger document sets 