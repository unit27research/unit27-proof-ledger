# U27-S04 // Proof Ledger

[![CI](https://github.com/unit27research/unit27-proof-ledger/actions/workflows/ci.yml/badge.svg)](https://github.com/unit27research/unit27-proof-ledger/actions/workflows/ci.yml)

Proof Ledger enforces evidence discipline by converting eval runs, demo commands, and test results into durable proof artifacts.

```text
U27-S04
PROOF LEDGER

CLASS: SYSTEM
FUNCTION: Evidence Recording + Proof Artifact Generation
REF_ID: PROOF-LEDGER-01
```

It answers one narrow question:

> What evidence supports the claims this repo is making right now?

## 60-Second Start

From this repo:

```bash
pip install -e .
proof-ledger demo
cat proof-ledger-demo/u27/PROOF_PACKET.md
```

On your own repo:

```bash
proof-ledger init
proof-ledger run --case tests-pass -- python -m pytest
proof-ledger run --case cli-smoke-test -- python -m your_package --help
proof-ledger packet
```

If the command exits nonzero or fails to launch, Proof Ledger records a failed run with captured evidence and returns a nonzero exit code.

## What It Does

Proof Ledger runs local proof commands and writes:

1. `u27/proof_ledger.json`
2. `u27/PROOF_PACKET.md`
3. `u27/evidence/run-0001.txt`
4. `evals/proof_cases.json`

It is designed to feel like an evidence ledger, not a benchmark suite or project review.

## Why It Exists

AI and agentic systems often ship with vague proof:

- "tested locally"
- "demo works"
- "evals pass"
- "ready for review"

Proof Ledger makes that evidence inspectable. It records what was tested, what command produced the evidence, what passed or failed, where the proof lives, and what can honestly be shown to a reviewer.

## Install

For local development:

```bash
pip install -e .
```

After this repo is public:

```bash
pipx install git+https://github.com/unit27research/unit27-proof-ledger
```

## Commands

Initialize proof files:

```bash
proof-ledger init
```

Record a run:

```bash
proof-ledger record \
  --case tests-pass \
  --command "python -m unittest discover -s tests" \
  --status pass \
  --evidence outputs/test-output.txt
```

Or execute a command and capture its evidence automatically:

```bash
proof-ledger run --case tests-pass -- python3 -m unittest discover -s tests
```

If the command exits nonzero or fails to launch, Proof Ledger records a failed run with captured evidence and returns a nonzero exit code.

Generate the proof packet:

```bash
proof-ledger packet
```

Create a complete demo project:

```bash
proof-ledger demo
```

## Default Cases

`proof-ledger init` creates practical starter cases:

```text
tests-pass
cli-smoke-test
package-builds
```

Edit `evals/proof_cases.json` to replace or extend these with project-specific claims.

## Artifacts

Proof Ledger writes:

```text
u27/proof_ledger.json
u27/PROOF_PACKET.md
u27/evidence/run-0001.txt
evals/proof_cases.json
```

The ledger is the durable evidence record. The packet is the reviewer-facing export.

## Case Shape

```json
{
  "id": "tests-pass",
  "claim": "The project test suite passes in the current local checkout.",
  "expected": "The configured test command exits 0 and stores stdout/stderr as evidence.",
  "limits": ["This claim covers the recorded local test command only."]
}
```

## System Shape

```text
cases -> runs -> evidence paths -> proof ledger -> proof packet
```

Proof Ledger does not decide whether a project is good. It records what evidence exists and prevents proof from collapsing into memory, vibes, or a throwaway terminal scroll.

## What It Does Not Do

Proof Ledger does not:

1. Judge product quality
2. Certify correctness
3. Replace eval design
4. Claim live behavior that was not recorded
5. Send data outside the local project

## Verify

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
proof-ledger init
proof-ledger run --case tests-pass -- python3 -m unittest discover -s tests
proof-ledger packet
```

## Acceptance

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m proof_ledger.cli init --root examples/sample-project
PYTHONPATH=src python3 -m proof_ledger.cli demo --root examples/sample-project
PYTHONPATH=src python3 -m proof_ledger.cli packet --root examples/sample-project
python3 -m pip wheel . --no-deps --no-build-isolation -w /tmp/proof-ledger-wheel
python3 scripts/verify_wheel.py /tmp/proof-ledger-wheel/unit27_proof_ledger-0.1.0-py3-none-any.whl
```

## License

MIT
