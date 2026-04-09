#!/usr/bin/env python3
"""
fix5b.py - Three fixes:
1. Fix CSS selectors: llm-case-explorer -> llm-case-section (correct class name)
2. Add 打分备注 rendering to case cards JS
3. Add CSS for score notes display
"""
import re

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTML size: {len(html)} bytes")

# ============================================================
# FIX 1: Fix CSS selectors and add alignment
# ============================================================
# The fix4 CSS used .llm-case-explorer but actual class is .llm-case-section
# Replace the old wrong CSS with correct selectors

old_css_block = """#proj2 .llm-case-explorer{max-width:1000px;margin:0 auto;padding:24px 64px}
#proj2 .llm-case-card{max-width:900px;margin:0 auto 24px auto}
#proj2 .llm-case-responses{grid-template-columns:repeat(2,1fr) !important;gap:12px}
#proj2 .llm-case-prompt{font-size:14px;line-height:1.6;padding:12px 16px;margin-bottom:16px;background:#f7f8fa;border-left:3px solid #165dff;border-radius:0 8px 8px 0}
#proj2 .llm-resp-body{max-height:300px;overflow-y:auto;font-size:13px;line-height:1.6}
#proj2 .llm-gsb-row{max-width:900px;margin:0 auto}"""

new_css_block = """#proj2 .llm-case-section{max-width:1000px;margin:32px auto 0;padding:24px 64px 40px}
#proj2 .llm-case-card{max-width:900px;margin:0 auto 24px auto}
#proj2 .llm-case-responses{grid-template-columns:repeat(2,1fr) !important;gap:12px}
#proj2 .llm-case-prompt{font-size:14px;line-height:1.6;padding:12px 16px;margin-bottom:16px;background:#f7f8fa;border-left:3px solid #165dff;border-radius:0 8px 8px 0}
#proj2 .llm-resp-body{max-height:300px;overflow-y:auto;font-size:13px;line-height:1.6}
#proj2 .llm-gsb-row{max-width:900px;margin:0 auto}
#proj2 .llm-case-filters{max-width:900px;margin:0 auto 16px}
#proj2 .llm-case-tag-level{max-width:900px;margin:0 auto 10px}
#proj2 .llm-case-sub-tabs{max-width:900px;margin:0 auto 16px}
#proj2 .llm-case-section h2{max-width:900px;margin:0 auto 16px}"""

if old_css_block in html:
    html = html.replace(old_css_block, new_css_block)
    print("FIX 1: Replaced CSS selectors (.llm-case-explorer -> .llm-case-section) + centered alignment")
else:
    print("WARNING: Could not find exact old CSS block, trying line by line...")
    html = html.replace('#proj2 .llm-case-explorer{', '#proj2 .llm-case-section{')
    # Add the alignment CSS after the gsb-row line
    gsb_css = '#proj2 .llm-gsb-row{max-width:900px;margin:0 auto}'
    extra_css = """
#proj2 .llm-case-filters{max-width:900px;margin:0 auto 16px}
#proj2 .llm-case-tag-level{max-width:900px;margin:0 auto 10px}
#proj2 .llm-case-sub-tabs{max-width:900px;margin:0 auto 16px}
#proj2 .llm-case-section h2{max-width:900px;margin:0 auto 16px}"""
    html = html.replace(gsb_css, gsb_css + extra_css)
    print("FIX 1: Applied fallback CSS fixes")

# ============================================================
# FIX 2: Add 打分备注 CSS
# ============================================================
notes_css = """
.llm-score-note{margin-top:8px;padding:8px 10px;background:#fffbe6;border-left:3px solid #faad14;border-radius:0 4px 4px 0;font-size:12px;line-height:1.5;color:#8c6e00}
.llm-score-note strong{color:#ad6800;font-weight:600;margin-right:4px}
.llm-score-note .note-label{display:inline-block;font-weight:600;color:#ad6800;min-width:60px}
.llm-score-note .note-row{margin-bottom:2px}
.llm-score-note .note-row:last-child{margin-bottom:0}"""

# Insert before the closing of the first style block (in <head>)
# Find the pagination CSS we added in fix4 and add after it
pager_css_end = '#proj2 .llm-case-pagination input[type=number]{width:60px;padding:4px 8px;border:1px solid #e5e6eb;border-radius:6px;font-size:13px;text-align:center}'
if pager_css_end in html:
    html = html.replace(pager_css_end, pager_css_end + notes_css)
    print("FIX 2: Added score notes CSS")
else:
    print("WARNING: Could not find pager CSS anchor, inserting before </style>")
    # Find first </style> in <head>
    style_end = html.index('</style>')
    html = html[:style_end] + notes_css + '\n' + html[style_end:]
    print("FIX 2: Added score notes CSS (fallback)")

# ============================================================
# FIX 3: Add 打分备注 rendering in JS
# ============================================================
# The current code builds:
#   h += '<div class="llm-resp-body">' + llmSan(data.r);
#   if (data.c) { ...COT... }
#   h += "</div></div>";
# 
# We want to add a score notes section after the resp-body, before closing </div></div>
# 
# New structure:
#   h += '<div class="llm-resp-body">...(response + COT)...</div>';
#   h += '<div class="llm-score-note">...(notes)...</div>';
#   h += '</div>';  // close resp-box

# Find the exact code pattern to replace
old_render = '''h += "</div></div>";
    }
    h += "</div>";

    /* GSB row */'''

new_render = '''h += "</div>";
      /* Score notes */
      var noteHtml = "";
      if (data.on) noteHtml += '<div class="note-row"><span class="note-label">\u5ba2\u89c2\u5907\u6ce8:</span> ' + llmSan(data.on) + '</div>';
      if (data.sn) noteHtml += '<div class="note-row"><span class="note-label">\u4e3b\u5ba2\u89c2\u5907\u6ce8:</span> ' + llmSan(data.sn) + '</div>';
      if (noteHtml) h += '<div class="llm-score-note">' + noteHtml + '</div>';
      h += "</div>";
    }
    h += "</div>";

    /* GSB row */'''

if old_render in html:
    html = html.replace(old_render, new_render, 1)
    print("FIX 3: Added score notes rendering in JS")
else:
    print("WARNING: Could not find exact render pattern. Trying broader search...")
    # Try a more flexible match
    m = re.search(r'h \+= "</div></div>";\s*\}\s*h \+= "</div>";\s*/\* GSB row \*/', html)
    if m:
        old_text = m.group()
        html = html.replace(old_text, new_render, 1)
        print("FIX 3: Added score notes rendering (regex match)")
    else:
        print("ERROR: Could not find rendering pattern!")
        # Let's debug
        idx = html.find('/* GSB row */')
        if idx > 0:
            print(f"  GSB row at {idx}, context:")
            print(repr(html[idx-200:idx+50]))

# Save
with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nSaved. New size: {len(html)} bytes")
