#!/usr/bin/env python3
"""
Rebuild v10 with correct LLM_DATA format matching the existing JS rendering functions.
"""
import json, os, re

# ── Load new stats ──
stats = json.load(open("llm_stats_new.json", encoding="utf-8"))

# ── Build LLM_DATA in the EXACT format the existing JS expects ──
# Format: sections[cat].metrics["GSB"]["豆包_客观"] = "3.45%"
# Top-level: wordcount[cat] = {"豆包": 357, "千问": 996, ...}
# Top-level: volume = {"知識": 136, ...}

def fmt_gsb(v):
    if v is None: return "-"
    return f"{v*100:.2f}%"

def fmt_pval(v):
    if v is None: return "-"
    return f"{v:.4f}"

def fmt_pct(v):
    if v is None: return "-"
    return f"{v*100:.1f}%"

def fmt_score(v):
    if v is None: return "-"
    return f"{v*100:.1f}%"

def fmt_wc(v):
    if v is None: return "0"
    return str(int(round(v)))

cats_order = ["整体", "知识", "写作", "语言", "闲聊"]
llm_sections = {}
llm_wordcount = {}

for cat in cats_order:
    if cat not in stats["sections"]:
        continue
    s = stats["sections"][cat]
    m = s["metrics"]
    
    metrics_dict = {}
    
    # For each metric, build {model_dim: value}
    # GSB -豆包 is always "-" (since GSB is豆包 vs others)
    gsb = {}
    for dim_key, dim_suffix in [("obj", "_客观"), ("subj", "_主客观")]:
        gsb["豆包" + dim_suffix] = "-"
        gsb["千问" + dim_suffix] = fmt_gsb(m["gsb"][dim_key]["qianwen"])
        gsb["Gemini" + dim_suffix] = fmt_gsb(m["gsb"][dim_key]["gemini"])
        gsb["GPT" + dim_suffix] = fmt_gsb(m["gsb"][dim_key]["gpt"])
    metrics_dict["GSB"] = gsb
    
    # p-value
    pv = {}
    for dim_key, dim_suffix in [("obj", "_客观"), ("subj", "_主客观")]:
        pv["豆包" + dim_suffix] = "-"
        pv["千问" + dim_suffix] = fmt_pval(m["pvalue"][dim_key]["qianwen"])
        pv["Gemini" + dim_suffix] = fmt_pval(m["pvalue"][dim_key]["gemini"])
        pv["GPT" + dim_suffix] = fmt_pval(m["pvalue"][dim_key]["gpt"])
    metrics_dict["p-value"] = pv
    
    # 可用率, 满分率, 劝退率, 均分
    for metric_name, stat_key, formatter in [
        ("可用率", "usable", fmt_pct),
        ("满分率", "perfect", fmt_pct),
        ("劝退率", "quit", fmt_pct),
        ("均分", "avg_score", fmt_score)
    ]:
        md = {}
        for dim_key, dim_suffix in [("obj", "_客观"), ("subj", "_主客观")]:
            md["豆包" + dim_suffix] = formatter(m[stat_key][dim_key]["doubao"])
            md["千问" + dim_suffix] = formatter(m[stat_key][dim_key]["qianwen"])
            md["Gemini" + dim_suffix] = formatter(m[stat_key][dim_key]["gemini"])
            md["GPT" + dim_suffix] = formatter(m[stat_key][dim_key]["gpt"])
        metrics_dict[metric_name] = md
    
    # 回复字数 (same values for both dimensions)
    wc_metric = {}
    for dim_suffix in ["_客观", "_主客观"]:
        wc_metric["豆包" + dim_suffix] = fmt_wc(m["wordcount"]["doubao"])
        wc_metric["千问" + dim_suffix] = fmt_wc(m["wordcount"]["qianwen"])
        wc_metric["Gemini" + dim_suffix] = fmt_wc(m["wordcount"]["gemini"])
        wc_metric["GPT" + dim_suffix] = fmt_wc(m["wordcount"]["gpt"])
    metrics_dict["回复字数"] = wc_metric
    
    llm_sections[cat] = {"count": s["count"], "metrics": metrics_dict}
    
    # Wordcount for the overview cards
    llm_wordcount[cat] = {
        "豆包": int(round(m["wordcount"]["doubao"])) if m["wordcount"]["doubao"] else 0,
        "千问": int(round(m["wordcount"]["qianwen"])) if m["wordcount"]["qianwen"] else 0,
        "Gemini": int(round(m["wordcount"]["gemini"])) if m["wordcount"]["gemini"] else 0,
        "GPT": int(round(m["wordcount"]["gpt"])) if m["wordcount"]["gpt"] else 0
    }

# Volume (without 整体)
llm_volume = {}
for cat in ["知识", "写作", "语言", "闲聊"]:
    if cat in stats["volume"]:
        llm_volume[cat] = stats["volume"][cat]

