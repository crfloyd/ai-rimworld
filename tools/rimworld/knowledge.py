"""Reviewed lessons and situation-specific retrieval; no automatic generalization."""

import json
import shutil
from pathlib import Path

from .core import (Error, append_json, atomic_json, atomic_text, digest, identifier, lock, now,
                   read_json, require_fields, slug)


TOPICS = ("combat", "medicine", "economy", "construction", "recruitment", "travel",
          "victory", "control", "memory", "history")
from .observations import freshness


STATUSES = ("provisional", "corroborated", "disputed", "retired")


def save_lesson(root, lesson, review, *, campaign=None, shared=False):
    if campaign is None and not shared:
        raise Error("Select a run for learning; shared-library writes require explicit shared=True review.")
    if campaign is not None and shared:
        raise Error("Use explicit promotion for moving a run lesson into shared advice.")
    require_fields(lesson, ("id", "title", "topics", "applicability", "observed",
                           "explanation", "recommendation", "exceptions", "verify", "evidence", "status"))
    slug(lesson["id"])
    if lesson["status"] not in STATUSES or not set(lesson["topics"]) <= set(TOPICS):
        raise Error("Unknown lesson status or topic.")
    if not review:
        raise Error("A lesson change requires a review explaining the supporting/contradicting evidence.")
    if not isinstance(lesson["evidence"], list) or not all(isinstance(e, dict) and e.get("source") for e in lesson["evidence"]):
        raise Error("Evidence must be a list of records with original sources.")
    if lesson["status"] == "corroborated" and len(lesson["evidence"]) < 2:
        raise Error("Corroboration requires multiple evidence records and review of their independence.")
    if not isinstance(lesson["applicability"], dict):
        raise Error("Applicability must state version/DLC/mod scope and limitations.")
    base = (campaign.path if campaign else Path(root)) / "knowledge"
    if base.is_symlink() or (base / "lessons").is_symlink():
        raise Error("Knowledge compartments must not be symlinks.")
    if campaign:
        for evidence in lesson["evidence"]:
            if evidence.get("observation"):
                campaign.observation(evidence["observation"])
            if evidence.get("outcome"):
                from .continuity import event_index
                event = event_index(campaign).get(evidence["outcome"])
                if not event or event.get("kind") != "outcome": raise Error("Lesson outcome evidence must belong to this run.")
    with lock(base / ".knowledge.lock"):
        path = base / "lessons" / (lesson["id"] + ".json")
        old = read_json(path) if path.exists() else None
        record = dict(lesson, reviewed_at=now(), review=review,
                      scope="run" if campaign else "shared",
                      campaign_id=campaign.meta["id"] if campaign else None,
                      revision=(old.get("revision", 0) if old else 0) + 1)
        append_json(base / "reviews.jsonl", {"at": now(), "before": old, "after": record})
        atomic_json(path, record)
        lines = [f"# {record['title']}", "", f"Status: {record['status']}; reviewed {record['reviewed_at']}.",
                 "Topics: " + ", ".join(record["topics"]), ""]
        for key in ("applicability", "observed", "explanation", "recommendation",
                    "exceptions", "verify", "evidence", "review"):
            value = record[key]
            lines += [f"## {key.replace('_', ' ').capitalize()}", "",
                      value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False), ""]
        atomic_text(path.with_suffix(".md"), "\n".join(lines))
        index(campaign.path if campaign else root)
        return record


def index(root):
    base = Path(root) / "knowledge"
    lines = ["# Knowledge index", "",
             "Load the topic needed for the current decision. Scope and evidence remain part of each lesson.",
             "Disputed and retired lessons are warnings/history, not active recommendations.", ""]
    for topic in TOPICS:
        playbook = base / "playbooks" / (topic + ".md")
        if playbook.exists():
            lines += [f"- [{topic}](playbooks/{topic}.md)"]
    lines += ["", "## Lessons", ""]
    for path in sorted((base / "lessons").glob("*.json")):
        lesson = read_json(path)
        lines += [f"- [{lesson['title']}](lessons/{path.stem}.md) — {lesson['status']}; " +
                  ", ".join(lesson["topics"])]
    atomic_text(base / "INDEX.md", "\n".join(lines) + "\n")


