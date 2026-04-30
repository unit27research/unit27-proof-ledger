# U27-S04 // Proof Ledger

Proof Ledger turns eval runs, demo commands, and test results into durable evidence records and reviewer-ready proof packets.

```text
U27-S04
PROOF LEDGER

CLASS: SYSTEM
FUNCTION: Evidence Recording + Proof Artifact Generation
REF_ID: PROOF-LEDGER-01
```

## Why It Exists

AI and agentic systems often ship with vague proof:

- "tested locally"
- "demo works"
- "evals pass"
- "ready for review"

Proof Ledger makes that evidence inspectable. It records what was tested, what command produced the evidence, what passed or failed, where the proof lives, and what can honestly be shown to a reviewer.

## CLI

Install locally:

```bash
pip install -e .
```

Initialize proof files in a project:

```bash
proof-ledger init
```

Record a run:

```bash
proof-ledger record \
  --case demo-command \
  --command "python -m unittest discover -s tests" \
  --status pass \
  --evidence outputs/test-output.txt
```

Or execute a command and capture its evidence automatically:

```bash
proof-ledger run --case demo-command -- python3 -m unittest discover -s tests
```

Generate the proof packet:

```bash
proof-ledger packet
```

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
  "id": "demo-command",
  "claim": "Proof Ledger can record demo command evidence.",
  "expected": "A command run is recorded with status and evidence.",
  "limits": ["This packet only reflects recorded local evidence."]
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
proof-ledger run --case demo-command -- python3 -m unittest discover -s tests
proof-ledger packet
```

## Acceptance

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m proof_ledger.cli init --root examples/sample-project
PYTHONPATH=src python3 -m proof_ledger.cli run --root examples/sample-project --case demo-command -- python3 -c "print('demo command completed')"
PYTHONPATH=src python3 -m proof_ledger.cli packet --root examples/sample-project
```

## License

MIT
