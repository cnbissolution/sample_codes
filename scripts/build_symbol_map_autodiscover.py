#!/usr/bin/env python3
# scripts/build_symbol_map_autodiscover.py (relative path keys)

import json, os, re, subprocess, sys
from pathlib import Path

REPO   = os.environ.get("SYMLINK_REPO", "cnbissolution/sample_codes")
BRANCH = os.environ.get("SYMLINK_BRANCH", "main")
SEARCH_DIRS = ["."]
INCLUDE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp"}
EXCLUDE_DIRS = {".git", ".github", "docs_build", "site", "build", "out", "dist", "__pycache__"}

ROOT = Path(__file__).resolve().parents[1]
CTAGS = ["ctags", "--fields=+n", "-x", "--c-kinds=f"]
FUNC_LINE_RE = re.compile(r"^(\w+)\s+\w+\s+(\d+)\s+(.+)$")

def list_source_files():
    files = []
    for d in SEARCH_DIRS:
        base = (ROOT / d).resolve()
        for p, dirs, fnames in os.walk(base):
            dirs[:] = [x for x in dirs if x not in EXCLUDE_DIRS]
            for fn in fnames:
                if Path(fn).suffix.lower() in INCLUDE_SUFFIXES:
                    files.append(Path(p) / fn)
    return files

def find_function_ranges(src: Path):
    text_lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
    try:
        res = subprocess.run(CTAGS + [str(src)], text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARN] ctags failed for {src}: {e.stderr}", file=sys.stderr)
        return {}
    starts = []
    for line in res.stdout.splitlines():
        m = FUNC_LINE_RE.match(line.strip())
        if not m:
            continue
        name, line_no, path = m.group(1), int(m.group(2)), m.group(3)
        starts.append((name, line_no))

    if not starts:
        print(f"[INFO] no functions found by ctags in {src}")
        return {}

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
    srcs = list_source_files()
    print(f"[INFO] scanning {len(srcs)} files")
    mapping = {}
    for src in srcs:
        rel = src.relative_to(ROOT).as_posix()  # e.g., src/client.c
        ranges = find_function_ranges(src)
        for func, (s, e) in ranges.items():
            key = f"{rel}/{func}"  # include subdir to avoid collisions
            target = f"https://github.com/{REPO}/blob/{BRANCH}/{rel}#L{s}-L{e}"
            mapping[key] = target
            print(f"[OK] {key} -> L{s}-L{e}")

    out = ROOT / "redirects_generated.json"
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] wrote {out} with {len(mapping)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
