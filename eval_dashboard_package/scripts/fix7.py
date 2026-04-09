#!/usr/bin/env python3
"""
fix7.py - Move the 数据看板/案例探查 sub-tab nav from the top
to between 题量分布 and 评估指标.

Current structure:
  <div class="llm-header">...</div>
  <div class="llm-top-nav" id="llmTopNav">数据看板 | 案例探查</div>
  <div id="llmTabCharts" class="llm-tab-panel active">
    <div class="llm-section">
      评分维度 filters
      回复字数概览
      题量分布 + llmVolume
      评估指标 + llmMetrics
      llmCharts
    </div>
  </div><!-- end llmTabCharts -->
  <div id="llmTabCases" class="llm-tab-panel">
    案例探查
  </div><!-- end llmTabCases -->

Target structure:
  <div class="llm-header">...</div>
  <div class="llm-section">
    评分维度 filters
    回复字数概览
    题量分布 + llmVolume
    <div class="llm-top-nav" id="llmTopNav">数据看板 | 案例探查</div>
    <div id="llmTabCharts" class="llm-tab-panel active">
      评估指标 + llmMetrics
      llmCharts
    </div>
    <div id="llmTabCases" class="llm-tab-panel">
      案例探查
    </div><!-- end llmTabCases -->
  </div>
"""
import re

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTML size: {len(html)} bytes")

# Strategy: Work within the proj2 section
proj2_start = html.find('id="proj2"')
proj2_end = html.find('</div><!-- end proj2 -->')

# Step 1: Remove the top-nav from its current position
old_nav_block = '''<div class="llm-top-nav" id="llmTopNav">
<div class="llm-top-nav-item active" data-tab="llmTabCharts">\u6570\u636e\u770b\u677f</div>
<div class="llm-top-nav-item" data-tab="llmTabCases">\u6848\u4f8b\u63a2\u67e5</div>
</div>
<div id="llmTabCharts" class="llm-tab-panel active">
'''
if old_nav_block in html:
    html = html.replace(old_nav_block, '', 1)
    print("Step 1: Removed old top-nav + llmTabCharts wrapper opening")
else:
    print("ERROR: Cannot find old nav block")
    exit(1)

# Step 2: Remove the llmTabCharts closing + llmTabCases opening
old_transition = '</div>\n</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n'
if old_transition in html:
    html = html.replace(old_transition, '', 1)
    print("Step 2: Removed old llmTabCharts close + llmTabCases open")
else:
    print("ERROR: Cannot find old transition block")
    # Try without leading </div>
    old_transition2 = '</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n'
    if old_transition2 in html:
        html = html.replace(old_transition2, '', 1)
        print("Step 2: Removed old transition (variant)")
    else:
        print("ERROR: Cannot find transition at all!")
        exit(1)

# Step 3: Remove the llmTabCases closing
old_cases_close = '</div><!-- end llmTabCases -->\n'
if old_cases_close in html:
    html = html.replace(old_cases_close, '', 1)
    print("Step 3: Removed old llmTabCases close")
else:
    print("WARNING: llmTabCases close not found")

# Now the structure should be:
#   <div class="llm-section">
#     filters + 回复字数 + 题量分布 + llmVolume
#     评估指标 + llmMetrics + llmCharts
#   </div>
#   <div class="llm-case-section">...</div>

# Step 4: Insert nav + tab wrappers between llmVolume and 评估指标
# Find the insertion point: after <div id="llmVolume"></div>
volume_marker = '<div id="llmVolume"></div>'
volume_idx = html.find(volume_marker)
if volume_idx < 0:
    print("ERROR: Cannot find llmVolume")
    exit(1)
insert_point = volume_idx + len(volume_marker)

# Find where 评估指标 section starts
metrics_marker = '<!-- Metrics cards -->\n<div class="llm-section-title">\u8bc4\u4f30\u6307\u6807</div>'
metrics_idx = html.find(metrics_marker, insert_point)
if metrics_idx < 0:
    # Try simpler
    metrics_marker = '<div class="llm-section-title">\u8bc4\u4f30\u6307\u6807</div>'
    metrics_idx = html.find(metrics_marker, insert_point)
