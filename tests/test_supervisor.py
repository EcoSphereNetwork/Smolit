import pytest
import asyncio
from unittest.mock import Mock, patch
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain
from agents.core.supervisor import SupervisorAgent
from tests.test_base_agent import MockLLM

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
async def mock_expert():
    expert = Mock()
    async def mock_process(x):
        return "Expert response"
    expert.process = mock_process
    expert.get_memory = lambda: {"history": ""}
    return expert

@pytest.fixture
async def supervisor_agent(mock_llm, mock_expert):
    experts = {
        "test_expert": mock_expert
    }
    return SupervisorAgent(mock_llm, experts)

@pytest.mark.asyncio
async def test_supervisor_initialization(supervisor_agent):
    assert supervisor_agent.llm is not None
    assert supervisor_agent.expert_agents is not None
    assert len(supervisor_agent.expert_agents) > 0

@pytest.mark.asyncio
async def test_supervisor_process(supervisor_agent):
    response = await supervisor_agent.process("Test input")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_add_expert(supervisor_agent, mock_expert):
    supervisor_agent.add_expert("new_expert", mock_expert)
    assert "new_expert" in supervisor_agent.expert_agents
    assert supervisor_agent.expert_agents["new_expert"] == mock_expert

@pytest.mark.asyncio
async def test_remove_expert(supervisor_agent):
    supervisor_agent.remove_expert("test_expert")
    assert "test_expert" not in supervisor_agent.expert_agents

@pytest.mark.asyncio
async def test_get_expert_status(supervisor_agent):
    status = await supervisor_agent.get_expert_status()
    assert isinstance(status, dict)
    assert "test_expert" in status
    assert status["test_expert"]["available"] is True

@pytest.mark.asyncio
async def test_supervisor_error_handling(supervisor_agent):
    with patch.object(supervisor_agent.chain, '__call__', side_effect=Exception("Test error")):
        response = await supervisor_agent.process("Test input")
        assert "Error" in response

