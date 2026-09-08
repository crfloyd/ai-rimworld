"""Original screenshots, reviewed chapters and operational reports."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zlib

from .core import (Error, append_json, atomic_json, atomic_text, contained, identifier,
                   journal, lock, now, read_json, require_fields)


def png_size(path):
    raw = Path(path).read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise Error("Use an original PNG screenshot.")
    offset, size, has_pixels = 8, None, False
    while offset + 12 <= len(raw):
        length = struct.unpack(">I", raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise Error("Truncated PNG chunk.")
        kind = raw[offset + 4:offset + 8]
        data = raw[offset + 8:offset + 8 + length]
        crc = struct.unpack(">I", raw[offset + 8 + length:end])[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise Error("PNG checksum mismatch.")
        if size is None:
            if kind != b"IHDR" or length != 13:
                raise Error("PNG lacks its initial image header.")
            size = struct.unpack(">II", data[:8])
            if not all(size):
                raise Error("Screenshot has invalid dimensions.")
        has_pixels |= kind == b"IDAT" and length > 0
        if kind == b"IEND":
            if not has_pixels or length != 0 or end != len(raw):
                raise Error("PNG lacks image data or has an invalid ending.")
            return size
        offset = end
    raise Error("PNG is incomplete.")


def windows(runner=subprocess.run):
    if sys.platform != "darwin":
        raise Error("Automatic window discovery currently supports macOS. Import an original OS/game PNG elsewhere.")
    script = """
