"""Thin git helpers. Signatures are verified with ssh-keygen whatever the user's git config says."""

import subprocess
import tempfile
from functools import cache
from pathlib import Path

ALLOWED_SIGNERS = Path("qms/signers/allowed_signers")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def work_tree(path: Path) -> Path | None:
    try:
        return Path(_git(path, "rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_shallow(git_root: Path) -> bool:
    return _git(git_root, "rev-parse", "--is-shallow-repository").strip() == "true"


def rel(git_root: Path, path: Path) -> str:
    return path.resolve().relative_to(git_root.resolve()).as_posix()


def commits_touching(git_root: Path, path: Path) -> list[str]:
    """Commits that changed path, newest first."""
    return _git(git_root, "log", "--format=%H", "--", rel(git_root, path)).split()


def parent(git_root: Path, sha: str) -> str | None:
    try:
        return _git(git_root, "rev-parse", f"{sha}^").strip()
    except subprocess.CalledProcessError:
        return None  # root commit


def show(git_root: Path, ref: str | None, path: Path) -> str | None:
    """File content at ref, or None if it did not exist there."""
    if ref is None:
        return None
    try:
        return _git(git_root, "show", f"{ref}:{rel(git_root, path)}")
    except subprocess.CalledProcessError:
        return None


@cache
def signature(git_root: Path, sha: str, allowed_signers: str) -> tuple[str, str]:
    """(status, principal) of commit sha checked against the given allowed_signers content. 'G' = good."""
    with tempfile.NamedTemporaryFile("w", suffix=".allowed_signers") as f:
        f.write(allowed_signers)
        f.flush()
        out = _git(
            git_root,
            "-c",
            "gpg.ssh.program=ssh-keygen",
            "-c",
            f"gpg.ssh.allowedSignersFile={f.name}",
            "log",
            "-1",
            "--format=%G?%x1f%GS",
            sha,
        )
    status, _, principal = out.strip().partition("\x1f")
    return status, principal
