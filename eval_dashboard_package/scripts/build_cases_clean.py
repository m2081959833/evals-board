#!/usr/bin/env python3
"""Build Case Explorer into viz_final_v2.html -> viz_final_v3.html (clean build)"""
import json, re

# Load case data
with open('cases_data.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Clean up categories
for c in cases:
    if not c.get('cat') or c['cat'] == '\\':
        c['cat'] = '其他'
    c['cat'] = c['cat'].replace('VLM（通用）', 'VLM通用').replace('VLM（教育）', 'VLM教育')

# Compute GSB labels
for c in cases:
    g = c.get('gsb_obj', '')
    try:
        v = int(g)
        if v > 0:
            c['gsb_label'] = '豆包胜 (+' + str(v) + ')'
            c['gsb_cls'] = 'gsb-win'
        elif v < 0:
            c['gsb_label'] = 'Qwen胜 (' + str(v) + ')'
            c['gsb_cls'] = 'gsb-lose'
        else:
            c['gsb_label'] = '平局'
            c['gsb_cls'] = 'gsb-tie'
    except:
        c['gsb_label'] = ''
        c['gsb_cls'] = ''

cats = sorted(set(c['cat'] for c in cases))
cases_json = json.dumps(cases, ensure_ascii=False, separators=(',', ':'))

# Load clean HTML
with open('viz_final_v2.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Original size:", len(html))

# ---- 1. Add CSS before </style> ----
case_css = """
/* ---- Case Explorer Styles ---- */
.case-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center}
.case-filters select{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;background:#fff;min-width:120px;cursor:pointer}
.case-filters input{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;flex:1;min-width:200px}
.case-filters select:focus,.case-filters input:focus{outline:none;border-color:#165dff}
.case-item{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);overflow:hidden;margin-bottom:12px}
.case-header{padding:12px 16px;background:#fafbfc;border-bottom:1px solid #f0f1f3;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.case-id{font-weight:600;font-size:14px;color:#1d2129}
.case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:500}
.tag-cat{background:#e8f3ff;color:#165dff}
.tag-src{background:#fff7e6;color:#ff7d00}
.tag-turn{background:#f0f1f3;color:#4e5969}
.gsb-win{background:#e8ffea;color:#00b42a}
.gsb-tie{background:#fff7e6;color:#ff7d00}
.gsb-lose{background:#ffece8;color:#f53f3f}
.case-prompt{padding:12px 16px;font-size:13px;color:#4e5969;line-height:1.6;border-bottom:1px solid #f0f1f3;max-height:120px;overflow:auto}
.case-compare{display:flex;gap:0}
.case-side{flex:1;padding:12px 16px;min-width:0}
.case-side.case-db{border-right:1px solid #f0f1f3}
.case-side-title{font-size:13px;font-weight:600;margin-bottom:8px}
.case-db .case-side-title{color:#165dff}
.case-qw .case-side-title{color:#ff7d00}
.case-scores{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
.score-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px}
.score-badge.obj{background:#e8f3ff;color:#165dff}
.score-badge.sub{background:#f0e8ff;color:#722ed1}
.case-wc{font-size:12px;color:#86909c}
.case-footer{padding:8px 16px;background:#fafbfc;border-top:1px solid #f0f1f3;font-size:12px;color:#86909c}
.case-pager{display:flex;align-items:center;justify-content:center;gap:12px;padding:16px 0}
.case-pager button{padding:6px 16px;border:1px solid #e5e6eb;border-radius:8px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969}
.case-pager button:hover:not([disabled]){border-color:#165dff;color:#165dff}
.case-pager button[disabled]{opacity:.4;cursor:not-allowed}
"""
html = html.replace('</style>', case_css + '</style>', 1)
print("Added CSS")

# ---- 2. Replace empty tabCases div ----
case_panel_html = '<div id="tabCases" class="tab-panel">\n'
case_panel_html += '  <div class="case-filters">\n'
case_panel_html += '    <input type="text" id="caseSearch" placeholder="搜索题目内容或ID..." oninput="filterCases()">\n'
case_panel_html += '    <select id="caseCat" onchange="filterCases()">\n'
case_panel_html += '      <option value="">全部类别</option>\n'
for cat in cats:
    case_panel_html += '      <option value="' + cat + '">' + cat + '</option>\n'
case_panel_html += '    </select>\n'
case_panel_html += '    <select id="caseSrc" onchange="filterCases()">\n'
case_panel_html += '      <option value="">全部来源</option>\n'
case_panel_html += '      <option value="APP">APP</option>\n'
case_panel_html += '      <option value="Web">Web</option>\n'
case_panel_html += '    </select>\n'
case_panel_html += '    <select id="caseGsb" onchange="filterCases()">\n'
case_panel_html += '      <option value="">全部GSB结果</option>\n'
case_panel_html += '      <option value="win">豆包胜</option>\n'
case_panel_html += '      <option value="tie">平局</option>\n'
case_panel_html += '      <option value="lose">Qwen胜</option>\n'
case_panel_html += '    </select>\n'
case_panel_html += '    <span id="caseCount" style="font-size:13px;color:#86909c;margin-left:8px"></span>\n'
case_panel_html += '  </div>\n'
case_panel_html += '  <div id="caseList"></div>\n'
case_panel_html += '  <div class="case-pager" id="casePager"></div>\n'
case_panel_html += '</div>'

# Find and replace the tabCases panel
pattern = r'<div id="tabCases" class="tab-panel">.*?</div>\s*(?=\n*<script>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    html = html[:match.start()] + case_panel_html + '\n\n' + html[match.end():]
    print("Replaced tabCases panel")
else:
    print("ERROR: tabCases not found!")
    exit(1)

# ---- 3. Add Case Explorer JS before </script> ----
case_js = """
/* ---- Case Explorer ---- */
var CASES = """ + cases_json + """;
var caseFiltered = CASES.slice();
var casePage = 0;
var casePerPage = 10;

function filterCases() {
  var q = (document.getElementById('caseSearch').value || '').toLowerCase();
  var cat = document.getElementById('caseCat').value;
  var src = document.getElementById('caseSrc').value;
  var gsb = document.getElementById('caseGsb').value;
  caseFiltered = [];
  for (var i = 0; i < CASES.length; i++) {
    var c = CASES[i];
    if (cat && c.cat !== cat) continue;
    if (src && c.src !== src) continue;
    if (gsb === 'win' && c.gsb_cls !== 'gsb-win') continue;
    if (gsb === 'tie' && c.gsb_cls !== 'gsb-tie') continue;
    if (gsb === 'lose' && c.gsb_cls !== 'gsb-lose') continue;
    if (q) {
      var txt = ((c.id || '') + ' ' + (c.q || '') + ' ' + (c.cat || '')).toLowerCase();
      if (txt.indexOf(q) < 0) continue;
    }
    caseFiltered.push(c);
  }
  casePage = 0;
  document.getElementById('caseCount').textContent = '共 ' + caseFiltered.length + ' 条';
  renderCases();
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderCases() {
  var list = document.getElementById('caseList');
  var start = casePage * casePerPage;
  var end = Math.min(start + casePerPage, caseFiltered.length);
  var h = '';
  if (caseFiltered.length === 0) {
    h = '<div style="padding:40px;text-align:center;color:#86909c">无匹配案例</div>';
  }
  for (var i = start; i < end; i++) {
    var c = caseFiltered[i];
    var promptText = esc(c.q || '').substring(0, 300);
    if ((c.q || '').length > 300) promptText += '...';

    h += '<div class="case-item">';
    h += '<div class="case-header">';
    h += '<span class="case-id">' + esc(c.id) + '</span>';
    h += '<span class="case-tag tag-cat">' + esc(c.cat) + '</span>';
    h += '<span class="case-tag tag-src">' + esc(c.src) + '</span>';
    if (c.turn) h += '<span class="case-tag tag-turn">' + esc(c.turn) + '</span>';
    if (c.gsb_label) h += '<span class="case-tag ' + c.gsb_cls + '">' + esc(c.gsb_label) + '</span>';
    h += '</div>';
    h += '<div class="case-prompt"><strong>Prompt:</strong> ' + promptText + '</div>';
    h += '<div class="case-compare">';
    h += '<div class="case-side case-db">';
    h += '<div class="case-side-title">豆包</div>';
    h += '<div class="case-scores">';
    if (c.db_obj !== '' && c.db_obj !== undefined) h += '<span class="score-badge obj">客观 ' + esc(c.db_obj) + '</span>';
    if (c.db_sub !== '' && c.db_sub !== undefined) h += '<span class="score-badge sub">主观 ' + esc(c.db_sub) + '</span>';
    h += '</div>';
    if (c.db_w) h += '<div class="case-wc">字数: ' + c.db_w + '</div>';
    h += '</div>';
    h += '<div class="case-side case-qw">';
    h += '<div class="case-side-title">Qwen3.5</div>';
    h += '<div class="case-scores">';
    if (c.qw_obj !== '' && c.qw_obj !== undefined) h += '<span class="score-badge obj">客观 ' + esc(c.qw_obj) + '</span>';
    if (c.qw_sub !== '' && c.qw_sub !== undefined) h += '<span class="score-badge sub">主观 ' + esc(c.qw_sub) + '</span>';
    h += '</div>';
    if (c.qw_w) h += '<div class="case-wc">字数: ' + c.qw_w + '</div>';
    h += '</div>';
    h += '</div>';
    h += '<div class="case-footer">Session: ' + esc(c.sid || '') + ' | 轮次: ' + (c.r || '') + '</div>';
    h += '</div>';
  }
  list.innerHTML = h;
  var totalPages = Math.ceil(caseFiltered.length / casePerPage) || 1;
  var ph = '<span>第 ' + (casePage + 1) + ' / ' + totalPages + ' 页</span>';
  ph += '<button onclick="goPage(-1)"' + (casePage <= 0 ? ' disabled' : '') + '>上一页</button>';
  ph += '<button onclick="goPage(1)"' + (casePage >= totalPages - 1 ? ' disabled' : '') + '>下一页</button>';
  document.getElementById('casePager').innerHTML = ph;
}

function goPage(d) {
  var totalPages = Math.ceil(caseFiltered.length / casePerPage) || 1;
  casePage = Math.max(0, Math.min(casePage + d, totalPages - 1));
  renderCases();
  window.scrollTo(0, document.getElementById('tabCases').offsetTop);
}

filterCases();
"""

# Insert before last </script>
last_script_end = html.rfind('</script>')
html = html[:last_script_end] + case_js + '\n' + html[last_script_end:]
print("Added case JS")

# Write output
with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Final size:", len(html), "bytes")
