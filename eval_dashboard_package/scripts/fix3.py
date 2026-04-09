#!/usr/bin/env python3
"""
Fix:
1. Move llm-charts-grid CSS to <head> so it's properly applied
2. Replace case filter UI with "一级标签"/"二级标签" tab switcher
"""

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# =====================================================
# Fix 1: Move chart grid CSS into the FIRST <style> block (in <head>)
# =====================================================

# Remove the existing llm-charts-grid CSS from its current location
chart_grid_css_block = """
.llm-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.llm-chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #e5e6eb}
.llm-chart-card .chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}
.llm-chart-card .chart-subtitle{font-size:12px;color:#86909c;margin-bottom:10px}
.llm-chart-card .chart-wrap{position:relative;height:240px}
.llm-chart-card .legend-note{font-size:11px;color:#86909c;text-align:center;margin-top:6px}
@media(max-width:900px){.llm-charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.llm-charts-grid{grid-template-columns:1fr}}
"""

if chart_grid_css_block in html:
    html = html.replace(chart_grid_css_block, '', 1)
    print("✓ Removed old chart grid CSS from post-</body> location")
else:
    # Try single line version
    for line in chart_grid_css_block.strip().split('\n'):
        line = line.strip()
        if line and line in html:
            pass  # will inject fresh copy anyway
    print("⚠ Old CSS block not found as exact match, will inject fresh copy")

# Also remove any inline duplicate
for css_line in [
    '.llm-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}',
]:
    while html.count(css_line) > 0:
        html = html.replace(css_line, '', 1)

# Now inject into the FIRST <style> block (which is in <head>)
# The first <style> starts with chart-related CSS
first_style_end = html.find('</style>')
inject_css = """\n.llm-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.llm-chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #e5e6eb}
.llm-chart-card .chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}
.llm-chart-card .chart-subtitle{font-size:12px;color:#86909c;margin-bottom:10px}
.llm-chart-card .chart-wrap{position:relative;height:240px}
.llm-chart-card .legend-note{font-size:11px;color:#86909c;text-align:center;margin-top:6px}
@media(max-width:900px){.llm-charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.llm-charts-grid{grid-template-columns:1fr}}
"""
html = html[:first_style_end] + inject_css + html[first_style_end:]
print(f"✓ Injected chart grid CSS into first <style> block (before pos {first_style_end})")

# =====================================================
# Fix 2: Replace case filter UI - "一级标签" / "二级标签" tabs
# =====================================================

old_case_html = '''<div class="llm-case-filters">
    <select id="llm-case-cat-filter" onchange="llmCaseState.catFilter=this.value;llmCaseState.subFilter='';llmBuildSubTabs();llmFilterCases();"><option value="">全部分类</option></select>
    <select id="llm-case-model-filter" onchange="llmCaseState.modelFilter=this.value;llmFilterCases();"><option value="">全部模型</option><option value="d">豆包</option><option value="qw">千问3</option><option value="gm">Gemini 3 Pro</option><option value="gp">GPT 5.2</option></select>
    <input type="text" id="llm-case-search" placeholder="搜索 Prompt / ID / 考点..." oninput="llmCaseState.searchFilter=this.value;llmFilterCases();">
    <span class="llm-case-count" id="llm-case-count"></span>
  </div>
  <div class="llm-case-sub-tabs" id="llm-case-sub-tabs"></div>'''

new_case_html = '''<div class="llm-case-filters">
    <select id="llm-case-model-filter" onchange="llmCaseState.modelFilter=this.value;llmFilterCases();"><option value="">全部模型</option><option value="d">豆包</option><option value="qw">千问3</option><option value="gm">Gemini 3 Pro</option><option value="gp">GPT 5.2</option></select>
    <input type="text" id="llm-case-search" placeholder="搜索 Prompt / ID / 考点..." oninput="llmCaseState.searchFilter=this.value;llmFilterCases();">
    <span class="llm-case-count" id="llm-case-count"></span>
  </div>
  <div class="llm-case-tag-level">
    <button class="llm-tag-level-btn active" onclick="llmSwitchTagLevel(this,1)">一级标签</button>
    <button class="llm-tag-level-btn" onclick="llmSwitchTagLevel(this,2)">二级标签</button>
  </div>
  <div class="llm-case-sub-tabs" id="llm-case-sub-tabs"></div>'''

assert old_case_html in html, "Old case filter HTML not found!"
html = html.replace(old_case_html, new_case_html, 1)
print("✓ Case filter HTML updated - 一级/二级标签 tab switcher")

# Add CSS for tag level buttons - inject into the first <style> too
tag_level_css = """\n.llm-case-tag-level{display:flex;gap:0;margin-bottom:10px}
.llm-tag-level-btn{padding:6px 18px;font-size:13px;font-weight:500;cursor:pointer;border:1px solid #d0d5dd;background:#fff;color:#4e5969;transition:all .15s}
.llm-tag-level-btn:first-child{border-radius:6px 0 0 6px}
.llm-tag-level-btn:last-child{border-radius:0 6px 6px 0;border-left:none}
.llm-tag-level-btn.active{background:#165dff;color:#fff;border-color:#165dff}
"""
# Insert at end of first style block
first_style_end_new = html.find('</style>')
html = html[:first_style_end_new] + tag_level_css + html[first_style_end_new:]
print("✓ Tag level CSS added")

