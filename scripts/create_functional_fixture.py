#!/usr/bin/env python3
"""Create deterministic multi-source fixture for week-report-image functional evals."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path, env=None):
    """Run one fixture setup command and fail with captured diagnostics."""
    subprocess.run(cmd, cwd=cwd, env=env, check=True, capture_output=True, text=True)


def prepare_root(root: Path) -> None:
    """Create an empty fixture-owned root without deleting arbitrary data."""
    marker = root / ".week-report-image-fixture"
    if root.exists() and any(root.iterdir()):
        if not marker.is_file():
            raise SystemExit(f"refusing to replace non-fixture directory: {root}")
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    marker.write_text("fixture-owned\n")


def main() -> int:
    """Create a repeatable seven-source fixture at the requested path."""
    ap = argparse.ArgumentParser()
    ap.add_argument("output")
    args = ap.parse_args()
    root = Path(args.output).expanduser().resolve()
    prepare_root(root)
    now = dt.datetime.now().astimezone()
    today = now.date().isoformat()

    files = {
        "project/status.md": f"# 星河增长项目周报\n\n日期：{today}\n状态：内部试用已完成；正式上线待业务验收。\n",
        "meetings/weekly-decision.md": f"# 周会纪要\n\n日期：{today}\n决定：先由华东销售团队试点。负责人：王宁。验收截止：{today}。\n",
        "tasks/tasks.json": json.dumps({"project": "星河增长项目", "updated": today, "tasks": [
            {"id": "T-1", "title": "内部试用", "state": "done"},
            {"id": "T-2", "title": "正式上线审批", "state": "blocked", "needs": "业务负责人确认"}
        ]}, ensure_ascii=False, indent=2) + "\n",
        "metrics/weekly-sales.csv": "project,date,metric,value,definition\n" + f"星河增长项目,{today},试点客户数,12,已完成内部试用的客户数\n",
        "release/acceptance.json": json.dumps({"project": "星河增长项目", "date": today, "environment": "internal", "accepted": True, "production": False}, ensure_ascii=False, indent=2) + "\n",
        "docs/roadmap.md": "# 星河增长项目下一步\n\n1. 完成业务验收\n2. 确认权限和审计规则\n3. 安排正式上线窗口\n",
    }
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    repo = root / "git" / "xinghe-app"
    repo.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.name", "Wang Ning"], repo)
    run(["git", "config", "user.email", "wangning@example.invalid"], repo)
    (repo / "README.md").write_text("# 星河增长应用\n\n支持试点客户工作流。\n")
    run(["git", "add", "README.md"], repo)
    env = os.environ.copy()
    stamp = now.isoformat()
    env.update({"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
    run(["git", "commit", "-q", "-m", "feat: complete internal pilot workflow"], repo, env)

    stale = root / "archive" / "old-status.md"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("# 旧状态\n\n尚未开始。\n")
    old = (now - dt.timedelta(days=30)).timestamp()
    os.utime(stale, (old, old))

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
