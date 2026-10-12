
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "generated/oracle-forms/test-report.json"

def run_tests():
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.returncode, (
        result.stdout + "\n" + result.stderr
    )

def main():
    code, output = run_tests()

    report = {
        "status": "passed" if code == 0 else "failed",
        "exit_code": code,
        "output": output[-12000:],
        "requires_repair": code != 0
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(report["status"])
    print(f"Rapport : {REPORT}")

    if code != 0:
        print("Correction par agent IA nécessaire.")

    sys.exit(0 if code == 0 else 1)

if __name__ == "__main__":
    main()
