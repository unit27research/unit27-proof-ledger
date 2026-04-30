# Design Notes

Proof Ledger is intentionally small. The point is not to create a dashboard, a compliance layer, or a generic AI trust platform. The point is to make system evidence durable enough that a reviewer can inspect it later.

The core design claim is:

> Serious AI/system work needs evidence records, not memory of terminal output.

## Why This Is Not An Eval Framework

Proof Ledger does not design evals. It can execute a command to capture evidence, but it does not replace the test runner, benchmark, or review process that defines whether the command matters.

That boundary matters:

1. Test runners already exist.
2. Eval design is project-specific.
3. The missing artifact is often the durable proof record.
4. Command output should be captured before it becomes terminal memory.
5. A proof packet should be generated from evidence, not written from confidence.

## System Layers

Proof Ledger has three layers:

- **Case layer:** Defines claims, expected behavior, and known limits.
- **Run layer:** Records command, status, timestamp, and evidence paths.
- **Evidence layer:** Captures stdout/stderr for executed commands when `proof-ledger run` is used.
- **Packet layer:** Renders verified claims, open failures, known limits, and case inventory.

The ledger is the source of truth. The packet is an export.

## Why Evidence Paths Are Required

A pass/fail label without evidence is too weak. Every recorded run must point to at least one local evidence file.

That requirement keeps the tool honest:

- A reviewer can inspect the proof.
- A future maintainer can compare regressions.
- Claims stay tied to artifacts instead of memory.
- The packet can say what is proven without pretending to certify more.

## Status Model

Proof Ledger uses four statuses:

```text
pass
fail
regression
blocked
```

This is deliberately smaller than a full issue tracker. The statuses answer the proof question: does recorded evidence support the claim right now?

## Failure Modes

Proof Ledger should fail or downgrade when:

- A run references an unknown case.
- A run has no evidence path.
- An evidence path does not exist.
- An evidence path points outside the project root.
- A command cannot launch; this should be recorded as failed evidence, not lost as terminal noise.
- A cases file is malformed.
- A ledger has an unsupported schema version.
- A proof packet tries to imply broader certainty than recorded evidence supports.

## What I Would Improve Next

The strongest next improvements would be:

1. Add case-level severity and reviewer notes.
2. Add JSON output for generated packets.
3. Add CI examples for preserving proof packets as artifacts.
4. Add README claim matching later, likely as a bridge to Boundary Engine.
5. Add comparison views for previous runs of the same case.

Those deepen the system without turning it into a platform.

## What This Demonstrates

This project is designed to show:

- Evidence discipline over vague readiness claims
- Durable records over terminal memory
- Reviewer artifacts over self-certification
- Small CLI surfaces over dashboards
- Local-first proof over external trust theater

The intended reviewer reaction is:

> I can see what was tested, where the evidence lives, and what claims are actually supported.
