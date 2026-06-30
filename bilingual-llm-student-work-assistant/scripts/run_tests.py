import subprocess
import sys
import os


def main() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src" if not env.get("PYTHONPATH") else f"src:{env['PYTHONPATH']}"
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        check=False,
        env=env,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
