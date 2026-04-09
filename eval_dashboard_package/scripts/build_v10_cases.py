#!/usr/bin/env python3
"""
Build v10 with LLM case explorer for Tab 2, and data source link for Tab 1.
Reads viz_final_v10.html (current), injects:
1. Data source link into Tab 1
2. LLM case data + explorer JS into Tab 2
"""
import json, os, re, html

# ── Load case data ──
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

# Group by session for display
session_order = []
seen = set()
for c in cases:
    sid = c["session_id"] or c["prompt_id"]
    if sid not in seen:
        seen.add(sid)
        session_order.append(sid)

print(f"Total cases: {len(cases)}, Sessions: {len(session_order)}")

# ── Sanitize text for embedding in JS string ──
def js_safe(s):
    if not s:
        return ""
    # Escape backslashes, quotes, newlines, and <script> tags
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("</", "<\\/")
    return s

# ── Build compact JSON for cases ──
# Minimize size: use short keys
compact_cases = []
for c in cases:
    cc = {
        "sid": c["session_id"],
        "pid": c["prompt_id"],
        "q": c["prompt"],
        "cat": c["category"] or "未分类",
        "sub": c["subcategory"],
        "sm": c["single_multi"],
        "src": c["source"],
        "op": c["obj_point"],
        "sp": c["subj_point"],
        "d": {  # doubao
            "r": c["models"]["doubao"]["reply"],
            "c": c["models"]["doubao"]["cot"],
            "od": c["models"]["doubao"]["obj_dcg_prompt"],
            "os": c["models"]["doubao"]["obj_dcg_session"],
            "sd": c["models"]["doubao"]["subj_dcg_prompt"],
            "ss": c["models"]["doubao"]["subj_dcg_session"],
            "w": c["models"]["doubao"]["word_count"]
        },
        "qw": {  # qianwen
            "r": c["models"]["qianwen"]["reply"],
            "c": c["models"]["qianwen"]["cot"],
            "od": c["models"]["qianwen"]["obj_dcg_prompt"],
            "os": c["models"]["qianwen"]["obj_dcg_session"],
            "sd": c["models"]["qianwen"]["subj_dcg_prompt"],
            "ss": c["models"]["qianwen"]["subj_dcg_session"],
            "w": c["models"]["qianwen"]["word_count"]
        },
        "gm": {  # gemini
            "r": c["models"]["gemini"]["reply"],
            "c": c["models"]["gemini"]["cot"],
            "od": c["models"]["gemini"]["obj_dcg_prompt"],
            "os": c["models"]["gemini"]["obj_dcg_session"],
            "sd": c["models"]["gemini"]["subj_dcg_prompt"],
            "ss": c["models"]["gemini"]["subj_dcg_session"],
            "w": c["models"]["gemini"]["word_count"]
        },
        "gp": {  # gpt
            "r": c["models"]["gpt"]["reply"],
            "c": c["models"]["gpt"]["cot"],
            "od": c["models"]["gpt"]["obj_dcg_prompt"],
            "os": c["models"]["gpt"]["obj_dcg_session"],
            "sd": c["models"]["gpt"]["subj_dcg_prompt"],
            "ss": c["models"]["gpt"]["subj_dcg_session"],
            "w": c["models"]["gpt"]["word_count"]
        },
        "gsb": {
            "qw": {  # vs qianwen
                "op": c["gsb"]["vs_qianwen"]["obj_prompt"],
                "os": c["gsb"]["vs_qianwen"]["obj_session"],
                "sp": c["gsb"]["vs_qianwen"]["subj_prompt"],
                "ss": c["gsb"]["vs_qianwen"]["subj_session"]
            },
            "gm": {  # vs gemini
                "op": c["gsb"]["vs_gemini"]["obj_prompt"],
                "os": c["gsb"]["vs_gemini"]["obj_session"],
                "sp": c["gsb"]["vs_gemini"]["subj_prompt"],
                "ss": c["gsb"]["vs_gemini"]["subj_session"]
            },
            "gp": {  # vs gpt
                "op": c["gsb"]["vs_gpt"]["obj_prompt"],
                "os": c["gsb"]["vs_gpt"]["obj_session"],
                "sp": c["gsb"]["vs_gpt"]["subj_prompt"],
                "ss": c["gsb"]["vs_gpt"]["subj_session"]
            }
        }
    }
    compact_cases.append(cc)

