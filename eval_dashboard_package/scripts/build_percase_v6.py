#!/usr/bin/env python3
"""Build Case Explorer: per-prompt view, 1 case per page, full content, image support."""
import json, re

with open('cases_data_full.json','r',encoding='utf-8') as f:
    cases = json.load(f)

cases_json = json.dumps(cases, ensure_ascii=False, separators=(',',':'))
print("Cases: %d, JSON: %d bytes (%.0f KB)" % (len(cases), len(cases_json), len(cases_json)/1024))

cats_set = sorted(set(c['cat'] for c in cases if c.get('cat')))

with open('current_page.html','r',encoding='utf-8') as f:
    html = f.read()

# ---- 1. CSS ----
case_css = r"""
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
    print("ERROR: tabCases not found"); exit(1)

# ---- 3. JS ----
case_js = "\n/* ---- Case Explorer (per-prompt, 1 per page) ---- */\n"
case_js += "var CASES = " + cases_json + ";\n"
case_js += r"""var caseFiltered = CASES.slice();
var casePage = 0;
var casePerPage = 1;

function filterCases() {
  var q = (document.getElementById('caseSearch').value || '').toLowerCase();
  var cat = document.getElementById('caseCat').value;
  var src = document.getElementById('caseSrc').value;
  var turn = document.getElementById('caseTurn').value;
  var gsb = document.getElementById('caseGsb').value;
  caseFiltered = [];
  for (var i = 0; i < CASES.length; i++) {
    var c = CASES[i];
    if (cat && c.cat !== cat) continue;
    if (src && c.src !== src) continue;
    if (turn && c.turn !== turn) continue;
    if (gsb === 'win' && c.gsb_cls !== 'gsb-win') continue;
    if (gsb === 'tie' && c.gsb_cls !== 'gsb-tie') continue;
    if (gsb === 'lose' && c.gsb_cls !== 'gsb-lose') continue;
    if (q) {
      var txt = (c.id + ' ' + c.sid + ' ' + c.q + ' ' + c.db_r + ' ' + c.qw_r).toLowerCase();
      if (txt.indexOf(q) < 0) continue;
    }
    caseFiltered.push(c);
  }
  casePage = 0;
  document.getElementById('caseCount').textContent = '\u5171 ' + caseFiltered.length + ' \u6761Prompt';
  renderCase();
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showLightbox(url) {
  var ov = document.createElement('div');
  ov.className = 'img-lightbox';
  ov.onclick = function(){ document.body.removeChild(ov); };
  var img = document.createElement('img');
  img.src = url;
  ov.appendChild(img);
  document.body.appendChild(ov);
}

function fmtScore(v) {
  if (v === '' || v === null || v === undefined) return '-';
  return String(v);
}

function renderCase() {
  var list = document.getElementById('caseList');
  if (caseFiltered.length === 0) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:#86909c">\u65e0\u5339\u914d\u6848\u4f8b</div>';
    document.getElementById('casePager').innerHTML = '';
    return;
  }
  var c = caseFiltered[casePage];
  var h = '<div class="case-block">';

  // Header
  h += '<div class="case-header">';
  h += '<span class="case-id">' + esc(c.id) + '</span>';
  h += '<span class="case-tag tag-session">Session: ' + esc(c.sid) + '</span>';
  if (c.cat) h += '<span class="case-tag tag-cat">' + esc(c.cat) + '</span>';
  h += '<span class="case-tag tag-src">' + esc(c.src) + '</span>';
  h += '<span class="case-tag tag-turn">' + esc(c.turn) + ' \u7b2c' + c.r + '\u8f6e</span>';
  if (c.gsb_label) h += '<span class="case-tag ' + c.gsb_cls + '">' + esc(c.gsb_label) + '</span>';
  h += '</div>';

  // Prompt
  h += '<div class="case-prompt"><strong>Prompt:</strong>\n';
  var promptText = esc(c.q || '');
  if (promptText) h += promptText;
  if (c.imgs && c.imgs.length > 0) {
    for (var ii = 0; ii < c.imgs.length; ii++) {
      h += '<img class="prompt-img" src="' + c.imgs[ii] + '" onclick="showLightbox(this.src)" alt="\u56fe\u7247" loading="lazy">';
    }
  }
  if (!promptText && (!c.imgs || c.imgs.length === 0)) {
    h += '<span style="color:#c9cdd4">\u65e0\u5185\u5bb9</span>';
  }
  h += '</div>';

  // Side-by-side comparison
  h += '<div class="case-compare">';

  // DB side
  h += '<div class="case-side side-db">';
  h += '<div class="side-title">\u8c46\u5305';
  if (c.db_w) h += ' <span style="font-weight:400;font-size:12px;color:#86909c">(' + c.db_w + '\u5b57)</span>';
  h += '</div>';
  h += '<div class="case-scores">';
  h += '<span class="score-badge obj">\u5ba2\u89c2 ' + fmtScore(c.db_obj) + '</span>';
  h += '<span class="score-badge sub">\u4e3b\u5ba2\u89c2 ' + fmtScore(c.db_sub) + '</span>';
  h += '</div>';
  if (c.db_r) {
    h += '<div class="case-reply">' + esc(c.db_r) + '</div>';
  } else {
    h += '<div class="case-reply" style="color:#c9cdd4">\u65e0\u56de\u590d</div>';
  }
  h += '</div>';

  // QW side
  h += '<div class="case-side side-qw">';
  h += '<div class="side-title">Qwen3.5';
  if (c.qw_w) h += ' <span style="font-weight:400;font-size:12px;color:#86909c">(' + c.qw_w + '\u5b57)</span>';
  h += '</div>';
  h += '<div class="case-scores">';
  h += '<span class="score-badge obj">\u5ba2\u89c2 ' + fmtScore(c.qw_obj) + '</span>';
  h += '<span class="score-badge sub">\u4e3b\u5ba2\u89c2 ' + fmtScore(c.qw_sub) + '</span>';
  h += '</div>';
  if (c.qw_r) {
    h += '<div class="case-reply">' + esc(c.qw_r) + '</div>';
  } else {
    h += '<div class="case-reply" style="color:#c9cdd4">\u65e0\u56de\u590d</div>';
  }
  h += '</div>';

  h += '</div>'; // case-compare

  // GSB row
  h += '<div class="gsb-row">';
  h += '<strong>GSB:</strong>';
  h += '<span>\u5ba2\u89c2 ' + fmtScore(c.gsb_obj) + '</span>';
  h += '<span>\u4e3b\u5ba2\u89c2 ' + fmtScore(c.gsb_sub) + '</span>';
  if (c.gsb_label) h += '<span class="case-tag ' + c.gsb_cls + '">' + esc(c.gsb_label) + '</span>';
  h += '</div>';

  h += '</div>'; // case-block
  list.innerHTML = h;

  // Pager
  var total = caseFiltered.length;
  var ph = '<button onclick="goCase(-1)"' + (casePage <= 0 ? ' disabled' : '') + '>\u4e0a\u4e00\u6761</button>';
  ph += '<span>\u7b2c ' + (casePage + 1) + ' / ' + total + ' \u6761</span>';
  ph += '<button onclick="goCase(1)"' + (casePage >= total - 1 ? ' disabled' : '') + '>\u4e0b\u4e00\u6761</button>';
  ph += ' <input type="number" id="casePageInput" min="1" max="' + total + '" value="' + (casePage + 1) + '" style="margin-left:12px">';
  ph += '<button onclick="jumpCase()">\u8df3\u8f6c</button>';
  document.getElementById('casePager').innerHTML = ph;
}

function goCase(d) {
  var total = caseFiltered.length;
  casePage = Math.max(0, Math.min(casePage + d, total - 1));
  renderCase();
  window.scrollTo(0, document.getElementById('tabCases').offsetTop);
}

function jumpCase() {
  var inp = document.getElementById('casePageInput');
  var v = parseInt(inp.value, 10);
  var total = caseFiltered.length;
  if (isNaN(v) || v < 1) v = 1;
  if (v > total) v = total;
  casePage = v - 1;
  renderCase();
  window.scrollTo(0, document.getElementById('tabCases').offsetTop);
}

filterCases();
"""

last_script_end = html.rfind('</script>')
html = html[:last_script_end] + case_js + '\n' + html[last_script_end:]
print("Added JS")

with open('viz_final_v6.html','w',encoding='utf-8') as f:
    f.write(html)
print("Final: %d bytes (%d KB)" % (len(html), len(html)/1024))
