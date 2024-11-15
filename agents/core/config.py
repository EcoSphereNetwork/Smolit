import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
import subprocess
import time
import requests
import logging
import signal

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
        self.logger = logging.getLogger("smolit")
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
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.default_config

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

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

    def wait_for_model_download(self) -> bool:
        """Wait for the model to be downloaded."""
        model_file = "TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"
        for _ in range(60):  # Wait up to 5 minutes
            if os.path.exists(model_file):
                if os.path.getsize(model_file) > 900_000_000:  # ~900MB
                    self.logger.info("Model download completed")
                    return True
            time.sleep(5)
            self.logger.info("Waiting for model download...")
        return False

    def start_llama_server(self) -> bool:
        """Start the Llama server using start_llama_server.sh."""
        try:
            # Check if script exists
            if not os.path.exists("start_llama_server.sh"):
                self.logger.error("start_llama_server.sh not found")
                return False

            # Check if server is already running
            try:
                response = requests.get("http://localhost:8080")
                if response.status_code == 200:
                    self.logger.info("Llama server is already running")
                    return True
            except requests.exceptions.RequestException:
                pass

            # Start the server script with output redirection
            self.logger.info("Starting Llama server...")
            with open("llama_server.log", "w") as log_file:
                self.llama_server_process = subprocess.Popen(
                    ["./start_llama_server.sh"],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid  # Create new process group
                )

            # Wait for model download if needed
            if not self.wait_for_model_download():
                self.logger.error("Model download timeout")
                self.stop_llama_server()
                return False

            # Wait for server to start (max 30 seconds)
            for i in range(15):
                try:
                    response = requests.get("http://localhost:8080")
                    if response.status_code == 200:
                        self.logger.info("Llama server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    # Check server log for errors
                    if os.path.exists("llama_server.log"):
                        with open("llama_server.log", "r") as f:
                            log_content = f.read()
                            if "error" in log_content.lower():
                                self.logger.error(f"Server error: {log_content}")
                                return False
                    self.logger.info(f"Waiting for server... ({i+1}/15)")
                    continue

            self.logger.error("Timeout waiting for Llama server")
            return False
        except Exception as e:
            self.logger.error(f"Error starting Llama server: {e}")
            return False

    def stop_llama_server(self) -> None:
        """Stop the Llama server if it's running."""
        try:
            if self.llama_server_process:
                os.killpg(os.getpgid(self.llama_server_process.pid), signal.SIGTERM)
                self.llama_server_process = None
                self.logger.info("Llama server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping Llama server: {e}")

    def __del__(self):
        """Ensure server is stopped when config object is destroyed."""
        self.stop_llama_server()

