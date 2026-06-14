import unittest
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Assuming this test file is in 'build_tests/'
PROJECT_ROOT = Path(__file__).parent.parent
INIT_SCRIPT = PROJECT_ROOT / "init.py"

class TestKBForgeBlueprint(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace for blueprint initialization
        self.test_workspace = PROJECT_ROOT / "tmp_test_vault"
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)
        
        # Clone blueprint structure (simplified for testing)
        # In a real CI, you'd clone the repo. Here we copy the current state.
        shutil.copytree(PROJECT_ROOT, self.test_workspace, ignore=shutil.ignore_patterns('tmp_test_vault', 'build_tests', '.git', '.obsidian'))

    def tearDown(self):
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)

    def test_blueprint_scrub(self):
        """Ensure no forbidden demo/confidential terms exist in the blueprint."""
        forbidden = ["Acme", "Nexi"]
        for path in self.test_workspace.rglob("*"):
            if path.is_file() and not str(path).startswith(str(self.test_workspace / ".git")) and "docs\\site" not in str(path):
                try:
                    text = path.read_text(encoding="utf-8")
                    for term in forbidden:
                        self.assertNotIn(term, text, f"Found forbidden term '{term}' in {path}")
                except UnicodeDecodeError:
                    print(f"Skipping non-text or binary file: {path}")
                    continue

    def test_init_scaffolding(self):
        """Verify the init script creates the required structure and welcome article."""
        # Simulate user inputs: domain, team, topics. Skip confirmation with --no-confirm.
        input_data = "my-domain\nMy Team\nauth\nwebhooks\nonboarding\n\n"
        
        process = subprocess.run(
            [sys.executable, str(self.test_workspace / "init.py"), "--no-confirm"],
            input=input_data,
            capture_output=True,
            text=True,
            cwd=self.test_workspace
        )
        
        print(f"Init stdout: {process.stdout}")
        print(f"Init stderr: {process.stderr}")
        
        self.assertEqual(process.returncode, 0, f"Init script failed: {process.stderr}")
        
        # Verify scaffolding
        expected_article = self.test_workspace / "01 Reference" / "articles" / "(C) my-domain.overview.md"
        self.assertTrue(expected_article.exists(), f"Expected article {expected_article} not found")
        self.assertTrue((self.test_workspace / "03 Accounts" / "(C) My Team.md").exists())

if __name__ == "__main__":
    unittest.main()
