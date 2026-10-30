"""Two-pass review: (1) structured findings from the diff, (2) verified report with test evidence."""
import json

REVIEW_SYSTEM_PROMPT = """\
You are a senior software engineer doing code review. You are given a unified diff.
Find real issues. Be precise and concrete; cite file paths and line numbers from the diff.
Do NOT invent issues that are not supported by the diff. If the diff is trivial or clean, return an empty findings list.

Return ONLY valid JSON, no markdown fences, with this exact shape:
{"findings": [{"file": "path/to/file.py", "line": 42, "severity": "critical|major|minor|nit", "category": "bug|security|performance|maintainability|style", "title": "short title", "description": "what is wrong and why it matters", "suggestion": "concrete fix"}]}

Severity guide: critical = crash / data loss / security hole; major = likely bug or serious perf issue;
minor = small correctness or robustness concern; nit = style / readability.
"""

VERIFY_SYSTEM_PROMPT = """\
You are verifying code-review findings against test evidence.
You receive: the original unified diff, the findings from a first review pass, and the output of running the project's test suite (which may be absent).

For each finding, decide KEEP or DROP. Drop findings contradicted by passing tests or not supported by evidence.
Write the final review as markdown:

# Code Review Report
## Summary
<2-3 sentence overall assessment>
## Findings
For each kept finding, in severity order:
### [severity] title (`file:line`)
- Category: ...
- Description: ...
- Suggestion: ...
- Test evidence: <what the test run showed, or "not covered by tests">
## Dropped
<Bulleted list of dropped findings with one-line reasons, or "None.">

Be honest: if tests don't cover a finding, say so instead of claiming verification.
"""

MAX_DIFF_CHARS = 60000


def _chat(client, model, system, user, temperature=0.2, max_tokens=4096, json_mode=False):
    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


def _parse_findings(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # drop opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    data = json.loads(text)
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings is not a list")
    return findings


def review_diff(client, model, diff_text):
    """First pass: structured findings from the diff."""
    if not diff_text.strip():
        raise ValueError("empty diff")
    user = f"Review this unified diff:\n\n{diff_text[:MAX_DIFF_CHARS]}"
    raw = _chat(client, model, REVIEW_SYSTEM_PROMPT, user, json_mode=True)
    try:
        return _parse_findings(raw)
    except (json.JSONDecodeError, ValueError):
        repair = _chat(
            client,
            model,
            "You output invalid JSON. Re-emit ONLY the corrected JSON object, no other text.",
            f"Invalid output:\n{raw}",
            json_mode=True,
        )
        return _parse_findings(repair)


def verify_and_report(client, model, diff_text, findings, test_output):
    """Second pass: verify findings against test evidence, emit final markdown report."""
    test_block = test_output if test_output else "(no test run was performed)"
    user = (
        f"Original diff:\n{diff_text[:MAX_DIFF_CHARS]}\n\n"
        f"First-pass findings (JSON):\n{json.dumps(findings, indent=2)}\n\n"
        f"Test output:\n{test_block}\n\n"
        "Write the final review report."
    )
    return _chat(client, model, VERIFY_SYSTEM_PROMPT, user, temperature=0.3, max_tokens=4096)
