from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferMemory
import asyncio

class BaseAgent:
    def __init__(self, llm: BaseLLM, memory: Optional[ConversationBufferMemory] = None):
        """Initialize the base agent."""
        self.llm = llm
        self.memory = memory or ConversationBufferMemory()
        self.chain = None
        self._initialize_chain()

    def _initialize_chain(self) -> None:
        """Initialize the LLM chain with default prompt."""
        prompt = PromptTemplate(
            input_variables=["input", "history"],
            template="""
            Based on the conversation history:
            {history}
            
            Human: {input}
            Assistant: Let me help you with that.
            """
        )
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    async def process(self, user_input: str) -> str:
        """Process user input and return response."""
        try:
            return await self.chain.arun(input=user_input)
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def get_memory(self) -> Dict[str, Any]:
        """Get current memory state."""
        try:
            return self.memory.load_memory_variables({})
        except Exception as e:
            return {"error": f"Error loading memory: {str(e)}"}

    async def clear_memory(self) -> None:
        """Clear the agent's memory."""
        try:
            self.memory.clear()
        except Exception as e:
            print(f"Error clearing memory: {e}")

