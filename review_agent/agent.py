"""The agentic loop: review -> run tests -> verify with evidence -> report."""
from . import client as client_mod
from . import reviewer
from . import test_runner


def run(diff_text, repo_path=".", test_cmd="auto", model=None,
        api_key=None, base_url=None, timeout=180):
    """Run the full review loop. Returns a dict with model, findings, test output and report."""
    cli = client_mod.get_client(base_url=base_url, api_key=api_key)
    model_id = client_mod.get_model(model)

    # Pass 1: structured findings from the diff (Nemotron on Token Factory).
    findings = reviewer.review_diff(cli, model_id, diff_text)

    # Agentic step: run the project's tests so the second pass has evidence.
    if test_cmd == "auto":
        test_cmd = test_runner.detect_test_command(repo_path)
    test_output = (
        test_runner.run_tests(test_cmd, cwd=repo_path, timeout=timeout)
        if test_cmd else None
    )

    # Pass 2: verify findings against test evidence, emit the final report.
    report = reviewer.verify_and_report(cli, model_id, diff_text, findings, test_output)

    return {
        "model": model_id,
        "findings": findings,
        "test_command": test_cmd,
        "test_output": test_output,
        "report": report,
    }
