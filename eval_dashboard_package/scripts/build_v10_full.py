#!/usr/bin/env python3
"""
Complete rebuild of v10 with:
1. Updated stats from new data source
2. Fixed LLM case explorer 
3. Data source link in Tab 1
"""
import json, os, re

# ── Load new stats ──
stats = json.load(open("llm_stats_new.json", encoding="utf-8"))
print(f"Stats sections: {list(stats['sections'].keys())}")

# ── Load and prepare case data ──
cases = json.load(open("llm_cases_data.json", encoding="utf-8"))

# Propagate category within sessions
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

# Build compact case JSON
compact = []
for c in cases:
    # Truncate very long replies for display (keep under control)
    def trunc(s, maxlen=3000):
        if not s: return ""
        if len(s) > maxlen:
            return s[:maxlen] + "\n...（已截断）"
        return s
    
    compact.append({
        "sid": c["session_id"], "pid": c["prompt_id"], "q": c["prompt"],
        "cat": c["category"] or "\u672a\u5206\u7c7b", "sub": c["subcategory"],
        "sm": c["single_multi"], "src": c["source"],
        "op": c["obj_point"], "sp": c["subj_point"],
        "d": {"r": trunc(c["models"]["doubao"]["reply"]), "c": trunc(c["models"]["doubao"]["cot"], 1000),
              "od": c["models"]["doubao"]["obj_dcg_prompt"], "os": c["models"]["doubao"]["obj_dcg_session"],
              "sd": c["models"]["doubao"]["subj_dcg_prompt"], "ss": c["models"]["doubao"]["subj_dcg_session"],
              "w": c["models"]["doubao"]["word_count"]},
        "qw": {"r": trunc(c["models"]["qianwen"]["reply"]), "c": trunc(c["models"]["qianwen"]["cot"], 1000),
               "od": c["models"]["qianwen"]["obj_dcg_prompt"], "os": c["models"]["qianwen"]["obj_dcg_session"],
               "sd": c["models"]["qianwen"]["subj_dcg_prompt"], "ss": c["models"]["qianwen"]["subj_dcg_session"],
               "w": c["models"]["qianwen"]["word_count"]},
        "gm": {"r": trunc(c["models"]["gemini"]["reply"]), "c": trunc(c["models"]["gemini"]["cot"], 1000),
               "od": c["models"]["gemini"]["obj_dcg_prompt"], "os": c["models"]["gemini"]["obj_dcg_session"],
               "sd": c["models"]["gemini"]["subj_dcg_prompt"], "ss": c["models"]["gemini"]["subj_dcg_session"],
               "w": c["models"]["gemini"]["word_count"]},
        "gp": {"r": trunc(c["models"]["gpt"]["reply"]), "c": trunc(c["models"]["gpt"]["cot"], 1000),
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

# ── Build new LLM_DATA for dashboard ──
def fmt_pct(v):
    if v is None: return "'-'"
    return f"'{v*100:.1f}%'"

def fmt_num(v):
    if v is None: return "'-'"
    return f"'{v:.1f}'" if isinstance(v, float) else f"'{v}'"

def fmt_gsb(v):
    if v is None: return "'-'"
    return f"'{v*100:.2f}%'"

# Build LLM_DATA JS object matching the format build_v10.py used
cats_order = ["整体", "知识", "写作", "语言", "闲聊"]
llm_data_lines = ["var LLM_DATA = {"]
llm_data_lines.append("  sections: {")
for cat in cats_order:
    if cat not in stats["sections"]:
        continue
    s = stats["sections"][cat]
    m = s["metrics"]
    llm_data_lines.append(f"    '{cat}': {{")
    llm_data_lines.append(f"      count: {s['count']},")
    llm_data_lines.append(f"      metrics: {{")
    
    # GSB
    for dim_key, dim_label in [("obj", "obj"), ("subj", "subj")]:
        gsb = m["gsb"][dim_key]
        pv = m["pvalue"][dim_key]
        us = m["usable"][dim_key]
        pf = m["perfect"][dim_key]
        qt = m["quit"][dim_key]
        av = m["avg_score"][dim_key]
        
        llm_data_lines.append(f"        {dim_label}: {{")
        llm_data_lines.append(f"          gsb: {{ qianwen: {fmt_gsb(gsb['qianwen'])}, gemini: {fmt_gsb(gsb['gemini'])}, gpt: {fmt_gsb(gsb['gpt'])} }},")
        llm_data_lines.append(f"          pvalue: {{ qianwen: {fmt_num(pv['qianwen'])}, gemini: {fmt_num(pv['gemini'])}, gpt: {fmt_num(pv['gpt'])} }},")
        llm_data_lines.append(f"          usable: {{ doubao: {fmt_pct(us['doubao'])}, qianwen: {fmt_pct(us['qianwen'])}, gemini: {fmt_pct(us['gemini'])}, gpt: {fmt_pct(us['gpt'])} }},")
        llm_data_lines.append(f"          perfect: {{ doubao: {fmt_pct(pf['doubao'])}, qianwen: {fmt_pct(pf['qianwen'])}, gemini: {fmt_pct(pf['gemini'])}, gpt: {fmt_pct(pf['gpt'])} }},")
        llm_data_lines.append(f"          quit: {{ doubao: {fmt_pct(qt['doubao'])}, qianwen: {fmt_pct(qt['qianwen'])}, gemini: {fmt_pct(qt['gemini'])}, gpt: {fmt_pct(qt['gpt'])} }},")
        llm_data_lines.append(f"          avg: {{ doubao: {fmt_num(av['doubao'])}, qianwen: {fmt_num(av['qianwen'])}, gemini: {fmt_num(av['gemini'])}, gpt: {fmt_num(av['gpt'])} }}")
        llm_data_lines.append(f"        }},")
    
    # Wordcount (same for obj/subj)
    wc = m["wordcount"]
    llm_data_lines.append(f"        wordcount: {{ doubao: {fmt_num(wc['doubao'])}, qianwen: {fmt_num(wc['qianwen'])}, gemini: {fmt_num(wc['gemini'])}, gpt: {fmt_num(wc['gpt'])} }}")
    llm_data_lines.append(f"      }}")
    llm_data_lines.append(f"    }},")

llm_data_lines.append("  },")

# Volume
llm_data_lines.append("  volume: {")
for cat in ["知识", "写作", "语言", "闲聊"]:
    if cat in stats["volume"]:
        llm_data_lines.append(f"    '{cat}': {stats['volume'][cat]},")
llm_data_lines.append("  }")
llm_data_lines.append("};")

llm_data_js = "\n".join(llm_data_lines)
print(f"LLM_DATA JS: {len(llm_data_js)} bytes")

# ── Read v10 HTML ──
html = open("viz_final_v10.html", "r", encoding="utf-8").read()
print(f"Original HTML: {len(html)} bytes")

# ── 1. Add data source link to Tab 1 ──
old_sub = '数据来源: 3月流式竞对 Excel · 生成时间: 2026-04-02</p>'
new_sub = '数据来源: 3月流式竞对 Excel · <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5">飞书数据表</a> · 生成时间: 2026-04-02</p>'
html = html.replace(old_sub, new_sub, 1)
print("✓ Tab 1 data source link")

# ── 2. Update LLM_DATA in existing JS ──
# Find and replace the existing LLM_DATA declaration
old_data_match = re.search(r'var LLM_DATA\s*=\s*\{.*?\};\s*', html, re.DOTALL)
if old_data_match:
    html = html[:old_data_match.start()] + llm_data_js + "\n" + html[old_data_match.end():]
    print("✓ Updated LLM_DATA stats")
else:
    print("⚠ Could not find existing LLM_DATA to replace")

# ── 3. Update data source link in Tab 2 header ──
# Change to point to new spreadsheet
old_link = 'href="https://bytedance.larkoffice.com/sheets/Bduwsms4ZhxdNNti0xecqkWinYd"'
new_link = 'href="https://bytedance.larkoffice.com/sheets/VaHEsMjHZhyqrEtKVPDcNa2inbf"'
html = html.replace(old_link, new_link, 1)
print("✓ Updated Tab 2 data source link")

# ── 4. Insert case section HTML before </div><!-- end proj2 --> ──
case_section_html = '''
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
html = html.replace(proj2_end, case_section_html + proj2_end, 1)
print("✓ Case HTML inserted")

# ── 5. Insert case CSS before </head> ──
case_css = '<style>.llm-case-section{margin-top:32px;padding:0 20px 40px}.llm-case-section h2{font-size:22px;font-weight:700;margin-bottom:16px;color:#1a1a2e}.llm-case-filters{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;align-items:center}.llm-case-filters select,.llm-case-filters input{padding:6px 12px;border:1px solid #d0d5dd;border-radius:6px;font-size:13px;background:#fff}.llm-case-filters input{width:240px}.llm-case-count{font-size:13px;color:#667;margin-left:8px}.llm-case-list{display:flex;flex-direction:column;gap:16px}.llm-case-card{background:#fff;border:1px solid #e4e7ec;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}.llm-case-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}.llm-case-meta{display:flex;gap:8px;flex-wrap:wrap}.llm-case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500}.llm-case-tag.cat{background:#eef4ff;color:#3538cd}.llm-case-tag.sub{background:#f0fdf4;color:#16a34a}.llm-case-tag.sm{background:#fefce8;color:#a16207}.llm-case-tag.sid{background:#f3f4f6;color:#4b5563}.llm-case-prompt{background:#f8f9fb;border-left:3px solid #6366f1;padding:12px 16px;margin-bottom:16px;border-radius:0 6px 6px 0;font-size:14px;line-height:1.6;white-space:pre-wrap;word-break:break-word}.llm-case-responses{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px}@media(max-width:1400px){.llm-case-responses{grid-template-columns:1fr 1fr}}@media(max-width:768px){.llm-case-responses{grid-template-columns:1fr}}.llm-resp-box{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden}.llm-resp-header{padding:8px 12px;font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}.llm-resp-header.doubao{background:#eef4ff;color:#3538cd}.llm-resp-header.qianwen{background:#fef3f2;color:#b42318}.llm-resp-header.gemini{background:#f0fdf4;color:#16a34a}.llm-resp-header.gpt{background:#f5f3ff;color:#6d28d9}.llm-resp-scores{font-weight:400;font-size:11px}.llm-resp-body{padding:12px;font-size:13px;line-height:1.6;max-height:300px;overflow-y:auto;white-space:pre-wrap;word-break:break-word}.llm-gsb-row{display:flex;gap:8px;margin-top:8px;padding:8px 12px;background:#fafafa;border-radius:6px;font-size:12px;flex-wrap:wrap}.llm-gsb-item{display:flex;align-items:center;gap:4px}.llm-gsb-val{font-weight:600}.llm-gsb-val.pos{color:#16a34a}.llm-gsb-val.neg{color:#dc2626}.llm-gsb-val.neu{color:#6b7280}.llm-case-pagination{display:flex;justify-content:center;gap:8px;margin-top:20px}.llm-case-pagination button{padding:6px 14px;border:1px solid #d0d5dd;border-radius:6px;background:#fff;cursor:pointer;font-size:13px}.llm-case-pagination button:hover{background:#f3f4f6}.llm-case-pagination button.active{background:#4f46e5;color:#fff;border-color:#4f46e5}.llm-case-pagination button:disabled{opacity:.5;cursor:not-allowed}.llm-cot-toggle{font-size:11px;color:#6366f1;cursor:pointer;margin-top:4px;text-decoration:underline}.llm-cot-content{display:none;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:8px;margin-top:8px;font-size:12px;max-height:200px;overflow-y:auto;white-space:pre-wrap}.llm-resp-body::-webkit-scrollbar,.llm-cot-content::-webkit-scrollbar{width:4px}.llm-resp-body::-webkit-scrollbar-thumb,.llm-cot-content::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:2px}</style>'
html = html.replace('</head>', case_css + '\n</head>', 1)
print("✓ Case CSS added")

# ── 6. Insert case JS + data before </body> ──
html = html.replace('</body>', '<script>\n' + js_code + '\n</script>\n</body>', 1)
print("✓ Case JS + data added")

# ── Save ──
out = "viz_final_v10_full.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
sz = os.path.getsize(out)
print(f"\nOutput: {out} ({sz} bytes, {sz/1024/1024:.1f} MB)")
