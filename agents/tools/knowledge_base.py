import os
from typing import List, Dict, Any, Optional
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
import json

class KnowledgeBase:
    def __init__(self, persist_directory: str = "./knowledge"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Use OpenAI embeddings
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key="lm_studio",  # Using LM Studio
            api_base="http://localhost:1234/v1"
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="smolit_knowledge",
            embedding_function=self.embedding_function
        )

    async def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document to the knowledge base."""
        try:
            # Generate a unique ID
            doc_id = str(hash(content))
            
            # Add document to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            return doc_id
            
        except Exception as e:
            return f"Error adding document: {str(e)}"

    async def query(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query the knowledge base."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
                
            return documents
            
        except Exception as e:
            return [{'error': f"Error querying knowledge base: {str(e)}"}]

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    async def update_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a document in the knowledge base."""
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata or {}]
            )
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': self.collection.name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {'error': f"Error getting stats: {str(e)}"}
