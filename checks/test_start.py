"""Reader entry point tests; no chapter calculation is replaced."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import start


class StarterTests(unittest.TestCase):
    def test_select_and_cancel(self):
        chapters = json.loads((start.ROOT / "chapters.json").read_text())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(start.choose_chapter(chapters, lambda _: "0"))
            choices = iter(["bad", "99", "2"])
            self.assertEqual(start.choose_chapter(chapters, lambda _: next(choices)), "01-logistic")

    def test_missing_quarto(self):
        with mock.patch.object(start.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Quarto was not found"):
                start.check_setup()

    def test_missing_and_wrong_package(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "requirements-lock.txt").write_text("example==1.0\n")
            with mock.patch.object(start.shutil, "which", return_value="quarto"), \
                 mock.patch.object(start.subprocess, "run", return_value=mock.Mock(stdout="1.5.54\n")), \
                 mock.patch.object(start.metadata, "version", side_effect=start.metadata.PackageNotFoundError):
                with self.assertRaisesRegex(RuntimeError, "example: missing"):
                    start.check_setup(root)
            with mock.patch.object(start.shutil, "which", return_value="quarto"), \
                 mock.patch.object(start.subprocess, "run", return_value=mock.Mock(stdout="1.5.54\n")), \
                 mock.patch.object(start.metadata, "version", return_value="2.0"):
                with self.assertRaisesRegex(RuntimeError, "expected ==1.0"):
                    start.check_setup(root)

    def test_success_and_no_browser(self):
        with tempfile.TemporaryDirectory(prefix="reader path ") as folder:
            root = Path(folder)
            report = root / "output/00-foundations/chapter.html"
            report.parent.mkdir(parents=True)
            report.write_text("<html></html>")
            with mock.patch.object(start.subprocess, "run") as run, \
                 mock.patch.object(start.webbrowser, "open", return_value=True) as browser:
                self.assertEqual(start.run_selected("00-foundations", root), report)
                run.assert_called_once_with([sys.executable, str(root / "run.py"), "00-foundations"], cwd=root, check=True)
                browser.assert_called_once_with(report.resolve().as_uri())
            with mock.patch.object(start.subprocess, "run"), mock.patch.object(start.webbrowser, "open") as browser:
                start.run_selected("00-foundations", root, open_report=False)
                browser.assert_not_called()
            with mock.patch.object(start.subprocess, "run"), \
                 mock.patch.object(start.webbrowser, "open", side_effect=start.webbrowser.Error):
                self.assertEqual(start.run_selected("00-foundations", root), report)

    def test_failed_run_does_not_open_old_report(self):
        with mock.patch.object(start.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "run.py")), \
             mock.patch.object(start.webbrowser, "open") as browser:
            with self.assertRaises(subprocess.CalledProcessError):
                start.run_selected("00-foundations")
            browser.assert_not_called()

    def test_missing_report(self):
        with tempfile.TemporaryDirectory() as folder, \
             mock.patch.object(start.subprocess, "run"), mock.patch.object(start.webbrowser, "open") as browser:
            with self.assertRaisesRegex(RuntimeError, "expected report"):
                start.run_selected("00-foundations", Path(folder))
            browser.assert_not_called()

    def test_check_only_and_list(self):
        for option in ("--check", "--list"):
            with mock.patch.object(sys, "argv", ["start.py", option]), \
                 mock.patch.object(start, "check_setup") as check, mock.patch.object(start, "run_selected") as run:
                start.main()
                self.assertEqual(check.call_count, int(option == "--check"))
                run.assert_not_called()

    def test_invalid_id_exits(self):
        with mock.patch.object(sys, "argv", ["start.py", "bad-id"]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                start.main()
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