if metrics_idx < 0:
    print("ERROR: Cannot find 评估指标")
    exit(1)

# Find where </div> closes llm-section (before llm-case-section)
case_section_marker = '<div class="llm-case-section" id="llm-case-section">'
case_section_idx = html.find(case_section_marker, metrics_idx)
if case_section_idx < 0:
    print("ERROR: Cannot find llm-case-section")
    exit(1)

# The </div> just before case_section closes the llm-section
# We need to find it
pre_case = html[metrics_idx:case_section_idx]
# The structure between metrics and case_section should be:
# llmMetrics + llmCharts + </div> (closing llm-section)
# We need to wrap llmMetrics + llmCharts in llmTabCharts,
# and wrap llm-case-section in llmTabCases

# Find the </div> that closes llm-section
# It's the last </div> before case_section_marker
last_close_idx = html.rfind('</div>', metrics_idx, case_section_idx)
if last_close_idx < 0:
    print("ERROR: Cannot find llm-section close")
    exit(1)

# Build the new structure
nav_html = '''
<div class="llm-top-nav" id="llmTopNav">
<div class="llm-top-nav-item active" data-tab="llmTabCharts">\u6570\u636e\u770b\u677f</div>
<div class="llm-top-nav-item" data-tab="llmTabCases">\u6848\u4f8b\u63a2\u67e5</div>
</div>
<div id="llmTabCharts" class="llm-tab-panel active">
'''

# Insert nav + llmTabCharts open before the metrics section
html = html[:metrics_idx] + nav_html + html[metrics_idx:]
print(f"Step 4: Inserted nav + llmTabCharts at offset {metrics_idx}")

# Now we need to:
# - Close llmTabCharts after llm-section closes (</div> before case section)
# - Open llmTabCases before case section
# - Close llmTabCases before </div><!-- end proj2 -->

# Re-find positions since we inserted content
case_section_idx2 = html.find(case_section_marker)
# Find the </div> just before case_section (closing llm-section)
last_close_idx2 = html.rfind('</div>', 0, case_section_idx2)
# After that </div>, insert close llmTabCharts + open llmTabCases
after_section_close = last_close_idx2 + len('</div>')

transition_html = '\n</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n'
html = html[:after_section_close] + transition_html + html[after_section_close:]
print(f"Step 5: Inserted llmTabCharts close + llmTabCases open at {after_section_close}")

# Close llmTabCases before </div><!-- end proj2 -->
end_proj2 = html.find('</div><!-- end proj2 -->')
html = html[:end_proj2] + '</div><!-- end llmTabCases -->\n' + html[end_proj2:]
print(f"Step 6: Inserted llmTabCases close before end proj2")

# Step 7: The llm-case-section is now inside llmTabCases but also inside llm-section's </div>
# Wait - let me check. After step 4, the structure is:
# <div class="llm-section">
#   filters + volume
#   <nav>
#   <div llmTabCharts>
#     metrics + charts
#   </div><!-- llm-section close -->
# </div><!-- end llmTabCharts -->
# <div llmTabCases>
#   <div llm-case-section>...</div>
# </div><!-- end llmTabCases -->
# </div><!-- end proj2 -->

# Hmm, the </div> that closes llm-section is now INSIDE llmTabCharts.
# That means llmTabCharts also includes that </div>.
# And llmTabCases is OUTSIDE llm-section.
# This should be fine because:
# - llm-section wraps: filters, volume, nav, llmTabCharts(metrics+charts)
# - llmTabCases is a sibling at proj2 level
# The CSS `#proj2 .llm-tab-panel{display:none}` and 
# `#proj2 .llm-tab-panel.active{display:block}` should work.

# Actually wait, there's a problem. The llm-section </div> is inside llmTabCharts.
# When llmTabCharts is hidden, the llm-section won't close properly.
# Let me restructure this differently.

# Better approach: close llm-section BEFORE the nav, then the tab panels are siblings.
# Let me rethink...

