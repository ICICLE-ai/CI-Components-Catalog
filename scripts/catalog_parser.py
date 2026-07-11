#!/usr/bin/env python3
"""
catalog_parser.py — reusable helpers for the ICICLE release orchestrator's
"append to the component catalog" step (.claude/skills/icicle-release).

Source of truth lives in the training-catalog skill folder; a deployment copy is
mirrored into CI-Components-Catalog/scripts/ next to build_graphml.py /
load_neo4j.py. Keep the two in sync when editing.

Needs PyYAML (already used by the graph scripts). Subcommands:

  csv-rows    Read the release CSV and print, as JSON, only rows that carry a
              `Component Catalog YAML File` link — each with component name, the
              GitHub yaml link, tags, and release. (Not every row has one.)
  append      Fetch a component's LinkML entry (GitHub blob->raw, or a local file),
              optionally set targetIcicleRelease and trainingTutorialsUrl, re-indent
              it to nest under `components:`, and append it to release_catalog.yml.
              Idempotent: if an entry with the same `id` exists, its block is
              replaced in place instead of duplicated.
  validate    Parse release_catalog.yml and assert every `hasDependentComponents`
              `related_to` resolves to an `id` that exists in the file. Exit 1 and
              list the broken refs otherwise. This is the guard that stops a bad
              dependency from crashing build_graphml.py (KeyError) in CI.

Typical flow for one component (run from the CI-Components-Catalog clone root):
  python3 catalog_parser.py append --catalog release_catalog.yml \
      --source https://github.com/ICICLE-ai/<repo>/blob/main/component.yaml \
      --release 2026-07 \
      --training-url https://icicle-ai.github.io/training-catalog/docs/category/<slug>
  python3 catalog_parser.py validate --catalog release_catalog.yml
"""

import argparse
import csv
import json
import re
import sys
import urllib.request

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("catalog_parser.py needs PyYAML: pip install pyyaml")


# -----------------------------
# Shared helpers (conventions match the doc/api/resource parsers)
# -----------------------------

def blob_to_raw(url: str) -> str:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/blob/(.+)$", url.strip())
    if m:
        user, repo, rest = m.groups()
        return f"https://raw.githubusercontent.com/{user}/{repo}/{rest}"
    return url.strip()


def parse_tags(cell) -> list:
    return [t.strip() for t in str(cell or "").split(",") if t.strip()]


def find_column(fieldnames, *candidates, prefix=False):
    lower = {c.strip().lower(): c for c in fieldnames}
    for cand in candidates:
        if cand.strip().lower() in lower:
            return lower[cand.strip().lower()]
    if prefix:
        for c in fieldnames:
            cl = c.strip().lower()
            if any(cl.startswith(cand.strip().lower()) for cand in candidates):
                return c
    return None


def fetch_text(source: str) -> str:
    if re.match(r"https?://", source):
        with urllib.request.urlopen(blob_to_raw(source)) as resp:  # noqa: S310
            return resp.read().decode("utf-8")
    with open(source, encoding="utf-8") as f:
        return f.read()


# -----------------------------
# Entry-text manipulation (preserve authored formatting — no yaml round-trip)
# -----------------------------

def strip_comment_lines(text: str) -> list:
    return [l.rstrip() for l in text.splitlines() if not l.lstrip().startswith("#")]


def field_indent(lines: list) -> str:
    """Leading whitespace of the entry's field lines (the line after `- id:`)."""
    for l in lines:
        if l.strip().startswith("- id:"):
            continue
        if l.strip():
            return l[: len(l) - len(l.lstrip())]
    return "  "


def entry_id(lines: list) -> str:
    for l in lines:
        m = re.match(r"\s*-?\s*id:\s*(.+)$", l)
        if m:
            return m.group(1).strip().strip("\"'")
    sys.exit("append: source entry has no `id:` field.")


def set_field(lines: list, key: str, value: str, after: str = None) -> list:
    """Replace `key:`'s line if present, else insert it (after `after:` if given,
    else at the end). Value written unquoted, at the entry's field indent."""
    ind = field_indent(lines)
    line = f"{ind}{key}: {value}"
    for i, l in enumerate(lines):
        if re.match(rf"\s*{re.escape(key)}\s*:", l):
            lines[i] = line
            return lines
    if after:
        for i, l in enumerate(lines):
            if re.match(rf"\s*{re.escape(after)}\s*:", l):
                lines.insert(i + 1, line)
                return lines
    lines.append(line)
    return lines


def reindent(lines: list, spaces: int = 2) -> list:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    pad = " " * spaces
    return [pad + l if l.strip() else "" for l in lines]


# -----------------------------
# release_catalog.yml manipulation
# -----------------------------

ENTRY_START = re.compile(r"^ {0,3}- id:\s*(.+)$")


