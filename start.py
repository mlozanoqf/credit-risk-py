"""Choose a chapter, run the existing verified runner, and open its report."""
import argparse
from importlib import metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import warnings
import webbrowser

ROOT = Path(__file__).resolve().parent


def check_setup(root=ROOT):
    print(f"Python: {sys.version.split()[0]} (reference series: 3.12)")
    if sys.version_info[:2] != (3, 12):
        warnings.warn("Use Python 3.12 for the recorded environment.")
    quarto = shutil.which("quarto")
    if not quarto:
        raise RuntimeError("Quarto was not found. Install it, reopen the terminal, and retry. See README.md.")
    version = subprocess.run([quarto, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    print(f"Quarto: {version} (reference: 1.5.54)")
    if version != "1.5.54":
        warnings.warn("Quarto differs from the tested version; report layout may differ.")
    try:
        from packaging.requirements import Requirement
    except ImportError as exc:
        raise RuntimeError("Packages are not ready. Run the pip install command in README.md using .venv's Python.") from exc
    mismatches = []
    for line in (root / "requirements-lock.txt").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        requirement = Requirement(line)
        if requirement.marker and not requirement.marker.evaluate():
            continue
        try:
            installed = metadata.version(requirement.name)
        except metadata.PackageNotFoundError:
            mismatches.append(f"{requirement.name}: missing")
            continue
        if installed not in requirement.specifier:
            mismatches.append(f"{requirement.name}: {installed}, expected {requirement.specifier}")
    if mismatches:
        raise RuntimeError("Packages differ from the recorded environment:\n" + "\n".join(mismatches)
                           + "\nRerun the pip install command in README.md using .venv's Python.")
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    print("Setup check passed. No packages or data were changed.")


def choose_chapter(chapters, input_fn=input):
    for number, chapter in enumerate(chapters, 1):
        print(f"{number}. {chapter['id']} | {chapter['title']}")
    while True:
        choice = input_fn("Choose a number (0 exits without running): ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(chapters):
            return chapters[int(choice) - 1]["id"]
        print("Enter one of the displayed numbers, or 0 to exit.")


def run_selected(chapter, root=ROOT, open_report=True):
    print(f"Running {chapter}. Keep this terminal open until Complete appears.", flush=True)
    subprocess.run([sys.executable, str(root / "run.py"), chapter], cwd=root, check=True)
    report = root / "output" / chapter / "chapter.html"
    if not report.is_file():
        raise RuntimeError(f"The expected report was not created: {report}")
    print(f"Your report is ready:\n{report}")
    if open_report:
        try:
            opened = webbrowser.open(report.resolve().as_uri())
        except webbrowser.Error:
            opened = False
        if not opened:
            print("The browser could not open. Open the HTML path printed above.")
    return report


def main():
    chapters = json.loads((ROOT / "chapters.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter", nargs="?", choices=[c["id"] for c in chapters])
    parser.add_argument("--check", action="store_true", help="Check setup without running a chapter.")
    parser.add_argument("--list", action="store_true", help="List chapters without running them.")
    parser.add_argument("--no-open", action="store_true", help="Keep the generated report closed.")
    args = parser.parse_args()
    if args.list:
        for chapter in chapters:
            print(f"{chapter['id']} | {chapter['title']}")
        return
    try:
        check_setup()
        if args.check:
            return
        chapter = args.chapter
        if chapter is None:
            if not sys.stdin.isatty():
                parser.error("Specify a chapter when using a noninteractive terminal; use --list for choices.")
            chapter = choose_chapter(chapters)
        if chapter is not None:
            run_selected(chapter, open_report=not args.no_open)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled. No further chapter will be started.")
        raise SystemExit(130)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Stopped: {exc}\nSee README.md troubleshooting. A failed run is not a completed report.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
