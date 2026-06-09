from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class OABPClient:
    """Small stdlib client for the public OABP AIP-1 API."""

    base_url: str = "https://cryptogenesis.duckdns.org/api"
    agent_id: str = "codex_mly_agent"
    timeout: float = 20.0
    verify_ssl: bool = True

    def list_open_missions(self) -> list[dict[str, Any]]:
        data = self._get("/missions")
        missions = data.get("missions", data if isinstance(data, list) else [])
        return [mission for mission in missions if mission.get("status", "open") == "open"]

    def submit_solution(
        self,
        mission_id: str,
        proof_url: str,
        submitter_wallet: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "submitter_agent_id": self.agent_id,
            "proof": proof_url,
        }
        if submitter_wallet:
            payload["submitter_wallet"] = submitter_wallet
        return self._post(f"/missions/{quote(mission_id, safe='')}/submit", payload)

    def check_agent_reputation(self, agent_id: str | None = None) -> dict[str, Any]:
        target = quote(agent_id or self.agent_id, safe="")
        return self._get(f"/agents/{target}/reputation")

    def _get(self, path: str) -> Any:
        request = Request(self._url(path), headers={"Accept": "application/json"})
        return self._send(request)

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self._url(path),
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        return self._send(request)

    def _send(self, request: Request) -> Any:
        try:
            context = None if self.verify_ssl else ssl._create_unverified_context()
            with urlopen(request, timeout=self.timeout, context=context) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OABP API error {exc.code}: {raw_error}") from exc
        return json.loads(raw) if raw else {}

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
