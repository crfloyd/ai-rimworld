"""Rebuildable indexed latest-by-scope evidence; originals remain in the journal.

The mapping hydrates only requested records. Routine views use SQL selectors instead
of parsing every past spatial query. No evidence or unresolved risk is evicted.
"""
import json
from contextlib import closing
import sqlite3
from collections.abc import Mapping


class Facts(Mapping):
    def __init__(self, path):
        self.path = path

    def connect(self):
        return closing(sqlite3.connect(self.path))

    def __getitem__(self, key):
        with self.connect() as db:
            row = db.execute('SELECT entry FROM facts WHERE key=?', (key,)).fetchone()
        if row is None: raise KeyError(key)
        return unpack(row[0])

    def __iter__(self):
        with self.connect() as db:
            keys = db.execute('SELECT key FROM facts ORDER BY rowid').fetchall()
        return iter(r[0] for r in keys)

    def __len__(self):
        with self.connect() as db:
            return db.execute('SELECT COUNT(*) FROM facts').fetchone()[0]

    def values(self):
        return self.select()

    def select(self, tools=None, risks=False):
        clauses, args = [], []
        if tools is not None:
            clauses.append('tool IN (' + ','.join('?' for _ in tools) + ')'); args.extend(tools)
        if risks: clauses.append('attention=1')
        where = ' WHERE ' + ' OR '.join(clauses) if clauses else ''
        with self.connect() as db:
            for row in db.execute('SELECT entry FROM facts' + where + ' ORDER BY rowid', args):
                yield unpack(row[0])


def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS facts (key TEXT PRIMARY KEY, tool TEXT NOT NULL, attention INTEGER NOT NULL, entry TEXT NOT NULL)')
    db.execute('CREATE INDEX IF NOT EXISTS facts_tool ON facts(tool)')
    db.execute('CREATE INDEX IF NOT EXISTS facts_attention ON facts(attention)')
    db.execute('CREATE TABLE IF NOT EXISTS metadata (id INTEGER PRIMARY KEY, state TEXT NOT NULL)')


def entries(state, tools=None, risks=False):
    facts = state['facts']
    if isinstance(facts, Facts): return facts.select(tools, risks)
    # Supports injected states in independent fixtures.
    from .safety import signals
    return (e for e in facts.values() if (tools is None and not risks) or
            e['latest']['tool'] in (tools or ()) or (risks and signals(e['latest'])))


def unpack(value):
    entry = json.loads(value)
    if entry['latest']['completeness'] == 'known': entry['last_known'] = entry['latest']
    return entry
