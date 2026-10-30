# Nemotron Review Agent

A code review agent for the **Nebius x NVIDIA Global AI Hackathon**
(Coding and Agentic Engineering track). Give it a diff: it reviews the code with
an NVIDIA Nemotron model, **runs your test suite**, then verifies each finding
against the test evidence before writing the final report. A genuine
review → run → verify agent loop, not a one-shot prompt.

## How it uses Nebius and NVIDIA

| Layer | What | Why |
|---|---|---|
| Inference | NVIDIA Nemotron on **Nebius Token Factory** (`https://api.tokenfactory.nebius.com/v1/`, OpenAI-compatible API) | All model calls go through Token Factory |
| Model | `nvidia/nemotron-3-super-120b-a12b` by default (override with `NEMOTRON_MODEL`, e.g. `nvidia/nemotron-3-nano-30b-a3b` for cheap runs, `nvidia/nemotron-3-ultra-550b-a55b` for deep reasoning) | Fast/cheap vs. deep-reasoning tradeoff per call |
| Agent loop | Pass 1: structured JSON findings → run tests → Pass 2: verify findings against test output | The agent *runs and tests code*, per the track brief |

## Quickstart

```bash
pip install -r requirements.txt
export NEBIUS_API_KEY=<your Token Factory key>   # create at https://tokenfactory.nebius.com/

# Review a diff file, auto-detect and run the project's tests:
python -m review_agent.cli --diff examples/sample.diff

# Review the uncommitted changes of a repo:
python -m review_agent.cli --repo /path/to/repo --range HEAD

# Pipe a diff in, skip tests, save the report:
git diff | python -m review_agent.cli --stdin --test-cmd none -o report.md

# List models served by Token Factory:
python -m review_agent.cli --list-models
```

## Web UI (for the hosted demo)

```bash
python app.py   # Gradio UI on :7860, deploy as-is to Hugging Face Spaces or Docker
```

`Dockerfile` is included (`docker build -t review-agent .`, pass `-e NEBIUS_API_KEY` at run).

## How it works

1. **Review pass**: the diff goes to Nemotron with a senior-engineer system prompt;
   findings come back as strict JSON (`file`, `line`, `severity`, `category`,
   `title`, `description`, `suggestion`).
2. **Test run**: the agent runs your test command (`auto` detects pytest / npm / go,
   or pass `--test-cmd`) with a timeout and captures the output.
3. **Verification pass**: findings + test output go back to Nemotron, which keeps,
   drops, or annotates each finding with test evidence and writes the final
   markdown report.

## Hackathon submission checklist

- [x] Runs on Nebius Token Factory, uses NVIDIA Nemotron
- [x] Public repo with an open-source license (MIT, see LICENSE)
- [x] README with setup and run instructions
- [ ] Demo URL (deploy `app.py`: Hugging Face Spaces / Docker)
- [ ] ≤3 min demo video showing the agent on a real diff
- [ ] Project description + feedback on Token Factory/Nemotron (Devpost form)

## Feedback on Nebius Token Factory and Nemotron

- Token Factory is OpenAI-compatible as documented. `client.models.list()` returned the Nemotron IDs from the docs. No SDK changes needed.
- Structured output (`response_format: {"type": "json_object"}`) worked on `nvidia/nemotron-3-super-120b-a12b`. Six model calls across three end-to-end runs, valid JSON every time, no repair pass triggered.
- Roughly 5 to 10 seconds per call. Fast enough for an interactive review loop.
- Billing docs matched the signup flow: card required, $1 trial credit stated. The credit did not show in the console balance immediately after signup (still $0 at time of writing). Either a display delay or a grant delay.

## License

MIT, see [LICENSE](LICENSE).
