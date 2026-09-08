#!/usr/bin/env python3
"""Create an explicitly synthetic demonstration outside all live campaigns."""

import argparse
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.rimworld.core import Error, atomic_json, atomic_text, read_json
from tools.rimworld.memory import Campaign, init_campaign
from tools.rimworld.knowledge import context
from tools.rimworld.metrics import metrics
from tools.rimworld.history import checkpoint


def demo(output):
    output = Path(output).resolve()
    if output.exists():
        raise Error("Demo output must be a new directory; it never overwrites an existing campaign.")
    output.mkdir(parents=True)
    shutil.copytree(ROOT / "knowledge", output / "knowledge")
    shutil.copytree(ROOT / "templates", output / "templates")
    spec = {"objective": "Synthetic offline demonstration; this is not a real playthrough.",
            "mode": "fresh", "rules": {"fixture_only": True, "honest_play": True},
            "setup": {"dlc": ["Biotech"], "mods": []}}
    init_campaign(output, "synthetic", spec)
    campaign = Campaign(output, "synthetic")
    def fixture_action(*args, **kwargs):
        return campaign.action(*args, **kwargs, origin="fixture")
    status = read_json(ROOT / "tests/fixtures/status.json")
    first = campaign.ingest("get_status", {}, status, origin="fixture")
    campaign.issue({"title": "An interrupted rescue needs follow-through", "rationale": "Patient safety is unverified",
                    "next_action": "Inspect patient location and route hazards", "revisit": "Before advancing",
                    "revisit_tick": 300000, "resolution": "Patient safely arrived and treatment checked",
                    "occurrences": 2})
    action = fixture_action("order_pawn", {"id": "PawnA"}, "Bring patient to safety", "rescue")
    campaign.action_update(action["id"], "accepted", internal=True)
    obs = campaign.ingest("get_pawn", {"id": "PawnA"},
                         {"id": "PawnA", "job": "dropped outside", "mapIndex": 0}, origin="fixture")
    campaign.action_update(action["id"], "interrupted", obs["id"], "Synthetic observation shows patient not delivered")
    guarded = campaign.ingest("get_area", {}, read_json(ROOT / "tests/fixtures/large-area.json"), origin="fixture")
    # Demonstrate compaction of a full ordinary area without dropping warnings.
    area = {"things": [{"id": f"FixtureTree{i}", "def": "Tree", "label": "Synthetic tree",
                        "x": i % 30, "z": i // 30} for i in range(700)],
            "terrainSummary": {"Soil": 700}, "mapIndex": 0}
    start = time.perf_counter()
    compact = campaign.ingest("get_area", {"minX": 0, "maxX": 29, "minZ": 0, "maxZ": 29},
                              area, origin="fixture")
    local_seconds = time.perf_counter() - start
    atomic_json(output / "medicine-context.json", context(campaign, "medicine", "PawnA"))
    chapter = output / "synthetic-chapter.md"
    chapter.write_text("# A synthetic checkpoint\n\nThis is an offline demonstration of the record workflow, not a game event.\n")
    checkpoint(campaign, {"day": 5, "chapter_file": str(chapter), "evidence": [first["id"], obs["id"]],
                         "missed_screenshots": "No game was opened; there is no documentary image.",
                         "review": "Fixture artifact only, clearly labeled.",
                         "report": {"overview": "Synthetic workflow demonstrated",
                                    "accomplishments": "Fresh records, preserved uncertainty, open rescue action",
                                    "losses_and_risks": "The interrupted action remains unresolved in the fixture",
                                    "next_five_days": "Not a real campaign", "next_year": "Not a real campaign"}})
    summary = {"fixture_only": True, "output": str(output),
               "area_payload_bytes": len(json.dumps(area).encode()),
               "compact_response_bytes": len(json.dumps(compact).encode()),
               "local_ingest_and_projection_seconds": round(local_seconds, 6),
               "large_guard_status": guarded["completeness"],
               "metrics": metrics(campaign),
               "limitations": "This measures local fixture processing and output size, not agent-loop speed or gameplay quality."}
    atomic_json(output / "demo-results.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    try:
        print(json.dumps(demo(parser.parse_args().output), indent=2))
    except Error as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        raise SystemExit(2)