def retrieve(root, topic, setup=None, *, full=False):
    if topic not in TOPICS:
        raise Error("Unknown topic: " + topic)
    base = Path(root) / "knowledge"
    setup = setup or {}
    dlcs = {x.lower() for x in setup.get("dlc", [])}
    result = {"topic": topic, "playbook": None, "lessons": [], "cautions": []}
    playbook = base / "playbooks" / (topic + ".md")
    if playbook.exists():
        result["playbook"] = playbook.read_text() if full else {"path": str(playbook), "load_before": "major topic decision if not already in context"}
    for path in sorted((base / "lessons").glob("*.json")):
        lesson = read_json(path)
        if topic not in lesson["topics"]:
            continue
        applicability = lesson["applicability"]
        required = {d.lower() for d in applicability.get("required_dlc", [])}
        required_mods = {str(m).lower() for m in applicability.get("required_mods", [])}
        mods = {str(m).lower() for m in setup.get("mods", [])}
        versions = applicability.get("game_versions", [])
        if (required_mods and not required_mods <= mods) or (versions and setup.get("game_version") not in versions):
            result["cautions"].append({"lesson": lesson["id"], "reason": "Exact game/mod applicability unverified", "detail": str(path)})
            continue
        if required and not required <= dlcs:
            result["cautions"].append({"lesson": lesson["id"], "reason": "DLC applicability unverified"})
            continue
        if lesson["status"] in ("retired", "disputed"):
            result["cautions"].append({"lesson": lesson["id"], "status": lesson["status"],
                                       "review": lesson["review"], "path": str(path.with_suffix(".md"))})
        else:
            # Version matching is explicitly reviewed; no invented semver equivalence for game builds.
            result["lessons"].append(lesson if full else {
                k: lesson[k] for k in ("id", "title", "status", "topics", "applicability",
                                      "recommendation", "exceptions", "verify", "revision") if k in lesson})
            result["lessons"][-1]["detail"] = str(path)
    return result


def context(campaign, topic, entity=None):
    tools_by_topic = {
        "combat": {"get_pawn", "get_area", "list_things", "list_fires"},
        "medicine": {"get_pawn", "get_resources"},
        "economy": {"get_resources", "get_area", "get_research", "get_conditions"},
        "construction": {"get_area", "inspect_thing", "room_graph", "get_resources"},
        "recruitment": {"get_pawn", "get_quest"},
        "travel": {"get_quest", "get_pawn", "get_resources", "inspect_thing", "get_map"},
        "victory": {"get_quest", "get_research", "inspect_thing", "get_resources"},
        "control": {"get_status", "get_window_ui", "inspect_thing"},
        "memory": {"get_status"}, "history": {"get_status"}}
    knowledge = run_knowledge(campaign, topic)
    state = campaign.state()
    details = []
    retired = campaign._retired()
    from .facts import entries
    for entry in entries(state, tools=tools_by_topic[topic]):
        obs = entry["latest"]
        if obs["id"] in retired:
            continue
        if obs["tool"] not in tools_by_topic[topic]:
            continue
        if entity and entity not in (obs["args"].get("id"), obs["args"].get("name")):
            continue
        details.append({"tool": obs["tool"], "scope": obs["scope"], "id": obs["id"],
                        "tick": obs["tick"], "captured_at": obs["captured_at"],
                        "completeness": obs["completeness"], "evidence": obs["raw"],
                        **freshness(obs, state, campaign.meta)})
    knowledge.update(campaign=campaign.meta["name"], facts=details,
                     strategy={"path": str(campaign.path / "STRATEGY.md"),
                               "required": "Read rationale before major commitments or if absent from context."},
                     issues=[i for i in campaign.issue_reviews(state) if i.get("critical") or
                             i.get("revisit_due") or i.get("recurring") or not i.get("topics") or topic in i["topics"]])
    if not details:
        knowledge["missing"] = "No matching campaign details recorded. Inspect before the dependent decision."
    return knowledge


def adopt_shared(campaign, review, *, initial=False):
    """Copy a reviewed baseline, never live-read another run's changing knowledge."""
    if not review: raise Error("Shared adoption requires a review.")
    base = campaign.path / "knowledge"
    if base.is_symlink(): raise Error("Knowledge directory must not be a symlink.")
    with lock(base / ".knowledge.lock"):
        adoption = identifier("adoption-")
        dest = base / "adoptions" / adoption
        source = campaign.root / "knowledge"
        manifest = {"id": adoption, "at": now(), "review": review, "campaign_id": campaign.meta["id"], "files": {}}
        for folder in ("lessons", "playbooks"):
            for path in sorted((source / folder).glob("*")):
                if path.is_symlink(): raise Error("Shared advice must not be a symlink.")
                if folder == "lessons":
                    if path.suffix != ".json" or read_json(path).get("scope") != "shared": continue
                elif path.suffix != ".md": continue
                rel = folder + "/" + path.name
                target = dest / "knowledge" / rel
                atomic_text(target, path.read_text())
                manifest["files"][rel] = digest(path.read_text())
        atomic_json(dest / "manifest.json", manifest)
        atomic_json(base / "adopted.json", {"id": adoption, "manifest": str(dest.relative_to(campaign.path) / "manifest.json")})
    return manifest


