#!/usr/bin/env python3
"""
fix6.py - Split LLM竞品评估 (proj2) into two sub-tabs:
  数据看板 | 案例探查
Matching the same design as Tab1 (三月流式竞对).
"""
import re

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTML size: {len(html)} bytes")

# ============================================================
# STEP 1: Add CSS for proj2 sub-tabs
# ============================================================
# Use scoped class names to avoid conflict with Tab1
subtab_css = """
/* proj2 sub-tab nav */
#proj2 .llm-top-nav{display:flex;gap:12px;margin-bottom:16px;border-bottom:2px solid #e5e6eb;padding-bottom:0}
#proj2 .llm-top-nav-item{padding:8px 18px;cursor:pointer;font-size:14px;font-weight:500;color:#4e5969;border-bottom:2px solid transparent;margin-bottom:-2px;transition:.2s}
#proj2 .llm-top-nav-item.active{color:#165dff;border-bottom-color:#165dff}
#proj2 .llm-top-nav-item:hover{color:#165dff}
#proj2 .llm-tab-panel{display:none}
#proj2 .llm-tab-panel.active{display:block}"""

# Insert into <head> style - find the score-note CSS we added previously
anchor = '.llm-score-note .note-row:last-child{margin-bottom:0}'
if anchor in html:
    html = html.replace(anchor, anchor + subtab_css)
    print("STEP 1: Added sub-tab CSS")
else:
    print("ERROR: Cannot find CSS anchor")
    exit(1)

# ============================================================
# STEP 2: Add top-nav HTML and wrap content in tab panels
# ============================================================
# The current structure is:
#   <div class="llm-header">...</div>
#   <div class="llm-section">
#     ... filter rows, charts, metrics ...
#   </div>
#   <div class="llm-case-section" id="llm-case-section">
#     ... case explorer ...
#   </div>
#   </div><!-- end proj2 -->
#
# Target structure:
#   <div class="llm-header">...</div>
#   <div class="llm-top-nav" id="llmTopNav">
#     <div class="llm-top-nav-item active" data-tab="llmTabCharts">数据看板</div>
#     <div class="llm-top-nav-item" data-tab="llmTabCases">案例探查</div>
#   </div>
#   <div id="llmTabCharts" class="llm-tab-panel active">
#     <div class="llm-section">...</div>
#   </div>
#   <div id="llmTabCases" class="llm-tab-panel">
#     <div class="llm-case-section" id="llm-case-section">...</div>
#   </div>
#   </div><!-- end proj2 -->

# Find the llm-header closing and llm-section opening
header_end = '</div>\n</div>\n<div class="llm-section">'
# More flexible search
proj2_start = html.find('id="proj2"')
proj2_chunk = html[proj2_start:proj2_start+2000]

# Find </div> of llm-sub, then </div> of llm-header, then <div class="llm-section">
llm_section_offset = proj2_chunk.find('<div class="llm-section">')
if llm_section_offset < 0:
    print("ERROR: Cannot find llm-section")
    exit(1)

# Insert top-nav before llm-section, and wrap llm-section in tab panel
abs_section_start = proj2_start + llm_section_offset

top_nav_html = '''<div class="llm-top-nav" id="llmTopNav">
<div class="llm-top-nav-item active" data-tab="llmTabCharts">\u6570\u636e\u770b\u677f</div>
<div class="llm-top-nav-item" data-tab="llmTabCases">\u6848\u4f8b\u63a2\u67e5</div>
</div>
<div id="llmTabCharts" class="llm-tab-panel active">
'''

html = html[:abs_section_start] + top_nav_html + html[abs_section_start:]
print(f"STEP 2a: Inserted top-nav + llmTabCharts wrapper at offset {abs_section_start}")

# Now find the </div> that closes llm-section and add closing </div> for llmTabCharts,
# then wrap llm-case-section in llmTabCases
# After our insertion, find llm-case-section
case_section_start = html.find('<div class="llm-case-section" id="llm-case-section">')
if case_section_start < 0:
    print("ERROR: Cannot find llm-case-section")
    exit(1)

# The </div> before llm-case-section closes llm-section. 
# We need to close llmTabCharts panel after llm-section closes, 
# then open llmTabCases before llm-case-section

