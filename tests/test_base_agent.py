import pytest
import asyncio
from unittest.mock import Mock, patch
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from agents.core.base_agent import BaseAgent
from typing import Any, List, Optional

class MockLLM(BaseLLM):
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        """Mock implementation of _generate."""
        return [{
            "text": "Mock response",
            "generation_info": {"finish_reason": "stop"}
        }]

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "mock"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Mock implementation of _call."""
        return "Mock response"

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def base_agent(mock_llm):
    return BaseAgent(mock_llm)

@pytest.mark.asyncio
async def test_base_agent_initialization(base_agent):
    assert base_agent.llm is not None
    assert base_agent.memory is not None
    assert base_agent.chain is not None

@pytest.mark.asyncio
async def test_base_agent_process(base_agent):
    response = await base_agent.process("Test input")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_base_agent_memory(base_agent):
    memory_state = base_agent.get_memory()
    assert isinstance(memory_state, dict)

@pytest.mark.asyncio
async def test_base_agent_clear_memory(base_agent):
    await base_agent.process("Test input")
    await base_agent.clear_memory()
    memory_state = base_agent.get_memory()
    assert len(memory_state.get('history', '')) == 0

@pytest.mark.asyncio
async def test_base_agent_error_handling(base_agent):
    with patch.object(base_agent.chain, '__call__', side_effect=Exception("Test error")):
        response = await base_agent.process("Test input")
        assert "Error" in response

