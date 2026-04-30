# Proof Packet

Project: unit27-proof-ledger
Generated: 2026-04-30T20:11:33+00:00

## Verified Claims

- Proof Ledger can initialize a project, record evidence-bearing runs, execute commands, and generate a reviewer-facing proof packet.
  - Case: `core-cli-acceptance`
  - Command: `python3 -m unittest discover -s tests`
  - Evidence: `u27/evidence/run-0003.txt`

- Proof Ledger packages as an installable Python project with a console entry point.
  - Case: `wheel-build`
  - Command: `/Users/joshuabloodworth/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip wheel . --no-deps --no-build-isolation -w /tmp/proof-ledger-wheel-final`
  - Evidence: `u27/evidence/run-0004.txt`

## Open Failures

- No failing, blocked, or regression runs are recorded.

## Known Limits
- This packet only reflects recorded local evidence.
- The current evidence covers local CLI behavior, not packaging publication or GitHub release state.
- Wheel evidence proves local packaging only; it does not prove PyPI publication or GitHub release state.

## Case Inventory
- `core-cli-acceptance`: pass - Proof Ledger can initialize a project, record evidence-bearing runs, execute commands, and generate a reviewer-facing proof packet.
- `wheel-build`: pass - Proof Ledger packages as an installable Python project with a console entry point.
