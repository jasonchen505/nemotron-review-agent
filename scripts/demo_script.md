# Demo video script (≤ 3 min)

Record your screen with voiceover. Total budget: 3 minutes.

## 0:00–0:20: What it is
"Nemotron Review Agent, a code review agent for the Coding and Agentic
Engineering track. Paste in a diff: it reviews the code with NVIDIA Nemotron,
runs your test suite, then verifies each finding against the test evidence."

## 0:20–1:40: Live CLI run
```bash
export NEBIUS_API_KEY=<your-key>
python -m review_agent.cli --diff examples/sample.diff \
  --test-cmd "python -m pytest examples/demo_shop/tests -q" -o report.md
```
(use the venv python you installed requirements into)
- Show the terminal: findings appear as a markdown report.
- Point out one caught bug (e.g. the mutable default arg / SQL injection in
  `examples/sample.diff`) and the "Test evidence" line under a finding.
  Two findings are kept with test evidence; the third is dropped as
  "not covered by tests". That honest keep/drop is the agentic part.

## 1:40–2:30: Web UI
```bash
python app.py
```
- Open localhost:7860, paste a diff, click Review, show the report rendering.

## 2:30–3:00: How Nebius + NVIDIA are used (judges look for this)
- "Every model call goes through Nebius Token Factory's OpenAI-compatible API
  at api.tokenfactory.nebius.com/v1."
- "Default model is nvidia/nemotron-3-super-120b-a12b; Nano for cheap runs,
  Ultra for deep reasoning, switchable via NEMOTRON_MODEL."
- "The agent loop is review → run tests → verify with evidence, not a one-shot
  prompt. That's the agentic engineering part."
- Close: repo link + "built for the Nebius x NVIDIA Global AI Hackathon".

## Tips
- Do one dry run first so the model calls are warm.
- Keep the terminal font large.
- Upload as public/unlisted YouTube video for the Devpost submission.
