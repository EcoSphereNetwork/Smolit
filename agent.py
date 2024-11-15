#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ========================================================#
# This file is a part of Smolit package            #
# Website: **Smolitux**                                   #
# GitHub:  https://github.com/eco-sphere-network/smolitux #
# MIT License                                             #
# Created By  : Sam Schimmelpfennig                       #
# Updated Date: 28.10.2024 10:00:00                       #
# ========================================================#

import requests
import subprocess

# Configuration for local LM Studio server
API_URL_BASE = "http://localhost:1234/v1/"
API_KEY = "lm_studio"

class AgentExperts:
    
    @staticmethod
    def call_local_llm(prompt):
        """Function to call the local LLM API."""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
        }
        
        try:
            response = requests.post(f"{API_URL_BASE}chat/completions", json=data, headers=headers)
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        
        except Exception as e:
            return f"Error fetching response: {e}"
    
    @staticmethod
    def run_script(script_name, *args):
        """Run an external script and return its output."""
        try:
            result = subprocess.run(
                ["python", script_name] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error running {script_name}: {e}"

    @staticmethod
    def expert_agent_1(user_input):
        """Expert agent for web searching."""
        # Here you can choose to run script1.py with user_input as an argument
        return AgentExperts.run_script("script1.py", user_input)

    @staticmethod
    def expert_agent_2(user_input):
        """Expert agent for calculations."""
        # Here you can choose to run script2.py with user_input as an argument
        return AgentExperts.run_script("script2.py", user_input)

    @staticmethod
    def web_search_tool(query):
        """Simulated web search functionality."""
        return f"Search results for: {query}"

    @staticmethod
    def expert_agent_1_with_tool(user_input):
        """Expert agent that uses a web search tool."""
        if "search" in user_input:
            return AgentExperts.web_search_tool(user_input)
        return AgentExperts.expert_agent_1(user_input)

    @staticmethod
    def main_agent(user_input):
        """Main agent that delegates tasks to expert agents based on commands."""
        if user_input.startswith("search"):
            return AgentExperts.expert_agent_1_with_tool(user_input)
        elif user_input.startswith("calculate"):
            return AgentExperts.expert_agent_2(user_input) 
        else:
            return AgentExperts.call_local_llm(user_input)
