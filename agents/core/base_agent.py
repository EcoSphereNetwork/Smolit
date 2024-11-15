from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferMemory

class BaseAgent:
    def __init__(self, llm: BaseLLM, memory: Optional[ConversationBufferMemory] = None):
        self.llm = llm
        self.memory = memory or ConversationBufferMemory()
        self.chain = None
        self._initialize_chain()

    def _initialize_chain(self):
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
        return await self.chain.arun(input=user_input)

    def get_memory(self) -> Dict[str, Any]:
        """Get current memory state."""
        return self.memory.load_memory_variables({})
