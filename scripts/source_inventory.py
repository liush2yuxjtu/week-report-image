#!/usr/bin/env python3
"""Bounded local source discovery for week-report-image.

Finds relevant files and Git repositories without reading secrets or scanning
unbounded cache/system trees. This is an inventory helper, not evidence grading.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PRUNE = {
    ".git", "node_modules", "Library", ".Trash", ".cache", ".npm", ".pnpm-store",
    "dist", "build", ".next", ".venv", "venv", "__pycache__",
}
TEXT_EXT = {".md", ".txt", ".csv", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".log"}
DOC_EXT = TEXT_EXT | {".pdf", ".docx", ".xlsx", ".xls", ".pptx"}
SECRET_NAMES = {".env", ".env.local", ".npmrc", ".pypirc", "credentials", "credentials.json"}


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=20)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def safe_remote(url: str) -> str:
    if not url:
        return ""
    if "://" in url:
        s = urlsplit(url)
        host = s.hostname or ""
        if s.port:
            host += f":{s.port}"
        return urlunsplit((s.scheme, host, s.path, "", ""))
    return re.sub(r"^[^@\s]+@", "", url)


def relevant(path: Path, terms: list[str]) -> tuple[bool, list[str]]:
    low = path.name.lower()
    hits = [t for t in terms if t in low]
    if hits:
        return True, hits
    if path.suffix.lower() not in TEXT_EXT:
        return False, []
    try:
        if path.stat().st_size > 2_000_000:
            return False, []
        text = path.read_text(errors="ignore")[:200_000].lower()
    except OSError:
        return False, []
    hits = [t for t in terms if t in text]
    return bool(hits), hits


def git_info(repo: Path, cutoff: str, terms: list[str]) -> dict:
    remote_lines = run(["git", "remote", "-v"], repo).splitlines()
    remotes = sorted({safe_remote(x.split()[1]) for x in remote_lines if len(x.split()) >= 2})
    fmt = "%H%x09%aI%x09%an%x09%ae%x09%s"
    log = run(["git", "log", "--all", f"--since={cutoff}", f"--format={fmt}"], repo)
    commits = []
    for line in log.splitlines():
        parts = line.split("\t", 4)
        if len(parts) != 5:
            continue
        hay = " ".join(parts[2:]).lower()
        if terms and not any(t in hay for t in terms):
            # Keep project activity even when person/topic terms do not match.
            matched = []
        else:
            matched = [t for t in terms if t in hay]
        commits.append({
            "hash": parts[0], "date": parts[1], "author": parts[2],
            "email": parts[3], "subject": parts[4], "matched_terms": matched,
        })
    return {
        "source_type": "git_repository",
        "path": str(repo),
        "status": "accessed",
        "remotes": remotes,
        "recent_commit_count": len(commits),
        "recent_commits": commits[:200],
    }


def walk(root: Path, max_depth: int):
    base_depth = len(root.parts)
    for current, dirs, files in os.walk(root):
        cur = Path(current)
        depth = len(cur.parts) - base_depth
        dirs[:] = [d for d in dirs if d not in PRUNE and not d.startswith(".cache")]
        if depth >= max_depth:
            dirs[:] = []
        if (cur / ".git").exists():
            yield "repo", cur
            dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            p = cur / name
            if name in SECRET_NAMES or name.startswith(".env"):
                continue
            if p.suffix.lower() in DOC_EXT:
                yield "file", p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--term", action="append", default=[])
    ap.add_argument("--since-days", type=int, default=7)
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    terms = sorted({x.strip().lower() for x in args.term if x.strip()})
    now = dt.datetime.now().astimezone()
    cutoff = (now - dt.timedelta(days=max(args.since_days - 1, 0))).date().isoformat()
    repos: dict[str, dict] = {}
    files: dict[str, dict] = {}
    roots = []

    for raw in args.root:
        root = Path(raw).expanduser().resolve()
        roots.append({"path": str(root), "status": "accessed" if root.exists() else "missing"})
        if not root.exists() or not root.is_dir():
            continue
        for kind, path in walk(root, args.max_depth):
            if kind == "repo":
                repos.setdefault(str(path), git_info(path, cutoff, terms))
                continue
            ok, hits = relevant(path, terms)
            if not ok:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            files[str(path)] = {
                "source_type": "project_file",
                "path": str(path),
                "status": "accessed",
                "modified_at": dt.datetime.fromtimestamp(stat.st_mtime, tz=now.tzinfo).isoformat(),
                "matched_terms": hits,
            }

    sources = list(repos.values()) + list(files.values())
    report = {
        "schema_version": 1,
        "generated_at": now.isoformat(),
        "cutoff_date": cutoff,
        "terms": terms,
        "roots": roots,
        "summary": {
            "sources_discovered": len(sources),
            "sources_accessed": sum(x["status"] == "accessed" for x in sources),
            "git_repositories": len(repos),
            "relevant_files": len(files),
            "recent_commits": sum(x.get("recent_commit_count", 0) for x in repos.values()),
        },
        "sources": sources,
        "limitations": [
            "Local bounded inventory only; remote APIs, task boards, chat, meetings, and analytics require separate probes.",
            "Inventory hits are candidates, not accepted business facts.",
        ],
    }
    out = Path(args.output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
