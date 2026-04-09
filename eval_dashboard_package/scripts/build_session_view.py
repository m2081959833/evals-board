#!/usr/bin/env python3
"""Build Case Explorer grouped by session, with conversation-style multi-round display"""
import json, re
from collections import OrderedDict

# Load trimmed case data
with open('cases_data_v2_trimmed.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Group by session
sessions = OrderedDict()
for c in cases:
    sid = c['sid']
    if sid not in sessions:
        sessions[sid] = []
    sessions[sid].append(c)

# Sort rounds within each session
for sid in sessions:
    sessions[sid].sort(key=lambda x: x.get('r', 0))

# Build session list for JS
session_list = []
for sid, items in sessions.items():
    first = items[0]
    # Collect all unique categories
    cats = list(OrderedDict.fromkeys(it['cat'] for it in items if it.get('cat')))
    # GSB: use first round's GSB for filtering
    gsb_cls = first.get('gsb_cls', '')
    gsb_label = first.get('gsb_label', '')
    session_list.append({
        'sid': sid,
        'cats': cats,
        'src': first.get('src', 'APP'),
        'turn': '多轮' if len(items) > 1 else '单轮',
        'rounds': len(items),
        'gsb_cls': gsb_cls,
        'gsb_label': gsb_label,
        'items': items
    })

print(f"Sessions: {len(session_list)}, Total rounds: {sum(s['rounds'] for s in session_list)}")

cats_set = sorted(set(c['cat'] for c in cases))
sessions_json = json.dumps(session_list, ensure_ascii=False, separators=(',', ':'))
print(f"Sessions JSON: {len(sessions_json)} bytes ({len(sessions_json)/1024:.0f} KB)")

# Load HTML
with open('current_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ---- 1. CSS ----
case_css = """
/* ---- Case Explorer ---- */
.case-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center}
.case-filters select{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;background:#fff;min-width:120px;cursor:pointer}
.case-filters input{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;flex:1;min-width:200px}
.case-filters select:focus,.case-filters input:focus{outline:none;border-color:#165dff}
.sess-block{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);overflow:hidden;margin-bottom:16px}
.sess-header{padding:12px 16px;background:#fafbfc;border-bottom:1px solid #f0f1f3;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.sess-id{font-weight:600;font-size:15px;color:#1d2129}
.case-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:500}
.tag-cat{background:#e8f3ff;color:#165dff}
.tag-src{background:#fff7e6;color:#ff7d00}
.tag-turn{background:#f0f1f3;color:#4e5969}
.tag-rounds{background:#f0f1f3;color:#4e5969}
.gsb-win{background:#e8ffea;color:#00b42a}
.gsb-tie{background:#fff7e6;color:#ff7d00}
.gsb-lose{background:#ffece8;color:#f53f3f}
.round-block{border-bottom:1px solid #f0f1f3}
.round-block:last-child{border-bottom:none}
.round-label{padding:8px 16px 4px;font-size:12px;font-weight:600;color:#86909c;background:#fafbfc}
.round-prompt{padding:8px 16px 10px;font-size:13px;color:#1d2129;line-height:1.6;background:#fafbfc;border-bottom:1px solid #f0f1f3;white-space:pre-wrap;word-break:break-all}
.round-prompt strong{color:#4e5969}
.round-compare{display:flex;gap:0}
.round-side{flex:1;padding:10px 16px;min-width:0}
.round-side.side-db{border-right:1px solid #f0f1f3}
.side-title{font-size:12px;font-weight:600;margin-bottom:6px;display:flex;align-items:center;gap:6px}
.side-db .side-title{color:#165dff}
.side-qw .side-title{color:#ff7d00}
.round-scores{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px}
.score-badge{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px}
.score-badge.obj{background:#e8f3ff;color:#165dff}
.score-badge.sub{background:#f0e8ff;color:#722ed1}
.round-reply{font-size:12px;color:#4e5969;line-height:1.5;max-height:120px;overflow:auto;background:#f7f8fa;border-radius:6px;padding:6px 8px;white-space:pre-wrap;word-break:break-all;margin-top:4px}
.round-wc{font-size:11px;color:#86909c;margin-top:2px}
.case-pager{display:flex;align-items:center;justify-content:center;gap:12px;padding:16px 0}
.case-pager button{padding:6px 16px;border:1px solid #e5e6eb;border-radius:8px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969}
.case-pager button:hover:not([disabled]){border-color:#165dff;color:#165dff}
.case-pager button[disabled]{opacity:.4;cursor:not-allowed}
.case-pager span{font-size:13px;color:#4e5969}
"""
html = html.replace('</style>', case_css + '</style>', 1)

# ---- 2. Replace tabCases ----
case_panel_html = '<div id="tabCases" class="tab-panel">\n'
case_panel_html += '  <div class="case-filters">\n'
case_panel_html += '    <input type="text" id="caseSearch" placeholder="搜索Session/Prompt内容..." oninput="filterCases()">\n'
case_panel_html += '    <select id="caseCat" onchange="filterCases()">\n'
case_panel_html += '      <option value="">全部类别</option>\n'
for cat in cats_set:
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

pattern = r'<div id="tabCases" class="tab-panel">.*?</div>\s*(?=\n*<script>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    html = html[:match.start()] + case_panel_html + '\n\n' + html[match.end():]
    print("Replaced tabCases")
else:
    print("ERROR"); exit(1)

# ---- 3. JS ----
case_js = "\n/* ---- Case Explorer (Session-grouped) ---- */\n"
case_js += "var SESSIONS = " + sessions_json + ";\n"
case_js += """var sessFiltered = SESSIONS.slice();
var sessPage = 0;
var sessPerPage = 3;

function filterCases() {
  var q = (document.getElementById('caseSearch').value || '').toLowerCase();
  var cat = document.getElementById('caseCat').value;
  var src = document.getElementById('caseSrc').value;
  var gsb = document.getElementById('caseGsb').value;
  sessFiltered = [];
  for (var i = 0; i < SESSIONS.length; i++) {
    var s = SESSIONS[i];
    if (src && s.src !== src) continue;
    if (gsb === 'win' && s.gsb_cls !== 'gsb-win') continue;
    if (gsb === 'tie' && s.gsb_cls !== 'gsb-tie') continue;
    if (gsb === 'lose' && s.gsb_cls !== 'gsb-lose') continue;
    if (cat) {
      var hasCat = false;
      for (var ci = 0; ci < s.cats.length; ci++) { if (s.cats[ci] === cat) { hasCat = true; break; } }
      if (!hasCat) continue;
    }
    if (q) {
      var txt = s.sid.toLowerCase();
      for (var ri = 0; ri < s.items.length; ri++) {
        txt += ' ' + ((s.items[ri].q || '') + ' ' + (s.items[ri].db_r || '') + ' ' + (s.items[ri].qw_r || '')).toLowerCase();
      }
      if (txt.indexOf(q) < 0) continue;
    }
    sessFiltered.push(s);
  }
  sessPage = 0;
  document.getElementById('caseCount').textContent = '共 ' + sessFiltered.length + ' 个Session';
  renderCases();
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderCases() {
  var list = document.getElementById('caseList');
  var start = sessPage * sessPerPage;
  var end = Math.min(start + sessPerPage, sessFiltered.length);
  var h = '';
  if (sessFiltered.length === 0) {
    h = '<div style="padding:40px;text-align:center;color:#86909c">无匹配案例</div>';
  }
  for (var si = start; si < end; si++) {
    var s = sessFiltered[si];
    h += '<div class="sess-block">';

    // Session header
    h += '<div class="sess-header">';
    h += '<span class="sess-id">' + esc(s.sid) + '</span>';
    for (var ci = 0; ci < s.cats.length; ci++) {
      h += '<span class="case-tag tag-cat">' + esc(s.cats[ci]) + '</span>';
    }
    h += '<span class="case-tag tag-src">' + esc(s.src) + '</span>';
    h += '<span class="case-tag tag-rounds">' + s.rounds + '轮对话</span>';
    if (s.gsb_label) h += '<span class="case-tag ' + s.gsb_cls + '">' + esc(s.gsb_label) + '</span>';
    h += '</div>';

    // Each round as conversation turn
    for (var ri = 0; ri < s.items.length; ri++) {
      var it = s.items[ri];
      h += '<div class="round-block">';

      // Round label + prompt
      var promptText = esc(it.q || '').substring(0, 300);
      if ((it.q || '').length > 300) promptText += '...';
      h += '<div class="round-label">第 ' + it.r + ' 轮 (' + esc(it.id) + ')';
      if (it.gsb_label && ri > 0) h += ' <span class="case-tag ' + (it.gsb_cls || '') + '" style="margin-left:6px">' + esc(it.gsb_label) + '</span>';
      h += '</div>';
      h += '<div class="round-prompt"><strong>Prompt:</strong> ' + promptText + '</div>';

      // Side-by-side replies
      h += '<div class="round-compare">';

      // DB
      h += '<div class="round-side side-db">';
      h += '<div class="side-title">豆包';
      if (it.db_w) h += ' <span style="font-weight:400;font-size:11px;color:#86909c">(' + it.db_w + '字)</span>';
      h += '</div>';
      h += '<div class="round-scores">';
      if (it.db_obj !== '' && it.db_obj !== undefined) h += '<span class="score-badge obj">客观 ' + esc(it.db_obj) + '</span>';
      if (it.db_sub !== '' && it.db_sub !== undefined) h += '<span class="score-badge sub">主观 ' + esc(it.db_sub) + '</span>';
      h += '</div>';
      if (it.db_r) {
        var dbText = esc(it.db_r);
        if (it.db_r.length >= 500) dbText += '...';
        h += '<div class="round-reply">' + dbText + '</div>';
      }
      h += '</div>';

      // QW
      h += '<div class="round-side side-qw">';
      h += '<div class="side-title">Qwen3.5';
      if (it.qw_w) h += ' <span style="font-weight:400;font-size:11px;color:#86909c">(' + it.qw_w + '字)</span>';
      h += '</div>';
      h += '<div class="round-scores">';
      if (it.qw_obj !== '' && it.qw_obj !== undefined) h += '<span class="score-badge obj">客观 ' + esc(it.qw_obj) + '</span>';
      if (it.qw_sub !== '' && it.qw_sub !== undefined) h += '<span class="score-badge sub">主观 ' + esc(it.qw_sub) + '</span>';
      h += '</div>';
      if (it.qw_r) {
        var qwText = esc(it.qw_r);
        if (it.qw_r.length >= 500) qwText += '...';
        h += '<div class="round-reply">' + qwText + '</div>';
      }
      h += '</div>';

      h += '</div>'; // round-compare
      h += '</div>'; // round-block
    }

    h += '</div>'; // sess-block
  }
  list.innerHTML = h;

  var totalPages = Math.ceil(sessFiltered.length / sessPerPage) || 1;
  var ph = '<span>第 ' + (sessPage + 1) + ' / ' + totalPages + ' 页</span>';
  ph += '<button onclick="goPage(-1)"' + (sessPage <= 0 ? ' disabled' : '') + '>上一页</button>';
  ph += '<button onclick="goPage(1)"' + (sessPage >= totalPages - 1 ? ' disabled' : '') + '>下一页</button>';
  document.getElementById('casePager').innerHTML = ph;
}

function goPage(d) {
  var totalPages = Math.ceil(sessFiltered.length / sessPerPage) || 1;
  sessPage = Math.max(0, Math.min(sessPage + d, totalPages - 1));
  renderCases();
  window.scrollTo(0, document.getElementById('tabCases').offsetTop);
}

filterCases();
"""

last_script_end = html.rfind('</script>')
html = html[:last_script_end] + case_js + '\n' + html[last_script_end:]
print("Added JS")

with open('viz_final_v5.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Final: {len(html)} bytes ({len(html)/1024:.0f} KB)")
