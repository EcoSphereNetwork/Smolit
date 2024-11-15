import pytest
import asyncio
from unittest.mock import Mock, patch
from agents.core.multi_agent_system import MultiAgentSystem
from langchain_community.llms.openai import OpenAI
from tests.test_base_agent import MockLLM

@pytest.fixture
def multi_agent_system():
    with patch('langchain_community.llms.openai.OpenAI', return_value=MockLLM()):
        system = MultiAgentSystem(
            api_key="test_key",
            api_base="http://localhost:1234/v1"
        )
        return system

@pytest.mark.asyncio
async def test_system_initialization(multi_agent_system):
    assert multi_agent_system.llm is not None
    assert multi_agent_system.supervisor is not None
    assert len(multi_agent_system.experts) > 0
    assert "command" in multi_agent_system.experts
    assert "knowledge" in multi_agent_system.experts
    assert "web" in multi_agent_system.experts

@pytest.mark.asyncio
async def test_command_execution(multi_agent_system):
    response = await multi_agent_system.execute_command("ls")
    assert isinstance(response, dict)
    assert "error" not in response or not response["error"]

@pytest.mark.asyncio
async def test_web_browsing(multi_agent_system):
    response = await multi_agent_system.browse_url("http://example.com")
    assert isinstance(response, dict)
    assert "error" not in response or not response["error"]

@pytest.mark.asyncio
async def test_knowledge_base(multi_agent_system):
    # Test adding documents
    docs = ["Test document 1", "Test document 2"]
    doc_ids = await multi_agent_system.add_knowledge(docs)
    assert isinstance(doc_ids, list)
    assert len(doc_ids) == len(docs)

@pytest.mark.asyncio
async def test_end_to_end_chat(multi_agent_system):
    # Test regular chat
    response = await multi_agent_system.process_input("Hello, how are you?")
    assert isinstance(response, str)
    assert len(response) > 0

    # Test command execution
    response = await multi_agent_system.process_input("List files in current directory")
    assert isinstance(response, str)
    assert len(response) > 0

    # Test web browsing
    response = await multi_agent_system.process_input("Search for Python programming")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_error_handling(multi_agent_system):
    # Test invalid command
    response = await multi_agent_system.execute_command("invalid_command")
    assert isinstance(response, dict)
    assert "error" in response

    # Test invalid URL
    response = await multi_agent_system.browse_url("invalid_url")
    assert isinstance(response, dict)
    assert "error" in response

    # Test system error handling
    with patch.object(multi_agent_system.supervisor, 'process', 
                     side_effect=Exception("Test error")):
        response = await multi_agent_system.process_input("Test input")
        assert "Error" in response

