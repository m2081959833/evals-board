#!/usr/bin/env python3
"""Add Case Explorer (案例探查) tab to viz_final_v3.html
Reference: left/right comparison layout with filters
"""
import json, re

# Load case data
with open('cases_data.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Clean up categories
for c in cases:
    if c['cat'] == '\\' or not c['cat']:
        c['cat'] = '其他'
    # Normalize category names
    c['cat'] = c['cat'].replace('VLM（通用）', 'VLM通用').replace('VLM（教育）', 'VLM教育')

# Get unique values for filters
all_cats = sorted(set(c['cat'] for c in cases))
all_sources = sorted(set(c['src'] for c in cases if c['src']))

# Compute GSB label for display
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

# Serialize compact JSON for embedding
cases_json = json.dumps(cases, ensure_ascii=False, separators=(',',':'))
print(f"Cases JSON: {len(cases_json)} bytes, {len(cases)} records")

# Load current HTML
with open('viz_final_v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ---- 1. Add Case Explorer CSS ----
case_css = """
/* Case Explorer */
.case-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center}
.case-filters select{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;background:#fff;min-width:120px;cursor:pointer}
.case-filters input{padding:6px 12px;border:1px solid #e5e6eb;border-radius:8px;font-size:13px;color:#4e5969;flex:1;min-width:200px}
.case-count{font-size:13px;color:#86909c;margin-left:auto;white-space:nowrap}
.case-list{display:flex;flex-direction:column;gap:16px}
.case-item{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);overflow:hidden}
.case-header{background:#1d2129;color:#fff;padding:14px 20px;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.case-tag{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500}
.case-tag.t-id{background:#f2f3f5;color:#1d2129}
.case-tag.t-cat{background:#e8f3ff;color:#165dff}
.case-tag.t-src{background:#fff7e6;color:#d46b08}
.case-tag.t-gsb.gsb-win{background:#e8ffea;color:#00b42a}
.case-tag.t-gsb.gsb-lose{background:#ffece8;color:#f53f3f}
.case-tag.t-gsb.gsb-tie{background:#f2f3f5;color:#86909c}
.case-prompt{padding:12px 20px;font-size:14px;color:#1d2129;border-bottom:1px solid #f2f3f5;line-height:1.6;max-height:120px;overflow-y:auto}
.case-prompt .link-icon{cursor:pointer;color:#86909c;margin-left:6px;font-size:12px}
.case-compare{display:flex}
.case-side{flex:1;padding:16px 20px;min-width:0}
.case-side:first-child{border-right:1px solid #f2f3f5}
.side-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:6px}
.side-name{font-size:14px;font-weight:600;display:flex;align-items:center;gap:6px}
.side-name .icon-db{color:#165dff}
.side-name .icon-qw{color:#f53f3f}
.score-badges{display:flex;gap:6px}
.score-badge{display:inline-flex;align-items:center;gap:3px;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:600}
.score-badge.obj{background:#e8f3ff;color:#165dff}
.score-badge.sub{background:#fff0f0;color:#f53f3f}
.word-count{font-size:12px;color:#86909c}
.side-body{font-size:13px;color:#4e5969;line-height:1.7;max-height:300px;overflow-y:auto;white-space:pre-wrap;word-break:break-word}
.case-footer{display:flex;gap:16px;padding:8px 20px;background:#fafafa;border-top:1px solid #f2f3f5;font-size:12px;color:#86909c}
.case-footer span{display:flex;align-items:center;gap:4px}
.case-pager{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:20px;padding:16px 0}
.case-pager button{padding:6px 16px;border:1px solid #e5e6eb;border-radius:8px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969}
.case-pager button:disabled{opacity:.4;cursor:not-allowed}
.case-pager button:hover:not(:disabled){border-color:#165dff;color:#165dff}
.case-pager .page-info{font-size:13px;color:#86909c}
.no-data{text-align:center;padding:60px 20px;color:#86909c;font-size:14px}
"""

# Insert CSS before closing </style>
html = html.replace('</style>', case_css + '</style>', 1)

# ---- 2. Add Case Explorer HTML tab panel ----
case_html = """
<div id="tabCases" class="tab-panel">
  <div class="case-filters" id="caseFilters">
    <input type="text" id="caseSearch" placeholder="搜索题目内容或ID..." oninput="filterCases()">
    <select id="cfCat" onchange="filterCases()"><option value="">全部分类</option></select>
    <select id="cfSrc" onchange="filterCases()"><option value="">全部端</option></select>
    <select id="cfGsb" onchange="filterCases()">
      <option value="">全部GSB</option>
      <option value="win">豆包胜</option>
      <option value="lose">Qwen胜</option>
      <option value="tie">平局</option>
    </select>
    <span class="case-count" id="caseCount"></span>
  </div>
  <div class="case-list" id="caseList"></div>
  <div class="case-pager" id="casePager"></div>
</div>
"""

# Insert before the closing </div> of page-container, right after tabCharts panel
# Find the end of tabCharts panel
tab_charts_end = html.find('</div><!-- /tabCharts -->')
if tab_charts_end == -1:
    # Try alternate ending
    tab_charts_end = html.find('</div>\n\n<div id="tabCases"')
    if tab_charts_end == -1:
        # Find by looking for the tabCases div (which may already exist as empty)
        existing_cases = html.find('<div id="tabCases"')
        if existing_cases >= 0:
            # Replace existing empty tabCases
            end_existing = html.find('</div>', existing_cases) + 6
            html = html[:existing_cases] + case_html + html[end_existing:]
            print("Replaced existing tabCases panel")
        else:
            # Insert before the scripts
            last_script = html.rfind('<script>')
            html = html[:last_script] + case_html + '\n' + html[last_script:]
            print("Inserted tabCases before scripts")
else:
    html = html[:tab_charts_end + len('</div><!-- /tabCharts -->')] + '\n' + case_html + html[tab_charts_end + len('</div><!-- /tabCharts -->'):]
    print("Inserted tabCases after tabCharts")

# ---- 3. Add Case Explorer JS ----
case_js = """
/* ---- Case Explorer ---- */
var CASES = __CASES_PLACEHOLDER__;
var caseFiltered = CASES.slice();
var casePage = 0;
var casePageSize = 10;

(function initCaseFilters() {
  var cats = {}, srcs = {};
  for (var i = 0; i < CASES.length; i++) {
    if (CASES[i].cat) cats[CASES[i].cat] = 1;
    if (CASES[i].src) srcs[CASES[i].src] = 1;
  }
  var catSel = document.getElementById('cfCat');
  var keys = Object.keys(cats).sort();
  for (var i = 0; i < keys.length; i++) {
    var o = document.createElement('option');
    o.value = keys[i]; o.textContent = keys[i];
    catSel.appendChild(o);
  }
  var srcSel = document.getElementById('cfSrc');
  var skeys = Object.keys(srcs).sort();
  for (var i = 0; i < skeys.length; i++) {
    var o = document.createElement('option');
    o.value = skeys[i]; o.textContent = skeys[i];
    srcSel.appendChild(o);
  }
})();

function filterCases() {
  var q = (document.getElementById('caseSearch').value || '').toLowerCase();
  var cat = document.getElementById('cfCat').value;
  var src = document.getElementById('cfSrc').value;
  var gsb = document.getElementById('cfGsb').value;
  
  caseFiltered = [];
  for (var i = 0; i < CASES.length; i++) {
    var c = CASES[i];
    if (cat && c.cat !== cat) continue;
    if (src && c.src !== src) continue;
    if (gsb === 'win' && c.gsb_cls !== 'gsb-win') continue;
    if (gsb === 'lose' && c.gsb_cls !== 'gsb-lose') continue;
    if (gsb === 'tie' && c.gsb_cls !== 'gsb-tie') continue;
    if (q && c.q.toLowerCase().indexOf(q) === -1 && c.id.toLowerCase().indexOf(q) === -1) continue;
    caseFiltered.push(c);
  }
  casePage = 0;
  renderCases();
}

function renderCases() {
  var list = document.getElementById('caseList');
  var pager = document.getElementById('casePager');
  var countEl = document.getElementById('caseCount');
  
  countEl.textContent = '共 ' + caseFiltered.length + ' 条';
  
  if (caseFiltered.length === 0) {
    list.innerHTML = '<div class="no-data">没有匹配的案例</div>';
    pager.innerHTML = '';
    return;
  }
  
  var totalPages = Math.ceil(caseFiltered.length / casePageSize);
  var start = casePage * casePageSize;
  var end = Math.min(start + casePageSize, caseFiltered.length);
  var page = caseFiltered.slice(start, end);
  
  var h = '';
  for (var i = 0; i < page.length; i++) {
    var c = page[i];
    h += '<div class="case-item">';
    h += '<div class="case-header">';
    h += '<span class="case-tag t-id">' + esc(c.id) + '</span>';
    h += '<span class="case-tag t-cat">' + esc(c.cat) + '</span>';
    if (c.src) h += '<span class="case-tag t-src">' + esc(c.src) + '</span>';
    if (c.turn) h += '<span class="case-tag t-id">' + esc(c.turn) + '</span>';
    if (c.gsb_label) h += '<span class="case-tag t-gsb ' + c.gsb_cls + '">' + esc(c.gsb_label) + '</span>';
    h += '</div>';
    h += '<div class="case-prompt">' + esc(c.q) + '</div>';
    h += '<div class="case-compare">';
    
    // 豆包 side
    h += '<div class="case-side">';
    h += '<div class="side-header">';
    h += '<span class="side-name"><span class="icon-db">🟦</span> 豆包（左）</span>';
    h += '<div class="score-badges">';
    if (c.db_obj) h += '<span class="score-badge obj">客观 ' + esc(c.db_obj) + '</span>';
    if (c.db_sub) h += '<span class="score-badge sub">主观 ' + esc(c.db_sub) + '</span>';
    h += '</div>';
    if (c.db_w) h += '<span class="word-count">' + c.db_w + '字</span>';
    h += '</div>';
    h += '</div>';
    
    // Qwen side
    h += '<div class="case-side">';
    h += '<div class="side-header">';
    h += '<span class="side-name"><span class="icon-qw">🟥</span> Qwen（右）</span>';
    h += '<div class="score-badges">';
    if (c.qw_obj) h += '<span class="score-badge obj">客观 ' + esc(c.qw_obj) + '</span>';
    if (c.qw_sub) h += '<span class="score-badge sub">主观 ' + esc(c.qw_sub) + '</span>';
    h += '</div>';
    if (c.qw_w) h += '<span class="word-count">' + c.qw_w + '字</span>';
    h += '</div>';
    h += '</div>';
    
    h += '</div>'; // case-compare
    
    // Footer
    h += '<div class="case-footer">';
    h += '<span>Session: ' + esc(c.sid) + '</span>';
    h += '<span>轮次: ' + c.r + '</span>';
    h += '</div>';
    
    h += '</div>'; // case-item
  }
  
  list.innerHTML = h;
  
  // Pager
  var ph = '';
  ph += '<button onclick="goPage(-1)"' + (casePage <= 0 ? ' disabled' : '') + '>上一页</button>';
  ph += '<span class="page-info">' + (casePage + 1) + ' / ' + totalPages + '</span>';
  ph += '<button onclick="goPage(1)"' + (casePage >= totalPages - 1 ? ' disabled' : '') + '>下一页</button>';
  pager.innerHTML = ph;
}

function goPage(d) {
  var totalPages = Math.ceil(caseFiltered.length / casePageSize);
  casePage = Math.max(0, Math.min(casePage + d, totalPages - 1));
  renderCases();
  /* scroll to top of case list */
  var el = document.getElementById('caseFilters');
  if (el) el.scrollIntoView({behavior: 'smooth'});
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
"""

# Replace placeholder with actual data
case_js = case_js.replace('__CASES_PLACEHOLDER__', cases_json)

# Insert JS before the closing </script> of the last script block
last_script_close = html.rfind('</script>')
html = html[:last_script_close] + '\n' + case_js + '\n' + html[last_script_close:]

# ---- 4. Make tab switching work for Cases tab ----
# Check if existing tab switch code handles tabCases
if 'tabCases' not in html.split('<script>')[-1].split('filterCases')[0]:
    # Need to ensure the tab nav click handler shows tabCases
    print("Tab switching should already work with existing nav code")

# Save
with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nGenerated viz_final_v3.html: {len(html)} bytes")
