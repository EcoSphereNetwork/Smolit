import subprocess
import shlex
from typing import Dict, Any, List, Optional
import os
import re

class CommandExecutor:
    def __init__(self):
        self.allowed_commands = {
            'ls': {'description': 'List directory contents', 'allowed_args': ['-l', '-a', '-h', '--help']},
            'pwd': {'description': 'Print working directory', 'allowed_args': ['--help']},
            'cat': {'description': 'Display file contents', 'allowed_args': ['-n', '--number']},
            'grep': {'description': 'Search for patterns', 'allowed_args': ['-i', '-n', '-v', '-r']},
            'echo': {'description': 'Display text', 'allowed_args': ['-n', '-e']},
            'find': {'description': 'Search for files', 'allowed_args': ['-name', '-type', '-size']},
        }
        self.blocked_patterns = [
            r'[;&|]',  # Command chaining
            r'>[>]?',  # Output redirection
            r'<',      # Input redirection
            r'\$\(',   # Command substitution
            r'`',      # Backtick substitution
        ]

    def is_safe_command(self, command: str) -> bool:
        """Check if a command is safe to execute."""
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, command):
                return False
        
        # Parse command and arguments
        try:
            parts = shlex.split(command)
        except ValueError:
            return False
            
        if not parts:
            return False
            
        base_cmd = parts[0]
        
        # Check if base command is allowed
        if base_cmd not in self.allowed_commands:
            return False
            
        # Check arguments
        allowed_args = self.allowed_commands[base_cmd]['allowed_args']
        for arg in parts[1:]:
            if arg.startswith('-'):
                if arg not in allowed_args:
                    return False
                    
        return True

    async def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a command safely."""
        if not self.is_safe_command(command):
            return {
                'error': 'Command not allowed or contains unsafe patterns',
                'command': command
            }
            
        try:
            # Split command into parts
            cmd_parts = shlex.split(command)
            
            # Execute command with timeout
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            return {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'error': f'Command timed out after {timeout} seconds',
                'command': command
            }
        except Exception as e:
            return {
                'error': str(e),
                'command': command
            }

    def get_allowed_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get list of allowed commands and their descriptions."""
        return self.allowed_commands
