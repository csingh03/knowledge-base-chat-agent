import os
import anthropic
from typing import List, Dict, Any, Optional

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def select_relevant_chunks(chunks: List[str], query: str, max_chunks: int = 5) -> List[str]:
    """
    Select the most relevant document chunks for the given query.
    Uses a simplified relevance scoring approach, which could be improved with better semantic matching.
    """
    # For real implementation, we could use BM25, TF-IDF, or other relevance scoring algorithms
    # Here we'll use a simple keyword matching approach
    query_terms = set(query.lower().split())
    
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        # Count how many query terms appear in the chunk
        score = sum(1 for term in query_terms if term in chunk.lower())
        chunk_scores.append((i, score))
    
    # Sort chunks by score in descending order
    sorted_chunks = sorted(chunk_scores, key=lambda x: x[1], reverse=True)
    
    # Return the top N chunks
    top_chunk_indices = [idx for idx, _ in sorted_chunks[:max_chunks]]
    return [chunks[i] for i in top_chunk_indices]

def create_context_from_chunks(chunks: List[str], max_tokens: int = 3000) -> str:
    """
    Combine document chunks into a single context string, 
    ensuring it doesn't exceed the maximum token limit.
    """
    context = ""
    estimated_tokens = 0
    
    for chunk in chunks:
        # Rough estimate: 1 token ≈ 4 characters
        chunk_tokens = len(chunk) // 4
        
        if estimated_tokens + chunk_tokens > max_tokens:
            break
            
        context += chunk + "\n\n---\n\n"
        estimated_tokens += chunk_tokens
    
    return context

def generate_answer(query: str, context: str) -> str:
    """
    Generate an answer using Claude 3.7 Sonnet with the Model Context Protocol approach.
    The context is directly inserted into the prompt without using embeddings.
    """
    prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context.
If the answer cannot be determined from the context, say "I don't have enough information to answer that."
Do not use any prior knowledge.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=500,
        temperature=0.2,
        system="You are a helpful assistant that answers questions based ONLY on the provided context.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def query_documents(query: str, all_chunks: List[str]) -> str:
    """Process a query against document chunks using Model Context Protocol."""
    # Select the most relevant chunks for the query
    relevant_chunks = select_relevant_chunks(all_chunks, query)
    
    # Create a context from the relevant chunks
    context = create_context_from_chunks(relevant_chunks)
    
    # Generate an answer using the context
    answer = generate_answer(query, context)
    
    return answer 