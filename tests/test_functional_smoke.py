from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FunctionalSmokeTest(unittest.TestCase):
    def test_skill_and_source_inventory(self) -> None:
        skill = (ROOT / "SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: week-report-image", skill)
        self.assertIn("description:", skill)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            inventory = Path(tmp) / "inventory.json"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/create_functional_fixture.py"), str(fixture)],
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/source_inventory.py"),
                    "--root",
                    str(fixture),
                    "--term",
                    "星河",
                    "--term",
                    "试用",
                    "--since-days",
                    "7",
                    "--max-depth",
                    "6",
                    "--output",
                    str(inventory),
                ],
                check=True,
            )
            data = json.loads(inventory.read_text())
            summary = data["summary"]
            self.assertEqual(data["schema_version"], 1)
            self.assertGreaterEqual(summary["sources_discovered"], 7)
            self.assertGreaterEqual(summary["git_repositories"], 1)
            self.assertGreaterEqual(summary["relevant_files"], 6)
            self.assertGreaterEqual(summary["recent_commits"], 1)
            self.assertFalse(any("/.env" in source["path"] for source in data["sources"]))

    def test_eval_json(self) -> None:
        for name in ("evals.json", "functional-evals.json"):
            data = json.loads((ROOT / "evals" / name).read_text())
            self.assertEqual(data["skill_name"], "week-report-image")
            self.assertGreaterEqual(len(data["evals"]), 3)


if __name__ == "__main__":
    unittest.main()
