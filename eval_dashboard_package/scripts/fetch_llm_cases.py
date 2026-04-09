#!/usr/bin/env python3
"""
Fetch LLM evaluation case data from Feishu Sheet API in batches,
then save as JSON for the case explorer.
"""
import subprocess, json, sys, os

SKILL_DIR = "/opt/tiger/mira_nas/plugins/prod/builtin/skills/lark-sheet-skill"
TOKEN = "Bduwsms4ZhxdNNti0xecqkWinYd"
SHEET = "ef21e1"

# Key columns we need (0-indexed):
# C0: Session题号, C1: Prompt题号, C2: Prompt
# C8: 一级分类, C9: 二级分类, C11: 单/多轮, C13: 来源
# C14: 客观考点, C15: 主观考点
# C24: 豆包回复, C25: 豆包COT
# C26: 豆包客观dcg(prompt), C29: 豆包客观dcg(session)
# C32: 豆包主客观dcg(prompt), C35: 豆包主客观dcg(session)
# C40: 千问回复, C41: 千问COT
# C42: 千问客观dcg(prompt), C45: 千问客观dcg(session)
# C48: 千问主客观dcg(prompt), C51: 千问主客观dcg(session)
# C54: 豆包vs千问 客观gsb(prompt), C57: 客观gsb(session)
# C60: 豆包vs千问 主客观gsb(prompt), C63: 主客观gsb(session)
# C70: Gemini回复, C71: Gemini COT
# C72: Gemini客观dcg(prompt), C75: Gemini客观dcg(session)
# C78: Gemini主客观dcg(prompt), C81: Gemini主客观dcg(session)
# C84: 豆包vsGemini 客观gsb(prompt), C87: 客观gsb(session)
# C90: 豆包vsGemini 主客观gsb(prompt), C93: 主客观gsb(session)
# C98: GPT回复, C99: GPT COT
# C100: GPT客观dcg(prompt), C103: GPT客观dcg(session)
# C106: GPT主客观dcg(prompt), C109: GPT主客观dcg(session)
# C112: 豆包vsGPT 客观gsb(prompt), C115: 客观gsb(session)
# C118: 豆包vsGPT 主客观gsb(prompt), C121: 主客观gsb(session)
# C124-C127: 回复字数(豆包/千问/Gemini/GPT)

def read_range(range_str):
    """Read a range from the Feishu sheet."""
    cmd = [
        "python3", "-m", "lark_sheet", "read-cells",
        TOKEN, range_str, "--value-render", "ToString"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR, timeout=120)
    output = result.stdout
    # Skip the first info line
    lines = output.split('\n', 1)
    if len(lines) > 1:
        data = json.loads(lines[1])
        if not data.get("is_error"):
            return data["data"]["values"]
    print(f"ERROR reading {range_str}: {output[:500]}", file=sys.stderr)
    return []

def safe_str(v):
    if v is None:
        return ""
    return str(v).strip()

