#!/usr/bin/env python3
"""
Knowledge Base Chat Agent with Model Context Protocol (MCP)
This application allows users to:
1. Connect to their Google Drive
2. Select documents (PDF, CSV, Excel)
3. Process them without creating embeddings
4. Ask questions about the documents using MCP
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = [
    "ANTHROPIC_API_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your .env file.")
    exit(1)

# Import the Gradio app
from app import app

if __name__ == "__main__":
    # Launch the Gradio interface
    print("Starting Knowledge Base Chat Agent...")
    app.launch(share=True) 