import Foundation
import CoreGraphics
let ws = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let matches = ws.filter { (($0[kCGWindowOwnerName as String] as? String) ?? "").lowercased().contains("rimworld") }
let data = try JSONSerialization.data(withJSONObject: matches.map { w in
    ["id": w[kCGWindowNumber as String] ?? 0,
     "owner": w[kCGWindowOwnerName as String] ?? "",
     "title": w[kCGWindowName as String] ?? "",
     "bounds": w[kCGWindowBounds as String] ?? [:]] as [String: Any]
})
print(String(data: data, encoding: .utf8)!)
"""
    try:
        result = runner(["/usr/bin/swift", "-e", script], capture_output=True, text=True, timeout=40)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Error(f"Window discovery unavailable: {exc}; use normal computer control.") from exc
    if result.returncode:
        raise Error("Window discovery failed; check local macOS capture/Swift availability: " + result.stderr[-800:])
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise Error("Window discovery returned malformed output.") from exc


def add_shot(campaign, source, tick, subject, caption, framing, origin="game", *, evidence=None, map_index=None, source_captured_at=None):
    if type(tick) not in (int, float) or tick < 0 or not subject or not caption or not framing:
        raise Error("Capture needs a nonnegative game tick, subject, caption and framing description.")
    if evidence:
        from .continuity import evidence_exists
        evidence_exists(campaign, evidence)
    source = Path(source).resolve()
    width, height = png_size(source)
    shot_id = identifier("shot-")
    day = int(tick / campaign.meta["ticks_per_day"])
    filename = f"day-{day:04d}-{shot_id}.png"
    target = campaign.path / "screenshots" / filename
    metadata = {"id": shot_id, "campaign_id": campaign.meta["id"], "session_id": campaign.meta.get("session_id"),
                "map_index": map_index, "evidence": evidence or [], "source_captured_at": source_captured_at,
                "association": "Importer-claimed scene; visual review and run evidence required for publication.", "tick": tick, "day": day, "subject": subject, "caption": caption,
                "framing": framing, "origin": origin, "captured_at": now(),
                "path": "screenshots/" + filename, "width": width, "height": height,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "reviewed": False, "review_note": None}
    with lock(campaign.path / ".memory.lock"):
        # The bytes are copied unchanged. No crop, enhancement, or reconstruction.
        shutil.copyfile(source, target)
        atomic_json(campaign.path / "screenshots" / (shot_id + ".json"), metadata)
    return metadata


def capture(campaign, window_id, tick, subject, caption, framing, **association):
    candidates = windows()
    if not any(w["id"] == window_id for w in candidates):
        raise Error("The supplied window is not in the current RimWorld window inventory.")
    temp = campaign.path / "screenshots" / (identifier("capture-") + ".png")
    try:
        subprocess.run(["/usr/sbin/screencapture", "-x", "-l", str(window_id), str(temp)],
                       check=True, timeout=20, capture_output=True)
        return add_shot(campaign, temp, tick, subject, caption, framing, source_captured_at=now(), **association)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Error(f"Normal OS screenshot capture failed: {exc}") from exc
    finally:
        if temp.exists():
            temp.unlink()


def review_shot(campaign, shot_id, note):
    if not re.fullmatch(r"shot-[a-f0-9]{32}", shot_id) or not note:
        raise Error("Provide a valid shot ID and a note from actual visual inspection.")
    path = campaign.path / "screenshots" / (shot_id + ".json")
    data = read_json(path)
    if data.get("campaign_id") != campaign.meta["id"]:
        raise Error("Screenshot lacks this run's association; reimport the unchanged original with appropriate evidence.")
    source = contained(campaign.path, data["path"])
    if hashlib.sha256(source.read_bytes()).hexdigest() != data["sha256"]:
        raise Error("Screenshot bytes changed; preserve original documentary evidence.")
    png_size(source)
    data.update(reviewed=True, review_note=note, reviewed_at=now())
    atomic_json(path, data)
    return data


def checkpoint(campaign, spec):
    require_fields(spec, ("day", "chapter_file", "report", "evidence", "review"))
    day = spec["day"]
    if type(day) is not int or day <= 0:
        raise Error("Checkpoint day must be a positive integer.")
    if day % campaign.meta["report_interval_days"]:
        raise Error("Use the scheduled checkpoint day; describe a delayed publication in its review.")
    report = spec["report"]
    require_fields(report, ("overview", "accomplishments", "losses_and_risks", "next_five_days", "next_year"))
    chapter = Path(spec["chapter_file"]).read_text()
    if not chapter.strip():
        raise Error("Chapter is empty.")
    if not spec.get("shots") and not spec.get("missed_screenshots"):
        raise Error("Supply reviewed shots or explain why documentary screenshots were missed.")
    state = campaign.state()
    events, _ = journal(campaign.path / "events.jsonl")
    evidence = {e["id"] for e in events}
    if any(e not in evidence and not campaign.has_observation(e) for e in spec["evidence"]):
        raise Error("Checkpoint cites unknown evidence IDs.")
    if state["latest_tick"] is None or state["latest_tick"] < day * campaign.meta["ticks_per_day"]:
        raise Error("Checkpoint is ahead of the last observed game time.")
    if re.search(r"<img\b|!\[[^\]]*\]\[", chapter, re.I):
        raise Error("Use inline Markdown image links so every documentary image can be checked.")
    declared_paths = set()
    image_targets = [target.strip("<>") for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", chapter)]
    for shot_id in spec.get("shots", []):
        if not re.fullmatch(r"shot-[a-f0-9]{32}", shot_id):
            raise Error("Invalid screenshot ID.")
        shot = read_json(campaign.path / "screenshots" / (shot_id + ".json"))
        if shot.get("campaign_id") != campaign.meta["id"] or not shot.get("evidence"):
            raise Error("Published shots must be associated with this run and cite its evidence.")
        from .continuity import evidence_exists
        evidence_exists(campaign, shot["evidence"])
        if not shot["reviewed"]:
            raise Error("Screenshot requires actual visual review before publication.")
        source = contained(campaign.path, shot["path"])
        if hashlib.sha256(source.read_bytes()).hexdigest() != shot["sha256"]:
            raise Error("Screenshot changed after review.")
        declared_paths.add(str(source))
        if shot["path"] not in image_targets and str(source) not in image_targets:
            raise Error("Chapter does not link one of its declared screenshots.")
    for target in image_targets:
        image = contained(campaign.path, target)
        if str(image) not in declared_paths:
            raise Error("Chapter contains an undeclared or unreviewed image: " + target)
        if not image.exists():
            raise Error("Broken screenshot link: " + target)
    warnings = [phrase for phrase in ("next chapter is due", "tool call", "verified the tool",
                                     "next full chapter") if phrase in chapter.lower()]
    committed = dict(spec)
    committed["chapter"] = chapter
    committed.pop("chapter_file")
    fingerprint = hashlib.sha256(json.dumps(committed, sort_keys=True).encode()).hexdigest()
    checkpoint_id = f"checkpoint-day-{day}"
    marker = f"<!-- {checkpoint_id}:{fingerprint} -->"
    target = campaign.path / "reports" / f"day-{day:04d}.json"
    with lock(campaign.path / ".memory.lock"):
        if target.exists() and read_json(target)["fingerprint"] != fingerprint:
            raise Error("A different checkpoint already exists for this day; preserve the published evidence.")
        atomic_json(target, dict(committed, fingerprint=fingerprint, committed_at=now(),
                                 narrative_warnings=warnings))
        report_md = [f"# Day {day} operational report", ""]
        for key, value in report.items():
            report_md += [f"## {key.replace('_', ' ').capitalize()}", "",
                          value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2), ""]
        atomic_text(target.with_suffix(".md"), "\n".join(report_md))
        book_path = campaign.path / "History.md"
        book = book_path.read_text()
        if marker not in book:
            atomic_text(book_path, book.rstrip() + "\n\n" + marker + "\n\n" + chapter.strip() + "\n")
        existing, _ = journal(campaign.path / "events.jsonl")
        if not any(e.get("id") == checkpoint_id for e in existing):
            append_json(campaign.path / "events.jsonl",
                        {"id": checkpoint_id, "kind": "checkpoint", "day": day, "at": now(),
                         "summary": report["overview"], "evidence": spec["evidence"],
                         "fingerprint": fingerprint})
    campaign.refresh()
    return {"checkpoint": checkpoint_id, "book": str(book_path), "report": str(target.with_suffix(".md")),
            "narrative_warnings": warnings, "review_basis": spec["review"]}