case_json = json.dumps(compact_cases, ensure_ascii=False, separators=(',', ':'))
print(f"Case JSON size: {len(case_json)} bytes ({len(case_json)/1024/1024:.1f} MB)")

# Save compact JSON separately for verification
with open("llm_cases_compact.json", "w", encoding="utf-8") as f:
    f.write(case_json)

# ── Build case explorer CSS ──
llm_case_css = """
<style>
/* LLM Case Explorer Styles */
.llm-case-section { margin-top: 32px; }
.llm-case-section h2 { font-size: 22px; font-weight: 700; margin-bottom: 16px; color: #1a1a2e; }
.llm-case-filters { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
.llm-case-filters select, .llm-case-filters input {
  padding: 6px 12px; border: 1px solid #d0d5dd; border-radius: 6px;
  font-size: 13px; background: #fff;
}
.llm-case-filters input { width: 240px; }
.llm-case-count { font-size: 13px; color: #667; margin-left: 8px; }
.llm-case-list { display: flex; flex-direction: column; gap: 16px; }
.llm-case-card {
  background: #fff; border: 1px solid #e4e7ec; border-radius: 10px;
  padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.llm-case-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.llm-case-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.llm-case-tag {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 500;
}
.llm-case-tag.cat { background: #eef4ff; color: #3538cd; }
.llm-case-tag.sub { background: #f0fdf4; color: #16a34a; }
.llm-case-tag.sm { background: #fefce8; color: #a16207; }
.llm-case-tag.sid { background: #f3f4f6; color: #4b5563; }
.llm-case-prompt {
  background: #f8f9fb; border-left: 3px solid #6366f1; padding: 12px 16px;
  margin-bottom: 16px; border-radius: 0 6px 6px 0; font-size: 14px; line-height: 1.6;
  white-space: pre-wrap; word-break: break-word;
}
.llm-case-responses { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.llm-case-responses.four-col { grid-template-columns: 1fr 1fr 1fr 1fr; }
@media (max-width: 1200px) {
  .llm-case-responses.four-col { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 768px) {
  .llm-case-responses.four-col { grid-template-columns: 1fr; }
}
.llm-resp-box {
  border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;
}
.llm-resp-header {
  padding: 8px 12px; font-weight: 600; font-size: 13px;
  display: flex; justify-content: space-between; align-items: center;
}
.llm-resp-header.doubao { background: #eef4ff; color: #3538cd; }
.llm-resp-header.qianwen { background: #fef3f2; color: #b42318; }
.llm-resp-header.gemini { background: #f0fdf4; color: #16a34a; }
.llm-resp-header.gpt { background: #f5f3ff; color: #6d28d9; }
.llm-resp-scores { font-weight: 400; font-size: 11px; }
.llm-resp-body {
  padding: 12px; font-size: 13px; line-height: 1.6;
  max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-break: break-word;
}
.llm-gsb-row {
  display: flex; gap: 8px; margin-top: 8px; padding: 8px 12px;
  background: #fafafa; border-radius: 6px; font-size: 12px; flex-wrap: wrap;
}
.llm-gsb-item { display: flex; align-items: center; gap: 4px; }
.llm-gsb-val { font-weight: 600; }
.llm-gsb-val.pos { color: #16a34a; }
.llm-gsb-val.neg { color: #dc2626; }
.llm-gsb-val.neu { color: #6b7280; }
.llm-case-pagination { display: flex; justify-content: center; gap: 8px; margin-top: 20px; }
.llm-case-pagination button {
  padding: 6px 14px; border: 1px solid #d0d5dd; border-radius: 6px;
  background: #fff; cursor: pointer; font-size: 13px;
}
.llm-case-pagination button:hover { background: #f3f4f6; }
.llm-case-pagination button.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.llm-case-pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.llm-cot-toggle {
  font-size: 11px; color: #6366f1; cursor: pointer; margin-top: 4px;
  text-decoration: underline;
}
.llm-cot-content {
  display: none; background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 4px; padding: 8px; margin-top: 8px; font-size: 12px;
  max-height: 200px; overflow-y: auto; white-space: pre-wrap;
}
.llm-resp-body::-webkit-scrollbar, .llm-cot-content::-webkit-scrollbar { width: 4px; }
.llm-resp-body::-webkit-scrollbar-thumb, .llm-cot-content::-webkit-scrollbar-thumb {
  background: #d1d5db; border-radius: 2px;
}
</style>
"""

