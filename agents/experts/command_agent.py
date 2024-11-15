import subprocess
from typing import Optional, Dict, Any
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from ..core.base_agent import BaseAgent

class CommandExecutionAgent(BaseAgent):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)
        self.allowed_commands = {
            'ls': 'List directory contents',
            'pwd': 'Print working directory',
            'cat': 'Display file contents',
            'echo': 'Display a line of text',
            'grep': 'Search for patterns in files'
        }

    def _initialize_chain(self):
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
        cmd_parts = command.split()
        if not cmd_parts:
            return {"error": "Empty command"}
            
        base_cmd = cmd_parts[0]
        if base_cmd not in self.allowed_commands:
            return {"error": f"Command '{base_cmd}' not allowed"}
            
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}

    async def process(self, user_input: str) -> str:
        """Process user input and execute command if valid."""
        # Get chain's analysis
        response = await self.chain.arun(
            input=user_input,
            allowed_commands=str(self.allowed_commands)
        )
        
        # Execute command if it's deemed safe
        # TODO: Implement proper command extraction from chain response
        # For now, just return the analysis
        return response
