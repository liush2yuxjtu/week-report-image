from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FunctionalSmokeTest(unittest.TestCase):
    """Verify public skill structure and deterministic source collection."""

    def test_skill_and_source_inventory(self) -> None:
        """Collect all fixture sources while excluding credential-like files."""
        skill = (ROOT / "SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: week-report-image", skill)
        self.assertIn("description:", skill)

        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            inventory = Path(tmp) / "inventory.json"
            create = [sys.executable, str(ROOT / "scripts/create_functional_fixture.py"), str(fixture)]
            subprocess.run(create, check=True)
            subprocess.run(create, check=True)

            (fixture / "secrets.yml").write_text("project: 星河\naccess_token: do-not-read\n")
            sensitive = fixture / ".aws"
            sensitive.mkdir()
            (sensitive / "credentials.json").write_text('{"project":"星河"}\n')

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
                    "--term",
                    "试点",
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
            source_paths = [source["path"].lower() for source in data["sources"]]
            self.assertEqual(data["schema_version"], 1)
            self.assertGreaterEqual(summary["sources_discovered"], 7)
            self.assertGreaterEqual(summary["git_repositories"], 1)
            self.assertGreaterEqual(summary["relevant_files"], 6)
            self.assertGreaterEqual(summary["recent_commits"], 1)
            self.assertFalse(any("secret" in path or "/.aws/" in path for path in source_paths))

    def test_eval_json(self) -> None:
        """Keep both end-to-end and collection eval suites parseable."""
        for name in ("evals.json", "functional-evals.json"):
            data = json.loads((ROOT / "evals" / name).read_text())
            self.assertEqual(data["skill_name"], "week-report-image")
            self.assertGreaterEqual(len(data["evals"]), 3)


if __name__ == "__main__":
    unittest.main()
