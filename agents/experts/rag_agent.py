from typing import List, Dict, Any
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..core.base_agent import BaseAgent
from ..tools.knowledge_base import KnowledgeBase

class RAGAgent(BaseAgent):
    def __init__(self, llm: BaseLLM, knowledge_base_path: str = "./knowledge"):
        """Initialize the RAG agent."""
        super().__init__(llm)
        self.knowledge_base = KnowledgeBase(knowledge_base_path)
        self._initialize_chain()

    def _initialize_chain(self) -> None:
        """Initialize the RAG chain."""
        prompt = PromptTemplate(
            input_variables=["input", "history", "context"],
            template="""
            Based on the conversation history:
            {history}
            
            And the following relevant context:
            {context}
            
            Human: {input}
            Assistant: Let me help you with that based on the available information.
            """
        )
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    async def add_documents(self, documents: List[str]) -> List[str]:
        """Add new documents to the knowledge base."""
        try:
            doc_ids = []
            for doc in documents:
                doc_id = await self.knowledge_base.add_document(doc)
                doc_ids.append(doc_id)
            return doc_ids
        except Exception as e:
            print(f"Error adding documents: {e}")
            return []

    async def process(self, user_input: str) -> str:
        """Process user input using RAG."""
        try:
            # Retrieve relevant documents
            docs = await self.knowledge_base.query(user_input, n_results=3)
            
            # Format context from retrieved documents
            context = "\n".join(
                f"Document {i+1}:\n{doc['content']}"
                for i, doc in enumerate(docs)
                if 'error' not in doc
            )
            
            if not context:
                context = "No relevant information found in knowledge base."
            
            # Generate response using retrieved context
            response = await self.chain.arun(
                input=user_input,
                context=context
            )
            
            return response
            
        except Exception as e:
            return f"Error processing RAG request: {str(e)}"

    async def get_relevant_docs(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get relevant documents for a query."""
        try:
            return await self.knowledge_base.query(query, n_results=k)
        except Exception as e:
            return [{"error": f"Error retrieving documents: {str(e)}"}]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return self.knowledge_base.get_stats()

