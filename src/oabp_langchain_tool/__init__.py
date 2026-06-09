from .client import OABPClient

__all__ = [
    "OABPClient",
    "OABPListMissionsTool",
    "OABPSubmitSolutionTool",
    "OABPCheckReputationTool",
]


def __getattr__(name):
    if name in {"OABPListMissionsTool", "OABPSubmitSolutionTool", "OABPCheckReputationTool"}:
        from .tools import OABPCheckReputationTool, OABPListMissionsTool, OABPSubmitSolutionTool

        return {
            "OABPListMissionsTool": OABPListMissionsTool,
            "OABPSubmitSolutionTool": OABPSubmitSolutionTool,
            "OABPCheckReputationTool": OABPCheckReputationTool,
        }[name]
    raise AttributeError(name)
