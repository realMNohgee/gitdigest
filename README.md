# GitDigest 🏷️

**Generate daily/weekly activity digests across multiple git repositories.** Zero dependencies, pure Python stdlib.

Scans directories for git repos and collects recent commits — grouped by repo with authors, messages, and changed files. Perfect for standup notes, activity reports, or tracking progress across a monorepo-less project landscape.

> Part of the **Trust & Reliability Layer for Agentic AI** — provenance, economics, truth, and interop tools for people building on agentic models.

## Why it exists

When you work across dozens of repos (microservices, libraries, tools), answering "what did I do today?" means running `git log` in each one. GitDigest does it in one command — scan, collect, and summarize commits across your entire project directory.

## One tool, many domains

| Domain | What GitDigest does |
|---|---|
| 📋 **Standup Prep** | Generate a daily activity summary across all your repos |
| 📊 **Progress Tracking** | See weekly commit activity at a glance |
| 🔍 **Code Auditing** | Find all recent changes across a project ecosystem |

## Install
```bash
git clone git@github.com:realMNohgee/gitdigest.git
cd gitdigest
python3 gitdigest.py --help
```

## Quick start
```bash
# Commits from today across ~/projects/
python3 gitdigest.py today

# Commits from the past 7 days
python3 gitdigest.py week

# Commits since a specific date
python3 gitdigest.py since 2026-06-01

# Scan custom directories
python3 gitdigest.py week --repos ~/work/ ~/side-projects/

# JSON output for scripting
python3 gitdigest.py week --format json
```

Output:
```
$ python3 gitdigest.py week
Git Digest — 2026-06-23 through today

Total: 31 commits across 22 repos

=== agentrouter (2 commits) ===
  2026-06-27T16:37:49
  add README + license
  Author: realMNohgee
  Hash: 1965be17

=== portalfolio (2 commits) ===
  2026-06-27T17:02:04
  fix: instant portfolio reveal on win
  Author: realMNohgee
  Files: game.html
  Hash: 81ef7cf1
```

## License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)** — the open, agent-agnostic marketplace for AI agent tools.
