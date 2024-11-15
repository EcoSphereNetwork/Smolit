import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
import subprocess
import time
import requests

@dataclass
class LLMEndpoint:
    name: str
    api_base: str
    api_key: str
    model: str
    type: str  # 'openai', 'llama', 'custom'

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.llama_server_process = None
        self.default_config = {
            "endpoints": {
                "lm_studio": {
                    "name": "LM Studio",
                    "api_base": "http://localhost:1234/v1",
                    "api_key": "lm_studio",
                    "model": "local",
                    "type": "openai"
                },
                "llama": {
                    "name": "Local Llama",
                    "api_base": "http://localhost:8080",
                    "api_key": "",
                    "model": "TinyLlama-1.1B-Chat",
                    "type": "llama"
                }
            },
            "active_endpoint": "lm_studio"
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return self.default_config
        except Exception:
            return self.default_config

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_active_endpoint(self) -> LLMEndpoint:
        """Get the currently active endpoint configuration."""
        active = self.config["active_endpoint"]
        endpoint = self.config["endpoints"][active]
        return LLMEndpoint(**endpoint)

    def set_active_endpoint(self, name: str) -> None:
        """Set the active endpoint by name."""
        if name in self.config["endpoints"]:
            self.config["active_endpoint"] = name
            self.save_config()

    def add_endpoint(self, endpoint: LLMEndpoint) -> None:
        """Add a new endpoint configuration."""
        self.config["endpoints"][endpoint.name] = {
            "name": endpoint.name,
            "api_base": endpoint.api_base,
            "api_key": endpoint.api_key,
            "model": endpoint.model,
            "type": endpoint.type
        }
        self.save_config()

    def remove_endpoint(self, name: str) -> None:
        """Remove an endpoint configuration."""
        if name in self.config["endpoints"]:
            del self.config["endpoints"][name]
            if self.config["active_endpoint"] == name:
                self.config["active_endpoint"] = next(iter(self.config["endpoints"]))
            self.save_config()

    def start_llama_server(self) -> bool:
        """Start the Llama server using start_llama_server.sh."""
        try:
            # Start the server script
            self.llama_server_process = subprocess.Popen(
                ["./start_llama_server.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for server to start (max 30 seconds)
            for _ in range(15):
                try:
                    response = requests.get("http://localhost:8080")
                    if response.status_code == 200:
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    continue

            return False
        except Exception:
            return False

    def stop_llama_server(self) -> None:
        """Stop the Llama server if it's running."""
        if self.llama_server_process:
            self.llama_server_process.terminate()
            self.llama_server_process = None

    def __del__(self):
        """Ensure server is stopped when config object is destroyed."""
        self.stop_llama_server()
