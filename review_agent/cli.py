"""CLI: review-agent --diff FILE | --stdin | --repo DIR --range REV"""
import argparse
import subprocess
import sys
from pathlib import Path

from . import agent as agent_mod
from . import client as client_mod


def read_diff(args):
    if args.diff:
        return Path(args.diff).read_text(encoding="utf-8")
    if args.stdin or (not args.repo and not sys.stdin.isatty()):
        return sys.stdin.read()
    if args.repo:
        cmd = ["git", "-C", args.repo, "diff", args.range]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"git diff failed: {proc.stderr.strip()}")
        return proc.stdout
    raise SystemExit("error: provide --diff, --stdin, or --repo")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="review-agent",
        description="Code review agent powered by NVIDIA Nemotron on Nebius Token Factory.",
    )
    src = p.add_mutually_exclusive_group()
    src.add_argument("--diff", help="path to a unified diff file")
    src.add_argument("--stdin", action="store_true", help="read diff from stdin")
    src.add_argument("--repo", help="git repo path; the diff is generated with git")
    p.add_argument("--range", default="HEAD",
                   help="git revision/range used with --repo (default: HEAD)")
    p.add_argument("--test-cmd", default="auto",
                   help='"auto" (default), "none", or a shell command to run as tests')
    p.add_argument("--model", default=None,
                   help="Token Factory model id (default: $NEMOTRON_MODEL or nemotron-3-super)")
    p.add_argument("--timeout", type=int, default=180,
                   help="test command timeout in seconds (default: 180)")
    p.add_argument("--output", "-o", help="write the markdown report to a file")
    p.add_argument("--list-models", action="store_true",
                   help="list models served by Token Factory and exit")
    args = p.parse_args(argv)

    if args.list_models:
        cli = client_mod.get_client()
        for mid, owner in client_mod.list_models(cli):
            print(f"{mid}  ({owner})")
        return 0

    diff_text = read_diff(args)
    if not diff_text.strip():
        print("error: empty diff", file=sys.stderr)
        return 2

    test_cmd = None if args.test_cmd == "none" else args.test_cmd
    result = agent_mod.run(
        diff_text,
        repo_path=args.repo or ".",
        test_cmd=test_cmd,
        model=args.model,
        timeout=args.timeout,
    )
    if args.output:
        Path(args.output).write_text(result["report"], encoding="utf-8")
        print(f"wrote {args.output}  (model={result['model']}, "
              f"findings={len(result['findings'])}, test={result['test_command']})")
    else:
        print(result["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