# Actually, the simplest fix is:
# 1. Close llm-section AFTER llmVolume (before the nav)
# 2. The nav + both tab panels sit at proj2 level
# 3. llmTabCharts contains metrics + charts (without the llm-section wrapper)
# 4. llmTabCases contains the case section

# Let me redo this. First let me check if the current state has issues.
# Actually, re-reading the structure:
# <div class="llm-section">  ← opens
#   ...filters + volume...
#   <nav>
#   <div llmTabCharts>
#     <!-- Metrics cards -->...
#     ...llmCharts...
#   </div> ← this closes llm-section (the original </div> from the HTML)
# </div><!-- end llmTabCharts -->  ← this closes llmTabCharts
# 
# Wait no, that's wrong. Let me count the divs more carefully.
# The original structure after my edits in steps 1-3 was:
# <div class="llm-section">
#   ...filters...volume...
#   ...metrics...charts...
# </div>   ← closes llm-section
# <div class="llm-case-section">...</div>
#
# Then in step 4, I inserted before metrics:
# <nav>
# <div llmTabCharts>
#
# So now:
# <div class="llm-section">
#   ...filters...volume...
#   <nav>
#   <div llmTabCharts>
#   ...metrics...charts...
# </div>   ← this was the llm-section close, but now it closes llmTabCharts!
# <div class="llm-case-section">...</div>
#
# Then step 5 inserted after that </div>:
# </div><!-- end llmTabCharts -->  ← but this doesn't have a matching open!
# <div llmTabCases>
#
# This is broken. Let me fix the div nesting.

print("\n--- Fixing div nesting ---")
# The issue is that I need to properly close llm-section before the nav,
# and the llmTabCharts/llmTabCases should be at the same level.

# Let me rewrite from scratch with the correct approach.
# Re-read the current HTML
with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Re-read HTML: {len(html)} bytes")

# APPROACH: Clean slate. Remove ALL my previous tab changes, then redo correctly.

# 1. Remove the nav
nav_block_new = '''
<div class="llm-top-nav" id="llmTopNav">
<div class="llm-top-nav-item active" data-tab="llmTabCharts">\u6570\u636e\u770b\u677f</div>
<div class="llm-top-nav-item" data-tab="llmTabCases">\u6848\u4f8b\u63a2\u67e5</div>
</div>
<div id="llmTabCharts" class="llm-tab-panel active">
'''
html = html.replace(nav_block_new, '', 1)

# 2. Remove transition
for t in [
    '</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n',
    '\n</div><!-- end llmTabCharts -->\n<div id="llmTabCases" class="llm-tab-panel">\n',
]:
    if t in html:
        html = html.replace(t, '', 1)
        break

# 3. Remove cases close
html = html.replace('</div><!-- end llmTabCases -->\n', '', 1)

print("Cleaned up previous tab changes")

# Now verify structure is clean
proj2_start = html.find('id="proj2"')
proj2_end_marker = '</div><!-- end proj2 -->'
proj2_end = html.find(proj2_end_marker)
proj2 = html[proj2_start:proj2_end]

vol_off = proj2.find('llmVolume')
met_off = proj2.find('\u8bc4\u4f30\u6307\u6807')
chart_off = proj2.find('llmCharts')
case_off = proj2.find('llm-case-section')
print(f"llmVolume: {vol_off}, 评估指标: {met_off}, llmCharts: {chart_off}, case-section: {case_off}")

# The clean structure should be:
# <div id="proj2">
#   <div class="llm-header">...</div>
#   <div class="llm-section">
#     filters + 回复字数 + 题量分布 + llmVolume
#     评估指标 + llmMetrics + llmCharts
#   </div>
#   <div class="llm-case-section" id="llm-case-section">...</div>
# </div><!-- end proj2 -->

# NEW APPROACH:
# Insert </div> to close llm-section after llmVolume
# Then insert: nav + llmTabCharts wrapper around (metrics + charts section)
# Then insert: llmTabCases wrapper around case section

# Find exact positions
abs_proj2_start = proj2_start
volume_end = html.find('<div id="llmVolume"></div>', abs_proj2_start) + len('<div id="llmVolume"></div>')

