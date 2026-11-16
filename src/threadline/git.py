"""Thin git helpers. Signatures are verified with ssh-keygen whatever the user's git config says."""

import subprocess
from pathlib import Path

ALLOWED_SIGNERS = Path("qms/signers/allowed_signers")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def work_tree(path: Path) -> Path | None:
    try:
        return Path(_git(path, "rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def signed_commits(git_root: Path, project_root: Path, path: Path) -> list[tuple[str, str, str]]:
    """(commit, status, principal) for every commit touching path. status 'G' = good signature."""
    signers = (project_root / ALLOWED_SIGNERS).resolve()
    out = _git(git_root, "-c", "gpg.ssh.program=ssh-keygen", "-c", f"gpg.ssh.allowedSignersFile={signers}",
               "log", "--format=%H%x1f%G?%x1f%GS", "--", str(path.resolve()))
    return [tuple(line.split("\x1f")) for line in out.splitlines()]


def show(git_root: Path, ref: str, path: Path) -> str | None:
    rel = path.resolve().relative_to(git_root.resolve())
    try:
        return _git(git_root, "show", f"{ref}:{rel.as_posix()}")
    except subprocess.CalledProcessError:
        return None  # file did not exist at ref
