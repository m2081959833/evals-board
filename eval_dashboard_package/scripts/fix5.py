#!/usr/bin/env python3
"""
fix5.py - Two fixes:
1. Add 打分备注 (score notes) from sheet to each case card
2. Fix case explorer tags alignment (too far left, should align with content)
"""
import json, re

# Load HTML
with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Load score notes
with open('score_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

# Load prompt IDs to build lookup
with open('prompt_ids.json', 'r', encoding='utf-8') as f:
    pids = json.load(f)

# Build pid -> index lookup
pid_to_idx = {}
for i, pid in enumerate(pids):
    if pid:
        pid_to_idx[pid] = i

print(f"Loaded {len(pid_to_idx)} prompt IDs")

# ============================================================
# FIX 1: Inject 打分备注 into LLM_CASES data
# ============================================================
# Find LLM_CASES in HTML
cases_match = re.search(r'var\s+LLM_CASES\s*=\s*\[', html)
if not cases_match:
    print("ERROR: Cannot find LLM_CASES")
    exit(1)

cases_start = cases_match.start()
# Find the closing ];
depth = 0
in_string = False
escape = False
arr_start = html.index('[', cases_start)
i = arr_start
for i in range(arr_start, len(html)):
    c = html[i]
    if escape:
        escape = False
        continue
    if c == '\\':
        if in_string:
            escape = True
        continue
    if c == '"' and not escape:
        in_string = not in_string
        continue
    if in_string:
        continue
    if c == '[':
        depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0:
            break

cases_end = i + 1
cases_json_str = html[arr_start:cases_end]
print(f"Found LLM_CASES: {len(cases_json_str)} chars")

# Parse cases
cases = json.loads(cases_json_str)
print(f"Parsed {len(cases)} cases")

# Add notes to each case
added_count = 0
for case in cases:
    pid = case.get('pid', '')
    idx = pid_to_idx.get(pid, -1)
    if idx < 0:
        continue
    
    # Add notes to each model
    for model_key, obj_key, sub_key in [
        ('d', 'd_obj', 'd_sub'),
        ('qw', 'qw_obj', 'qw_sub'),
        ('gm', 'gm_obj', 'gm_sub'),
        ('gp', 'gp_obj', 'gp_sub'),
    ]:
        if model_key in case:
            obj_note = notes[obj_key][idx] if idx < len(notes[obj_key]) else ''
            sub_note = notes[sub_key][idx] if idx < len(notes[sub_key]) else ''
            case[model_key]['on'] = obj_note   # 客观打分备注
            case[model_key]['sn'] = sub_note   # 主客观打分备注
            if obj_note or sub_note:
                added_count += 1

print(f"Added notes to {added_count} model entries")

# Serialize back - use ensure_ascii=False for Chinese chars, separators for compact
new_cases_str = json.dumps(cases, ensure_ascii=False, separators=(',', ':'))
html = html[:arr_start] + new_cases_str + html[cases_end:]
print(f"Replaced LLM_CASES ({len(cases_json_str)} -> {len(new_cases_str)} chars)")

# ============================================================
# FIX 2: Update rendering JS to show 打分备注 in case cards
# ============================================================
# Find the function that renders model response cards
# Current rendering has: model name + scores + response text + COT
# We need to add 打分备注 after scores

# The rendering code builds HTML like:
# '<div class="llm-resp-header">...<span>客观:'+od+' 主客观:'+sd+'</span></div>'
# '<div class="llm-resp-body">'+resp+'</div>'
# We need to add a notes div after resp-body

# Find the pattern where resp-body is built
# Look for the pattern in script blocks
old_resp_pattern = "llm-resp-body"
# Let's find the renderCases function more precisely
render_match = re.search(r'function\s+llmRenderCases\s*\(', html)
if render_match:
    print(f"Found llmRenderCases at offset {render_match.start()}")
else:
    print("WARNING: llmRenderCases not found, searching for resp-body pattern")

# Strategy: find where llm-resp-body div is constructed and add notes after it
# The current code builds something like:
#   h += '<div class="llm-resp-body">' + respHtml + '</div>';
# We want to add:
#   h += '<div class="llm-score-note">..notes..</div>';

# Let's find the exact pattern. Search for the code that builds resp-body
# and the COT toggle after it
resp_body_pattern = re.search(r"'<div class=\"llm-resp-body\">'", html)
if resp_body_pattern:
    print(f"Found resp-body builder at {resp_body_pattern.start()}")

# Let me find the full rendering logic by looking at the JS more carefully
# Search for where model cards are built with od/sd scores
score_pattern = re.search(r"客观:'\s*\+\s*(\w+)\s*\+\s*'\s*主客观:", html)
if not score_pattern:
    score_pattern = re.search(r"客观:", html[cases_match.start():])
    
# Let me look at the rendering code around llmRenderCases
if render_match:
    func_start = render_match.start()
    # Get ~3000 chars of the function
    func_preview = html[func_start:func_start+5000]
    # Find where model response divs are built
    lines = func_preview.split('\n')
    for li, line in enumerate(lines):
        if 'resp-body' in line or 'resp-header' in line or 'score-note' in line:
            print(f"  Line {li}: {line.strip()[:120]}")

print("\n--- Looking for the exact rendering pattern ---")
# Find the pattern more broadly
for m in re.finditer(r'llm-resp-body', html):
    context = html[max(0,m.start()-100):m.start()+200]
    print(f"  At {m.start()}: ...{repr(context[:300])}...")
    break

# Let's extract the full render function
if render_match:
    # Find end of function - look for next top-level function
    func_code = html[render_match.start():render_match.start()+8000]
    # Write to file for inspection
    with open('_render_func.js', 'w') as f:
        f.write(func_code)
    print("Wrote _render_func.js for inspection")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved HTML with updated LLM_CASES data (notes injected)")
print("Next step: inspect _render_func.js to find exact insertion point for notes UI")
