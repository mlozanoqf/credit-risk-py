"""Missing restricted inputs must stop before Quarto or network access."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RunnerTests(unittest.TestCase):
    def test_restricted_chapters_preflight(self):
        for chapter in ('01-logistic', '02-tree-based'):
            for present in ((), ('credit_scoring.rds',), ('reference-split.csv',)):
                with self.subTest(chapter=chapter, present=present), tempfile.TemporaryDirectory() as name:
                    root = Path(name)
                    shutil.copy2(ROOT/'run.py', root/'run.py')
                    (root/'chapters.json').write_text(json.dumps([
                        {'id': chapter, 'status': 'implemented', 'source': 'missing.qmd'}]))
                    data = root/'data/credit-scoring'
                    data.mkdir(parents=True)
                    for filename in present:
                        (data/filename).touch()
                    result = subprocess.run([sys.executable, str(root/'run.py'), chapter],
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('authorized local inputs', result.stderr)
                    self.assertIn('No data will be downloaded', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertFalse((root/'output').exists())


if __name__ == '__main__':
    unittest.main()
