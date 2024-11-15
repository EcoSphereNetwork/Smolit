from typing import List, Dict, Any
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..core.base_agent import BaseAgent

class RAGAgent(BaseAgent):
    def __init__(self, llm: BaseLLM, knowledge_base_path: str = "./knowledge"):
        super().__init__(llm)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.initialize_knowledge_base(knowledge_base_path)

    def initialize_knowledge_base(self, knowledge_base_path: str):
        """Initialize the vector store with documents from knowledge base."""
        try:
            # Load existing vector store or create new one
            self.vector_store = Chroma(
                persist_directory=knowledge_base_path,
                embedding_function=self.embeddings
            )
        except Exception:
            # If no existing store, create empty one
            self.vector_store = Chroma(
                embedding_function=self.embeddings
            )

    def _initialize_chain(self):
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

    async def add_documents(self, documents: List[str]):
        """Add new documents to the knowledge base."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.create_documents(documents)
        self.vector_store.add_documents(texts)

    async def process(self, user_input: str) -> str:
        """Process user input using RAG."""
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(user_input, k=3)
        context = "\n".join(doc.page_content for doc in docs)
        
        # Generate response using retrieved context
        response = await self.chain.arun(
            input=user_input,
            context=context
        )
        
        return response

    def get_relevant_docs(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get relevant documents for a query."""
        docs = self.vector_store.similarity_search(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
