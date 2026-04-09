#!/usr/bin/env python3
"""Fix chart visibility + subcategory filters."""

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: switchProject - re-render charts when switching to proj2
old_sp = "document.getElementById(target).className = 'project-panel active';\n}"
new_sp = """document.getElementById(target).className = 'project-panel active';
  if (target === 'proj2' && typeof renderLlmDashboard === 'function') {
    setTimeout(function() { renderLlmDashboard(); }, 50);
  }
}"""
c = html.count(old_sp)
print(f"switchProject pattern found: {c}")
html = html.replace(old_sp, new_sp, 1)

# Fix 2: llmBuildSubTabs - show all subcategories when no category filter
old_sub = """  var cat = llmCaseState.catFilter;
  if (!cat) { el.innerHTML = ""; return; }
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (LLM_CASES[i].cat === cat && LLM_CASES[i].sub) {
      subMap[LLM_CASES[i].sub] = (subMap[LLM_CASES[i].sub] || 0) + 1;
    }
  }"""

new_sub = """  var cat = llmCaseState.catFilter;
  var subMap = {};
  for (var i = 0; i < LLM_CASES.length; i++) {
    if (cat && LLM_CASES[i].cat !== cat) continue;
    if (LLM_CASES[i].sub) {
      subMap[LLM_CASES[i].sub] = (subMap[LLM_CASES[i].sub] || 0) + 1;
    }
  }"""

c = html.count(old_sub)
print(f"llmBuildSubTabs pattern found: {c}")
html = html.replace(old_sub, new_sub, 1)

# Fix 3: Init - call llmBuildSubTabs on load
old_init_end = """    llmRenderCases();
  };
})();"""
new_init_end = """    llmBuildSubTabs();
    llmRenderCases();
  };
})();"""
# Only replace the LAST occurrence (in the case explorer script)
rpos = html.rfind(old_init_end)
if rpos >= 0:
    html = html[:rpos] + new_init_end + html[rpos + len(old_init_end):]
    print("Init fix applied")

# Verify
assert 'setTimeout' in html[html.index('function switchProject'):html.index('function switchProject')+600], "switchProject fix failed"
print("✓ All fixes applied")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Size: {len(html):,} bytes")
