#!/usr/bin/env python3
"""
Build v10 with LLM case explorer for Tab 2, and data source link for Tab 1.
"""
import json, os

# Load case data and propagate categories
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

# Build compact JSON
compact_cases = []
for c in cases:
    cc = {
        "sid": c["session_id"], "pid": c["prompt_id"], "q": c["prompt"],
        "cat": c["category"] or "未分类", "sub": c["subcategory"],
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
    }
    compact_cases.append(cc)

case_json = json.dumps(compact_cases, ensure_ascii=False, separators=(',', ':'))
print(f"Cases: {len(cases)}, JSON: {len(case_json)/1024:.0f} KB")

# Read v10 HTML
with open("viz_final_v10.html", "r", encoding="utf-8") as f:
    html = f.read()
print(f"Original: {len(html)} bytes")

# ──────────────────────────────────────────────
# 1. Add data source link in Tab 1
# Replace the existing subtitle line in proj1
# Current: <p>数据来源: 3月流式竞对 Excel · 生成时间: 2026-04-02</p>
old_subtitle = '数据来源: 3月流式竞对 Excel · 生成时间: 2026-04-02</p>'
new_subtitle = '数据来源: 3月流式竞对 Excel · <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5">飞书数据表</a> · 生成时间: 2026-04-02</p>'
if old_subtitle in html:
    html = html.replace(old_subtitle, new_subtitle, 1)
    print("✓ Added data source link to Tab 1")
else:
    print("⚠ Could not find Tab 1 subtitle to replace")

# ──────────────────────────────────────────────
# 2. Insert case explorer HTML before </div><!-- end proj2 -->
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
if proj2_end in html:
    html = html.replace(proj2_end, case_section_html + '\n' + proj2_end, 1)
    print("✓ Added case HTML to Tab 2")
else:
    print("⚠ Could not find proj2 end marker")

# ──────────────────────────────────────────────
# 3. Insert case explorer CSS before </head>
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

