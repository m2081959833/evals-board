import json, re, os

# Load data
with open('cases_data_v7.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

with open('current_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('case_explorer_v7.js', 'r', encoding='utf-8') as f:
    case_logic_js = f.read()

print('Cases:', len(cases))
print('HTML size:', len(html))
print('JS size:', len(case_logic_js))

cases_json_str = json.dumps(cases, ensure_ascii=False)
# Sanitize any </script> inside JSON string values
cases_json_str = cases_json_str.replace('</script', '<\\/script').replace('</Script', '<\\/Script')

case_js = "var CASES = " + cases_json_str + ";\n" + case_logic_js

# Build new CSS for annotation fields
extra_css = """
<style>
/* Scores grid */
.scores-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin: 8px 0; }
.score-cell { background: #f7f8fa; border-radius: 6px; padding: 8px; }
.score-cell-title { font-size: 11px; color: #86909c; margin-bottom: 2px; }
.score-cell-val { font-size: 18px; font-weight: 700; color: #1d2129; }
.score-cell-ann { font-size: 11px; color: #86909c; margin-top: 3px; line-height: 1.5; word-break: break-all; }

/* Rich media box */
.rich-media-box { background: #fffbe6; border: 1px solid #ffe58f; border-radius: 6px; padding: 8px 10px; margin: 8px 0; }
.rich-media-title { font-size: 12px; font-weight: 600; color: #d4a017; margin-bottom: 4px; }
.ann-row { font-size: 12px; line-height: 1.6; display: flex; gap: 6px; }
.ann-label { color: #86909c; flex-shrink: 0; }
.ann-val { color: #4e5969; word-break: break-all; }

/* GSB detail section */
.gsb-detail-section { background: #f2f3f5; border-radius: 8px; padding: 12px 16px; margin-top: 12px; }
.gsb-detail-title { font-size: 14px; font-weight: 600; color: #1d2129; margin-bottom: 8px; display: flex; align-items: center; }
.gsb-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; }
.gsb-cell { background: #fff; border-radius: 6px; padding: 8px; }
.gsb-cell-title { font-size: 11px; color: #86909c; margin-bottom: 2px; }
.gsb-cell-val { font-size: 18px; font-weight: 700; color: #1d2129; }

/* COT block */
.cot-block { margin-top: 8px; }
.cot-block summary { cursor: pointer; font-size: 12px; color: #165dff; font-weight: 500; }
.cot-text { font-size: 12px; color: #4e5969; max-height: 300px; overflow-y: auto; }

/* Tag rich */
.tag-rich { background: #fff7e6; color: #d4a017; }

/* img placeholder */
.img-placeholder { display: flex; align-items: center; gap: 8px; padding: 16px; background: #f7f8fa; border: 1px dashed #c9cdd4; border-radius: 8px; cursor: pointer; color: #86909c; margin: 8px 0; }
.img-placeholder:hover { background: #e8f3ff; border-color: #165dff; color: #165dff; }
.img-icon { font-size: 24px; }
.prompt-img-wrap { margin: 8px 0; }
.prompt-img { max-width: 100%; max-height: 400px; border-radius: 8px; cursor: pointer; }
.img-lightbox { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 9999; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.img-lightbox img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }

@media (max-width: 768px) {
  .gsb-grid { grid-template-columns: 1fr 1fr; }
}
</style>
"""

# Insert extra CSS before </head>
html = html.replace('</head>', extra_css + '\n</head>')

# Replace tabCases panel content
new_tab_cases = """<div id="tabCases" class="tab-panel">
  <div class="card" style="margin-bottom:16px">
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
      <input type="text" id="caseSearch" placeholder="\u641c\u7d22 Prompt / \u56de\u590d..." style="flex:1;min-width:200px;padding:6px 12px;border:1px solid #e5e6eb;border-radius:6px" onchange="filterCases()" onkeyup="if(event.keyCode===13)filterCases()">
      <select id="caseCat" onchange="filterCases()"><option value="">\u5168\u90e8\u65b9\u5411</option></select>
      <select id="caseSrc" onchange="filterCases()"><option value="">\u5168\u90e8\u6765\u6e90</option></select>
      <select id="caseTurn" onchange="filterCases()"><option value="">\u5355\u8f6e/\u591a\u8f6e</option><option value="\u5355\u8f6e">\u5355\u8f6e</option><option value="\u591a\u8f6e">\u591a\u8f6e</option></select>
      <select id="caseGsb" onchange="filterCases()"><option value="">GSB\u7ed3\u679c</option><option value="win">\u8c46\u5305\u80dc</option><option value="tie">\u5e73\u5c40</option><option value="lose">Qwen\u80dc</option></select>
      <span id="caseCount" style="font-size:13px;color:#86909c">\u5171 0 \u6761Prompt</span>
    </div>
  </div>
  <div id="caseList"></div>
  <div id="casePager" class="pager-bar"></div>
</div>"""

# Use regex to replace tabCases panel
pattern = r'<div id="tabCases" class="tab-panel">.*?</div>\s*(?=\n*<script>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    html = html[:match.start()] + new_tab_cases + '\n' + html[match.end():]
    print('Replaced tabCases panel')
else:
    print('WARNING: Could not find tabCases panel, trying alternative...')
    # Fallback: insert before last </div> before <script>
    idx = html.rfind('<div id="tabCases"')
    if idx >= 0:
        end_idx = html.find('</div>', idx)
        if end_idx >= 0:
            # Find closing after content
            depth = 0
            pos = idx
            while pos < len(html):
                if html[pos:pos+4] == '<div':
                    depth += 1
                elif html[pos:pos+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        html = html[:idx] + new_tab_cases + '\n' + html[pos+6:]
                        print('Replaced tabCases via fallback')
                        break
                pos += 1

# Populate filter dropdowns from data
cats = sorted(list(set(c['cat'] for c in cases if c['cat'])))
srcs = sorted(list(set(c['src'] for c in cases if c['src'])))

populate_js = "\n(function(){\n"
populate_js += "  var catSel = document.getElementById('caseCat');\n"
for cat in cats:
    populate_js += "  catSel.options.add(new Option('" + cat + "','" + cat + "'));\n"
populate_js += "  var srcSel = document.getElementById('caseSrc');\n"
for src in srcs:
    populate_js += "  srcSel.options.add(new Option('" + src + "','" + src + "'));\n"
populate_js += "})();\n"

full_script = '<script>\n' + case_js + populate_js + '</script>'

# Find insertion point: before the closing </body> or at the end
if '</body>' in html:
    html = html.replace('</body>', full_script + '\n</body>')
else:
    html += '\n' + full_script

# Verify script tag balance
open_count = len(re.findall(r'<script', html, re.IGNORECASE))
close_count = len(re.findall(r'</script', html, re.IGNORECASE))
print('Script tags: open=%d close=%d' % (open_count, close_count))
if open_count != close_count:
    print('WARNING: Script tag mismatch!')

# Save
out_path = 'viz_final_v7.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved:', out_path, 'size:', os.path.getsize(out_path))
