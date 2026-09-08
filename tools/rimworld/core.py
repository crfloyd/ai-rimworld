"""Small file primitives. No game access occurs in this module."""

import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import uuid


class Error(Exception):
    """An actionable failure, rather than an empty successful result."""


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identifier(prefix=""):
    return prefix + uuid.uuid4().hex


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", value):
        raise Error("Use a 1–64 character lowercase identifier: letters, digits, - or _.")
    return value


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise Error(f"Cannot read JSON at {path}: {exc}") from exc


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def atomic_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_json(path, value):
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def append_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(canonical(value) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def journal(path, offset=0):
    """Read complete records; corruption is never silently skipped."""
    path = Path(path)
    if not path.exists():
        if offset:
            raise Error(f"Missing journal {path} with nonzero projection offset.")
        return [], 0
    with path.open("rb") as stream:
        if offset > path.stat().st_size:
            raise Error(f"Journal shrank: {path}. Reconcile evidence before rebuilding.")
        stream.seek(offset)
        data = stream.read()
        end = stream.tell()
    if data and not data.endswith(b"\n"):
        raise Error(f"Incomplete journal tail at {path}; preserve it and reconcile before writing.")
    try:
        return [json.loads(line) for line in data.splitlines() if line], end
    except (UnicodeDecodeError, ValueError) as exc:
        raise Error(f"Corrupt journal {path}: {exc}") from exc


_held_locks = threading.local()


@contextlib.contextmanager
def lock(path):
    path = Path(path).resolve()
    held = getattr(_held_locks, "paths", set())
    if str(path) in held:
        yield
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Error(f"Another process owns {path}. Inspect it; do not start another controller.") from exc
        held.add(str(path)); _held_locks.paths = held
        try:
            yield
        finally:
            held.remove(str(path))
            fcntl.flock(stream, fcntl.LOCK_UN)


def require_fields(value, fields):
    if not isinstance(value, dict):
        raise Error("Expected a JSON object.")
    missing = [f for f in fields if f not in value or value[f] in (None, "", [])]
    if missing:
        raise Error("Missing required fields: " + ", ".join(missing))


def contained(root, relative):
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise Error(f"Path escapes its workspace: {relative}")
    return target


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return None
    except (TypeError, ValueError):
        return None


def journal_entries(path, offset=0):
    """Stream validated records with byte offsets for a rebuildable, constant-size index entry."""
    path = Path(path)
    if not path.exists():
        if offset: raise Error(f"Missing journal {path} with nonzero offset.")
        return
    with path.open("rb") as stream:
        if offset > path.stat().st_size: raise Error(f"Journal shrank: {path}; reconcile evidence.")
        stream.seek(offset)
        while True:
            start = stream.tell()
            line = stream.readline()
            if not line: break
            if not line.endswith(b"\n"): raise Error(f"Incomplete journal tail at {path}; reconcile before writing.")
            try:
                value = json.loads(line)
            except (UnicodeDecodeError, ValueError) as exc:
                raise Error(f"Corrupt journal {path} at byte {start}: {exc}") from exc
            yield value, start, stream.tell()
