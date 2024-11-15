from typing import Dict, Any, Optional
from langchain.llms import OpenAI
from .supervisor import SupervisorAgent
from ..experts.command_agent import CommandExecutionAgent
from ..experts.rag_agent import RAGAgent
from ..experts.web_agent import WebAgent
import json
import os

class MultiAgentSystem:
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        # Initialize LLM with local or OpenAI settings
        self.llm = OpenAI(
            openai_api_key=api_key or "lm_studio",
            openai_api_base=api_base or "http://localhost:1234/v1"
        )
        
        # Load system prompts
        self.prompts = self._load_prompts()
        
        # Initialize expert agents
        self.command_agent = CommandExecutionAgent(self.llm)
        self.rag_agent = RAGAgent(self.llm)
        self.web_agent = WebAgent(self.llm)
        
        # Create expert agents dictionary
        self.experts = {
            "command": self.command_agent,
            "knowledge": self.rag_agent,
            "web": self.web_agent
        }
        
        # Initialize supervisor
        self.supervisor = SupervisorAgent(self.llm, self.experts)

    def _load_prompts(self) -> Dict[str, Any]:
        """Load system prompts from JSON file."""
        prompts_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'prompts', 'system_prompts.json'
        )
        try:
            with open(prompts_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return {}

    async def process_input(self, user_input: str) -> str:
        """Process user input through the multi-agent system."""
        try:
            # Let supervisor analyze and route the request
            response = await self.supervisor.process(user_input)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def add_expert(self, name: str, agent: Any):
        """Add a new expert agent to the system."""
        self.experts[name] = agent
        self.supervisor.add_expert(name, agent)

    def remove_expert(self, name: str):
        """Remove an expert agent from the system."""
        if name in self.experts:
            del self.experts[name]
            self.supervisor.remove_expert(name)

    async def add_knowledge(self, documents: list):
        """Add documents to the RAG agent's knowledge base."""
        await self.rag_agent.add_documents(documents)

    async def browse_url(self, url: str) -> Dict[str, Any]:
        """Browse a URL using the web agent."""
        return await self.web_agent.browse_url(url)

    async def search_web(self, query: str) -> Dict[str, Any]:
        """Perform a web search using the web agent."""
        return await self.web_agent.search_web(query)

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using the command agent."""
        return await self.command_agent.execute_command(command)

