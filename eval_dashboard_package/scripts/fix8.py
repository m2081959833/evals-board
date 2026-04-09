#!/usr/bin/env python3
"""fix8.py - Constrain sub-tab nav and tab panels to match llm-section width."""

path = 'viz_final_v10_full.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# The llm-section has: max-width:1200px;padding:0 20px;margin:20px auto
# Add same constraints to .llm-top-nav and .llm-tab-panel

old_nav_css = '#proj2 .llm-top-nav{display:flex;gap:12px;margin-bottom:16px;border-bottom:2px solid #e5e6eb;padding-bottom:0}'
new_nav_css = '#proj2 .llm-top-nav{display:flex;gap:12px;margin-bottom:16px;border-bottom:2px solid #e5e6eb;padding-bottom:0;max-width:1200px;margin-left:auto;margin-right:auto;padding-left:20px;padding-right:20px}'

if old_nav_css in html:
    html = html.replace(old_nav_css, new_nav_css, 1)
    print("OK: Updated .llm-top-nav CSS with width constraints")
else:
    print("WARN: Could not find .llm-top-nav CSS to update")

old_panel_hidden = '#proj2 .llm-tab-panel{display:none}'
new_panel_hidden = '#proj2 .llm-tab-panel{display:none;max-width:1200px;margin-left:auto;margin-right:auto;padding-left:20px;padding-right:20px}'

if old_panel_hidden in html:
    html = html.replace(old_panel_hidden, new_panel_hidden, 1)
    print("OK: Updated .llm-tab-panel CSS with width constraints")
else:
    print("WARN: Could not find .llm-tab-panel CSS to update")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Done!")

# Verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

for term in ['llm-top-nav{', 'llm-tab-panel{d']:
    idx = content.find('#proj2 .' + term)
    if idx >= 0:
        end = content.find('}', idx)
        print(f"  => {content[idx:end+1]}")
