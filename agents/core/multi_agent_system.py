from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOpenAI
from .supervisor import SupervisorAgent
from ..experts.command_agent import CommandExecutionAgent
from ..experts.rag_agent import RAGAgent
from ..experts.web_agent import WebAgent
import json
import os
from .logging_config import setup_logger

logger = setup_logger()

class MultiAgentSystem:
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """Initialize the multi-agent system."""
        try:
            # Initialize LLM with local or OpenAI settings
            self.llm = ChatOpenAI(
                model="TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile",
                openai_api_key=api_key or "sk-dummy-key",
                openai_api_base=api_base or "http://localhost:8080/v1",
                max_tokens=256
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
            logger.info("Multi-agent system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing multi-agent system: {e}")
            raise

    def _load_prompts(self) -> Dict[str, Any]:
        """Load system prompts from JSON file."""
        prompts_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'prompts', 'system_prompts.json'
        )
        try:
            with open(prompts_path, 'r') as f:
                prompts = json.load(f)
            logger.debug(f"Loaded prompts from {prompts_path}")
            return prompts
        except Exception as e:
            logger.error(f"Error loading prompts from {prompts_path}: {e}")
            return {}

    async def process_input(self, user_input: str) -> str:
        """Process user input through the multi-agent system."""
        try:
            logger.info(f"Processing user input: {user_input}")
            # Let supervisor analyze and route the request
            response = await self.supervisor.process(user_input)
            logger.debug(f"Response generated: {response}")
            return response
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def add_expert(self, name: str, agent: Any) -> None:
        """Add a new expert agent to the system."""
        try:
            self.experts[name] = agent
            self.supervisor.add_expert(name, agent)
            logger.info(f"Added new expert agent: {name}")
        except Exception as e:
            logger.error(f"Error adding expert {name}: {e}")
            raise

    def remove_expert(self, name: str) -> None:
        """Remove an expert agent from the system."""
        try:
            if name in self.experts:
                del self.experts[name]
                self.supervisor.remove_expert(name)
                logger.info(f"Removed expert agent: {name}")
        except Exception as e:
            logger.error(f"Error removing expert {name}: {e}")
            raise

    async def add_knowledge(self, documents: list) -> list:
        """Add documents to the RAG agent's knowledge base."""
        try:
            logger.info(f"Adding {len(documents)} documents to knowledge base")
            return await self.rag_agent.add_documents(documents)
        except Exception as e:
            logger.error(f"Error adding documents to knowledge base: {e}")
            return []

    async def browse_url(self, url: str) -> Dict[str, Any]:
        """Browse a URL using the web agent."""
        try:
            logger.info(f"Browsing URL: {url}")
            return await self.web_agent.browse_url(url)
        except Exception as e:
            error_msg = f"Error browsing URL: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    async def search_web(self, query: str) -> Dict[str, Any]:
        """Perform a web search using the web agent."""
        try:
            logger.info(f"Performing web search: {query}")
            return await self.web_agent.search_web(query)
        except Exception as e:
            error_msg = f"Error performing web search: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using the command agent."""
        try:
            logger.info(f"Executing command: {command}")
            return await self.command_agent.execute_command(command)
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

