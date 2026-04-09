#!/usr/bin/env python3
"""
Fix Tab 2:
1. Charts already use 3-per-row grid (llm-charts-grid) - verify it's working
2. Case section: rename to "Case 探查", add model filter, add subcategory filter tabs, add more side padding
"""
import re, json

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# =====================================================
# PART 1: Update the case section HTML in proj2
# =====================================================

old_case_html = '''<div class="llm-case-section" id="llm-case-section">
  <h2>Case 详情</h2>
  <div class="llm-case-filters">
    <select id="llm-case-cat-filter" onchange="llmCaseState.catFilter=this.value;llmFilterCases();"><option value="">全部分类</option></select>
    <input type="text" id="llm-case-search" placeholder="搜索 Prompt / ID / 考点..." oninput="llmCaseState.searchFilter=this.value;llmFilterCases();">
    <span class="llm-case-count" id="llm-case-count"></span>
  </div>
  <div class="llm-case-list" id="llm-case-list"></div>
  <div class="llm-case-pagination" id="llm-case-pagination"></div>
</div>'''

new_case_html = '''<div class="llm-case-section" id="llm-case-section">
  <h2>Case 探查</h2>
  <div class="llm-case-filters">
    <select id="llm-case-cat-filter" onchange="llmCaseState.catFilter=this.value;llmCaseState.subFilter='';llmBuildSubTabs();llmFilterCases();"><option value="">全部分类</option></select>
    <select id="llm-case-model-filter" onchange="llmCaseState.modelFilter=this.value;llmFilterCases();"><option value="">全部模型</option><option value="d">豆包</option><option value="qw">千问3</option><option value="gm">Gemini 3 Pro</option><option value="gp">GPT 5.2</option></select>
    <input type="text" id="llm-case-search" placeholder="搜索 Prompt / ID / 考点..." oninput="llmCaseState.searchFilter=this.value;llmFilterCases();">
    <span class="llm-case-count" id="llm-case-count"></span>
  </div>
  <div class="llm-case-sub-tabs" id="llm-case-sub-tabs"></div>
  <div class="llm-case-list" id="llm-case-list"></div>
  <div class="llm-case-pagination" id="llm-case-pagination"></div>
</div>'''

assert old_case_html in html, "Old case HTML not found!"
html = html.replace(old_case_html, new_case_html, 1)
print("✓ Case section HTML updated")

# =====================================================
# PART 2: Update case section CSS - more side padding, sub-tabs style
# =====================================================

old_case_css = '.llm-case-section{margin-top:32px;padding:0 20px 40px}'
new_case_css = '.llm-case-section{margin-top:32px;padding:0 48px 40px}'

html = html.replace(old_case_css, new_case_css)
print("✓ Case section padding updated (20px -> 48px)")

# Add sub-tabs CSS after the case section styles
sub_tabs_css = """.llm-case-sub-tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;padding:4px 0}.llm-case-sub-tab{display:inline-block;padding:4px 12px;border-radius:14px;font-size:12px;font-weight:500;cursor:pointer;border:1px solid #d0d5dd;background:#fff;color:#4e5969;transition:all .15s}.llm-case-sub-tab:hover{border-color:#165dff;color:#165dff}.llm-case-sub-tab.active{background:#165dff;color:#fff;border-color:#165dff}"""

# Insert after the case section padding rule
insert_marker = new_case_css
idx = html.index(insert_marker) + len(insert_marker)
html = html[:idx] + sub_tabs_css + html[idx:]
print("✓ Sub-tab CSS added")

# Also add model filter select styling
model_select_css = ".llm-case-filters select{min-width:100px}"
# Find the existing filter styles and append
filter_marker = ".llm-case-filters input{width:240px}"
idx = html.index(filter_marker) + len(filter_marker)
html = html[:idx] + model_select_css + html[idx:]
print("✓ Model filter CSS added")

# =====================================================
# PART 3: Replace the case explorer JS (the last <script> block)
# =====================================================