# =====================================================
# Fix 3: Update case explorer JS for tag level switching
# =====================================================

# Replace llmBuildSubTabs to support tag levels
old_build = """function llmBuildSubTabs() {
  var el = document.getElementById("llm-case-sub-tabs");
  if (!el) return;
  var cat = llmCaseState.catFilter;
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (cat && LLM_CASES[i].cat !== cat) continue;
    if (LLM_CASES[i].sub) {
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
}"""

new_build = """var llmTagLevel = 1; /* 1=一级标签, 2=二级标签 */

function llmSwitchTagLevel(btn, level) {
  llmTagLevel = level;
  var btns = btn.parentNode.querySelectorAll(".llm-tag-level-btn");
  for (var i = 0; i < btns.length; i++) btns[i].className = "llm-tag-level-btn";
  btn.className = "llm-tag-level-btn active";
  llmCaseState.catFilter = "";
  llmCaseState.subFilter = "";
  llmBuildSubTabs();
  llmFilterCases();
}

function llmBuildSubTabs() {
  var el = document.getElementById("llm-case-sub-tabs");
  if (!el) return;
  var tagMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    var tag = llmTagLevel === 1 ? LLM_CASES[i].cat : LLM_CASES[i].sub;
    if (tag) tagMap[tag] = (tagMap[tag] || 0) + 1;
  }
  var tags = Object.keys(tagMap).sort();
  if (tags.length === 0) { el.innerHTML = ""; return; }
  var currentVal = llmTagLevel === 1 ? llmCaseState.catFilter : llmCaseState.subFilter;
  var h = '<span class="llm-case-sub-tab' + (!currentVal ? ' active' : '') + '" onclick="llmSetTag(this,\\'\\')">\\u5168\\u90e8 (' + LLM_CASES.length + ')</span>';
  for (var i = 0; i < tags.length; i++) {
    var isActive = currentVal === tags[i] ? ' active' : '';
    var safeTag = tags[i].replace(/'/g, "\\\\'");
    h += '<span class="llm-case-sub-tab' + isActive + '" onclick="llmSetTag(this,\\'' + safeTag + '\\')">' + tags[i] + ' (' + tagMap[tags[i]] + ')</span>';
  }
  el.innerHTML = h;
}

function llmSetTag(el, tag) {
  if (llmTagLevel === 1) {
    llmCaseState.catFilter = tag;
    llmCaseState.subFilter = "";
  } else {
    llmCaseState.subFilter = tag;
    llmCaseState.catFilter = "";
  }
  var tabs = el.parentNode.querySelectorAll(".llm-case-sub-tab");
  for (var i = 0; i < tabs.length; i++) tabs[i].className = "llm-case-sub-tab";
  el.className = "llm-case-sub-tab active";
  llmFilterCases();
}"""

assert old_build in html, "Old llmBuildSubTabs not found!"
html = html.replace(old_build, new_build, 1)
print("✓ Tag level JS updated")

# Update filter function - catFilter and subFilter both work
old_filter = """  var cat = llmCaseState.catFilter;
  var sub = llmCaseState.subFilter;
  var search = llmCaseState.searchFilter.toLowerCase();
  var model = llmCaseState.modelFilter;
  llmCaseState.filtered = LLM_CASES.filter(function(c) {
    if (cat && c.cat !== cat) return false;
    if (sub && c.sub !== sub) return false;"""

new_filter = """  var cat = llmCaseState.catFilter;
  var sub = llmCaseState.subFilter;
  var search = llmCaseState.searchFilter.toLowerCase();
  var model = llmCaseState.modelFilter;
  llmCaseState.filtered = LLM_CASES.filter(function(c) {
    if (cat && (c.cat || '') !== cat) return false;
    if (sub && (c.sub || '') !== sub) return false;"""

html = html.replace(old_filter, new_filter, 1)
print("✓ Filter function updated")

# Remove old cat-filter dropdown init (it was building the <select>)
# The <select id="llm-case-cat-filter"> no longer exists
old_cat_init = """    /* Build category dropdown (一级分类) */
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
    /* Build subcategory tabs (二级分类) - show all initially */
    llmBuildSubTabs();"""

new_cat_init = """    /* Build tag level pills */
    llmBuildSubTabs();"""

html = html.replace(old_cat_init, new_cat_init, 1)
print("✓ Init simplified")

# Verify
print(f"\nFinal size: {len(html):,} bytes")

# Check CSS is now BEFORE first </body>
css_pos = html.find('.llm-charts-grid{')
body_pos = html.find('</body>')
print(f"Chart grid CSS at {css_pos}, first </body> at {body_pos}")
print(f"CSS before </body>: {css_pos < body_pos}")
assert css_pos < body_pos, "CSS STILL after </body>!"

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ Saved!")