# ──────────────────────────────────────────────
# 4. Insert case JS + data before </body>
case_js = '''<script>
var LLM_CASES=__CASE_DATA__;
var llmCaseState={filtered:LLM_CASES,page:0,perPage:10,catFilter:"",searchFilter:""};
function llmFilterCases(){var cat=llmCaseState.catFilter;var search=llmCaseState.searchFilter.toLowerCase();llmCaseState.filtered=LLM_CASES.filter(function(c){if(cat&&c.cat!==cat)return false;if(search){var h=(c.q+" "+c.pid+" "+c.sid+" "+c.sub+" "+c.op+" "+c.sp).toLowerCase();if(h.indexOf(search)===-1)return false}return true});llmCaseState.page=0;llmRenderCases()}
function llmGsbCls(v){if(v===null||v===undefined)return"neu";return v>0?"pos":v<0?"neg":"neu"}
function llmFmt(v){if(v===null||v===undefined)return"-";return String(v)}
function llmSan(s){if(!s)return"<em style=\\'color:#aaa\\'>(\\u65E0\\u56DE\\u590D)</em>";var d=document.createElement("div");d.textContent=s;return d.innerHTML}
function llmToggleCot(btn){var el=btn.nextElementSibling;if(!el)return;if(el.style.display==="block"){el.style.display="none";btn.textContent="\\u5C55\\u5F00\\u601D\\u8003\\u8FC7\\u7A0B \\u25BC"}else{el.style.display="block";btn.textContent="\\u6536\\u8D77\\u601D\\u8003\\u8FC7\\u7A0B \\u25B2"}}
function llmRenderCases(){var container=document.getElementById("llm-case-list");if(!container)return;var cases=llmCaseState.filtered;var start=llmCaseState.page*llmCaseState.perPage;var end=Math.min(start+llmCaseState.perPage,cases.length);var items=cases.slice(start,end);var countEl=document.getElementById("llm-case-count");if(countEl)countEl.textContent="\\u5171 "+cases.length+" \\u6761";var h="";for(var i=0;i<items.length;i++){var c=items[i];var idx=start+i+1;h+='<div class="llm-case-card"><div class="llm-case-header"><div class="llm-case-meta">';h+='<span class="llm-case-tag sid">#'+idx+" "+llmSan(c.pid)+"</span>";if(c.cat)h+='<span class="llm-case-tag cat">'+llmSan(c.cat)+"</span>";if(c.sub)h+='<span class="llm-case-tag sub">'+llmSan(c.sub)+"</span>";if(c.sm)h+='<span class="llm-case-tag sm">'+llmSan(c.sm)+"</span>";h+="</div></div>";h+='<div class="llm-case-prompt">'+llmSan(c.q)+"</div>";var models=[{k:"d",n:"\\u8C46\\u5305",cls:"doubao"},{k:"qw",n:"\\u5343\\u95EE3",cls:"qianwen"},{k:"gm",n:"Gemini 3 Pro",cls:"gemini"},{k:"gp",n:"GPT 5.2",cls:"gpt"}];h+='<div class="llm-case-responses">';for(var m=0;m<models.length;m++){var md=models[m];var data=c[md.k];h+='<div class="llm-resp-box"><div class="llm-resp-header '+md.cls+'"><span>'+md.n+"</span><span class=\\"llm-resp-scores\\">";if(data.od!==null&&data.od!==undefined)h+="\\u5BA2\\u89C2:"+llmFmt(data.od)+" ";if(data.sd!==null&&data.sd!==undefined)h+="\\u4E3B\\u5BA2\\u89C2:"+llmFmt(data.sd);h+="</span></div>";h+='<div class="llm-resp-body">'+llmSan(data.r);if(data.c){h+='<div class="llm-cot-toggle" onclick="llmToggleCot(this)">\\u5C55\\u5F00\\u601D\\u8003\\u8FC7\\u7A0B \\u25BC</div>';h+='<div class="llm-cot-content">'+llmSan(data.c)+"</div>"}h+="</div></div>"}h+="</div>";var gsbPairs=[{k:"qw",l:"vs \\u5343\\u95EE"},{k:"gm",l:"vs Gemini"},{k:"gp",l:"vs GPT"}];var hasGsb=false;for(var g=0;g<gsbPairs.length;g++){var gd=c.gsb[gsbPairs[g].k];if(gd.op!==null||gd.sp!==null){hasGsb=true;break}}if(hasGsb){h+='<div class="llm-gsb-row"><strong style="font-size:12px;margin-right:4px">GSB(prompt):</strong>';for(var g=0;g<gsbPairs.length;g++){var gd=c.gsb[gsbPairs[g].k];h+='<span class="llm-gsb-item">'+gsbPairs[g].l+" \\u5BA2\\u89C2:<span class=\\"llm-gsb-val "+llmGsbCls(gd.op)+"\\">"+llmFmt(gd.op)+"</span> \\u4E3B\\u5BA2\\u89C2:<span class=\\"llm-gsb-val "+llmGsbCls(gd.sp)+"\\">"+llmFmt(gd.sp)+"</span></span>";if(g<gsbPairs.length-1)h+='<span style="color:#ddd;margin:0 4px">|</span>'}h+="</div>"}h+="</div>"}container.innerHTML=h;var pagEl=document.getElementById("llm-case-pagination");if(!pagEl)return;var totalPages=Math.ceil(cases.length/llmCaseState.perPage);if(totalPages<=1){pagEl.innerHTML="";return}var ph='<button '+(llmCaseState.page<=0?"disabled":"")+" onclick=\\"llmCaseState.page--;llmRenderCases();window.scrollTo(0,document.getElementById('llm-case-section').offsetTop)\\">\\u4E0A\\u4E00\\u9875</button>";var sp=Math.max(0,llmCaseState.page-3);var ep=Math.min(totalPages-1,sp+6);sp=Math.max(0,ep-6);for(var p=sp;p<=ep;p++){ph+='<button class=\\"'+(p===llmCaseState.page?"active":"")+"\\\" onclick=\\\"llmCaseState.page="+p+";llmRenderCases();window.scrollTo(0,document.getElementById('llm-case-section').offsetTop)\\\">"+(p+1)+"</button>"}ph+='<button '+(llmCaseState.page>=totalPages-1?"disabled":"")+" onclick=\\"llmCaseState.page++;llmRenderCases();window.scrollTo(0,document.getElementById('llm-case-section').offsetTop)\\">\\u4E0B\\u4E00\\u9875</button>";pagEl.innerHTML=ph}
(function(){var origOnload=window.onload;window.onload=function(){if(origOnload)origOnload();var catSet={};for(var i=0;i<LLM_CASES.length;i++){var cat=LLM_CASES[i].cat;if(cat)catSet[cat]=(catSet[cat]||0)+1}var sel=document.getElementById("llm-case-cat-filter");if(sel){var cats=Object.keys(catSet).sort();for(var j=0;j<cats.length;j++){var opt=document.createElement("option");opt.value=cats[j];opt.textContent=cats[j]+" ("+catSet[cats[j]]+")";sel.appendChild(opt)}}llmRenderCases()}})();
</script>'''

# The inline JS above has escaping issues with nested quotes. Let me use a different approach.
# Write the JS to a file and read it properly.
print("Writing JS to file for clean injection...")
