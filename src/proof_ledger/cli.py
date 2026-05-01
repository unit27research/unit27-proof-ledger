from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from proof_ledger.core import LedgerError, generate_packet, get_case, init_project, load_ledger, next_run_id, record_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="proof-ledger",
        description="Turn eval runs, demo commands, and test results into durable proof artifacts.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    init_parser = subparsers.add_parser("init", help="Create u27 proof ledger files.")
    init_parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")

    record_parser = subparsers.add_parser("record", help="Record one evidence-bearing run.")
    record_parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    record_parser.add_argument("--case", required=True, help="Case id from evals/proof_cases.json.")
    record_parser.add_argument("--command", dest="run_command", required=True, help="Command that produced the evidence.")
    record_parser.add_argument(
        "--status",
        required=True,
        choices=["pass", "fail", "regression", "blocked"],
        help="Run result.",
    )
    record_parser.add_argument(
        "--evidence",
        required=True,
        action="append",
        help="Evidence path. Repeat for multiple files.",
    )
    record_parser.add_argument("--note", default="", help="Optional reviewer note.")

    packet_parser = subparsers.add_parser("packet", help="Generate u27/PROOF_PACKET.md.")
    packet_parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")

    run_parser = subparsers.add_parser("run", help="Execute a command, capture output, and record evidence.")
    run_parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    run_parser.add_argument("--case", required=True, help="Case id from evals/proof_cases.json.")
    run_parser.add_argument("--note", default="", help="Optional reviewer note.")
    run_parser.add_argument("run_args", nargs=argparse.REMAINDER, help="Command to execute after --.")

    demo_parser = subparsers.add_parser("demo", help="Create a complete demo project and proof packet.")
    demo_parser.add_argument("--root", default="proof-ledger-demo", help="Demo project root. Defaults to proof-ledger-demo.")

    args = parser.parse_args(argv)

    try:
        if args.action == "init":
            root = Path(args.root).absolute()
            paths = init_project(root)
            print("Initialized Proof Ledger")
            print(f"Ledger: {paths.ledger_path.relative_to(root)}")
            print(f"Cases: {paths.cases_path.relative_to(root)}")
            return 0

        if args.action == "record":
            run = record_run(
                Path(args.root),
                case_id=args.case,
                command=args.run_command,
                status=args.status,
                evidence=args.evidence,
                note=args.note,
            )
            print(f"Recorded {run['id']}")
            return 0

        if args.action == "packet":
            generate_packet(Path(args.root))
            print("Generated u27/PROOF_PACKET.md")
            return 0

        if args.action == "run":
            root = Path(args.root).absolute()
            command_args = args.run_args[1:] if args.run_args[:1] == ["--"] else args.run_args
            if not command_args:
                raise LedgerError("run requires a command after --")
            run, exit_code = _execute_and_record(root, args.case, command_args, args.note)
            print(f"Recorded {run['id']}")
            return exit_code

        if args.action == "demo":
            root = Path(args.root).absolute()
            init_project(root)
            readme = root / "README.md"
            if not readme.exists():
                readme.write_text("# Proof Ledger Demo\n\nA tiny project used to show proof-ledger output.\n", encoding="utf-8")
            test_run, test_exit = _execute_and_record(
                root,
                "tests-pass",
                [sys.executable, "-c", "print('demo tests passed')"],
                "Demo test evidence.",
            )
            smoke_run, smoke_exit = _execute_and_record(
                root,
                "cli-smoke-test",
                [sys.executable, "-c", "print('demo cli smoke ok')"],
                "Demo smoke evidence.",
            )
            generate_packet(root)
            print(f"Demo project: {root}")
            print(f"Recorded {test_run['id']} and {smoke_run['id']}")
            print(f"Demo proof packet: {root / 'u27' / 'PROOF_PACKET.md'}")
            return 0 if test_exit == 0 and smoke_exit == 0 else 1
    except LedgerError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    return 1


def _execute_and_record(root: Path, case_id: str, command_args: list[str], note: str) -> tuple[dict, int]:
    ledger = load_ledger(root / "u27" / "proof_ledger.json")
    get_case(root, ledger, case_id)
    run_id = next_run_id(ledger)
    evidence_dir = root / "u27" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{run_id}.txt"
    try:
        completed = subprocess.run(command_args, cwd=root, text=True, capture_output=True, check=False)
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        extra_lines: list[str] = []
    except OSError as error:
        exit_code = 1
        stdout = ""
        stderr = ""
        extra_lines = [f"launch_error: {error}"]

    evidence_path.write_text(
        "\n".join(
            [
                f"$ {shlex.join(command_args)}",
                f"exit_code: {exit_code}",
                *extra_lines,
                "",
                "## stdout",
                stdout,
                "## stderr",
                stderr,
            ]
        ),
        encoding="utf-8",
    )
    status = "pass" if exit_code == 0 else "fail"
    run = record_run(
        root,
        case_id=case_id,
        command=shlex.join(command_args),
        status=status,
        evidence=[str(evidence_path)],
        note=note,
    )
    return run, exit_code


if __name__ == "__main__":
    raise SystemExit(main())
