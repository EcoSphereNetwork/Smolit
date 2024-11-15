import subprocess
from typing import Optional, Dict, Any
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ..core.base_agent import BaseAgent
from ..tools.command_executor import CommandExecutor

class CommandExecutionAgent(BaseAgent):
    def __init__(self, llm: BaseLLM):
        """Initialize the command execution agent."""
        super().__init__(llm)
        self.executor = CommandExecutor()
        self._initialize_chain()

    def _initialize_chain(self) -> None:
        """Initialize the command execution chain."""
        prompt = PromptTemplate(
            input_variables=["input", "history", "allowed_commands"],
            template="""
            Based on the conversation history:
            {history}
            
            Allowed commands: {allowed_commands}
            
            Human: {input}
            Assistant: Let me help you execute that command safely.
            
            1. Command Analysis:
            - Validate if the command is allowed
            - Check for potential security risks
            - Ensure proper command syntax
            
            2. Execution Plan:
            - Prepare command with proper arguments
            - Consider error handling
            """
        )
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command safely."""
        try:
            return await self.executor.execute(command)
        except Exception as e:
            return {
                "error": f"Error executing command: {str(e)}",
                "command": command
            }

    async def process(self, user_input: str) -> str:
        """Process user input and execute command if valid."""
        try:
            # Get chain's analysis
            response = await self.chain.arun(
                input=user_input,
                allowed_commands=str(self.executor.get_allowed_commands())
            )
            
            # TODO: Implement proper command extraction from chain response
            # For now, just return the analysis
            return response
            
        except Exception as e:
            return f"Error processing command request: {str(e)}"

    def get_allowed_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get list of allowed commands and their descriptions."""
        return self.executor.get_allowed_commands()