# ── Build case explorer JS ──
llm_case_js = """
<script>
/* LLM Case Explorer */
var LLM_CASES = __CASE_DATA__;

var llmCaseState = {
  filtered: LLM_CASES,
  page: 0,
  perPage: 10,
  catFilter: "",
  searchFilter: "",
  viewMode: "four"  // four-col view
};

function llmFilterCases() {
  var cat = llmCaseState.catFilter;
  var search = llmCaseState.searchFilter.toLowerCase();
  llmCaseState.filtered = LLM_CASES.filter(function(c) {
    if (cat && c.cat !== cat) return false;
    if (search) {
      var haystack = (c.q + " " + c.pid + " " + c.sid + " " + c.sub + " " + c.op + " " + c.sp).toLowerCase();
      if (haystack.indexOf(search) === -1) return false;
    }
    return true;
  });
  llmCaseState.page = 0;
  llmRenderCases();
}

function llmGsbClass(v) {
  if (v === null || v === undefined) return "neu";
  if (v > 0) return "pos";
  if (v < 0) return "neg";
  return "neu";
}

function llmFmtScore(v) {
  if (v === null || v === undefined) return "-";
  return String(v);
}

function llmSanitize(s) {
  if (!s) return "<em style='color:#aaa'>（无回复）</em>";
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function llmToggleCot(btn) {
  var el = btn.nextElementSibling;
  if (!el) return;
  if (el.style.display === "block") {
    el.style.display = "none";
    btn.textContent = "展开思考过程 ▼";
  } else {
    el.style.display = "block";
    btn.textContent = "收起思考过程 ▲";
  }
}

function llmRenderCases() {
  var container = document.getElementById("llm-case-list");
  if (!container) return;
  var cases = llmCaseState.filtered;
  var start = llmCaseState.page * llmCaseState.perPage;
  var end = Math.min(start + llmCaseState.perPage, cases.length);
  var pageItems = cases.slice(start, end);

  // Update count
  var countEl = document.getElementById("llm-case-count");
  if (countEl) countEl.textContent = "共 " + cases.length + " 条";

  var html = "";
  for (var i = 0; i < pageItems.length; i++) {
    var c = pageItems[i];
    var idx = start + i + 1;

    html += '<div class="llm-case-card">';
    html += '<div class="llm-case-header"><div class="llm-case-meta">';
    html += '<span class="llm-case-tag sid">#' + idx + ' ' + llmSanitize(c.pid) + '</span>';
    if (c.cat) html += '<span class="llm-case-tag cat">' + llmSanitize(c.cat) + '</span>';
    if (c.sub) html += '<span class="llm-case-tag sub">' + llmSanitize(c.sub) + '</span>';
    if (c.sm) html += '<span class="llm-case-tag sm">' + llmSanitize(c.sm) + '</span>';
    html += '</div></div>';

    html += '<div class="llm-case-prompt">' + llmSanitize(c.q) + '</div>';

    // 4-model responses
    var models = [
      {key: "d", name: "豆包", cls: "doubao"},
      {key: "qw", name: "千问3", cls: "qianwen"},
      {key: "gm", name: "Gemini 3 Pro", cls: "gemini"},
      {key: "gp", name: "GPT 5.2", cls: "gpt"}
    ];

    html += '<div class="llm-case-responses four-col">';
    for (var m = 0; m < models.length; m++) {
      var md = models[m];
      var data = c[md.key];
      html += '<div class="llm-resp-box">';
      html += '<div class="llm-resp-header ' + md.cls + '">';
      html += '<span>' + md.name + '</span>';
      html += '<span class="llm-resp-scores">';
      if (data.od !== null && data.od !== undefined) html += '客观:' + llmFmtScore(data.od) + ' ';
      if (data.sd !== null && data.sd !== undefined) html += '主客观:' + llmFmtScore(data.sd);
      html += '</span></div>';
      html += '<div class="llm-resp-body">' + llmSanitize(data.r) + '';
      if (data.c) {
        html += '<div class="llm-cot-toggle" onclick="llmToggleCot(this)">展开思考过程 ▼</div>';
        html += '<div class="llm-cot-content">' + llmSanitize(data.c) + '</div>';
      }
      html += '</div></div>';
    }
    html += '</div>';

    // GSB scores row
    var gsbPairs = [
      {key: "qw", label: "vs 千问"},
      {key: "gm", label: "vs Gemini"},
      {key: "gp", label: "vs GPT"}
    ];
    var hasGsb = false;
    for (var g = 0; g < gsbPairs.length; g++) {
      var gd = c.gsb[gsbPairs[g].key];
      if (gd.op !== null || gd.sp !== null) { hasGsb = true; break; }
    }
    if (hasGsb) {
      html += '<div class="llm-gsb-row">';
      html += '<strong style="font-size:12px;margin-right:4px">GSB(prompt):</strong>';
      for (var g = 0; g < gsbPairs.length; g++) {
        var gd = c.gsb[gsbPairs[g].key];
        html += '<span class="llm-gsb-item">' + gsbPairs[g].label + ' 客观:<span class="llm-gsb-val ' + llmGsbClass(gd.op) + '">' + llmFmtScore(gd.op) + '</span>';
        html += ' 主客观:<span class="llm-gsb-val ' + llmGsbClass(gd.sp) + '">' + llmFmtScore(gd.sp) + '</span></span>';
        if (g < gsbPairs.length - 1) html += '<span style="color:#ddd;margin:0 4px">|</span>';
      }
      html += '</div>';
    }

    html += '</div>';
  }

  container.innerHTML = html;

  // Pagination
  var pagEl = document.getElementById("llm-case-pagination");
  if (!pagEl) return;
  var totalPages = Math.ceil(cases.length / llmCaseState.perPage);
  if (totalPages <= 1) { pagEl.innerHTML = ""; return; }

  var phtml = '<button ' + (llmCaseState.page <= 0 ? 'disabled' : '') + ' onclick="llmCaseState.page--;llmRenderCases();window.scrollTo(0,document.getElementById(\'llm-case-section\').offsetTop)">上一页</button>';
  // Show page numbers (max 7)
  var startP = Math.max(0, llmCaseState.page - 3);
  var endP = Math.min(totalPages - 1, startP + 6);
  startP = Math.max(0, endP - 6);
  for (var p = startP; p <= endP; p++) {
    phtml += '<button class="' + (p === llmCaseState.page ? 'active' : '') + '" onclick="llmCaseState.page=' + p + ';llmRenderCases();window.scrollTo(0,document.getElementById(\'llm-case-section\').offsetTop)">' + (p + 1) + '</button>';
  }
  phtml += '<button ' + (llmCaseState.page >= totalPages - 1 ? 'disabled' : '') + ' onclick="llmCaseState.page++;llmRenderCases();window.scrollTo(0,document.getElementById(\'llm-case-section\').offsetTop)">下一页</button>';
  pagEl.innerHTML = phtml;
}

/* Init on load */
(function() {
  var origOnload = window.onload;
  window.onload = function() {
    if (origOnload) origOnload();
    // Build category filter options
    var catSet = {};
    for (var i = 0; i < LLM_CASES.length; i++) {
      var cat = LLM_CASES[i].cat;
      if (cat) catSet[cat] = (catSet[cat] || 0) + 1;
    }
    var sel = document.getElementById("llm-case-cat-filter");
    if (sel) {
      var cats = Object.keys(catSet).sort();
      for (var j = 0; j < cats.length; j++) {
        var opt = document.createElement("option");
        opt.value = cats[j];
        opt.textContent = cats[j] + " (" + catSet[cats[j]] + ")";
        sel.appendChild(opt);
      }
    }
    llmRenderCases();
  };
})();
</script>
"""

