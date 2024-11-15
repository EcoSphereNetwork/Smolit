from typing import Dict, Any
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from ..core.base_agent import BaseAgent
from ..tools.web_browser import WebBrowser

class WebAgent(BaseAgent):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)
        self.browser = WebBrowser()

    def _initialize_chain(self):
        """Initialize the web browsing chain."""
        prompt = PromptTemplate(
            input_variables=["input", "history", "web_content"],
            template="""
            Based on the conversation history:
            {history}
            
            And the following web content:
            {web_content}
            
            Human: {input}
            Assistant: Let me help you with that web content.
            
            1. Content Analysis:
            - Extract key information
            - Identify main points
            - Note any relevant links
            
            2. Response:
            - Provide clear summary
            - Answer specific questions
            - Suggest related information
            """
        )
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    async def process(self, user_input: str) -> str:
        """Process user input using web browsing capabilities."""
        # Check if input is a URL
        if user_input.startswith(('http://', 'https://')):
            web_result = await self.browser.browse(user_input)
        else:
            # Treat as search query
            web_result = await self.browser.search(user_input)
        
        # Generate response using chain
        response = await self.chain.arun(
            input=user_input,
            web_content=str(web_result)
        )
        
        return response

    async def browse_url(self, url: str) -> Dict[str, Any]:
        """Browse a specific URL."""
        return await self.browser.browse(url)

    async def search_web(self, query: str) -> Dict[str, Any]:
        """Perform a web search."""
        return await self.browser.search(query)
