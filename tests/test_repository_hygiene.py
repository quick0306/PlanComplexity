import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_csv_files_are_ignored_and_not_tracked(self):
        # Generated report CSVs may carry patient identifiers, so fail fast if re-tracked.
        ignore_lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

        self.assertIn("*.csv", ignore_lines)

        tracked_csv = subprocess.check_output(
            ["git", "ls-files", "*.csv"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        self.assertEqual([], tracked_csv)


if __name__ == "__main__":
    unittest.main()