llm_data = {
    "sections": llm_sections,
    "volume": llm_volume,
    "wordcount": llm_wordcount
}

llm_data_json = json.dumps(llm_data, ensure_ascii=False)
print(f"LLM_DATA JSON: {len(llm_data_json)} bytes")

# ── Load case data ──
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

compact = []
for c in cases:
    def trunc(s, maxlen=3000):
        if not s: return ""
        return s[:maxlen] + "\n...（已截断）" if len(s) > maxlen else s
    
    compact.append({
        "sid": c["session_id"], "pid": c["prompt_id"], "q": c["prompt"],
        "cat": c["category"] or "未分类", "sub": c["subcategory"],
        "sm": c["single_multi"], "src": c["source"],
        "op": c["obj_point"], "sp": c["subj_point"],
        "d": {"r": trunc(c["models"]["doubao"]["reply"]), "c": trunc(c["models"]["doubao"]["cot"], 1000),
              "od": c["models"]["doubao"]["obj_dcg_prompt"], "sd": c["models"]["doubao"]["subj_dcg_prompt"],
              "w": c["models"]["doubao"]["word_count"]},
        "qw": {"r": trunc(c["models"]["qianwen"]["reply"]), "c": trunc(c["models"]["qianwen"]["cot"], 1000),
               "od": c["models"]["qianwen"]["obj_dcg_prompt"], "sd": c["models"]["qianwen"]["subj_dcg_prompt"],
               "w": c["models"]["qianwen"]["word_count"]},
        "gm": {"r": trunc(c["models"]["gemini"]["reply"]), "c": trunc(c["models"]["gemini"]["cot"], 1000),
               "od": c["models"]["gemini"]["obj_dcg_prompt"], "sd": c["models"]["gemini"]["subj_dcg_prompt"],
               "w": c["models"]["gemini"]["word_count"]},
        "gp": {"r": trunc(c["models"]["gpt"]["reply"]), "c": trunc(c["models"]["gpt"]["cot"], 1000),
               "od": c["models"]["gpt"]["obj_dcg_prompt"], "sd": c["models"]["gpt"]["subj_dcg_prompt"],
               "w": c["models"]["gpt"]["word_count"]},
        "gsb": {
            "qw": {"op": c["gsb"]["vs_qianwen"]["obj_prompt"], "sp": c["gsb"]["vs_qianwen"]["subj_prompt"]},
            "gm": {"op": c["gsb"]["vs_gemini"]["obj_prompt"], "sp": c["gsb"]["vs_gemini"]["subj_prompt"]},
            "gp": {"op": c["gsb"]["vs_gpt"]["obj_prompt"], "sp": c["gsb"]["vs_gpt"]["subj_prompt"]}
        }
    })

case_json = json.dumps(compact, ensure_ascii=False, separators=(',', ':'))
print(f"Cases: {len(cases)}, JSON: {len(case_json)//1024} KB")

# ── Read JS template ──
js_code = open("llm_case_explorer.js", "r", encoding="utf-8").read()
js_code = js_code.replace("__CASE_DATA_PLACEHOLDER__", case_json)

# ── Read v10 HTML ──
html = open("viz_final_v10.html", "r", encoding="utf-8").read()
print(f"Original HTML: {len(html)} bytes")

# ── 1. Replace LLM_DATA with correct format ──
m = re.search(r'var LLM_DATA\s*=\s*\{', html)
if m:
    start = m.start()
    depth = 0
    pos = m.end() - 1
    while pos < len(html):
        if html[pos] == '{': depth += 1
        elif html[pos] == '}':
            depth -= 1
            if depth == 0:
                # Replace including the trailing semicolon
                end_pos = pos + 1
                if end_pos < len(html) and html[end_pos] == ';':
                    end_pos += 1
                html = html[:start] + "var LLM_DATA = " + llm_data_json + ";" + html[end_pos:]
                print("✓ Replaced LLM_DATA with new stats")
                break
        pos += 1
else:
    print("⚠ Could not find LLM_DATA")

# ── 2. Add data source link to Tab 1 ──
old_sub = '数据来源: 3月流式竞对 Excel · 生成时间: 2026-04-02</p>'
new_sub = '数据来源: 3月流式竞对 Excel · <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5">飞书数据表</a> · 生成时间: 2026-04-02</p>'
html = html.replace(old_sub, new_sub, 1)
print("✓ Tab 1 data source link")

# ── 3. Update Tab 2 data source link ──
old_link = 'href="https://bytedance.larkoffice.com/sheets/Bduwsms4ZhxdNNti0xecqkWinYd"'
new_link = 'href="https://bytedance.larkoffice.com/sheets/VaHEsMjHZhyqrEtKVPDcNa2inbf"'
html = html.replace(old_link, new_link, 1)
print("✓ Tab 2 data source link updated")

