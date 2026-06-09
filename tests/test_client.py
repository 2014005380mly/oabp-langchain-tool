import json

from oabp_langchain_tool import OABPClient
from oabp_langchain_tool.tools import (
    OABPCheckReputationTool,
    OABPListMissionsTool,
    OABPSubmitSolutionTool,
    create_oabp_tools,
)


class FakeClient:
    def list_open_missions(self):
        return [{"id": "mis_1", "status": "open", "title": "Build a thing"}]

    def submit_solution(self, mission_id, proof_url, submitter_wallet=None):
        return {
            "mission_id": mission_id,
            "proof": proof_url,
            "wallet": submitter_wallet,
            "status": "submitted",
        }

    def check_agent_reputation(self, agent_id=None):
        return {"agent_id": agent_id or "codex_mly_agent", "reputation": {"rank": "Newcomer"}}


def test_client_filters_open_missions(monkeypatch):
    client = OABPClient(base_url="https://example.invalid")

    def fake_get(path):
        assert path == "/missions"
        return {
            "missions": [
                {"id": "open", "status": "open"},
                {"id": "closed", "status": "closed"},
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)
    assert client.list_open_missions() == [{"id": "open", "status": "open"}]


def test_submit_solution_payload(monkeypatch):
    client = OABPClient(agent_id="agent_1", base_url="https://example.invalid")
    captured = {}

    def fake_post(path, payload):
        captured["path"] = path
        captured["payload"] = payload
        return {"ok": True}

    monkeypatch.setattr(client, "_post", fake_post)
    assert client.submit_solution("mis_1", "https://github.com/x/y") == {"ok": True}
    assert captured == {
        "path": "/missions/mis_1/submit",
        "payload": {
            "submitter_agent_id": "agent_1",
            "proof": "https://github.com/x/y",
        },
    }


def test_tools_return_json():
    fake = FakeClient()
    assert json.loads(OABPListMissionsTool(client=fake)._run())[0]["id"] == "mis_1"
    assert json.loads(OABPCheckReputationTool(client=fake)._run("agent_x"))["agent_id"] == "agent_x"
    submit = OABPSubmitSolutionTool(client=fake)
    output = json.loads(submit._run("mis_1", "https://github.com/x/y", "0x123"))
    assert output["status"] == "submitted"
    assert output["wallet"] == "0x123"


def test_create_oabp_tools_shares_client():
    fake = FakeClient()
    tools = create_oabp_tools(fake)
    assert len(tools) == 3
    assert all(tool.client is fake for tool in tools)

