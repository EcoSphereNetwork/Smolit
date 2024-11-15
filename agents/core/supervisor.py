from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain
from .base_agent import BaseAgent
import asyncio

class SupervisorAgent(BaseAgent):
    def __init__(self, llm: BaseLLM, expert_agents: Dict[str, BaseAgent]):
        """Initialize the supervisor agent."""
        super().__init__(llm)
        self.expert_agents = expert_agents
        self._initialize_chain()

    def _initialize_chain(self) -> None:
        """Initialize the supervisor chain with routing logic."""
        prompt = PromptTemplate(
            input_variables=["input", "history", "available_experts"],
            template="""
            Based on the conversation history:
            {history}
            
            Available expert agents: {available_experts}
            
            Human: {input}
            Assistant: Let me analyze the request and route it to the appropriate expert.
            
            1. Task Analysis:
            - Identify the main task or query
            - Determine required expertise
            
            2. Expert Selection:
            - Choose the most suitable expert(s)
            - Consider if multiple experts are needed
            
            3. Response Plan:
            - Outline steps to fulfill the request
            - Coordinate between experts if needed
            """
        )
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    async def process(self, user_input: str) -> str:
        """Process user input by routing to appropriate expert(s)."""
        try:
            # Get available experts list
            experts_list = ", ".join(self.expert_agents.keys())
            
            # Get supervisor's decision
            response = await self.chain.arun(
                input=user_input,
                available_experts=experts_list
            )
            
            # TODO: Implement proper response parsing and expert routing
            # For now, return supervisor's analysis
            return response
            
        except Exception as e:
            return f"Error in supervisor processing: {str(e)}"

    def add_expert(self, name: str, agent: BaseAgent) -> None:
        """Add a new expert agent to the supervisor."""
        try:
            self.expert_agents[name] = agent
        except Exception as e:
            print(f"Error adding expert {name}: {e}")

    def remove_expert(self, name: str) -> None:
        """Remove an expert agent from the supervisor."""
        try:
            if name in self.expert_agents:
                del self.expert_agents[name]
        except Exception as e:
            print(f"Error removing expert {name}: {e}")

    async def get_expert_status(self) -> Dict[str, Any]:
        """Get status of all expert agents."""
        try:
            return {
                name: {
                    "available": True,
                    "memory": agent.get_memory()
                }
                for name, agent in self.expert_agents.items()
            }
        except Exception as e:
            return {"error": f"Error getting expert status: {str(e)}"}