def run_knowledge(campaign, topic, *, full=False):
    local = retrieve(campaign.path, topic, campaign.meta.get("setup"), full=full)
    selected = campaign.path / "knowledge" / "adopted.json"
    if not selected.exists():
        local["cautions"].append({"reason": "No adopted shared baseline; adopt explicitly after review. Legacy root lessons are not assumed run-local."})
        return local
    adoption = read_json(selected)
    slug(adoption["id"])
    base = campaign.path / "knowledge" / "adoptions" / adoption["id"]
    manifest = read_json(base / "manifest.json")
    if manifest.get("campaign_id") != campaign.meta["id"]: raise Error("Adoption belongs to another run.")
    for rel, expected in manifest["files"].items():
        from .core import contained
        if digest(contained(base / "knowledge", rel).read_text()) != expected:
            raise Error("Adopted shared advice changed; reconcile its evidence before use.")
    inherited = retrieve(base, topic, campaign.meta.get("setup"), full=full)
    local_ids = {p.stem for p in (campaign.path / "knowledge" / "lessons").glob("*.json")}
    local["lessons"] += [dict(lesson, inherited_from=adoption["id"]) for lesson in inherited["lessons"] if lesson["id"] not in local_ids]
    local["cautions"] += inherited["cautions"]
    local["playbook"] = local["playbook"] or inherited["playbook"]
    local["adopted_baseline"] = adoption["id"]
    return local


def promote(campaign, lesson_id, generalized, review):
    """Explicit editorial promotion; the entire private run lesson is never copied."""
    local = read_json(campaign.path / "knowledge" / "lessons" / (slug(lesson_id) + ".json"))
    if local.get("campaign_id") != campaign.meta["id"]:
        raise Error("Promotion source must be a lesson owned by this run.")
    if not review or not generalized.get("generalization_review"):
        raise Error("Review applicability, counterexamples and removal of run-specific identifiers in the generalized draft.")
    text = json.dumps(generalized)
    if "campaigns/" in text or campaign.meta["id"] in text:
        raise Error("Shared advice cannot embed private run paths or campaign identity.")
    draft = dict(generalized, promoted_source_digest=digest(local))
    result = save_lesson(campaign.root, draft, review, shared=True)
    campaign.event({"kind": "lesson_promotion", "summary": review,
                    "local_lesson": lesson_id, "shared_lesson": result["id"], "revision": result["revision"]})
    return result


def recall(campaign, query, entity=None, limit=8):
    """Evidence retrieval for an agent's question; no strategic decision or action."""
    import re
    from .mechanics import search
    if type(limit) is not int or not 1 <= limit <= 100: raise Error("Use 1–100 recall results.")
    terms = set(re.findall(r"\w+",query.lower()))
    def score(value):
        text = json.dumps(value,ensure_ascii=False).lower()
        return sum(t in text for t in terms) + (3 if entity and entity.lower() in text else 0)
    lessons = []
    for path in (campaign.path/'knowledge/lessons').glob('*.json'):
        value=read_json(path);rank=score(value)
        if rank: lessons.append((rank,value,path))
    lessons.sort(key=lambda v:(-v[0],v[1]['id']))
    cards=[]
    for rank,v,path in lessons[:limit]:
        cards.append({k:v[k] for k in ('id','title','status','recommendation','exceptions','verify','evidence','applicability') if k in v})
        cards[-1]['detail']=str(path)
    actions=[a for a in campaign._actions(open_only=True).values() if score(a)]
    issues=[i for i in campaign.issue_reviews() if i.get('critical') or i.get('revisit_due') or score(i)]
    return {'query':query,'entity':entity,'live_checked':False,
            'mechanics':search(campaign.root,query,limit=limit,environment=campaign.meta.get('setup',{})),
            'local_lessons':cards,'remaining_lessons':max(0,len(lessons)-len(cards)),
            'pending_intentions':[{k:a[k] for k in ('id','intent','family','status','check','reason') if k in a} for a in actions],
            'unresolved_issues':issues,'strategy':str(campaign.path/'STRATEGY.md'),
            'limits':'Keyword retrieval, not exhaustive reasoning. Use packet for all urgent state; retrieve missing evidence before decisions. Lessons remain hypotheses/advice at their recorded status.'}
