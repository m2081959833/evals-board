#!/usr/bin/env python3
"""Build Case Explorer v6: per-prompt, 1/page, full content, images, safe escaping."""
import json, re

with open('cases_data_full_safe.json','r',encoding='utf-8') as f:
    cases_json_str = f.read()

cases = json.loads(cases_json_str)
print("Cases: %d, JSON: %d bytes" % (len(cases), len(cases_json_str)))

cats_set = sorted(set(c['cat'] for c in cases if c.get('cat')))

with open('current_page.html','r',encoding='utf-8') as f:
    html = f.read()

# ---- 1. CSS ----
case_css = """
/* ---- Case Explorer (per-prompt) ---- */
.case-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center}
.case-filters select{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;background:#fff;min-width:120px;cursor:pointer}
.case-filters input{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;flex:1;min-width:200px}
.case-filters select:focus,.case-filters input:focus{outline:none;border-color:#165dff}
.case-block{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);overflow:hidden;margin-bottom:16px}
.case-header{padding:14px 20px;background:#fafbfc;border-bottom:1px solid #f0f1f3;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.case-id{font-weight:700;font-size:16px;color:#1d2129}
.case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:500}
.tag-cat{background:#e8f3ff;color:#165dff}
.tag-src{background:#fff7e6;color:#ff7d00}
.tag-turn{background:#f0f1f3;color:#4e5969}
.tag-session{background:#f0f1f3;color:#4e5969}
.gsb-win{background:#e8ffea;color:#00b42a}
.gsb-tie{background:#fff7e6;color:#ff7d00}
.gsb-lose{background:#ffece8;color:#f53f3f}
.case-prompt{padding:14px 20px;font-size:14px;color:#1d2129;line-height:1.7;background:#fafbfc;border-bottom:1px solid #f0f1f3;white-space:pre-wrap;word-break:break-all}
.case-prompt strong{color:#4e5969;font-size:13px}
.case-prompt .prompt-img{max-width:400px;max-height:400px;border-radius:8px;margin-top:8px;display:block;cursor:pointer;border:1px solid #e5e6eb}
.case-prompt .prompt-img:hover{box-shadow:0 2px 8px rgba(0,0,0,.12)}
.prompt-img-wrap{display:inline-block;margin-top:8px}
.img-placeholder{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;background:#f0f1f3;border:1px dashed #c9cdd4;border-radius:8px;cursor:pointer;color:#4e5969;font-size:13px;margin-top:8px;transition:background .2s}
.img-placeholder:hover{background:#e5e6eb}
.img-placeholder .img-icon{font-size:20px}
.case-compare{display:flex;gap:0}
.case-side{flex:1;padding:16px 20px;min-width:0}
.case-side.side-db{border-right:1px solid #f0f1f3}
.side-title{font-size:14px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px}
.side-db .side-title{color:#165dff}
.side-qw .side-title{color:#ff7d00}
.case-scores{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.score-badge{display:inline-block;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:500}
.score-badge.obj{background:#e8f3ff;color:#165dff}
.score-badge.sub{background:#f0e8ff;color:#722ed1}
.case-reply{font-size:13px;color:#4e5969;line-height:1.7;background:#f7f8fa;border-radius:8px;padding:12px 14px;white-space:pre-wrap;word-break:break-all;max-height:600px;overflow:auto}
.case-wc{font-size:12px;color:#86909c;margin-top:6px}
.gsb-row{padding:10px 20px;background:#fafbfc;border-top:1px solid #f0f1f3;display:flex;gap:12px;align-items:center;font-size:13px;color:#4e5969}
.gsb-row strong{color:#1d2129}
.case-pager{display:flex;align-items:center;justify-content:center;gap:12px;padding:16px 0}
.case-pager button{padding:6px 16px;border:1px solid #e5e6eb;border-radius:8px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969}
.case-pager button:hover:not([disabled]){border-color:#165dff;color:#165dff}
.case-pager button[disabled]{opacity:.4;cursor:not-allowed}
.case-pager span{font-size:13px;color:#4e5969}
.case-pager input[type=number]{width:60px;padding:4px 8px;border:1px solid #e5e6eb;border-radius:6px;font-size:13px;text-align:center}
.img-lightbox{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:9999;display:flex;align-items:center;justify-content:center;cursor:pointer}
.img-lightbox img{max-width:90vw;max-height:90vh;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.3)}
"""
html = html.replace('</style>', case_css + '\n</style>', 1)

# ---- 2. Replace tabCases ----
case_panel = '<div id="tabCases" class="tab-panel">\n'
case_panel += '  <div class="case-filters">\n'
case_panel += '    <input type="text" id="caseSearch" placeholder="\u641c\u7d22Prompt/\u56de\u590d\u5185\u5bb9..." oninput="filterCases()">\n'
case_panel += '    <select id="caseCat" onchange="filterCases()">\n'
case_panel += '      <option value="">\u5168\u90e8\u7c7b\u522b</option>\n'
for cat in cats_set:
    case_panel += '      <option value="' + cat + '">' + cat + '</option>\n'
case_panel += '    </select>\n'
case_panel += '    <select id="caseSrc" onchange="filterCases()">\n'
case_panel += '      <option value="">\u5168\u90e8\u6765\u6e90</option>\n'
case_panel += '      <option value="APP">APP</option>\n'
case_panel += '      <option value="Web">Web</option>\n'
case_panel += '    </select>\n'
case_panel += '    <select id="caseTurn" onchange="filterCases()">\n'
case_panel += '      <option value="">\u5168\u90e8\u8f6e\u6b21</option>\n'
case_panel += '      <option value="\u5355\u8f6e">\u5355\u8f6e</option>\n'
case_panel += '      <option value="\u591a\u8f6e">\u591a\u8f6e</option>\n'
case_panel += '    </select>\n'
case_panel += '    <select id="caseGsb" onchange="filterCases()">\n'
case_panel += '      <option value="">\u5168\u90e8GSB\u7ed3\u679c</option>\n'
case_panel += '      <option value="win">\u8c46\u5305\u80dc</option>\n'
case_panel += '      <option value="tie">\u5e73\u5c40</option>\n'
case_panel += '      <option value="lose">Qwen\u80dc</option>\n'
case_panel += '    </select>\n'
case_panel += '    <span id="caseCount" style="font-size:13px;color:#86909c;margin-left:8px"></span>\n'
case_panel += '  </div>\n'
case_panel += '  <div id="caseList"></div>\n'
case_panel += '  <div class="case-pager" id="casePager"></div>\n'
case_panel += '</div>'

pattern = r'<div id="tabCases" class="tab-panel">.*?</div>\s*(?=\n*<script>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    html = html[:match.start()] + case_panel + '\n\n' + html[match.end():]
    print("Replaced tabCases")
else:
    print("ERROR"); exit(1)

# ---- 3. JS (read from separate file to avoid Python string issues) ----
with open('case_explorer.js','r',encoding='utf-8') as f:
    case_logic_js = f.read()

case_js = "\n/* ---- Case Explorer (per-prompt, 1 per page) ---- */\n"
case_js += "var CASES = " + cases_json_str + ";\n"
case_js += case_logic_js + "\n"

last_script_end = html.rfind('</script>')
html = html[:last_script_end] + case_js + '\n' + html[last_script_end:]
print("Added JS")

# Final verification: count script boundaries
opens = html.count('<script>')
closes = html.count('</script>')
print("Script opens: %d, closes: %d" % (opens, closes))

with open('viz_final_v6.html','w',encoding='utf-8') as f:
    f.write(html)
print("Final: %d bytes (%d KB)" % (len(html), len(html)/1024))
