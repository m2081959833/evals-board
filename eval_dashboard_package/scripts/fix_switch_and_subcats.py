#!/usr/bin/env python3
"""
Fix:
1. switchProject must re-render LLM charts when switching to proj2 (Chart.js hidden canvas issue)
2. Case explorer: use subcategory as primary filter (二级分类)
"""

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: Add renderLlmDashboard() call in switchProject when target is proj2
old_switch = """function switchProject(el) {
  var tabs = document.querySelectorAll('.project-tab');
  var panels = document.querySelectorAll('.project-panel');
  for (var i = 0; i < tabs.length; i++) tabs[i].className = 'project-tab';
  for (var i = 0; i < panels.length; i++) panels[i].className = 'project-panel';
  el.className = 'project-tab active';
  var target = el.getAttribute('data-project');
  document.getElementById(target).className = 'project-panel active';
}"""

new_switch = """function switchProject(el) {
  var tabs = document.querySelectorAll('.project-tab');
  var panels = document.querySelectorAll('.project-panel');
  for (var i = 0; i < tabs.length; i++) tabs[i].className = 'project-tab';
  for (var i = 0; i < panels.length; i++) panels[i].className = 'project-panel';
  el.className = 'project-tab active';
  var target = el.getAttribute('data-project');
  document.getElementById(target).className = 'project-panel active';
  if (target === 'proj2' && typeof renderLlmDashboard === 'function') {
    setTimeout(function() { renderLlmDashboard(); }, 50);
  }
}"""

assert old_switch in html, "switchProject not found!"
html = html.replace(old_switch, new_switch, 1)
print("✓ switchProject updated - re-renders charts on proj2 switch")

# Fix 2: Change case explorer category filter to use subcategory (二级分类) as primary
# Currently the dropdown uses c.cat (一级分类: 知识/写作/语言/闲聊/未分类)
# User wants subcategory (二级分类: 知识问答-人文社科, 创作-学生作文, etc.) as the primary filter tabs

# The case section HTML already has the sub-tabs area. Let me update the JS init
# to build subcategory tabs instead of just sub-tabs under a category.

# Replace the init section of case explorer JS
old_init = """/* Init */
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
})();"""

new_init = """/* Init */
(function() {
  var origOnload = window.onload;
  window.onload = function() {
    if (origOnload) origOnload();
    /* Build category dropdown (一级分类) */
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
    llmBuildSubTabs();
    llmRenderCases();
  };
})();"""

assert old_init in html, "Old init not found!"
html = html.replace(old_init, new_init, 1)
print("✓ Init updated - builds sub-tabs on load")

# Update llmBuildSubTabs to show ALL subcategories when no category is selected
old_build_sub = """function llmBuildSubTabs() {
  var el = document.getElementById("llm-case-sub-tabs");
  if (!el) return;
  var cat = llmCaseState.catFilter;
  if (!cat) { el.innerHTML = ""; return; }
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (LLM_CASES[i].cat === cat && LLM_CASES[i].sub) {
      subMap[LLM_CASES[i].sub] = (subMap[LLM_CASES[i].sub] || 0) + 1;
    }
  }"""

new_build_sub = """function llmBuildSubTabs() {
  var el = document.getElementById("llm-case-sub-tabs");
  if (!el) return;
  var cat = llmCaseState.catFilter;
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (cat && LLM_CASES[i].cat !== cat) continue;
    if (LLM_CASES[i].sub) {
      subMap[LLM_CASES[i].sub] = (subMap[LLM_CASES[i].sub] || 0) + 1;
    }
  }"""

assert old_build_sub in html, "Old llmBuildSubTabs not found!"
html = html.replace(old_build_sub, new_build_sub, 1)
print("✓ llmBuildSubTabs updated - shows all subcategories when no category selected")

# Verify
import re
start = html.index('function switchProject')
end = html.index('\n}', start) + 2
# Get next few lines to verify setTimeout
snippet = html[start:start+500]
assert 'setTimeout' in snippet, "setTimeout not in switchProject!"
assert 'renderLlmDashboard' in snippet, "renderLlmDashboard not in switchProject!"

# Check brace balance in main script block
main_start = html.index('/* === Project Tab Switching === */')
main_end = html.index('</script>', main_start)
main_js = html[main_start:main_end]
opens = main_js.count('{')
closes = main_js.count('}')
print(f"Main JS braces: {opens} opens, {closes} closes")
assert opens == closes, f"BRACE MISMATCH!"

print(f"Final size: {len(html):,} bytes")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ All done!")
