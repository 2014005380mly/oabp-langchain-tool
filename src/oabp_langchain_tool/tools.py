from __future__ import annotations

import json
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .client import OABPClient


class OABPToolBase(BaseTool):
    client: OABPClient = Field(default_factory=OABPClient)

    class Config:
        arbitrary_types_allowed = True


class OABPListMissionsTool(OABPToolBase):
    name: str = "oabp_list_open_missions"
    description: str = "List currently open OABP/AIP-1 bounty missions."

    def _run(self) -> str:
        return json.dumps(self.client.list_open_missions(), ensure_ascii=False, indent=2)


class SubmitSolutionArgs(BaseModel):
    mission_id: str = Field(..., description="OABP mission id, for example mis_334ad09eccaa.")
    proof_url: str = Field(..., description="Public URL proving the completed work.")
    submitter_wallet: str | None = Field(default=None, description="Optional wallet for USDC/ETH payouts.")


class OABPSubmitSolutionTool(OABPToolBase):
    name: str = "oabp_submit_solution"
    description: str = "Submit a proof URL to an OABP/AIP-1 mission."
    args_schema: Type[BaseModel] = SubmitSolutionArgs

    def _run(
        self,
        mission_id: str,
        proof_url: str,
        submitter_wallet: str | None = None,
    ) -> str:
        result = self.client.submit_solution(mission_id, proof_url, submitter_wallet)
        return json.dumps(result, ensure_ascii=False, indent=2)


class ReputationArgs(BaseModel):
    agent_id: str | None = Field(default=None, description="Agent id to inspect; defaults to this tool's agent.")


class OABPCheckReputationTool(OABPToolBase):
    name: str = "oabp_check_agent_reputation"
    description: str = "Check OABP/AIP-3 reputation, ELO, rank, and mission stats for an agent."
    args_schema: Type[BaseModel] = ReputationArgs

    def _run(self, agent_id: str | None = None) -> str:
        result = self.client.check_agent_reputation(agent_id)
        return json.dumps(result, ensure_ascii=False, indent=2)


def create_oabp_tools(client: OABPClient | None = None) -> list[BaseTool]:
    shared_client = client or OABPClient()
    return [
        OABPListMissionsTool(client=shared_client),
        OABPSubmitSolutionTool(client=shared_client),
        OABPCheckReputationTool(client=shared_client),
    ]

