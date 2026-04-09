#!/usr/bin/env python3
"""Parse the new data stats sheet from the copied spreadsheet."""
import subprocess, json, sys

SKILL_DIR = "/opt/tiger/mira_nas/plugins/prod/builtin/skills/lark-sheet-skill"
TOKEN = "VaHEsMjHZhyqrEtKVPDcNa2inbf"
SHEET = "mn7cXH"

def read_range(r):
    cmd = ["python3", "-m", "lark_sheet", "read-cells", TOKEN, r, "--value-render", "ToString"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR, timeout=120)
    out = result.stdout
    idx = out.index('{')
    data = json.loads(out[idx:])
    return data["data"]["values"]

rows = read_range(f"{SHEET}!A1:P70")
print(f"Total rows: {len(rows)}", file=sys.stderr)

def safe_str(v):
    if v is None: return ""
    return str(v).strip()

def safe_float(v):
    if v is None: return None
    s = str(v).strip()
    if not s or s == '-' or s == '#ERROR' or s == 'N/A': return None
    try: return float(s)
    except: return None

def pad(row, n=16):
    while len(row) < n:
        row.append(None)
    return row

# Find section starts
section_starts = []
for i, row in enumerate(rows):
    row = pad(row)
    if row[0] and "竞品评估" in str(row[0]):
        section_starts.append(i)

print(f"Section starts at rows: {section_starts}", file=sys.stderr)

sections = {}
for si, start in enumerate(section_starts):
    header_row = pad(rows[start])
    cat_text = safe_str(header_row[2])
    parts = cat_text.split()
    cat = parts[0] if parts else "未知"
    count_str = parts[1].replace("题", "") if len(parts) > 1 else "0"
    count = int(count_str) if count_str.isdigit() else 0
    print(f"\nSection {si}: {cat} ({count}题) at row {start}", file=sys.stderr)

    gsb_row = pad(rows[start + 3])
    pval_row = pad(rows[start + 4])
    usable_row = pad(rows[start + 5])
    perfect_row = pad(rows[start + 6])
    quit_row = pad(rows[start + 7])
    avg_row = pad(rows[start + 8])
    wordcount_row = pad(rows[start + 9])

    section = {
        "cat": cat, "count": count,
        "metrics": {
            "gsb": {
                "obj": {"doubao": safe_float(gsb_row[2]), "qianwen": safe_float(gsb_row[3]),
                        "gemini": safe_float(gsb_row[4]), "gpt": safe_float(gsb_row[5])},
                "subj": {"doubao": safe_float(gsb_row[6]), "qianwen": safe_float(gsb_row[7]),
                         "gemini": safe_float(gsb_row[8]), "gpt": safe_float(gsb_row[9])}
            },
            "pvalue": {
                "obj": {"doubao": safe_float(pval_row[2]), "qianwen": safe_float(pval_row[3]),
                        "gemini": safe_float(pval_row[4]), "gpt": safe_float(pval_row[5])},
                "subj": {"doubao": safe_float(pval_row[6]), "qianwen": safe_float(pval_row[7]),
                         "gemini": safe_float(pval_row[8]), "gpt": safe_float(pval_row[9])}
            },
            "usable": {
                "obj": {"doubao": safe_float(usable_row[2]), "qianwen": safe_float(usable_row[3]),
                        "gemini": safe_float(usable_row[4]), "gpt": safe_float(usable_row[5])},
                "subj": {"doubao": safe_float(usable_row[6]), "qianwen": safe_float(usable_row[7]),
                         "gemini": safe_float(usable_row[8]), "gpt": safe_float(usable_row[9])}
            },
            "perfect": {
                "obj": {"doubao": safe_float(perfect_row[2]), "qianwen": safe_float(perfect_row[3]),
                        "gemini": safe_float(perfect_row[4]), "gpt": safe_float(perfect_row[5])},
                "subj": {"doubao": safe_float(perfect_row[6]), "qianwen": safe_float(perfect_row[7]),
                         "gemini": safe_float(perfect_row[8]), "gpt": safe_float(perfect_row[9])}
            },
            "quit": {
                "obj": {"doubao": safe_float(quit_row[2]), "qianwen": safe_float(quit_row[3]),
                        "gemini": safe_float(quit_row[4]), "gpt": safe_float(quit_row[5])},
                "subj": {"doubao": safe_float(quit_row[6]), "qianwen": safe_float(quit_row[7]),
                         "gemini": safe_float(quit_row[8]), "gpt": safe_float(quit_row[9])}
            },
            "avg_score": {
                "obj": {"doubao": safe_float(avg_row[2]), "qianwen": safe_float(avg_row[3]),
                        "gemini": safe_float(avg_row[4]), "gpt": safe_float(avg_row[5])},
                "subj": {"doubao": safe_float(avg_row[6]), "qianwen": safe_float(avg_row[7]),
                         "gemini": safe_float(avg_row[8]), "gpt": safe_float(avg_row[9])}
            },
            "wordcount": {
                "doubao": safe_float(wordcount_row[2]), "qianwen": safe_float(wordcount_row[3]),
                "gemini": safe_float(wordcount_row[4]), "gpt": safe_float(wordcount_row[5])
            }
        }
    }
    sections[cat] = section

# Volume data
volume = {}
for row in rows:
    row = pad(row)
    cat_v = safe_str(row[12])
    count_v = safe_str(row[13])
    if cat_v and count_v and count_v.isdigit():
        volume[cat_v] = int(count_v)

print(f"\nVolume: {volume}", file=sys.stderr)

result = {"sections": sections, "volume": volume}

for cat, s in sections.items():
    m = s["metrics"]
    print(f"\n{cat} ({s['count']}题):", file=sys.stderr)
    print(f"  GSB obj: qw={m['gsb']['obj']['qianwen']}, gm={m['gsb']['obj']['gemini']}, gp={m['gsb']['obj']['gpt']}", file=sys.stderr)
    print(f"  GSB subj: qw={m['gsb']['subj']['qianwen']}, gm={m['gsb']['subj']['gemini']}, gp={m['gsb']['subj']['gpt']}", file=sys.stderr)
    print(f"  usable obj: db={m['usable']['obj']['doubao']}", file=sys.stderr)
    print(f"  wordcount: db={m['wordcount']['doubao']}, qw={m['wordcount']['qianwen']}", file=sys.stderr)

with open("llm_stats_new.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\nSaved to llm_stats_new.json", file=sys.stderr)
