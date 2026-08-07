"""Path rules for business-article outputs."""

from __future__ import annotations

import os
import pwd
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def real_user_home() -> Path:
    """Return the OS login user's home directory, not an agent sandbox cwd."""
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
    except Exception:
        return Path(os.environ.get("HOME", "~")).expanduser().resolve()


def wechat_workspace_root() -> Path:
    return real_user_home() / "wechat_articles"


def latest_workflow_path() -> Path:
    return wechat_workspace_root() / "_runtime" / "business_workflow" / "latest.json"


def expand_user_path(value: str) -> Path:
    text = value.strip()
    if text == "~":
        return real_user_home()
    if text.startswith("~/"):
        return (real_user_home() / text[2:]).resolve()
    return Path(text).expanduser().resolve()


def reject_literal_tilde(path: Path) -> None:
    if "~" in path.parts:
        fail(
            f"Invalid path contains a literal '~' segment: {path}. "
            "Use the real OS home directory path, e.g. "
            f"{wechat_workspace_root()}."
        )


def ensure_topic_dir(path: Path) -> Path:
    topic_dir = path.resolve()
    reject_literal_tilde(topic_dir)
    root = wechat_workspace_root().resolve()
    try:
        topic_dir.relative_to(root)
    except ValueError:
        fail(
            f"Invalid topic directory outside the real user workspace: {topic_dir}. "
            f"All business-article outputs must live under {root}."
        )
    return topic_dir
