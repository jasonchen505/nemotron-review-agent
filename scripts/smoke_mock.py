"""End-to-end smoke test with a mocked Token Factory client (no API key needed).

Runs the full agent loop — review pass, test run, verification pass — against
examples/sample.diff using canned model responses.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from review_agent import agent as agent_mod

REVIEW_JSON = {
    "findings": [
        {
            "file": "pricing.py",
            "line": 1,
            "severity": "major",
            "category": "bug",
            "title": "Mutable default argument",
            "description": "history=[] is shared across calls",
            "suggestion": "Use history=None and create the list inside.",
        }
    ]
}


class _Msg:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content):
        self.choices = [_Choice(content)]


class _Completions:
    def create(self, **kwargs):
        if kwargs.get("response_format"):
            return _Resp(json.dumps(REVIEW_JSON))
        return _Resp(
            "# Code Review Report\n## Summary\nMock verified.\n"
            "## Findings\n### [major] Mutable default argument\n## Dropped\nNone.\n"
        )


class _Chat:
    completions = _Completions()


class FakeClient:
    chat = _Chat()


agent_mod.client_mod.get_client = lambda **kw: FakeClient()
agent_mod.client_mod.get_model = lambda explicit=None: "mock-model"

diff = Path("examples/sample.diff").read_text(encoding="utf-8")
result = agent_mod.run(diff, test_cmd="echo mock-tests-ok", repo_path=".")

assert "Code Review Report" in result["report"], "report missing"
assert result["findings"][0]["title"] == "Mutable default argument"
assert "mock-tests-ok" in (result["test_output"] or "")
print("SMOKE OK")
print("model:", result["model"])
print("test_command:", result["test_command"])
