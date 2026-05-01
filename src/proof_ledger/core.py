from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


LEDGER_VERSION = "0.1"


class LedgerError(Exception):
    """Raised when a proof ledger operation cannot be completed."""


@dataclass(frozen=True)
class InitPaths:
    ledger_path: Path
    cases_path: Path


def init_project(root: Path | str) -> InitPaths:
    project_root = Path(root).absolute()
    u27_dir = project_root / "u27"
    evals_dir = project_root / "evals"
    u27_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = u27_dir / "proof_ledger.json"
    cases_path = evals_dir / "proof_cases.json"

    if not cases_path.exists():
        _write_json(cases_path, _default_cases())

    if not ledger_path.exists():
        ledger = {
            "schema_version": LEDGER_VERSION,
            "project": {
                "name": project_root.name,
                "created_at": _now(),
            },
            "cases_path": "evals/proof_cases.json",
            "runs": [],
        }
        _write_json(ledger_path, ledger)

    return InitPaths(ledger_path=ledger_path, cases_path=cases_path)


def load_ledger(path: Path | str) -> dict:
    ledger_path = Path(path)
    if not ledger_path.exists():
        raise LedgerError(f"Ledger not found: {ledger_path}")
    with ledger_path.open("r", encoding="utf-8") as handle:
        ledger = json.load(handle)
    if ledger.get("schema_version") != LEDGER_VERSION:
        raise LedgerError("Unsupported ledger schema_version")
    return ledger


def record_run(
    root: Path | str,
    *,
    case_id: str,
    command: str,
    status: str,
    evidence: Iterable[str],
    note: str = "",
) -> dict:
    project_root = Path(root).absolute()
    ledger_path = project_root / "u27" / "proof_ledger.json"
    ledger = load_ledger(ledger_path)
    case = get_case(project_root, ledger, case_id)

    if status not in {"pass", "fail", "regression", "blocked"}:
        raise LedgerError("status must be pass, fail, regression, or blocked")

    evidence_paths = [_relative_existing_path(project_root, item) for item in evidence]
    if not evidence_paths:
        raise LedgerError("At least one evidence path is required")

    run = {
        "id": next_run_id(ledger),
        "case_id": case_id,
        "claim": case["claim"],
        "command": command,
        "status": status,
        "recorded_at": _now(),
        "evidence": evidence_paths,
        "note": note,
    }
    ledger["runs"].append(run)
    _write_json(ledger_path, ledger)
    return run


def next_run_id(ledger: dict) -> str:
    highest = 0
    for run in ledger.get("runs", []):
        run_id = str(run.get("id", ""))
        if not run_id.startswith("run-"):
            continue
        try:
            highest = max(highest, int(run_id.removeprefix("run-")))
        except ValueError:
            continue
    return f"run-{highest + 1:04d}"


def get_case(root: Path | str, ledger: dict, case_id: str) -> dict:
    project_root = Path(root).absolute()
    cases = _load_cases(project_root / ledger["cases_path"])
    case = next((item for item in cases if item["id"] == case_id), None)
    if case is None:
        raise LedgerError(f"Unknown case_id: {case_id}")
    return case


def generate_packet(root: Path | str) -> str:
    project_root = Path(root).absolute()
    ledger = load_ledger(project_root / "u27" / "proof_ledger.json")
    cases = _load_cases(project_root / ledger["cases_path"])
    case_by_id = {case["id"]: case for case in cases}
    latest_runs = _latest_runs_by_case(ledger["runs"])
    passing_runs = [run for run in latest_runs if run["status"] == "pass"]
    nonpassing_runs = [run for run in latest_runs if run["status"] != "pass"]

    lines = [
        "# Proof Packet",
        "",
        f"Project: {ledger['project']['name']}",
        f"Generated: {_now()}",
        "",
        "## Verified Claims",
    ]
    if passing_runs:
        for run in passing_runs:
            lines.extend(
                [
                    "",
                    f"- {run['claim']}",
                    f"  - Case: `{run['case_id']}`",
                    f"  - Command: `{run['command']}`",
                    f"  - Evidence: {', '.join(f'`{item}`' for item in run['evidence'])}",
                ]
            )
    else:
        lines.append("")
        lines.append("- No passing evidence has been recorded.")

    lines.extend(["", "## Open Failures"])
    if nonpassing_runs:
        for run in nonpassing_runs:
            lines.extend(
                [
                    "",
                    f"- `{run['status']}`: {run['claim']}",
                    f"  - Case: `{run['case_id']}`",
                    f"  - Command: `{run['command']}`",
                ]
            )
    else:
        lines.append("")
        lines.append("- No failing, blocked, or regression runs are recorded.")

    lines.extend(["", "## Known Limits"])
    limits = []
    for case in cases:
        for limit in case.get("limits", []):
            if limit not in limits:
                limits.append(limit)
    if limits:
        for limit in limits:
            lines.append(f"- {limit}")
    else:
        lines.append("- This packet only reflects recorded local evidence.")

    lines.extend(["", "## Case Inventory"])
    for case_id, case in sorted(case_by_id.items()):
        matching_runs = [run for run in ledger["runs"] if run["case_id"] == case_id]
        latest = matching_runs[-1]["status"] if matching_runs else "unrecorded"
        lines.append(f"- `{case_id}`: {latest} - {case['claim']}")

    packet = "\n".join(lines) + "\n"
    packet_path = project_root / "u27" / "PROOF_PACKET.md"
    packet_path.write_text(packet, encoding="utf-8")
    return packet


def _default_cases() -> list[dict]:
    return [
        {
            "id": "tests-pass",
            "claim": "The project test suite passes in the current local checkout.",
            "expected": "The configured test command exits 0 and stores stdout/stderr as evidence.",
            "limits": ["This claim covers the recorded local test command only."],
        },
        {
            "id": "cli-smoke-test",
            "claim": "The primary CLI or demo command runs successfully.",
            "expected": "The smoke command exits 0 and produces inspectable output.",
            "limits": ["This smoke test does not prove every CLI option or integration path."],
        },
        {
            "id": "package-builds",
            "claim": "The project can produce its expected build or package artifact.",
            "expected": "The build command exits 0 and stores build output as evidence.",
            "limits": ["This claim covers local artifact creation, not distribution or release state."],
        },
    ]


def _latest_runs_by_case(runs: list[dict]) -> list[dict]:
    latest = {}
    for run in runs:
        latest[run["case_id"]] = run
    return list(latest.values())


def _load_cases(path: Path) -> list[dict]:
    if not path.exists():
        raise LedgerError(f"Cases file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        cases = payload
    elif isinstance(payload, dict):
        cases = payload.get("cases")
    else:
        cases = None
    if not isinstance(cases, list):
        raise LedgerError("Cases file must contain a cases list")
    for case in cases:
        if not all(key in case for key in ("id", "claim", "expected")):
            raise LedgerError("Each case must include id, claim, and expected")
    return cases


def _relative_existing_path(root: Path, value: str) -> str:
    path = Path(value)
    full_path = path.absolute() if path.is_absolute() else (root / path).absolute()
    if not full_path.exists():
        raise LedgerError(f"Evidence path not found: {value}")
    try:
        return full_path.relative_to(root).as_posix()
    except ValueError:
        try:
            return full_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError as error:
            raise LedgerError(f"Evidence path must be inside project root: {value}") from error


def _write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