def safe_float(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s == "-" or s == "#ERROR" or s == "N/A":
        return None
    try:
        return float(s)
    except:
        return None

# Read all data rows (rows 5-346, i.e. A5:EC346)
# We need columns A through EC (133 columns = A..EC)
# Read in batches of 50 rows
all_rows = []
BATCH = 50
START_ROW = 5
END_ROW = 346

for batch_start in range(START_ROW, END_ROW + 1, BATCH):
    batch_end = min(batch_start + BATCH - 1, END_ROW)
    range_str = f"{SHEET}!A{batch_start}:EC{batch_end}"
    print(f"Reading rows {batch_start}-{batch_end}...", file=sys.stderr)
    rows = read_range(range_str)
    if rows:
        all_rows.extend(rows)
    else:
        print(f"No data for rows {batch_start}-{batch_end}", file=sys.stderr)

print(f"Total rows fetched: {len(all_rows)}", file=sys.stderr)

# Parse into case objects
cases = []
for row_idx, row in enumerate(all_rows):
    # Pad row to 133 columns
    while len(row) < 133:
        row.append(None)

    session_id = safe_str(row[0])
    prompt_id = safe_str(row[1])
    prompt = safe_str(row[2])

    # Skip empty rows
    if not prompt and not session_id:
        continue

    category = safe_str(row[8])   # 一级分类
    subcategory = safe_str(row[9])  # 二级分类
    single_multi = safe_str(row[11])  # 单/多轮
    source = safe_str(row[13])  # 来源
    obj_point = safe_str(row[14])  # 客观考点
    subj_point = safe_str(row[15])  # 主观考点

    case = {
        "session_id": session_id,
        "prompt_id": prompt_id,
        "prompt": prompt,
        "category": category,
        "subcategory": subcategory,
        "single_multi": single_multi,
        "source": source,
        "obj_point": obj_point,
        "subj_point": subj_point,
        "models": {
            "doubao": {
                "reply": safe_str(row[24]),
                "cot": safe_str(row[25]),
                "obj_dcg_prompt": safe_float(row[26]),
                "obj_dcg_session": safe_float(row[29]),
                "subj_dcg_prompt": safe_float(row[32]),
                "subj_dcg_session": safe_float(row[35]),
                "word_count": safe_float(row[124])
            },
            "qianwen": {
                "reply": safe_str(row[40]),
                "cot": safe_str(row[41]),
                "obj_dcg_prompt": safe_float(row[42]),
                "obj_dcg_session": safe_float(row[45]),
                "subj_dcg_prompt": safe_float(row[48]),
                "subj_dcg_session": safe_float(row[51]),
                "word_count": safe_float(row[125])
            },
            "gemini": {
                "reply": safe_str(row[70]),
                "cot": safe_str(row[71]),
                "obj_dcg_prompt": safe_float(row[72]),
                "obj_dcg_session": safe_float(row[75]),
                "subj_dcg_prompt": safe_float(row[78]),
                "subj_dcg_session": safe_float(row[81]),
                "word_count": safe_float(row[126])
            },
            "gpt": {
                "reply": safe_str(row[98]),
                "cot": safe_str(row[99]),
                "obj_dcg_prompt": safe_float(row[100]),
                "obj_dcg_session": safe_float(row[103]),
                "subj_dcg_prompt": safe_float(row[106]),
                "subj_dcg_session": safe_float(row[109]),
                "word_count": safe_float(row[127])
            }
        },
        "gsb": {
            "vs_qianwen": {
                "obj_prompt": safe_float(row[54]),
                "obj_session": safe_float(row[57]),
                "subj_prompt": safe_float(row[60]),
                "subj_session": safe_float(row[63])
            },
            "vs_gemini": {
                "obj_prompt": safe_float(row[84]),
                "obj_session": safe_float(row[87]),
                "subj_prompt": safe_float(row[90]),
                "subj_session": safe_float(row[93])
            },
            "vs_gpt": {
                "obj_prompt": safe_float(row[112]),
                "obj_session": safe_float(row[115]),
                "subj_prompt": safe_float(row[118]),
                "subj_session": safe_float(row[121])
            }
        }
    }
    cases.append(case)

print(f"Total cases parsed: {len(cases)}", file=sys.stderr)

# Save
with open("llm_cases_data.json", "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False)

print(f"Saved to llm_cases_data.json ({os.path.getsize('llm_cases_data.json')} bytes)", file=sys.stderr)

# Print summary
cats = {}
for c in cases:
    cat = c["category"] or "未分类"
    cats[cat] = cats.get(cat, 0) + 1
print("\nCategory distribution:", file=sys.stderr)
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}", file=sys.stderr)

# Check first case
if cases:
    c = cases[0]
    print(f"\nFirst case:", file=sys.stderr)
    print(f"  Session: {c['session_id']}, Prompt: {c['prompt_id']}", file=sys.stderr)
    print(f"  Category: {c['category']}, Subcategory: {c['subcategory']}", file=sys.stderr)
    print(f"  Prompt: {c['prompt'][:100]}...", file=sys.stderr)
    print(f"  豆包 reply length: {len(c['models']['doubao']['reply'])}", file=sys.stderr)
    print(f"  千问 reply length: {len(c['models']['qianwen']['reply'])}", file=sys.stderr)
    print(f"  Gemini reply length: {len(c['models']['gemini']['reply'])}", file=sys.stderr)
    print(f"  GPT reply length: {len(c['models']['gpt']['reply'])}", file=sys.stderr)
    print(f"  GSB vs千问 obj_prompt: {c['gsb']['vs_qianwen']['obj_prompt']}", file=sys.stderr)
