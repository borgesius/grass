#!/usr/bin/env python3
"""
plant.py — GitHub contribution graph art generator

Maps a 7-row ASCII art pattern to dates in the past year and generates
backdated git commits to paint the contribution graph.

Grid orientation:
  - 7 rows = Sunday (top) to Saturday (bottom)
  - Columns = oldest week (left) to newest week (right)

Intensity levels:
  '#' = 100 commits  (darkest green)
  'O' =  75 commits  (dark green)
  'o' =  50 commits  (medium green)
  '.' =  25 commits  (light green)
  ' ' =   0 commits  (empty)

Usage:
  python3 plant.py <pattern_file> [--dry-run] [--clear] [--intensity N] [--repo PATH]
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone


INTENSITY = {
    "#": 100,  # level 4 — darkest green
    "O": 75,   # level 3
    "o": 50,   # level 2
    ".": 25,   # level 1 — lightest green
    " ": 0,
    "\t": 0,
}

GRASS_MARKER = "🌱 grass"


def check_grass_marker(repo: str) -> None:
    marker = os.path.join(repo, ".grass")
    if not os.path.exists(marker):
        print(f"❌ Safety check failed: no .grass marker found in {os.path.abspath(repo)}")
        print("   This doesn't look like a grass repo.")
        print("   Pass --repo /path/to/grass explicitly, or create a .grass file in the target repo.")
        sys.exit(1)


def find_grid_start() -> datetime:
    today = datetime.now(tz=timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    days_since_sunday = today.weekday() + 1
    if today.weekday() == 6:
        days_since_sunday = 0
    last_sunday = today - timedelta(days=days_since_sunday % 7)
    return last_sunday - timedelta(weeks=51)


def parse_pattern(text: str) -> list[list[int]]:
    lines = text.splitlines()
    if len(lines) < 7:
        lines += [" " * (len(lines[0]) if lines else 0)] * (7 - len(lines))
    lines = lines[:7]
    width = max(len(line) for line in lines) if lines else 0
    rows = []
    for line in lines:
        padded = line.ljust(width)
        row = [INTENSITY.get(ch, 0) for ch in padded]
        rows.append(row)
    return rows


def build_date_map(rows: list[list[int]], start: datetime) -> list[tuple[datetime, int]]:
    num_cols = max(len(row) for row in rows) if rows else 0
    entries = []
    for col in range(num_cols):
        week_start = start + timedelta(weeks=col)
        for row_idx, row in enumerate(rows):
            count = row[col] if col < len(row) else 0
            if count > 0:
                date = week_start + timedelta(days=row_idx)
                if date.date() <= datetime.now(tz=timezone.utc).date():
                    entries.append((date, count))
    return entries


def count_existing_grass_commits(repo: str, date: datetime) -> int:
    date_str = date.strftime("%Y-%m-%d")
    result = subprocess.run(
        ["git", "log", "--oneline", "--after", f"{date_str} 00:00:00",
         "--before", f"{date_str} 23:59:59", "--all"],
        cwd=repo, capture_output=True, text=True,
    )
    return sum(1 for line in result.stdout.splitlines() if GRASS_MARKER in line)


def make_commit(repo: str, date: datetime, message: str) -> None:
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        cwd=repo, env=env, check=True, capture_output=True,
    )


def clear_graph_commits(repo: str, dry_run: bool) -> None:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        cwd=repo, capture_output=True, text=True,
    )
    grass_commits = [l for l in result.stdout.splitlines() if GRASS_MARKER in l]

    if not grass_commits:
        print("No grass commits found — nothing to clear.")
        return

    print(f"Found {len(grass_commits)} grass commit(s) to remove.")
    if dry_run:
        print("[dry-run] Would reset repo to a clean orphan branch and force-push.")
        return

    print("Resetting repo to clean state (preserving working files)...")

    # Stash working files so we can restore them after the orphan reset
    subprocess.run(["git", "stash", "--include-untracked"], cwd=repo, capture_output=True)

    subprocess.run(["git", "checkout", "--orphan", "_grass_reset"], cwd=repo, check=True, capture_output=True)
    # Stage only tracked files (don't rm -rf — that nukes the working tree)
    subprocess.run(["git", "reset", "HEAD"], cwd=repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Initial commit"],
        cwd=repo, check=True, capture_output=True,
    )
    subprocess.run(["git", "branch", "-D", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "branch", "-m", "main"], cwd=repo, check=True, capture_output=True)

    result = subprocess.run(
        ["git", "push", "--force", "origin", "main"],
        cwd=repo, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Push failed: {result.stderr}")
        return

    # Restore stashed files
    subprocess.run(["git", "stash", "pop"], cwd=repo, capture_output=True)

    print("✅ Cleared. History reset, working files preserved.")
    print("Run plant.py again to paint a new pattern.")


def preview(entries: list[tuple[datetime, int]], start: datetime) -> None:
    date_map: dict[tuple[int, int], int] = {}
    for date, count in entries:
        delta = date.date() - start.date()
        col = delta.days // 7
        row = delta.days % 7
        date_map[(col, row)] = count

    num_cols = max((c for c, r in date_map), default=0) + 1

    def sym(count: int) -> str:
        if count == 0:    return "·"
        elif count <= 25: return "."
        elif count <= 50: return "o"
        elif count <= 75: return "O"
        else:             return "#"

    print("    " + "".join(str(c % 10) for c in range(num_cols)))
    for row in range(7):
        day = ["Su","Mo","Tu","We","Th","Fr","Sa"][row]
        line = day + "  " + "".join(sym(date_map.get((col, row), 0)) for col in range(num_cols))
        print(line)
    print(f"\nTotal dates to paint: {len(entries)}")
    print(f"Total commits to create: {sum(c for _, c in entries)}")


def run_plant(pattern_file: str, repo: str, dry_run: bool, clear: bool, intensity: int | None = None) -> None:
    check_grass_marker(repo)

    if clear:
        clear_graph_commits(repo, dry_run)
        return

    with open(pattern_file, "r") as f:
        text = f.read()

    rows = parse_pattern(text)
    if intensity is not None:
        rows = [[intensity if v > 0 else 0 for v in row] for row in rows]

    start = find_grid_start()
    entries = build_date_map(rows, start)

    print(f"Pattern: {pattern_file}")
    print(f"Grid start (Sunday): {start.date()}")
    print()
    preview(entries, start)
    print()

    if dry_run:
        print("[dry-run] No commits created.")
        return

    print("Checking existing grass commits (idempotency)...")
    plan: list[tuple[datetime, int]] = []
    total_needed = 0
    for date, count in sorted(entries):
        existing = count_existing_grass_commits(repo, date)
        delta = max(0, count - existing)
        if delta > 0:
            plan.append((date, delta))
            total_needed += delta

    if total_needed == 0:
        print("✅ Already up to date — no new commits needed.")
        return

    skipped = sum(c for _, c in entries) - total_needed
    if skipped > 0:
        print(f"Skipping {skipped} already-present commits, adding {total_needed} new ones.")

    done = 0
    for date, count in plan:
        for i in range(count):
            msg = f"{GRASS_MARKER} {date.strftime('%Y-%m-%d')} [{i+1}/{count}]"
            make_commit(repo, date, msg)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{total_needed} commits...", flush=True)

    print(f"✅ Done — {total_needed} commits created.")
    print("Push with: git push")


def setup_new_repo(remote_url: str, repo: str) -> None:
    """
    Set up this clone as a fresh grass repo pointed at a new remote.
    Wipes all grass commits, swaps the remote, and pushes just the scripts.
    """
    check_grass_marker(repo)

    print(f"Setting up grass for new remote: {remote_url}")

    # Clear all grass commits first
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        cwd=repo, capture_output=True, text=True,
    )
    grass_commits = [l for l in result.stdout.splitlines() if GRASS_MARKER in l]
    if grass_commits:
        print(f"Clearing {len(grass_commits)} existing grass commits...")
        clear_graph_commits(repo, dry_run=False)

    # Swap remote
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=repo, check=True)
    print(f"Remote set to: {remote_url}")

    # Push scripts to new remote
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        cwd=repo, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Push failed: {result.stderr.strip()}")
        print("Make sure the remote repo exists and you have push access.")
        sys.exit(1)

    print("✅ Setup complete. Your grass repo is ready.")
    print(f"   Remote: {remote_url}")
    print("   Next: python3 plant.py patterns/heart.txt --intensity 100 && git push")


def main() -> None:
    parser = argparse.ArgumentParser(description="Paint GitHub contribution graph art using backdated commits.")
    parser.add_argument("pattern", nargs="?", help="Path to 7-row ASCII art pattern file")
    parser.add_argument("--repo", default=".", help="Path to git repo (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating commits")
    parser.add_argument("--clear", action="store_true", help="Wipe all grass commits and reset repo")
    parser.add_argument("--intensity", type=int, default=None, help="Override all cells with N commits")
    parser.add_argument("--setup", metavar="REMOTE_URL", help="Set up this clone for a new GitHub repo (swaps remote, clears grass, pushes scripts)")
    args = parser.parse_args()

    if args.setup:
        setup_new_repo(remote_url=args.setup, repo=args.repo)
        return

    if not args.clear and not args.pattern:
        parser.error("pattern file is required unless --clear or --setup is used")

    run_plant(
        pattern_file=args.pattern or "",
        repo=args.repo,
        dry_run=args.dry_run,
        clear=args.clear,
        intensity=args.intensity,
    )


if __name__ == "__main__":
    main()
