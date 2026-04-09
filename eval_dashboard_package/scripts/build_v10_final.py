#!/usr/bin/env python3
"""
Build v10 with LLM case explorer for Tab 2, and data source link for Tab 1.
Clean approach: read JS from file, inject data, inject into HTML.
"""
import json, os

# ── Load case data and propagate categories ──
cases = json.load(open("llm_cases_data.json", encoding="utf-8"))
sessions = {}
for c in cases:
    sid = c["session_id"]
    if sid not in sessions:
        sessions[sid] = []
    sessions[sid].append(c)
for sid, prompts in sessions.items():
    cats = [p["category"] for p in prompts if p["category"]]
    if cats:
        for p in prompts:
            if not p["category"]:
                p["category"] = cats[0]

# Build compact JSON (short keys to save space)
compact = []
for c in cases:
    compact.append({
        "sid": c["session_id"], "pid": c["prompt_id"], "q": c["prompt"],
        "cat": c["category"] or "\u672a\u5206\u7c7b", "sub": c["subcategory"],
        "sm": c["single_multi"], "src": c["source"],
        "op": c["obj_point"], "sp": c["subj_point"],
        "d": {"r": c["models"]["doubao"]["reply"], "c": c["models"]["doubao"]["cot"],
              "od": c["models"]["doubao"]["obj_dcg_prompt"], "os": c["models"]["doubao"]["obj_dcg_session"],
              "sd": c["models"]["doubao"]["subj_dcg_prompt"], "ss": c["models"]["doubao"]["subj_dcg_session"],
              "w": c["models"]["doubao"]["word_count"]},
        "qw": {"r": c["models"]["qianwen"]["reply"], "c": c["models"]["qianwen"]["cot"],
               "od": c["models"]["qianwen"]["obj_dcg_prompt"], "os": c["models"]["qianwen"]["obj_dcg_session"],
               "sd": c["models"]["qianwen"]["subj_dcg_prompt"], "ss": c["models"]["qianwen"]["subj_dcg_session"],
               "w": c["models"]["qianwen"]["word_count"]},
        "gm": {"r": c["models"]["gemini"]["reply"], "c": c["models"]["gemini"]["cot"],
               "od": c["models"]["gemini"]["obj_dcg_prompt"], "os": c["models"]["gemini"]["obj_dcg_session"],
               "sd": c["models"]["gemini"]["subj_dcg_prompt"], "ss": c["models"]["gemini"]["subj_dcg_session"],
               "w": c["models"]["gemini"]["word_count"]},
        "gp": {"r": c["models"]["gpt"]["reply"], "c": c["models"]["gpt"]["cot"],
               "od": c["models"]["gpt"]["obj_dcg_prompt"], "os": c["models"]["gpt"]["obj_dcg_session"],
               "sd": c["models"]["gpt"]["subj_dcg_prompt"], "ss": c["models"]["gpt"]["subj_dcg_session"],
               "w": c["models"]["gpt"]["word_count"]},
        "gsb": {
            "qw": {"op": c["gsb"]["vs_qianwen"]["obj_prompt"], "os": c["gsb"]["vs_qianwen"]["obj_session"],
                   "sp": c["gsb"]["vs_qianwen"]["subj_prompt"], "ss": c["gsb"]["vs_qianwen"]["subj_session"]},
            "gm": {"op": c["gsb"]["vs_gemini"]["obj_prompt"], "os": c["gsb"]["vs_gemini"]["obj_session"],
                   "sp": c["gsb"]["vs_gemini"]["subj_prompt"], "ss": c["gsb"]["vs_gemini"]["subj_session"]},
            "gp": {"op": c["gsb"]["vs_gpt"]["obj_prompt"], "os": c["gsb"]["vs_gpt"]["obj_session"],
                   "sp": c["gsb"]["vs_gpt"]["subj_prompt"], "ss": c["gsb"]["vs_gpt"]["subj_session"]}
        }
    })

case_json = json.dumps(compact, ensure_ascii=False, separators=(',', ':'))
print(f"Cases: {len(cases)}, JSON: {len(case_json)//1024} KB")

# ── Read JS template ──
js_code = open("llm_case_explorer.js", "r", encoding="utf-8").read()
js_code = js_code.replace("__CASE_DATA_PLACEHOLDER__", case_json)
print(f"JS code size (with data): {len(js_code)//1024} KB")

# ── Read v10 HTML ──
html = open("viz_final_v10.html", "r", encoding="utf-8").read()
print(f"Original HTML: {len(html)//1024} KB")

# ── 1. Add data source link to Tab 1 ──
old_sub = 'data-source: 3\u6708\u6d41\u5f0f\u7ade\u5bf9 Excel \u00b7 \u751f\u6210\u65f6\u95f4: 2026-04-02'
new_sub = 'data-source: 3\u6708\u6d41\u5f0f\u7ade\u5bf9 Excel \u00b7 <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5">\u98de\u4e66\u6570\u636e\u8868</a> \u00b7 \u751f\u6210\u65f6\u95f4: 2026-04-02'

# Actually let me find the real text in the HTML
import re
# Find the subtitle in proj1
m = re.search(r'(<p>)(数据来源[^<]*)(</p>)', html[:5000])
if m:
    old_text = m.group(2)
    new_text = old_text.rstrip() + ' · <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5">飞书数据表</a>'
    html = html.replace(m.group(0), m.group(1) + new_text + m.group(3), 1)
    print(f"✓ Added data source link to Tab 1 (replaced: {old_text[:50]}...)")