last_script_pos = html.rfind('<script>')
last_close_pos = html.rfind('</script>')
old_case_block = html[last_script_pos:last_close_pos + 9]

# Extract the LLM_CASES data from the old block
old_inner = old_case_block[8:-9]  # strip <script> and </script>
cases_end = old_inner.find('];') + 2
cases_data_str = old_inner[:cases_end]  # "var LLM_CASES = [...];"

new_case_js = cases_data_str + r'''
var llmCaseState = {filtered: LLM_CASES, page: 0, perPage: 10, catFilter: "", subFilter: "", searchFilter: "", modelFilter: ""};

function llmFilterCases() {
  var cat = llmCaseState.catFilter;
  var sub = llmCaseState.subFilter;
  var search = llmCaseState.searchFilter.toLowerCase();
  var model = llmCaseState.modelFilter;
  llmCaseState.filtered = LLM_CASES.filter(function(c) {
    if (cat && c.cat !== cat) return false;
    if (sub && c.sub !== sub) return false;
    if (search) {
      var h = (c.q + " " + c.pid + " " + c.sid + " " + c.sub + " " + (c.op || "") + " " + (c.sp || "")).toLowerCase();
      if (h.indexOf(search) === -1) return false;
    }
    /* Model filter: only show cases where the selected model has a response */
    if (model && c[model]) {
      var mr = c[model].r;
      if (!mr || mr === "") return false;
    }
    return true;
  });
  llmCaseState.page = 0;
  llmRenderCases();
}

function llmBuildSubTabs() {
  var el = document.getElementById("llm-case-sub-tabs");
  if (!el) return;
  var cat = llmCaseState.catFilter;
  if (!cat) { el.innerHTML = ""; return; }
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (LLM_CASES[i].cat === cat && LLM_CASES[i].sub) {
      subMap[LLM_CASES[i].sub] = (subMap[LLM_CASES[i].sub] || 0) + 1;
    }
  }
  var subs = Object.keys(subMap).sort();
  if (subs.length === 0) { el.innerHTML = ""; return; }
  var h = '<span class="llm-case-sub-tab' + (!llmCaseState.subFilter ? ' active' : '') + '" onclick="llmSetSub(this,\'\')">\u5168\u90e8</span>';
  for (var i = 0; i < subs.length; i++) {
    var isActive = llmCaseState.subFilter === subs[i] ? ' active' : '';
    h += '<span class="llm-case-sub-tab' + isActive + '" onclick="llmSetSub(this,\'' + subs[i].replace(/'/g, "\\'") + '\')">' + subs[i] + ' (' + subMap[subs[i]] + ')</span>';
  }
  el.innerHTML = h;
}

function llmSetSub(el, sub) {
  llmCaseState.subFilter = sub;
  var tabs = el.parentNode.querySelectorAll(".llm-case-sub-tab");
  for (var i = 0; i < tabs.length; i++) tabs[i].className = "llm-case-sub-tab";
  el.className = "llm-case-sub-tab active";
  llmFilterCases();
}

function llmGsbCls(v) {
  if (v === null || v === undefined) return "neu";
  return v > 0 ? "pos" : v < 0 ? "neg" : "neu";
}

function llmFmt(v) {
  if (v === null || v === undefined) return "-";
  return String(v);
}

function llmSan(s) {
  if (!s) return '<em style="color:#aaa">\uff08\u65e0\u56de\u590d\uff09</em>';
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function llmToggleCot(btn) {
  var el = btn.nextElementSibling;
  if (!el) return;
  if (el.style.display === "block") {
    el.style.display = "none";
    btn.textContent = "\u5c55\u5f00\u601d\u8003\u8fc7\u7a0b \u25bc";
  } else {
    el.style.display = "block";
    btn.textContent = "\u6536\u8d77\u601d\u8003\u8fc7\u7a0b \u25b2";
  }
}

function llmRenderCases() {
  var container = document.getElementById("llm-case-list");
  if (!container) return;
  var cases = llmCaseState.filtered;
  var start = llmCaseState.page * llmCaseState.perPage;
  var end = Math.min(start + llmCaseState.perPage, cases.length);
  var items = cases.slice(start, end);
  var countEl = document.getElementById("llm-case-count");
  if (countEl) countEl.textContent = "\u5171 " + cases.length + " \u6761";

  var modelFilter = llmCaseState.modelFilter;
  /* Determine which models to show */
  var allModels = [
    {k: "d", n: "\u8c46\u5305", cls: "doubao"},
    {k: "qw", n: "\u5343\u95ee3", cls: "qianwen"},
    {k: "gm", n: "Gemini 3 Pro", cls: "gemini"},
    {k: "gp", n: "GPT 5.2", cls: "gpt"}
  ];
  var showModels = allModels;
  if (modelFilter) {
    /* When filtering by model, show doubao + selected model side by side */
    if (modelFilter === "d") {
      showModels = [allModels[0]];
    } else {
      showModels = [allModels[0]];
      for (var mi = 0; mi < allModels.length; mi++) {
        if (allModels[mi].k === modelFilter) { showModels.push(allModels[mi]); break; }
      }
    }
  }
  var gridCols = showModels.length <= 2 ? showModels.length : 4;

  var h = "";
  for (var i = 0; i < items.length; i++) {
    var c = items[i];
    var idx = start + i + 1;
    h += '<div class="llm-case-card"><div class="llm-case-header"><div class="llm-case-meta">';
    h += '<span class="llm-case-tag sid">#' + idx + " " + llmSan(c.pid) + "</span>";
    if (c.cat) h += '<span class="llm-case-tag cat">' + llmSan(c.cat) + "</span>";
    if (c.sub) h += '<span class="llm-case-tag sub">' + llmSan(c.sub) + "</span>";
    if (c.sm) h += '<span class="llm-case-tag sm">' + llmSan(c.sm) + "</span>";
    h += "</div></div>";
    h += '<div class="llm-case-prompt">' + llmSan(c.q) + "</div>";

    h += '<div class="llm-case-responses" style="grid-template-columns:repeat(' + gridCols + ',1fr)">';
    for (var m = 0; m < showModels.length; m++) {
      var md = showModels[m];
      var data = c[md.k];
      if (!data) continue;
      h += '<div class="llm-resp-box"><div class="llm-resp-header ' + md.cls + '"><span>' + md.n + "</span>";
      h += '<span class="llm-resp-scores">';
      if (data.od !== null && data.od !== undefined) h += "\u5ba2\u89c2:" + llmFmt(data.od) + " ";
      if (data.sd !== null && data.sd !== undefined) h += "\u4e3b\u5ba2\u89c2:" + llmFmt(data.sd);
      h += "</span></div>";
      h += '<div class="llm-resp-body">' + llmSan(data.r);
      if (data.c) {
        h += '<div class="llm-cot-toggle" onclick="llmToggleCot(this)">\u5c55\u5f00\u601d\u8003\u8fc7\u7a0b \u25bc</div>';
        h += '<div class="llm-cot-content">' + llmSan(data.c) + "</div>";
      }
      h += "</div></div>";
    }
    h += "</div>";

    /* GSB row */
    var gsbPairs = [
      {k: "qw", l: "vs \u5343\u95ee"},
      {k: "gm", l: "vs Gemini"},
      {k: "gp", l: "vs GPT"}
    ];
    var hasGsb = false;
    for (var g = 0; g < gsbPairs.length; g++) {
      var gd = c.gsb[gsbPairs[g].k];
      if (gd && (gd.op !== null || gd.sp !== null)) { hasGsb = true; break; }
    }
    if (hasGsb) {
      h += '<div class="llm-gsb-row"><strong style="font-size:12px;margin-right:4px">GSB(prompt):</strong>';
      for (var g = 0; g < gsbPairs.length; g++) {
        var gd = c.gsb[gsbPairs[g].k];
        if (!gd) continue;
        h += '<span class="llm-gsb-item">' + gsbPairs[g].l;
        h += ' \u5ba2\u89c2:<span class="llm-gsb-val ' + llmGsbCls(gd.op) + '">' + llmFmt(gd.op) + "</span>";
        h += ' \u4e3b\u5ba2\u89c2:<span class="llm-gsb-val ' + llmGsbCls(gd.sp) + '">' + llmFmt(gd.sp) + "</span></span>";
        if (g < gsbPairs.length - 1) h += '<span style="color:#ddd;margin:0 4px">|</span>';
      }
      h += "</div>";
    }
    h += "</div>";
  }
  container.innerHTML = h;

  /* Pagination */
  var pagEl = document.getElementById("llm-case-pagination");
  if (!pagEl) return;
  var totalPages = Math.ceil(cases.length / llmCaseState.perPage);
  if (totalPages <= 1) { pagEl.innerHTML = ""; return; }
  var ph = "";
  ph += '<button ' + (llmCaseState.page <= 0 ? "disabled" : "") + ' onclick="llmGoPage(' + (llmCaseState.page - 1) + ')">\u4e0a\u4e00\u9875</button>';
  var sp = Math.max(0, llmCaseState.page - 3);
  var ep = Math.min(totalPages - 1, sp + 6);
  sp = Math.max(0, ep - 6);
  for (var p = sp; p <= ep; p++) {
    ph += '<button class="' + (p === llmCaseState.page ? "active" : "") + '" onclick="llmGoPage(' + p + ')">' + (p + 1) + "</button>";
  }
  ph += '<button ' + (llmCaseState.page >= totalPages - 1 ? "disabled" : "") + ' onclick="llmGoPage(' + (llmCaseState.page + 1) + ')">\u4e0b\u4e00\u9875</button>';
  pagEl.innerHTML = ph;
}

function llmGoPage(p) {
  llmCaseState.page = p;
  llmRenderCases();
  var el = document.getElementById("llm-case-section");
  if (el) window.scrollTo(0, el.offsetTop);
}

/* Init */
(function() {
  var origOnload = window.onload;
  window.onload = function() {
    if (origOnload) origOnload();
    /* Build category dropdown */
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
'''