# What comes between llmVolume and 评估指标?
between = html[volume_end:html.find('<div class="llm-section-title">\u8bc4\u4f30\u6307\u6807</div>', volume_end)]
print(f"Between volume and metrics: {repr(between)}")

metrics_start = html.find('<!-- Metrics cards -->', volume_end)
if metrics_start < 0:
    metrics_start = html.find('<div class="llm-section-title">\u8bc4\u4f30\u6307\u6807</div>', volume_end)

# Find end of llm-section (</div> before llm-case-section)
case_section_abs = html.find('<div class="llm-case-section"', metrics_start)
# The </div> closing llm-section is between llmCharts and case_section
section_close_idx = html.rfind('</div>', metrics_start, case_section_abs)

print(f"volume_end={volume_end}, metrics_start={metrics_start}, section_close={section_close_idx}, case_section={case_section_abs}")

# The content between metrics_start and section_close_idx+6 is:
# <!-- Metrics cards -->
# <div class="llm-section-title">评估指标</div>
# <div id="llmMetrics" class="llm-card-grid"></div>
# <!-- Bar charts -->
# <div id="llmCharts"></div>
# </div>   ← this closes llm-section

# I need to:
# 1. Close llm-section right after llmVolume
# 2. Insert nav
# 3. Wrap metrics+charts in llmTabCharts (without the llm-section wrapper)
# 4. Wrap case-section in llmTabCases

# Extract the metrics+charts content (without the closing </div> of llm-section)
charts_content = html[metrics_start:section_close_idx]  # does NOT include the </div>
print(f"Charts content length: {len(charts_content)}")
print(f"Charts content start: {repr(charts_content[:200])}")

# Build new HTML to replace from volume_end to case_section_abs
# Old: ...llmVolume</div>\n\n<!-- Metrics cards -->...llmCharts</div>\n\n</div>\n<div class="llm-case-section"...
# New: ...llmVolume</div>\n</div><!-- close llm-section -->\n<nav>\n<div llmTabCharts>\nchart_content\n</div>\n<div llmTabCases>\n<div class="llm-case-section"...

new_html = (
    '\n</div><!-- close llm-section for always-visible part -->\n'
    '<div class="llm-top-nav" id="llmTopNav">\n'
    '<div class="llm-top-nav-item active" data-tab="llmTabCharts">\u6570\u636e\u770b\u677f</div>\n'
    '<div class="llm-top-nav-item" data-tab="llmTabCases">\u6848\u4f8b\u63a2\u67e5</div>\n'
    '</div>\n'
    '<div id="llmTabCharts" class="llm-tab-panel active">\n'
    + charts_content + '\n'
    '</div><!-- end llmTabCharts -->\n'
    '<div id="llmTabCases" class="llm-tab-panel">\n'
)

# Replace from volume_end to case_section_abs
# The old content is: html[volume_end : case_section_abs]
# which includes the metrics+charts + closing </div> of llm-section
old_segment = html[volume_end:case_section_abs]
html = html[:volume_end] + new_html + html[case_section_abs:]

print(f"Replaced segment ({len(old_segment)} chars) with new structure ({len(new_html)} chars)")

# Add llmTabCases close before </div><!-- end proj2 -->
end_proj2 = html.find('</div><!-- end proj2 -->')
html = html[:end_proj2] + '</div><!-- end llmTabCases -->\n' + html[end_proj2:]
print("Added llmTabCases close")

# Verify final structure
proj2_start_new = html.find('id="proj2"')
proj2_end_new = html.find('</div><!-- end proj2 -->')
proj2_new = html[proj2_start_new:proj2_end_new]

print("\n--- Final structure verification ---")
for kw in ['llm-section', 'llmVolume', 'llmTopNav', 'llmTabCharts', '\u8bc4\u4f30\u6307\u6807', 'llmCharts', 'end llmTabCharts', 'llmTabCases', 'llm-case-section', 'end llmTabCases']:
    idx = proj2_new.find(kw)
    print(f"  {kw}: offset {idx}")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nSaved. Size: {len(html)} bytes")
