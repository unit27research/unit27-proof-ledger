import json
import tempfile
import unittest
from pathlib import Path

from proof_ledger.core import (
    LedgerError,
    generate_packet,
    init_project,
    load_ledger,
    record_run,
)


class ProofLedgerCoreTests(unittest.TestCase):
    def test_init_project_writes_ledger_and_case_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            paths = init_project(root)

            self.assertEqual(paths.ledger_path, root / "u27" / "proof_ledger.json")
            self.assertTrue(paths.ledger_path.exists())
            self.assertTrue((root / "evals" / "proof_cases.json").exists())

            ledger = load_ledger(paths.ledger_path)
            self.assertEqual(ledger["schema_version"], "0.1")
            self.assertEqual(ledger["project"]["name"], root.name)
            self.assertEqual(ledger["runs"], [])
            cases = json.loads((root / "evals" / "proof_cases.json").read_text(encoding="utf-8"))
            self.assertEqual([case["id"] for case in cases], ["tests-pass", "cli-smoke-test", "package-builds"])

    def test_record_run_requires_known_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(root)

            with self.assertRaises(LedgerError) as error:
                record_run(
                    root,
                    case_id="missing-case",
                    command="npm test",
                    status="pass",
                    evidence=["test-output.txt"],
                )

            self.assertIn("Unknown case_id", str(error.exception))

    def test_record_run_appends_evidence_bearing_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(root)
            evidence_path = root / "outputs" / "test-output.txt"
            evidence_path.parent.mkdir()
            evidence_path.write_text("3 passed", encoding="utf-8")

            run = record_run(
                root,
                case_id="tests-pass",
                command="python -m unittest",
                status="pass",
                evidence=[str(evidence_path)],
                note="Baseline test command passed.",
            )

            ledger = load_ledger(root / "u27" / "proof_ledger.json")
            self.assertEqual(run["case_id"], "tests-pass")
            self.assertEqual(ledger["runs"][0]["status"], "pass")
            self.assertEqual(ledger["runs"][0]["evidence"][0], "outputs/test-output.txt")

    def test_record_run_rejects_evidence_outside_project(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            init_project(root)
            evidence_path = Path(outside) / "external.txt"
            evidence_path.write_text("outside", encoding="utf-8")

            with self.assertRaises(LedgerError) as error:
                record_run(
                    root,
                    case_id="tests-pass",
                    command="external proof",
                    status="pass",
                    evidence=[str(evidence_path)],
                )

            self.assertIn("Evidence path must be inside project root", str(error.exception))

    def test_generate_packet_groups_verified_claims_and_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(root)
            evidence_path = root / "outputs" / "demo.txt"
            evidence_path.parent.mkdir()
            evidence_path.write_text("demo ok", encoding="utf-8")
            record_run(
                root,
                case_id="tests-pass",
                command="proof-ledger demo",
                status="pass",
                evidence=[str(evidence_path)],
            )

            packet = generate_packet(root)

            self.assertIn("# Proof Packet", packet)
            self.assertIn("## Verified Claims", packet)
            self.assertIn("The project test suite passes in the current local checkout.", packet)
            self.assertIn("## Known Limits", packet)
            self.assertIn("This claim covers the recorded local test command only.", packet)
            self.assertTrue((root / "u27" / "PROOF_PACKET.md").exists())

    def test_generate_packet_uses_latest_run_per_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(root)
            first = root / "outputs" / "first.txt"
            second = root / "outputs" / "second.txt"
            first.parent.mkdir()
            first.write_text("first", encoding="utf-8")
            second.write_text("second", encoding="utf-8")
            record_run(root, case_id="tests-pass", command="first command", status="pass", evidence=[str(first)])
            record_run(root, case_id="tests-pass", command="second command", status="pass", evidence=[str(second)])

            packet = generate_packet(root)

            self.assertNotIn("first command", packet)
            self.assertIn("second command", packet)


if __name__ == "__main__":
    unittest.main()
