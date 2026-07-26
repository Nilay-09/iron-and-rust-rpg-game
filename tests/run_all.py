"""
Run every test suite and report a summary.

Each suite is run in its own subprocess on purpose: the suites monkeypatch
module-level globals (Dialogue/console/start_duel) to run headless, so sharing
one interpreter would let them contaminate each other. Subprocess isolation
keeps them honest.

Usage (from the repo root):

    python tests/run_all.py

Exits non-zero if any suite fails.
"""
import os
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)

SUITES = [
    "test_story_engine",   # Milestone 3 — story engine / honor
    "test_combat",         # Milestone 4 — combat & Dead Eye
    "test_gang",           # Milestone 5 — gang camp
    "test_endings",        # Milestone 6 — endings
    "test_depth",          # Milestone 7 — depth pass
    "test_memory",         # Milestone 8 — systemic depth
    "test_playthrough",    # Milestone 9 — integration playthrough
]


def main():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(REPO_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"          # unicode-safe on any console

    passed, failed = [], []
    for name in SUITES:
        path = os.path.join(TESTS_DIR, f"{name}.py")
        print(f"\n{'=' * 60}\nRunning {name}\n{'=' * 60}")
        result = subprocess.run(
            [sys.executable, "-X", "utf8", path], env=env
        )
        (passed if result.returncode == 0 else failed).append(name)

    total = len(SUITES)
    print(f"\n{'=' * 60}\nSUMMARY: {len(passed)}/{total} suites passed")
    if failed:
        print("FAILED: " + ", ".join(failed))
    print("=" * 60)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
