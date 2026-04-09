#!/usr/bin/env python3
"""
Fix v3:
1. Move llm-charts-grid CSS to <head>
2. Replace case filter UI with 一级标签/二级标签 tab switcher
3. Update JS for tag level switching
"""
import re

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('new_tag_js.js', 'r', encoding='utf-8') as f:
    new_tag_js = f.read()

print(f"Original size: {len(html):,} bytes")

# =====================================================
# Fix 1: Move chart grid CSS into the FIRST <style> block
# =====================================================

# Remove ALL existing chart grid CSS lines
css_lines = [
    '.llm-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}',
    '.llm-chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #e5e6eb}',
    '.llm-chart-card .chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}',
    '.llm-chart-card .chart-subtitle{font-size:12px;color:#86909c;margin-bottom:10px}',
    '.llm-chart-card .chart-wrap{position:relative;height:240px}',
    '.llm-chart-card .legend-note{font-size:11px;color:#86909c;text-align:center;margin-top:6px}',
    '@media(max-width:900px){.llm-charts-grid{grid-template-columns:repeat(2,1fr)}}',
    '@media(max-width:600px){.llm-charts-grid{grid-template-columns:1fr}}',
]
for line in css_lines:
    cnt = html.count(line)
    if cnt:
        html = html.replace(line, '')
        print(f"  Removed {cnt}x: {line[:50]}...")

# Inject fresh CSS into first <style> block
first_style_end = html.find('</style>')
inject_css = '\n/* === Chart Grid (fix3) === */\n' + '\n'.join(css_lines) + '\n'
inject_css += '/* === Tag Level Buttons === */\n'
inject_css += '.llm-case-tag-level{display:flex;gap:0;margin-bottom:10px}\n'
inject_css += '.llm-tag-level-btn{padding:6px 18px;font-size:13px;font-weight:500;cursor:pointer;border:1px solid #d0d5dd;background:#fff;color:#4e5969;transition:all .15s}\n'
inject_css += '.llm-tag-level-btn:first-child{border-radius:6px 0 0 6px}\n'
inject_css += '.llm-tag-level-btn:last-child{border-radius:0 6px 6px 0;border-left:none}\n'
inject_css += '.llm-tag-level-btn.active{background:#165dff;color:#fff;border-color:#165dff}\n'

html = html[:first_style_end] + inject_css + html[first_style_end:]
print(f"[OK] Injected CSS into <head> <style> block")

# =====================================================
# Fix 2: Replace case filter HTML
# =====================================================

# Remove the cat-filter <select>
cat_pat = re.compile(r'<select\s+id="llm-case-cat-filter"[^>]*>.*?</select>\s*', re.DOTALL)
m = cat_pat.search(html)
if m:
    html = html[:m.start()] + html[m.end():]
    print(f"[OK] Removed cat-filter select ({m.end()-m.start()} chars)")
else:
    print("[WARN] cat-filter select not found")

# Insert tag level buttons before sub-tabs div
sub_marker = '<div class="llm-case-sub-tabs" id="llm-case-sub-tabs"></div>'
tag_btns = '''<div class="llm-case-tag-level">
    <button class="llm-tag-level-btn active" onclick="llmSwitchTagLevel(this,1)">一级标签</button>
    <button class="llm-tag-level-btn" onclick="llmSwitchTagLevel(this,2)">二级标签</button>
  </div>
  '''
if sub_marker in html:
    html = html.replace(sub_marker, tag_btns + sub_marker, 1)
    print("[OK] Inserted tag level buttons")
else:
    print("[WARN] sub-tabs marker not found")

# =====================================================
# Fix 3: Replace JS functions
# =====================================================

# Find llmBuildSubTabs function start
build_start = html.find('function llmBuildSubTabs() {')
if build_start < 0:
    print("[ERR] llmBuildSubTabs not found!")
    exit(1)

# Find llmSetSub function
setsub_start = html.find('function llmSetSub(el, sub) {')
if setsub_start < 0:
    print("[ERR] llmSetSub not found!")
    exit(1)

# Find end of llmSetSub - match braces
depth = 0
in_func = False
setsub_end = setsub_start
for i in range(setsub_start, min(setsub_start + 2000, len(html))):
    c = html[i]
    if c == '{':
        depth += 1
        in_func = True
    elif c == '}':
        depth -= 1
        if in_func and depth == 0:
            setsub_end = i + 1
            break

old_js = html[build_start:setsub_end]
print(f"  Old JS block: {len(old_js)} chars (pos {build_start}..{setsub_end})")

html = html[:build_start] + new_tag_js + html[setsub_end:]
print("[OK] Replaced JS functions with new tag-level code")

# =====================================================
# Fix 4: Simplify init code (remove cat dropdown builder)
# =====================================================

cat_init_marker = '/* Build category dropdown'
pos = html.find(cat_init_marker)
if pos > 0:
    end_marker = 'llmBuildSubTabs();'
    end_pos = html.find(end_marker, pos)
    if end_pos > 0:
        end_pos += len(end_marker)
        html = html[:pos] + '/* Build tag pills */\n    llmBuildSubTabs();' + html[end_pos:]
        print("[OK] Simplified init code")
else:
    print("[WARN] Cat init already simplified")

# =====================================================
# Verification
# =====================================================
print(f"\nFinal size: {len(html):,} bytes")

css_pos = html.find('.llm-charts-grid{')
first_body = html.find('</body>')
last_body = html.rfind('</body>')
print(f"Chart CSS at: {css_pos}")
print(f"First </body> at: {first_body}")
print(f"Last </body> at: {last_body}")
print(f"CSS before </body>: {css_pos < first_body}")

if css_pos >= first_body:
    print("[FAIL] CSS still after </body>!")
    exit(1)

# Verify new functions exist
for fn in ['llmSwitchTagLevel', 'llmBuildSubTabs', 'llmSetTag']:
    if fn in html:
        print(f"  [OK] {fn} found")
    else:
        print(f"  [FAIL] {fn} missing!")

# Verify old function removed
if 'llmSetSub' in html:
    print("  [WARN] llmSetSub still present!")
else:
    print("  [OK] llmSetSub removed")

# Brace balance check in script blocks
scripts = re.findall(r'<script[\s>](.*?)</script>', html, re.DOTALL)
print(f"\nScript blocks found: {len(scripts)}")
for i, s in enumerate(scripts):
    opens = s.count('{')
    closes = s.count('}')
    if opens != closes:
        print(f"  Block {i}: open={opens} close={closes} diff={opens-closes}")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\n[DONE] Saved viz_final_v10_full.html")
