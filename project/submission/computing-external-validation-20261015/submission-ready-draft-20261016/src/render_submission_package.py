"""Render the submission-preparation PDFs and preserve a dedicated QA record."""
from pathlib import Path
import runpy
import shutil

R = Path(__file__).resolve().parents[1]
runpy.run_path(str(R / "src/render_and_check.py"), run_name="__main__")
shutil.copy2(R / "qa/render_checks.json", R / "qa/render_checks_submission.json")
print("submission render record written")
