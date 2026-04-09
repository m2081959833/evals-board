#!/usr/bin/env python3
"""
Fix:
1. Case explorer: one case per page, narrower layout, more side padding (match Tab1 style)
2. Rename "指标对比图表" to "数据看板"
"""

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Original size: {len(html):,}")

# =====================================================
# Fix 1: Rename "指标对比图表" to "数据看板"
# =====================================================
count = html.count('指标对比图表')
html = html.replace('指标对比图表', '数据看板')
print(f"[OK] Replaced '指标对比图表' -> '数据看板' ({count}x)")

# =====================================================
# Fix 2: Update llmCaseState.perPage to 1
# =====================================================
old_perpage = 'perPage: 5'
new_perpage = 'perPage: 1'
if old_perpage in html:
    html = html.replace(old_perpage, new_perpage, 1)
    print("[OK] Changed perPage 5 -> 1")
else:
    # Try other values
    import re
    m = re.search(r'perPage:\s*\d+', html[html.find('llmCaseState'):])
    if m:
        old = m.group()
        print(f"Found: {old}")
        html = html.replace(old, 'perPage: 1', 1)
        print(f"[OK] Changed {old} -> perPage: 1")

# =====================================================
# Fix 3: Update case card layout - stack responses vertically instead of grid
# Change grid-template-columns from repeat(N,1fr) to repeat(2,1fr) max
# And make the case card narrower with more padding
# =====================================================

# Update CSS: make proj2 case section narrower and match Tab1 style
first_style_end = html.find('</style>')
new_css = """
/* === Case Explorer Tab1-style layout (fix4) === */
#proj2 .llm-case-explorer{max-width:1000px;margin:0 auto;padding:24px 64px}
#proj2 .llm-case-card{max-width:900px;margin:0 auto 24px auto}
#proj2 .llm-case-responses{grid-template-columns:repeat(2,1fr) !important;gap:12px}
#proj2 .llm-case-prompt{font-size:14px;line-height:1.6;padding:12px 16px;margin-bottom:16px;background:#f7f8fa;border-left:3px solid #165dff;border-radius:0 8px 8px 0}
#proj2 .llm-resp-body{max-height:300px;overflow-y:auto;font-size:13px;line-height:1.6}
#proj2 .llm-gsb-row{max-width:900px;margin:0 auto}
/* Case pager style matching Tab1 */
#proj2 .llm-case-pagination{display:flex;align-items:center;justify-content:center;gap:12px;padding:16px 0}
#proj2 .llm-case-pagination button{padding:6px 16px;border:1px solid #e5e6eb;border-radius:8px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969}
#proj2 .llm-case-pagination button:hover:not([disabled]){border-color:#165dff;color:#165dff}
#proj2 .llm-case-pagination button[disabled]{opacity:.4;cursor:not-allowed}
#proj2 .llm-case-pagination input[type=number]{width:60px;padding:4px 8px;border:1px solid #e5e6eb;border-radius:6px;font-size:13px;text-align:center}
"""

html = html[:first_style_end] + new_css + html[first_style_end:]
print("[OK] Added case layout CSS overrides")

# =====================================================
# Fix 4: Update pagination to match Tab1 style (prev/next + page input)
# Find the existing pagination rendering code and replace
# =====================================================

# Find the pagination part of llmRenderCases
pag_marker = '/* Pagination */'
pag_idx = html.find(pag_marker, html.find('function llmRenderCases'))
if pag_idx > 0:
    # Find the end of llmRenderCases function
    # From pag_marker, find the closing of the function
    depth = 0
    func_start = html.find('function llmRenderCases')
    # Count up to pag_idx to know current depth
    for i in range(func_start, pag_idx):
        if html[i] == '{': depth += 1
        elif html[i] == '}': depth -= 1
    
    # Now find end from pag_idx
    end_idx = pag_idx
    for i in range(pag_idx, min(pag_idx + 3000, len(html))):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                end_idx = i + 1
                break
    
    old_pagination = html[pag_idx:end_idx]
    print(f"  Old pagination block: {len(old_pagination)} chars")
    
    new_pagination = '''/* Pagination */
  var pagEl = document.getElementById("llm-case-pagination");
  if (!pagEl) return;
  var totalPages = Math.ceil(cases.length / llmCaseState.perPage);
  if (totalPages <= 1) { pagEl.innerHTML = ""; return; }
  var curPage = llmCaseState.page + 1;
  var ph = '<button onclick="llmCaseState.page=0;llmRenderCases()" ' + (curPage <= 1 ? 'disabled' : '') + '>&laquo;</button>';
  ph += '<button onclick="llmCaseState.page--;llmRenderCases()" ' + (curPage <= 1 ? 'disabled' : '') + '>&lsaquo; 上一条</button>';
  ph += '<span>' + curPage + ' / ' + totalPages + '</span>';
  ph += '<input type="number" min="1" max="' + totalPages + '" value="' + curPage + '" onchange="var v=parseInt(this.value);if(v>=1&&v<=' + totalPages + '){llmCaseState.page=v-1;llmRenderCases()}">';
  ph += '<button onclick="llmCaseState.page++;llmRenderCases()" ' + (curPage >= totalPages ? 'disabled' : '') + '>下一条 &rsaquo;</button>';
  ph += '<button onclick="llmCaseState.page=totalPages-1;llmRenderCases()" ' + (curPage >= totalPages ? 'disabled' : '') + '>&raquo;</button>';
  pagEl.innerHTML = ph;
}'''
    
    html = html[:pag_idx] + new_pagination + html[end_idx:]
    print("[OK] Replaced pagination with Tab1-style prev/next")
else:
    print("[WARN] Pagination marker not found")

# =====================================================
# Fix 5: Also update the section padding for the charts area
# The proj2 panel should have similar padding to Tab1
# =====================================================

# Update the charts section heading
old_heading = '<h3 style="margin:32px 0 16px;color:#1d2129">数据看板</h3>'
if old_heading not in html:
    # Try to find the original heading format
    import re
    m = re.search(r'<h3[^>]*>数据看板</h3>', html)
    if m:
        print(f"  Found heading: {m.group()}")

# =====================================================
# Verify
# =====================================================
print(f"\nFinal size: {len(html):,}")
if 'perPage: 1' in html:
    print("[OK] perPage = 1")
if '数据看板' in html:
    print("[OK] '数据看板' present")
if '指标对比图表' not in html:
    print("[OK] '指标对比图表' removed")

# Brace check
import re
scripts = re.findall(r'<script[\s>](.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    opens = s.count('{')
    closes = s.count('}')
    diff = opens - closes
    if diff != 0 and i != 3:
        print(f"  Block {i}: diff={diff} *** CHECK ***")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\n[DONE] Saved")
