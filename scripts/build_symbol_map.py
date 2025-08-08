#!/usr/bin/env python3
# scripts/build_symbol_map.py
# Generate mapping from file+function to GitHub blob line link

import json, re, subprocess
from pathlib import Path

# ====== EDIT HERE ======
REPO   = "cnbissolution/sample_codes"   # GitHub org/user + repo
BRANCH = "main"                          # Fixed branch to target
FILES  = ["server.cpp"]                  # Files to index (relative paths)
# =======================

ROOT = Path(__file__).resolve().parents[1]
CTAGS = ["ctags", "--fields=+n", "-x", "--c-kinds=f"]
FUNC_LINE_RE = re.compile(r"^(\w+)\s+\w+\s+(\d+)\s+(.+)$")

def find_function_ranges(src: Path):
    text_lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
    res = subprocess.run(CTAGS + [str(src)], text=True, capture_output=True, check=True)
    starts = []
    for line in res.stdout.splitlines():
        m = FUNC_LINE_RE.match(line.strip())
        if not m:
            continue
        name, line_no, path = m.group(1), int(m.group(2)), m.group(3)
        if Path(path).name != src.name:
            continue
        starts.append((name, line_no))

    ranges = {}
    for name, start in starts:
        i = start - 1
        depth = 0
        opened = False
        end = start
        for j in range(i, len(text_lines)):
            line = text_lines[j]
            for ch in line:
                if ch == '{':
                    depth += 1
                    opened = True
                elif ch == '}':
                    depth -= 1
            if opened and depth == 0:
                end = j + 1
                break
        ranges[name] = (start, end)
    return ranges

def main():
    mapping = {}
    for rel in FILES:
        src = ROOT / rel
        if not src.exists():
            print(f"[WARN] not found: {src}")
            continue
        ranges = find_function_ranges(src)
        for func, (s, e) in ranges.items():
            key = f"{src.name}/{func}"
            target = f"https://github.com/{REPO}/blob/{BRANCH}/{rel}#L{s}-L{e}"
            mapping[key] = target

    static_json = ROOT / "redirects_static.json"
    if static_json.exists():
        static = json.loads(static_json.read_text(encoding="utf-8"))
        mapping.update(static)

    out = ROOT / "redirects_generated.json"
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] wrote {out} with {len(mapping)} entries")

if __name__ == "__main__":
    main()