# ── Build case explorer HTML ──
llm_case_html = """
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
"""

# ── Now modify viz_final_v10.html ──
print("Reading viz_final_v10.html...")
with open("viz_final_v10.html", "r", encoding="utf-8") as f:
    content = f.read()

print(f"Original size: {len(content)} bytes")

# 1. Add data source link to Tab 1
# Find the data source section in Tab 1 (proj1 panel)
# In v10, Tab 1 contains the existing v9 content
# Look for a good place to insert data source link - near the top of proj1 content
datasource_link_html = """<div style="text-align:center;margin:8px 0 0 0;font-size:13px;color:#667;">
  数据来源: <a href="https://bytedance.larkoffice.com/sheets/KcATsIAxfh3UOYtyq8ncFLeNnkl?sheet=nq0bBB" target="_blank" style="color:#4f46e5;">飞书数据表</a>
</div>"""

# Insert after the first proj1 panel div opening
# Look for project-panel proj1
proj1_marker = 'class="project-panel proj1"'
if proj1_marker in content:
    idx = content.index(proj1_marker)
    # Find the next > to close the div tag
    gt_idx = content.index(">", idx)
    # Insert our data source link right after
    content = content[:gt_idx+1] + "\n" + datasource_link_html + "\n" + content[gt_idx+1:]
    print("✓ Added data source link to Tab 1")
