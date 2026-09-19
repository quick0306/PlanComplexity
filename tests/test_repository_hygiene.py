import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_hashed_evidence_survives_git_line_ending_conversion(self):
        # Exercise actual Git add/checkout, including Windows and Linux settings.
        # A byte change would invalidate baseline provenance and report manifests.
        evidence_paths = [
            "validation/reference_cases/cases/example/expected_metrics.json",
            "validation/reference_cases/history/example/expected_metrics.json",
            "validation/reference_cases/history/example/expected_metrics_provenance.json",
            "run_reports/validation/reference_case_results.json",
            "run_reports/validation/validation_summary.md",
        ]
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)

            git("init", "-q")
            attributes = REPO_ROOT / ".gitattributes"
            if attributes.exists():
                (repo / ".gitattributes").write_bytes(attributes.read_bytes())
            for autocrlf in ("true", "input", "false"):
                git("config", "core.autocrlf", autocrlf)
                git("config", "core.safecrlf", "false")
                for newline in (b"\r\n", b"\n"):
                    original = b'{"metric": 0.123456789}' + newline
                    for name in evidence_paths:
                        path = repo / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(original)
                    git("add", ".")
                    for name in evidence_paths:
                        with self.subTest(autocrlf=autocrlf, newline=newline, path=name):
                            self.assertEqual(original, git("show", ":" + name))
                    git("checkout-index", "--all", "--force")
                    for name in evidence_paths:
                        with self.subTest(autocrlf=autocrlf, newline=newline, path=name):
                            self.assertEqual(original, (repo / name).read_bytes())

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
