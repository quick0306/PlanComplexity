import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ValidationSmokeTests(unittest.TestCase):
    def test_validation_modules_import(self):
        import validation
        import validation_runtime  # noqa: F401
        import validation_models  # noqa: F401
        self.assertEqual(validation.PACKAGE_SENTINEL, "real-validation-package")


if __name__ == "__main__":
    unittest.main()