# ── 4. Insert case section HTML ──
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
html = html.replace('</div><!-- end proj2 -->', case_section_html + '</div><!-- end proj2 -->', 1)
print("✓ Case HTML inserted")

# ── 5. Insert CSS ──
case_css = '<style>.llm-case-section{margin-top:32px;padding:0 20px 40px}.llm-case-section h2{font-size:22px;font-weight:700;margin-bottom:16px;color:#1a1a2e}.llm-case-filters{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;align-items:center}.llm-case-filters select,.llm-case-filters input{padding:6px 12px;border:1px solid #d0d5dd;border-radius:6px;font-size:13px;background:#fff}.llm-case-filters input{width:240px}.llm-case-count{font-size:13px;color:#667;margin-left:8px}.llm-case-list{display:flex;flex-direction:column;gap:16px}.llm-case-card{background:#fff;border:1px solid #e4e7ec;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}.llm-case-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}.llm-case-meta{display:flex;gap:8px;flex-wrap:wrap}.llm-case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500}.llm-case-tag.cat{background:#eef4ff;color:#3538cd}.llm-case-tag.sub{background:#f0fdf4;color:#16a34a}.llm-case-tag.sm{background:#fefce8;color:#a16207}.llm-case-tag.sid{background:#f3f4f6;color:#4b5563}.llm-case-prompt{background:#f8f9fb;border-left:3px solid #6366f1;padding:12px 16px;margin-bottom:16px;border-radius:0 6px 6px 0;font-size:14px;line-height:1.6;white-space:pre-wrap;word-break:break-word}.llm-case-responses{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px}@media(max-width:1400px){.llm-case-responses{grid-template-columns:1fr 1fr}}@media(max-width:768px){.llm-case-responses{grid-template-columns:1fr}}.llm-resp-box{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden}.llm-resp-header{padding:8px 12px;font-weight:600;font-size:13px;display:flex;justify-content:space-between;align-items:center}.llm-resp-header.doubao{background:#eef4ff;color:#3538cd}.llm-resp-header.qianwen{background:#fef3f2;color:#b42318}.llm-resp-header.gemini{background:#f0fdf4;color:#16a34a}.llm-resp-header.gpt{background:#f5f3ff;color:#6d28d9}.llm-resp-scores{font-weight:400;font-size:11px}.llm-resp-body{padding:12px;font-size:13px;line-height:1.6;max-height:300px;overflow-y:auto;white-space:pre-wrap;word-break:break-word}.llm-gsb-row{display:flex;gap:8px;margin-top:8px;padding:8px 12px;background:#fafafa;border-radius:6px;font-size:12px;flex-wrap:wrap}.llm-gsb-item{display:flex;align-items:center;gap:4px}.llm-gsb-val{font-weight:600}.llm-gsb-val.pos{color:#16a34a}.llm-gsb-val.neg{color:#dc2626}.llm-gsb-val.neu{color:#6b7280}.llm-case-pagination{display:flex;justify-content:center;gap:8px;margin-top:20px}.llm-case-pagination button{padding:6px 14px;border:1px solid #d0d5dd;border-radius:6px;background:#fff;cursor:pointer;font-size:13px}.llm-case-pagination button:hover{background:#f3f4f6}.llm-case-pagination button.active{background:#4f46e5;color:#fff;border-color:#4f46e5}.llm-case-pagination button:disabled{opacity:.5;cursor:not-allowed}.llm-cot-toggle{font-size:11px;color:#6366f1;cursor:pointer;margin-top:4px;text-decoration:underline}.llm-cot-content{display:none;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:8px;margin-top:8px;font-size:12px;max-height:200px;overflow-y:auto;white-space:pre-wrap}.llm-resp-body::-webkit-scrollbar,.llm-cot-content::-webkit-scrollbar{width:4px}.llm-resp-body::-webkit-scrollbar-thumb,.llm-cot-content::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:2px}</style>'
html = html.replace('</head>', case_css + '\n</head>', 1)
print("✓ Case CSS")

# ── 6. Insert case JS before </body> ──
html = html.replace('</body>', '<script>\n' + js_code + '\n</script>\n</body>', 1)
print("✓ Case JS + data")

# ── Save ──
out = "viz_final_v10_full.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
sz = os.path.getsize(out)
print(f"\nOutput: {out} ({sz} bytes, {sz/1024/1024:.1f} MB)")

# Verify
print("\nVerification:")
m = re.search(r'"GSB":\{"豆包_客观":"([^"]*)"', html)
if m: print(f'  GSB 豆包_客观 = {m.group(1)}')
m = re.search(r'"千问_客观":"([^"]*)"', html)
if m: print(f'  First 千问_客观 = {m.group(1)}')
m = re.search(r'"volume":\{', html)
if m: print(f'  volume found at pos {m.start()}')
m = re.search(r'"wordcount":\{', html)
if m: print(f'  wordcount found at pos {m.start()}')