else:
    print("⚠ Could not find Tab 1 subtitle")

# ── 2. Insert case section HTML before </div><!-- end proj2 --> ──
case_html = '''
<div class="llm-case-section" id="llm-case-section">
  <h2>Case 详情</h2>
  <div class="llm-case-filters">
    <select id="llm-case-cat-filter" onchange="llmCaseState.catFilter=this.value;llmFilterCases();">
      <option value="">全部分类</option>
    </select>
    <input type="text" id="llm-case-search" placeholder="搜索 Prompt / ID / 考点..." oninput="llmCaseState.searchFilter=this.value;llmFilterCases();">
    <span class="llm-case-count" id="llm-case-count"></span>
  </div>
  <div class="llm-case-list" id="llm-case-list"></div>
  <div class="llm-case-pagination" id="llm-case-pagination"></div>
</div>
'''

proj2_end = '</div><!-- end proj2 -->'
if proj2_end in html:
    html = html.replace(proj2_end, case_html + proj2_end, 1)
    print("✓ Added case HTML to Tab 2")
else:
    print("⚠ Could not find proj2 end marker")

# ── 3. Insert CSS before </head> ──
case_css = '''<style>
.llm-case-section{margin-top:32px;padding:0 20px 40px}
.llm-case-section h2{font-size:22px;font-weight:700;margin-bottom:16px;color:#1a1a2e}
.llm-case-filters{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
.llm-case-filters select,.llm-case-filters input{padding:6px 12px;border:1px solid #d0d5dd;border-radius:6px;font-size:13px;background:#fff}
.llm-case-filters input{width:240px}
.llm-case-count{font-size:13px;color:#667;margin-left:8px}
.llm-case-list{display:flex;flex-direction:column;gap:16px}
.llm-case-card{background:#fff;border:1px solid #e4e7ec;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.llm-case-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.llm-case-meta{display:flex;gap:8px;flex-wrap:wrap}
.llm-case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500}
.llm-case-tag.cat{background:#eef4ff;color:#3538cd}
.llm-case-tag.sub{background:#f0fdf4;color:#16a34a}
.llm-case-tag.sm{background:#fefce8;color:#a16207}
.llm-case-tag.sid{background:#f3f4f6;color:#4b5563}
.llm-case-prompt{background:#f8f9fb;border-left:3px solid #6366f1;padding:12px 16px;margin-bottom:16px;border-radius:0 6px 6px 0;font-size:14px;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.llm-case-responses{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px}
@media(max-width:1400px){.llm-case-responses{grid-template-columns:1fr 1fr}}
@media(max-width:768px){.llm-case-responses{grid-template-columns:1fr}}
.llm-resp-box{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden}
.llm-resp-header{padding:8px 12px;font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}
.llm-resp-header.doubao{background:#eef4ff;color:#3538cd}
.llm-resp-header.qianwen{background:#fef3f2;color:#b42318}
.llm-resp-header.gemini{background:#f0fdf4;color:#16a34a}
.llm-resp-header.gpt{background:#f5f3ff;color:#6d28d9}
.llm-resp-scores{font-weight:400;font-size:11px}
.llm-resp-body{padding:12px;font-size:13px;line-height:1.6;max-height:300px;overflow-y:auto;white-space:pre-wrap;word-break:break-word}
.llm-gsb-row{display:flex;gap:8px;margin-top:8px;padding:8px 12px;background:#fafafa;border-radius:6px;font-size:12px;flex-wrap:wrap}
.llm-gsb-item{display:flex;align-items:center;gap:4px}
.llm-gsb-val{font-weight:600}
.llm-gsb-val.pos{color:#16a34a}
.llm-gsb-val.neg{color:#dc2626}
.llm-gsb-val.neu{color:#6b7280}
.llm-case-pagination{display:flex;justify-content:center;gap:8px;margin-top:20px}
.llm-case-pagination button{padding:6px 14px;border:1px solid #d0d5dd;border-radius:6px;background:#fff;cursor:pointer;font-size:13px}
.llm-case-pagination button:hover{background:#f3f4f6}
.llm-case-pagination button.active{background:#4f46e5;color:#fff;border-color:#4f46e5}
.llm-case-pagination button:disabled{opacity:.5;cursor:not-allowed}
.llm-cot-toggle{font-size:11px;color:#6366f1;cursor:pointer;margin-top:4px;text-decoration:underline}
.llm-cot-content{display:none;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:8px;margin-top:8px;font-size:12px;max-height:200px;overflow-y:auto;white-space:pre-wrap}
.llm-resp-body::-webkit-scrollbar,.llm-cot-content::-webkit-scrollbar{width:4px}
.llm-resp-body::-webkit-scrollbar-thumb,.llm-cot-content::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:2px}
</style>'''

html = html.replace('</head>', case_css + '\n</head>', 1)
print("✓ Added case CSS")

# ── 4. Insert JS before </body> ──
html = html.replace('</body>', '<script>\n' + js_code + '\n</script>\n</body>', 1)
print("✓ Added case JS + data")

# ── Save ──
out = "viz_final_v10_cases.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

sz = os.path.getsize(out)
print(f"\nOutput: {out} ({sz} bytes, {sz/1024/1024:.1f} MB)")
