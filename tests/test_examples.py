import subprocess
import sys
import unittest


class ExampleSmokeTests(unittest.TestCase):
    def test_python_example_runs_from_repository_root(self):
        result = subprocess.run(
            [sys.executable, "-m", "examples.python.reference_demo"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "Generated 64 preambles",
                "First preamble: root=1, shift=0",
                "Last preamble: root=1, shift=819",
            ],
        )


if __name__ == "__main__":
    unittest.main()
