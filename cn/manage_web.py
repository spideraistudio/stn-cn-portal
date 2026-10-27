"""Convenient local PC entry point, using a web-only data directory."""
from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
from cn_web.cli import main as account_cli


def main():
    parser = argparse.ArgumentParser(description="All Crop CN — Phase 7.1 accounts and navigation")
    parser.add_argument("action", choices=["setup-admin", "start-local"])
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    data = args.data or base / "AllCropCNWeb"
    if args.action == "setup-admin":
        username = input("Administrator username: ").strip()
        try:
            quota = int(input("Administrator storage allowance in MiB (whole number): "))
        except ValueError:
            parser.error("Enter a whole number for the storage allowance")
        sys.argv = [sys.argv[0], "--data", str(data), "bootstrap-admin", "--username", username, "--quota-mib", str(quota)]
    else:
        sys.argv = [sys.argv[0], "--data", str(data), "serve-local"]
    account_cli()


if __name__ == "__main__":
    main()