def entry_spans(cat_lines: list):
    """Yield (id, start, end) for each top-level component entry block."""
    starts = [i for i, l in enumerate(cat_lines) if ENTRY_START.match(l)]
    for idx, i in enumerate(starts):
        cid = ENTRY_START.match(cat_lines[i]).group(1).strip().strip("\"'")
        end = starts[idx + 1] if idx + 1 < len(starts) else len(cat_lines)
        yield cid, i, end


# -----------------------------
# Subcommands
# -----------------------------

def cmd_csv_rows(args):
    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fn = reader.fieldnames or []
        comp_c = find_column(fn, "Component")
        yaml_c = find_column(fn, "Component Catalog YAML File", "Component Catalog YAML",
                             "Catalog YAML", prefix=True)
        tags_c = find_column(fn, "Tags", prefix=True)
        rel_c = find_column(fn, "Release Dates", "Release", prefix=True)
        if not yaml_c:
            sys.exit("CSV has no 'Component Catalog YAML File' column.")
        only = {n.strip().lower() for n in ",".join(args.only or []).split(",") if n.strip()}
        rows = []
        for r in reader:
            link = (r.get(yaml_c) or "").strip()
            if not link or link.lower() == "nan":
                continue
            name = (r.get(comp_c) or "").strip() if comp_c else ""
            if only and name.strip().lower() not in only:
                continue
            rows.append({
                "component": name,
                "yaml_url": link,
                "tags": parse_tags(r.get(tags_c)) if tags_c else [],
                "release": (r.get(rel_c) or "").strip() if rel_c else "",
            })
    json.dump(rows, sys.stdout, indent=2)
    print()


def cmd_append(args):
    lines = strip_comment_lines(fetch_text(args.source))
    if args.release:
        set_field(lines, "targetIcicleRelease", args.release)
    if args.training_url:
        set_field(lines, "trainingTutorialsUrl", args.training_url,
                  after="trainingTutorialsAvailable")
        if args.also_usage_url:
            set_field(lines, "usageDocumentationUrl", args.training_url,
                      after="usageDocumentationAvailable")
    cid = entry_id(lines)
    block = reindent(lines, args.indent)

    with open(args.catalog, encoding="utf-8") as f:
        cat = f.read().splitlines()

    existing = next(((c, s, e) for c, s, e in entry_spans(cat) if c == cid), None)
    if existing:
        _, s, e = existing
        # keep trailing blank lines that belonged to the old block
        tail = e
        while tail > s and not cat[tail - 1].strip():
            tail -= 1
        cat[s:tail] = block
        action = "replaced"
    else:
        if cat and cat[-1].strip():
            cat.append("")
        cat += block
        action = "appended"

    out = "\n".join(cat).rstrip("\n") + "\n"
    with open(args.catalog, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"{action}: {cid}")


def cmd_validate(args):
    with open(args.catalog, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    comps = (data or {}).get("components") or []
    ids = {str(c.get("id")) for c in comps}
    broken = []
    for c in comps:
        for dep in (c.get("hasDependentComponents") or []):
            rid = str(dep.get("related_to"))
            if rid not in ids:
                broken.append((str(c.get("id")), rid))
    print(f"components: {len(comps)} | dependency edges checked: "
          f"{sum(len(c.get('hasDependentComponents') or []) for c in comps)}")
    if broken:
        print(f"UNRESOLVED dependsOn ({len(broken)}) — build_graphml.py would KeyError:")
        for owner, rid in broken:
            print(f"  {owner}  ->  related_to: {rid}  (no such id)")
        sys.exit(1)
    print("OK: every related_to resolves to an existing id.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("csv-rows", help="emit rows with a Component Catalog YAML File link")
    s.add_argument("--csv", required=True)
    s.add_argument("--only", nargs="+", metavar="COMPONENT")
    s.set_defaults(func=cmd_csv_rows)

    s = sub.add_parser("append", help="append/replace one component entry in release_catalog.yml")
    s.add_argument("--catalog", required=True, help="path to release_catalog.yml")
    s.add_argument("--source", required=True, help="component yaml: GitHub blob/raw link or local path")
    s.add_argument("--release", help="set targetIcicleRelease to this YYYY-MM (omit to keep the source's)")
    s.add_argument("--training-url", help="set trainingTutorialsUrl to this deployed category URL")
    s.add_argument("--also-usage-url", action="store_true",
                   help="also set usageDocumentationUrl to --training-url")
    s.add_argument("--indent", type=int, default=2, help="spaces to nest under components: (default 2)")
    s.set_defaults(func=cmd_append)

    s = sub.add_parser("validate", help="assert every related_to resolves to an existing id")
    s.add_argument("--catalog", required=True)
    s.set_defaults(func=cmd_validate)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
