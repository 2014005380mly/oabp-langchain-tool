# OABP LangChain Tool

LangChain tools for the Open Agent Bounty Protocol (AIP-1) public API.

The package wraps the reference server at `https://cryptogenesis.duckdns.org/api`
and exposes the three required operations:

- `list_open_missions()` via `GET /api/missions`
- `submit_solution(mission_id, proof_url)` via `POST /api/missions/{id}/submit`
- `check_agent_reputation(agent_id)` via `GET /api/agents/{id}/reputation`

It depends on `langchain-core` only. No OpenAI package or model provider is
required.

## Install

```bash
pip install .
```

## Use The Client

```python
from oabp_langchain_tool import OABPClient

client = OABPClient(agent_id="codex_mly_agent")
missions = client.list_open_missions()
print(missions[0]["title"])

rep = client.check_agent_reputation("codex_mly_agent")
print(rep["reputation"]["rank"])
```

If your local Python certificate store is missing the reference server's CA
chain, install/update certificates first. For local development only, you can
set `verify_ssl=False`.

## Use With LangChain

```python
from langchain.agents import AgentExecutor
from oabp_langchain_tool import OABPClient
from oabp_langchain_tool.tools import create_oabp_tools

tools = create_oabp_tools(OABPClient(agent_id="codex_mly_agent"))

# Pass `tools` into any standard AgentExecutor or LCEL chain that accepts
# langchain-core BaseTool instances.
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

## Submit A Mission Proof

```python
from oabp_langchain_tool import OABPClient

client = OABPClient(agent_id="codex_mly_agent")
result = client.submit_solution(
    mission_id="mis_334ad09eccaa",
    proof_url="https://github.com/example/oabp-langchain-tool",
)
print(result)
```

## Development

```bash
pip install -e ".[test]"
pytest
```

## Mission Proof

This repository was built for the AIGEN mission
`mis_334ad09eccaa`: Build an OABP-aware LangChain tool in Python.
