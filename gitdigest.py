#!/usr/bin/env python3
"""gitdigest — Generate daily/weekly activity digests across multiple git repos.

Zero dependencies, pure Python stdlib.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def find_git_repos(directories: list[str]) -> list[Path]:
    """Scan directories for git repositories (directories containing .git)."""
    repos = []
    seen = set()
    for d in directories:
        root = Path(d).expanduser().resolve()
        if not root.is_dir():
            continue
        # Walk up to 2 levels deep
        for path in root.iterdir():
            if path.name.startswith("."):
                continue
            git_dir = path / ".git"
            if git_dir.is_dir() and str(path) not in seen:
                repos.append(path)
                seen.add(str(path))
    repos.sort()
    return repos


def run_git_log(repo: Path, since: str, until: str = None) -> list[dict]:
    """Run git log in a repo and return parsed commits."""
    cmd = ["git", "-C", str(repo), "log",
           "--format=%H%n%an%n%ae%n%aI%n%s%n---FILES---",
           "--name-only",
           f"--since={since}"]
    if until:
        cmd.append(f"--until={until}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    output = result.stdout.strip()
    if not output:
        return []

    commits = []
    blocks = output.split("---FILES---\n")
    # Each block is: hash\nauthor\nemail\ndate\nmessage\nfiles...
    raw_blocks = output.split("\n---FILES---")
    for i, block in enumerate(raw_blocks):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if len(lines) < 5:
            continue
        # Lines before ---FILES--- marker: hash, author, email, date, message
        # If this is the last block, it may not have the marker split correctly
        hash_ = lines[0].strip()
        author = lines[1].strip() if len(lines) > 1 else ""
        email = lines[2].strip() if len(lines) > 2 else ""
        date = lines[3].strip() if len(lines) > 3 else ""
        message = lines[4].strip() if len(lines) > 4 else ""
        files = [f.strip() for f in lines[5:] if f.strip()]
        commits.append({
            "hash": hash_,
            "author": author,
            "email": email,
            "date": date,
            "message": message,
            "files": files
        })
    return commits


def output(data, fmt: str):
    """Print output in text or JSON format."""
    if fmt == "json":
        json.dump(data, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        if isinstance(data, dict):
            for k, v in data.items():
                print(v)
        elif isinstance(data, list):
            for item in data:
                print(item)
        else:
            print(data)


def cmd_today(args):
    repos = find_git_repos(args.repos)
    if not repos:
        output({"error": "No git repositories found."}, args.format)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    all_results = {}

    for repo in repos:
        commits = run_git_log(repo, since=today)
        if commits:
            all_results[str(repo)] = commits

    if args.format == "json":
        output({"date": today, "repos": all_results}, args.format)
    else:
        print(f"Git Digest — {today}\n")
        if not all_results:
            print("No commits found today.")
        else:
            for repo_path, commits in all_results.items():
                repo_name = Path(repo_path).name
                print(f"=== {repo_name} ({len(commits)} commit{'s' if len(commits) != 1 else ''}) ===")
                for c in commits:
                    ts = c["date"][:19] if len(c["date"]) > 19 else c["date"]
                    files_str = ", ".join(c["files"][:5])
                    if len(c["files"]) > 5:
                        files_str += f" (+{len(c['files']) - 5} more)"
                    print(f"  {ts}")
                    print(f"  {c['message']}")
                    print(f"  Author: {c['author']}")
                    print(f"  Files: {files_str}")
                    print(f"  Hash: {c['hash'][:8]}")
                    print()
                print()


def cmd_week(args):
    repos = find_git_repos(args.repos)
    if not repos:
        output({"error": "No git repositories found."}, args.format)
        sys.exit(1)

    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    all_results = {}

    for repo in repos:
        commits = run_git_log(repo, since=since)
        if commits:
            all_results[str(repo)] = commits

    if args.format == "json":
        output({"since": since, "until": datetime.now().strftime("%Y-%m-%d"),
                "repos": all_results}, args.format)
    else:
        print(f"Git Digest — {since} through today\n")
        if not all_results:
            print("No commits in the past 7 days.")
        else:
            total = sum(len(v) for v in all_results.values())
            print(f"Total: {total} commits across {len(all_results)} repo{'s' if len(all_results) != 1 else ''}\n")
            for repo_path, commits in all_results.items():
                repo_name = Path(repo_path).name
                print(f"=== {repo_name} ({len(commits)} commit{'s' if len(commits) != 1 else ''}) ===")
                for c in commits:
                    ts = c["date"][:19] if len(c["date"]) > 19 else c["date"]
                    files_str = ", ".join(c["files"][:5])
                    if len(c["files"]) > 5:
                        files_str += f" (+{len(c['files']) - 5} more)"
                    print(f"  {ts}")
                    print(f"  {c['message']}")
                    print(f"  Author: {c['author']}")
                    print(f"  Files: {files_str}")
                    print(f"  Hash: {c['hash'][:8]}")
                    print()
                print()


def cmd_since(args):
    repos = find_git_repos(args.repos)
    if not repos:
        output({"error": "No git repositories found."}, args.format)
        sys.exit(1)

    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        output({"error": f"Invalid date '{args.date}'. Use YYYY-MM-DD format."}, args.format)
        sys.exit(1)

    all_results = {}
    for repo in repos:
        commits = run_git_log(repo, since=args.date)
        if commits:
            all_results[str(repo)] = commits

    if args.format == "json":
        output({"since": args.date, "until": datetime.now().strftime("%Y-%m-%d"),
                "repos": all_results}, args.format)
    else:
        print(f"Git Digest — {args.date} through today\n")
        if not all_results:
            print(f"No commits since {args.date}.")
        else:
            total = sum(len(v) for v in all_results.values())
            print(f"Total: {total} commits across {len(all_results)} repo{'s' if len(all_results) != 1 else ''}\n")
            for repo_path, commits in all_results.items():
                repo_name = Path(repo_path).name
                print(f"=== {repo_name} ({len(commits)} commit{'s' if len(commits) != 1 else ''}) ===")
                for c in commits:
                    ts = c["date"][:19] if len(c["date"]) > 19 else c["date"]
                    files_str = ", ".join(c["files"][:5])
                    if len(c["files"]) > 5:
                        files_str += f" (+{len(c['files']) - 5} more)"
                    print(f"  {ts}")
                    print(f"  {c['message']}")
                    print(f"  Author: {c['author']}")
                    print(f"  Files: {files_str}")
                    print(f"  Hash: {c['hash'][:8]}")
                    print()
                print()


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")

    p = argparse.ArgumentParser(
        prog="gitdigest",
        description="Generate daily/weekly activity digests across multiple git repos.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # today
    s_today = sub.add_parser("today", parents=[common],
                             help="Show commits from today")
    s_today.add_argument("--repos", nargs="+", default=["~/projects/"],
                         help="Directories to scan for git repos (default: ~/projects/)")

    # week
    s_week = sub.add_parser("week", parents=[common],
                            help="Show commits from past 7 days")
    s_week.add_argument("--repos", nargs="+", default=["~/projects/"],
                        help="Directories to scan for git repos (default: ~/projects/)")

    # since
    s_since = sub.add_parser("since", parents=[common],
                             help="Show commits since a given date")
    s_since.add_argument("date", help="Date in YYYY-MM-DD format")
    s_since.add_argument("--repos", nargs="+", default=["~/projects/"],
                         help="Directories to scan for git repos (default: ~/projects/)")

    args = p.parse_args()

    if args.cmd == "today":
        cmd_today(args)
    elif args.cmd == "week":
        cmd_week(args)
    elif args.cmd == "since":
        cmd_since(args)


if __name__ == "__main__":
    main()