# Find the </div> just before the case section
# Look backwards from case_section_start for </div>
pre_case = html[case_section_start-200:case_section_start]
last_close_div = pre_case.rfind('</div>')
if last_close_div >= 0:
    abs_close = case_section_start - 200 + last_close_div + len('</div>')
    # Insert: close llmTabCharts + open llmTabCases
    insert_html = '\n</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n'
    html = html[:abs_close] + insert_html + html[abs_close:]
    print(f"STEP 2b: Inserted llmTabCharts close + llmTabCases open at offset {abs_close}")
else:
    print("ERROR: Cannot find closing </div> before case section")
    exit(1)

# Now find end of llm-case-section (which is </div><!-- end proj2 -->)
end_proj2 = html.find('</div><!-- end proj2 -->')
if end_proj2 < 0:
    print("ERROR: Cannot find end proj2 marker")
    exit(1)

# Insert </div> to close llmTabCases before </div><!-- end proj2 -->
html = html[:end_proj2] + '</div><!-- end llmTabCases -->\n' + html[end_proj2:]
print(f"STEP 2c: Inserted llmTabCases close before end proj2")

# ============================================================
# STEP 3: Remove the old section titles that are now redundant
# ============================================================
# Remove the "数据看板" section title inside the charts area (it's now in the nav tab)
# The <div class="llm-section-title">数据看板</div> should be removed
html = html.replace('<div class="llm-section-title">\u6570\u636e\u770b\u677f</div>', '', 1)
print("STEP 3a: Removed redundant '数据看板' section title")

# Remove the <h2>Case 探查</h2> inside case section (now in nav tab)
html = html.replace('<h2>Case \u63a2\u67e5</h2>', '', 1)
print("STEP 3b: Removed redundant 'Case 探查' heading")

# ============================================================
# STEP 4: Add JS to handle sub-tab switching
# ============================================================
# Find where the existing llm JS code starts (after SheetJS, in the rendering block)
# We need to add click handlers for the llm top nav
# Find switchProject function or the end of the LLM rendering code

nav_js = """
/* proj2 sub-tab switching */
var llmNavItems = document.querySelectorAll('#llmTopNav .llm-top-nav-item');
for (var ni = 0; ni < llmNavItems.length; ni++) {
  (function(el) {
    el.onclick = function() {
      for (var j = 0; j < llmNavItems.length; j++) llmNavItems[j].classList.remove('active');
      var panels = document.querySelectorAll('#proj2 .llm-tab-panel');
      for (var j = 0; j < panels.length; j++) panels[j].classList.remove('active');
      el.classList.add('active');
      var target = document.getElementById(el.getAttribute('data-tab'));
      if (target) target.classList.add('active');
      /* Re-render charts if switching to charts tab (Chart.js hidden container issue) */
      if (el.getAttribute('data-tab') === 'llmTabCharts') {
        setTimeout(function() { if (typeof renderLlmCharts === 'function') renderLlmCharts(); }, 100);
      }
      /* Re-render cases if switching to cases tab */
      if (el.getAttribute('data-tab') === 'llmTabCases') {
        setTimeout(function() { if (typeof llmRenderCases === 'function') llmRenderCases(); }, 100);
      }
    };
  })(llmNavItems[ni]);
}
"""

# Find a good place to insert - after llmBuildSubTabs is called initially
# Look for the initial call to build sub tabs or render
init_call = 'llmBuildSubTabs();'
init_idx = html.rfind(init_call)
if init_idx > 0:
    # Insert after the line
    insert_after = init_idx + len(init_call)
    html = html[:insert_after] + '\n' + nav_js + html[insert_after:]
    print(f"STEP 4: Added sub-tab switching JS after llmBuildSubTabs()")
else:
    print("WARNING: Could not find llmBuildSubTabs() init call")
    # Fallback: insert before </body>
    body_end = html.rfind('</body>')
    html = html[:body_end] + '<script>' + nav_js + '</script>\n' + html[body_end:]
    print("STEP 4: Added sub-tab switching JS (fallback before </body>)")

# ============================================================
# STEP 5: Update switchProject to handle sub-tab visibility
# ============================================================
# When switching to proj2, the charts need to re-render since they may be in a hidden tab
# The existing switchProject already calls renderLlmCharts with setTimeout
# This should work fine since llmTabCharts is active by default

# Save
with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nSaved. New size: {len(html)} bytes")
