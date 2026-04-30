# Proof Packet

Project: sample-project
Generated: 2026-04-30T23:30:02+00:00

## Verified Claims

- The project test suite passes in the current local checkout.
  - Case: `tests-pass`
  - Command: `python3 -c 'print('"'"'demo tests passed'"'"')'`
  - Evidence: `u27/evidence/run-0001.txt`

- The primary CLI or demo command runs successfully.
  - Case: `cli-smoke-test`
  - Command: `python3 -c 'print('"'"'demo cli smoke ok'"'"')'`
  - Evidence: `u27/evidence/run-0002.txt`

## Open Failures

- No failing, blocked, or regression runs are recorded.

## Known Limits
- This claim covers the recorded local test command only.
- This smoke test does not prove every CLI option or integration path.
- This claim covers local artifact creation, not distribution or release state.

## Case Inventory
- `cli-smoke-test`: pass - The primary CLI or demo command runs successfully.
- `package-builds`: unrecorded - The project can produce its expected build or package artifact.
- `tests-pass`: pass - The project test suite passes in the current local checkout.