new_case_block = '<script>\n/* LLM Case Explorer - ES5 only */\n' + new_case_js + '\n</script>'

html = html[:last_script_pos] + new_case_block + html[last_close_pos + 9:]
print("✓ Case explorer JS replaced")

# =====================================================
# PART 4: Verify
# =====================================================

# Check brace balance in the case explorer
case_js_start = html.rfind('<script>')
case_js_end = html.rfind('</script>')
case_js = html[case_js_start+8:case_js_end]
# Only check code part (skip the data array)
code_start = case_js.find('];') + 2
code_only = case_js[code_start:]
opens = code_only.count('{')
closes = code_only.count('}')
print(f"Case JS braces: {opens} opens, {closes} closes")
assert opens == closes, f"BRACE MISMATCH in case JS!"

# Check the main script block braces too
main_script_start = html.index('/* === Project Tab Switching === */')
main_script_end = html.index('</script>', main_script_start)
main_js = html[main_script_start:main_script_end]
opens = main_js.count('{')
closes = main_js.count('}')
print(f"Main JS braces: {opens} opens, {closes} closes")
assert opens == closes, f"BRACE MISMATCH in main JS!"

# Overall script tag balance
all_opens = len(re.findall(r'<script[\s>]', html))
all_closes = html.count('</script>')
print(f"Script tags: {all_opens} opens, {all_closes} closes")

# </body> positions
pos = 0
body_positions = []
while True:
    idx = html.find('</body>', pos)
    if idx < 0: break
    body_positions.append(idx)
    pos = idx + 1
print(f"</body> positions: {body_positions}")

print(f"Final size: {len(html):,} bytes")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ All done!")