else:
    print("⚠ Could not find proj1 marker")

# 2. Insert case explorer CSS before </head>
content = content.replace("</head>", llm_case_css + "\n</head>")
print("✓ Added LLM case CSS")

# 3. Insert case explorer HTML into Tab 2 (proj2)
# Find the end of proj2's dashboard content, before its closing </div>
# proj2 panel contains the LLM dashboard, we add cases after it
proj2_marker = 'class="project-panel proj2"'
if proj2_marker in content:
    # Find the closing </div> of proj2 panel
    # The proj2 panel structure is: <div class="project-panel proj2"> ... </div>
    # We need to insert before its closing tag
    # Find proj2 start
    p2_start = content.index(proj2_marker)
    
    # Find the matching closing div - look for <!-- end proj2 --> or similar
    # Let's find a safe insertion point - before the closing of proj2
    # In build_v10.py, proj2 ends with </div><!--proj2-->
    proj2_end_marker = "</div><!--proj2-->"
    if proj2_end_marker in content:
        p2_end = content.index(proj2_end_marker)
        content = content[:p2_end] + llm_case_html + "\n" + content[p2_end:]
        print("✓ Added LLM case HTML to Tab 2")
    else:
        # Try to find it another way - look for end of proj2 wrap
        # Insert before the last </div> that closes proj2's wrap
        print("⚠ Could not find proj2 end marker, trying alternative...")
        # Find the wrap div inside proj2
        wrap_after_p2 = content.find('<div class="wrap">', p2_start)
        if wrap_after_p2 > 0:
            # Find the closing </div> for this wrap
            # Count div nesting
            depth = 0
            pos = wrap_after_p2
            while pos < len(content):
                if content[pos:pos+4] == "<div":
                    depth += 1
                elif content[pos:pos+6] == "</div>":
                    depth -= 1
                    if depth == 0:
                        # Insert before this closing div
                        content = content[:pos] + llm_case_html + "\n" + content[pos:]
                        print("✓ Added LLM case HTML to Tab 2 (alt method)")
                        break
                pos += 1
else:
    print("⚠ Could not find proj2 marker")

# 4. Insert case data + JS before </body>
case_js_with_data = llm_case_js.replace("__CASE_DATA__", case_json)
content = content.replace("</body>", case_js_with_data + "\n</body>")
print("✓ Added LLM case JS + data")

# ── Save ──
output_file = "viz_final_v10_cases.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nOutput: {output_file} ({os.path.getsize(output_file)} bytes, {os.path.getsize(output_file)/1024/1024:.1f} MB)")
