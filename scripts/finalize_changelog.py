#!/usr/bin/env python3
"""
Finalize CHANGELOG.md for a release.

Converts the ## [Unreleased] heading to ## [X.Y.Z] - YYYY-MM-DD
and inserts a fresh empty ## [Unreleased] section above it for the
next development cycle.

Usage (called by publish.yml):
    VERSION=1.2.3 python scripts/finalize_changelog.py
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    version = os.environ.get("VERSION", "").strip()
    if not version:
        print("❌ VERSION environment variable is not set.", file=sys.stderr)
        raise SystemExit(1)

    path = Path("CHANGELOG.md")
    if not path.exists():
        print("❌ CHANGELOG.md not found.", file=sys.stderr)
        raise SystemExit(1)

    content = path.read_text(encoding="utf-8")

    if "## [Unreleased]" not in content:
        print("⚠️  No [Unreleased] section found in CHANGELOG.md — skipping.")
        return

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    versioned_heading = f"## [{version}] - {today}"

    content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n---\n\n{versioned_heading}",
        1,
    )

    path.write_text(content, encoding="utf-8")
    print(f"✅ CHANGELOG.md: [Unreleased] → [{version}] - {today}")


if __name__ == "__main__":
    main()
