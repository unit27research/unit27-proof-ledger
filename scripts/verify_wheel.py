from __future__ import annotations

import sys
import zipfile
from pathlib import Path


REQUIRED_FILES = {
    "proof_ledger/__init__.py",
    "proof_ledger/cli.py",
    "proof_ledger/core.py",
}

REQUIRED_ENTRY_POINT = "proof-ledger = proof_ledger.cli:main"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: verify_wheel.py PATH_TO_WHEEL", file=sys.stderr)
        return 2

    wheel_path = Path(args[0])
    if not wheel_path.exists():
        print(f"error: wheel not found: {wheel_path}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())
        missing = sorted(REQUIRED_FILES - names)
        if missing:
            print("error: wheel missing required files:", file=sys.stderr)
            for name in missing:
                print(f"- {name}", file=sys.stderr)
            return 1

        entry_point_files = sorted(
            name for name in names if name.startswith("unit27_proof_ledger-") and name.endswith(".dist-info/entry_points.txt")
        )
        if len(entry_point_files) != 1:
            print("error: expected exactly one unit27_proof_ledger entry_points.txt", file=sys.stderr)
            return 1

        entry_points = wheel.read(entry_point_files[0]).decode("utf-8")
        if REQUIRED_ENTRY_POINT not in entry_points:
            print("error: proof-ledger entry point missing", file=sys.stderr)
            return 1

    print("wheel verified: unit27-proof-ledger")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
