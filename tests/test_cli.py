import subprocess
import sys
import tempfile
import unittest
import os
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"


class ProofLedgerCliTests(unittest.TestCase):
    def run_cli(self, root, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_PATH)
        return subprocess.run(
            [sys.executable, "-m", "proof_ledger.cli", *args],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_init_command_creates_project_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(tmp, "init")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Initialized Proof Ledger", result.stdout)
            self.assertTrue((Path(tmp) / "u27" / "proof_ledger.json").exists())

    def test_record_command_requires_evidence_and_writes_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.run_cli(root, "init")
            evidence = root / "outputs" / "test.txt"
            evidence.parent.mkdir()
            evidence.write_text("ok", encoding="utf-8")

            result = self.run_cli(
                root,
                "record",
                "--case",
                "demo-command",
                "--command",
                "python -m unittest",
                "--status",
                "pass",
                "--evidence",
                str(evidence),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Recorded run-0001", result.stdout)

    def test_packet_command_generates_markdown_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.run_cli(root, "init")
            evidence = root / "outputs" / "demo.txt"
            evidence.parent.mkdir()
            evidence.write_text("ok", encoding="utf-8")
            self.run_cli(
                root,
                "record",
                "--case",
                "demo-command",
                "--command",
                "proof-ledger demo",
                "--status",
                "pass",
                "--evidence",
                str(evidence),
            )

            result = self.run_cli(root, "packet")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Generated u27/PROOF_PACKET.md", result.stdout)
            self.assertIn("Proof Ledger can record demo command evidence.", (root / "u27" / "PROOF_PACKET.md").read_text())

    def test_run_command_executes_command_and_captures_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.run_cli(root, "init")

            result = self.run_cli(
                root,
                "run",
                "--case",
                "demo-command",
                "--",
                sys.executable,
                "-c",
                "print('proof ok')",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Recorded run-0001", result.stdout)
            evidence_files = list((root / "u27" / "evidence").glob("run-0001.txt"))
            self.assertEqual(len(evidence_files), 1)
            self.assertIn("proof ok", evidence_files[0].read_text())

    def test_run_command_validates_case_before_executing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.run_cli(root, "init")
            marker = root / "should-not-exist.txt"

            result = self.run_cli(
                root,
                "run",
                "--case",
                "missing-case",
                "--",
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Unknown case_id", result.stderr)
            self.assertFalse(marker.exists())
            self.assertFalse((root / "u27" / "evidence").exists())

    def test_run_command_records_launch_failure_as_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.run_cli(root, "init")

            result = self.run_cli(
                root,
                "run",
                "--case",
                "demo-command",
                "--",
                "definitely-not-a-real-proof-ledger-command",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Recorded run-0001", result.stdout)
            evidence = root / "u27" / "evidence" / "run-0001.txt"
            self.assertTrue(evidence.exists())
            self.assertIn("launch_error:", evidence.read_text())


if __name__ == "__main__":
    unittest.main()
