# Proof Packet

Project: unit27-proof-ledger
Generated: 2026-04-30T23:17:32+00:00

## Verified Claims

- Proof Ledger can initialize a project, record evidence-bearing runs, execute commands, handle launch failures, and generate a reviewer-facing proof packet.
  - Case: `core-cli-acceptance`
  - Command: `python3 -m unittest discover -s tests`
  - Evidence: `u27/evidence/run-0001.txt`

- Proof Ledger packages as an installable Python project.
  - Case: `wheel-build`
  - Command: `/Users/joshuabloodworth/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip wheel . --no-deps --no-build-isolation -w /tmp/proof-ledger-wheel-hardening`
  - Evidence: `u27/evidence/run-0002.txt`

- Proof Ledger's built wheel contains the CLI modules and proof-ledger console entry point.
  - Case: `wheel-contents`
  - Command: `/Users/joshuabloodworth/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/verify_wheel.py /tmp/proof-ledger-wheel-hardening/unit27_proof_ledger-0.1.0-py3-none-any.whl`
  - Evidence: `u27/evidence/run-0003.txt`

## Open Failures

- No failing, blocked, or regression runs are recorded.

## Known Limits
- This packet only reflects recorded local evidence.
- The current evidence covers local CLI behavior, not packaging publication or GitHub release state.
- Wheel evidence proves local packaging only; it does not prove PyPI publication or GitHub release state.
- Wheel contents evidence proves local artifact structure only; it does not prove installation in every target environment.

## Case Inventory
- `core-cli-acceptance`: pass - Proof Ledger can initialize a project, record evidence-bearing runs, execute commands, handle launch failures, and generate a reviewer-facing proof packet.
- `wheel-build`: pass - Proof Ledger packages as an installable Python project.
- `wheel-contents`: pass - Proof Ledger's built wheel contains the CLI modules and proof-ledger console entry point.
