#!/usr/bin/env python3
"""
Build viz_final_v10.html:
- Based on viz_final_v9.html (v8 + front-end import)
- Add a top-level project tab bar to switch between:
  Tab 1: "3月流式竞对【豆包 vs Qwen3.5】" (existing content)
  Tab 2: "【LLM竞品评估】豆包随机session题库..." (new dashboard, no cases)
"""
import json, re, os

# ============================================================
# 1. Parse LLM evaluation stats data
# ============================================================
with open('_mira_lark__read_lark_content_33f74c7b859d.json', 'r') as f:
    raw = json.load(f)
text = json.loads(raw[0]['text'])['content']
stat_lines = text.strip().split('\n')

def parse_row(line):
    parts = line.split('|')
    if len(parts) > 2:
        return [p.strip() for p in parts[1:-1]]
    return []

# Find GSB rows (start of each stats block)
gsb_rows = []
for i, line in enumerate(stat_lines):
    cells = parse_row(line)
    if len(cells) >= 10 and 'Session' in str(cells[0]) and 'GSB' in str(cells[1]):
        gsb_rows.append(i)

def find_section_title(gsb_line):
    for j in range(gsb_line - 5, gsb_line):
        if j < 0: continue
        combined = ' '.join(str(c) for c in parse_row(stat_lines[j])[:3])
        m = re.search(r'(\S+)\s+(\d+)题', combined)
        if m: return m.group(1), int(m.group(2))
    return None, 0

def extract_block(gsb_line_idx):
    metrics = {}
    metric_names = ['GSB', 'p-value', '可用率', '满分率', '劝退率', '均分', '回复字数']
    for mi, mname in enumerate(metric_names):
        ri = gsb_line_idx + mi
        if ri >= len(stat_lines): break
        cells = parse_row(stat_lines[ri])
        if len(cells) >= 10:
            metrics[mname] = {
                '豆包_客观': cells[2], '千问_客观': cells[3],
                'Gemini_客观': cells[4], 'GPT_客观': cells[5],
                '豆包_主客观': cells[6], '千问_主客观': cells[7],
                'Gemini_主客观': cells[8], 'GPT_主客观': cells[9],
            }
    return metrics

# Extract all sections
llm_sections = {}
for gi in gsb_rows:
    cat, count = find_section_title(gi)
    if not cat: continue
    llm_sections[cat] = {'count': count, 'metrics': extract_block(gi)}

# Volume
llm_volume = {'整体': 203}
for i in range(12, 22):
    if i >= len(stat_lines): break
    cells = parse_row(stat_lines[i])
    if len(cells) >= 14 and cells[12] and cells[13]:
        try: llm_volume[cells[12]] = int(cells[13])
        except: pass

# Word count summary
llm_wordcount = {}
for i in range(73, 85):
    if i >= len(stat_lines): break
    cells = parse_row(stat_lines[i])
    if len(cells) >= 5 and cells[0] in ['整体','知识','写作','语言','闲聊']:
        try:
            llm_wordcount[cells[0]] = {
                '豆包': int(cells[1]) if cells[1] and cells[1] != '-' else 0,
                '千问': int(cells[2]) if cells[2] and cells[2] != '-' else 0,
                'Gemini': int(cells[3]) if cells[3] and cells[3] != '-' else 0,
                'GPT': int(cells[4]) if cells[4] and cells[4] != '-' else 0,
            }
        except: pass

print('LLM sections:', list(llm_sections.keys()))
print('LLM volume:', llm_volume)
print('LLM wordcount:', llm_wordcount)

LLM_DATA = {
    'sections': llm_sections,
    'volume': llm_volume,
    'wordcount': llm_wordcount
}

# ============================================================
# 2. Load viz_final_v9.html
# ============================================================
with open('viz_final_v9.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 3. Add project tab CSS
# ============================================================
project_tab_css = """<style>
/* Project-level tab bar */
.project-tabs{display:flex;gap:0;background:#1d2129;padding:0 24px;justify-content:center;position:sticky;top:0;z-index:100}
.project-tab{padding:12px 28px;color:#a6a9ad;font-size:14px;font-weight:500;cursor:pointer;border-bottom:3px solid transparent;transition:all .2s;white-space:nowrap}
.project-tab:hover{color:#c9cdd4}
.project-tab.active{color:#fff;border-bottom-color:#165dff}
.project-panel{display:none}
.project-panel.active{display:block}
/* LLM eval specific */
.llm-header{text-align:center;padding:32px 20px 16px}
.llm-header h1{font-size:22px;font-weight:700;color:#1d2129;margin:0 0 8px}
.llm-header .llm-sub{font-size:13px;color:#86909c}
.llm-section{margin:20px auto;max-width:1200px;padding:0 20px}
.llm-section-title{font-size:16px;font-weight:600;color:#1d2129;margin:24px 0 12px;padding-left:12px;border-left:3px solid #165dff}
.llm-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:20px}
.llm-card{background:#fff;border-radius:10px;padding:16px 18px;border:1px solid #e5e6eb}
.llm-card .card-title{font-size:13px;color:#86909c;margin-bottom:10px;font-weight:500}
.llm-metric-table{width:100%;border-collapse:collapse;font-size:12px}
.llm-metric-table th{text-align:left;color:#86909c;font-weight:500;padding:4px 6px;border-bottom:1px solid #f2f3f5}
.llm-metric-table td{padding:4px 6px;color:#4e5969}
.llm-metric-table td.val-good{color:#00b42a;font-weight:600}
.llm-metric-table td.val-bad{color:#f53f3f;font-weight:600}
.llm-metric-table td.val-neutral{color:#4e5969}
.llm-metric-table tr:hover{background:#f7f8fa}
.llm-vol-bar{display:flex;align-items:center;gap:8px;margin:4px 0}
.llm-vol-label{min-width:40px;font-size:12px;color:#4e5969;text-align:right}
.llm-vol-track{flex:1;height:20px;background:#f2f3f5;border-radius:4px;overflow:hidden;position:relative}
.llm-vol-fill{height:100%;border-radius:4px;display:flex;align-items:center;justify-content:flex-end;padding-right:6px;font-size:11px;color:#fff;font-weight:500;min-width:24px}
.llm-overview-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.llm-ov-card{background:#fff;border-radius:10px;padding:14px 16px;border:1px solid #e5e6eb;text-align:center}
.llm-ov-card .ov-name{font-size:13px;color:#86909c;margin-bottom:6px}
.llm-ov-card .ov-val{font-size:20px;font-weight:700;color:#1d2129}
.llm-ov-card .ov-sub{font-size:11px;color:#86909c;margin-top:2px}
.llm-filter-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
.llm-filter-row .label{font-size:13px;color:#4e5969;font-weight:500;margin-right:4px}
.llm-fbtn{padding:4px 14px;border-radius:6px;border:1px solid #e5e6eb;background:#fff;font-size:12px;color:#4e5969;cursor:pointer;transition:all .15s}
.llm-fbtn:hover{border-color:#165dff;color:#165dff}
.llm-fbtn.active{background:#165dff;color:#fff;border-color:#165dff}
.llm-dim-toggle{display:flex;gap:0;margin-bottom:16px}
.llm-dim-btn{padding:6px 20px;border:1px solid #e5e6eb;background:#fff;font-size:13px;color:#4e5969;cursor:pointer;transition:all .15s}
.llm-dim-btn:first-child{border-radius:6px 0 0 6px}
.llm-dim-btn:last-child{border-radius:0 6px 6px 0}
.llm-dim-btn.active{background:#165dff;color:#fff;border-color:#165dff}
.chart-container-llm{background:#fff;border-radius:10px;padding:16px;border:1px solid #e5e6eb;margin-bottom:16px}
.chart-container-llm .chart-title{font-size:14px;font-weight:600;color:#1d2129;margin-bottom:12px}
</style>"""
html = html.replace('</head>', project_tab_css + '\n</head>')

# ============================================================
# 4. Wrap existing content in project panel, add project tabs + LLM panel
# ============================================================

# Find the <body> content start - the main wrapper div
body_start = html.find('<body')
body_tag_end = html.find('>', body_start) + 1

# Find the first <div class="wrap"> or similar main container
wrap_start = html.find('<div class="wrap">', body_tag_end)
if wrap_start < 0:
    wrap_start = html.find('<div', body_tag_end)

# Insert project tabs before the wrap div
project_tabs_html = """
<div class="project-tabs" id="projectTabs">
<div class="project-tab active" data-project="proj1" onclick="switchProject(this)">3\u6708\u6d41\u5f0f\u7ade\u5bf9\u3010\u8c46\u5305 vs Qwen3.5\u3011</div>
<div class="project-tab" data-project="proj2" onclick="switchProject(this)">LLM\u7ade\u54c1\u8bc4\u4f30\uff5c\u8c46\u5305 vs \u5343\u95ee3 vs Gemini 3 Pro vs GPT5.2\uff5c26\u5e741\u6708</div>
</div>
<div id="proj1" class="project-panel active">
"""

html = html[:wrap_start] + project_tabs_html + html[wrap_start:]

# Find the SheetJS script block (near end) and close proj1 panel before it, add proj2 panel
sheetjs_marker = '/* SheetJS xlsx.full.min.js */'
sheetjs_pos = html.find(sheetjs_marker)
# Go back to find the <script> tag
script_start = html.rfind('<script>', 0, sheetjs_pos)

# LLM panel HTML
llm_panel_html = """
</div><!-- end proj1 -->
<div id="proj2" class="project-panel">
<div class="llm-header">
<h1>\u3010LLM\u7ade\u54c1\u8bc4\u4f30\u3011\u8c46\u5305\u968f\u673asession\u9898\u5e93</h1>
<div class="llm-sub">\u8c46\u5305 vs \u5343\u95ee3 vs Gemini 3 Pro vs GPT5.2 \u00b7 26\u5e741\u6708 \u00b7 \u6570\u636e\u6765\u6e90: <a href="https://bytedance.larkoffice.com/sheets/Bduwsms4ZhxdNNti0xecqkWinYd" target="_blank" style="color:#165dff">\u98de\u4e66\u8868\u683c</a></div>
</div>
<div class="llm-section">

<!-- Filter row: dimension toggle -->
<div class="llm-filter-row">
<span class="label">\u8bc4\u5206\u7ef4\u5ea6</span>
<button class="llm-fbtn active" onclick="switchLlmDim(this,'obj')">\u5ba2\u89c2</button>
<button class="llm-fbtn" onclick="switchLlmDim(this,'sub')">\u4e3b\u89c2+\u5ba2\u89c2</button>
</div>

<!-- Filter row: category -->
<div class="llm-filter-row" id="llmCatFilter">
<span class="label">\u5206\u7c7b</span>
</div>

<!-- Overview cards (word count) -->
<div class="llm-section-title">\u56de\u590d\u5b57\u6570\u6982\u89c8</div>
<div id="llmWordCount" class="llm-overview-grid"></div>

<!-- Volume distribution -->
<div class="llm-section-title">\u9898\u91cf\u5206\u5e03</div>
<div id="llmVolume"></div>

<!-- Metrics cards -->
<div class="llm-section-title">\u8bc4\u4f30\u6307\u6807</div>
<div id="llmMetrics" class="llm-card-grid"></div>

<!-- Bar charts -->
<div class="llm-section-title">\u6307\u6807\u5bf9\u6bd4\u56fe\u8868</div>
<div id="llmCharts"></div>

</div>
</div><!-- end proj2 -->
"""

html = html[:script_start] + llm_panel_html + '\n' + html[script_start:]

# ============================================================
# 5. Add LLM dashboard JS (before </body>)
# ============================================================
llm_data_json = json.dumps(LLM_DATA, ensure_ascii=False)

llm_js = """
<script>
/* === Project Tab Switching === */
function switchProject(el) {
  var tabs = document.querySelectorAll('.project-tab');
  var panels = document.querySelectorAll('.project-panel');
  for (var i = 0; i < tabs.length; i++) tabs[i].className = 'project-tab';
  for (var i = 0; i < panels.length; i++) panels[i].className = 'project-panel';
  el.className = 'project-tab active';
  var target = el.getAttribute('data-project');
  document.getElementById(target).className = 'project-panel active';
}

/* === LLM Eval Dashboard === */
var LLM_DATA = """ + llm_data_json + """;
var llmDim = 'obj'; // 'obj' or 'sub'
var llmCat = '\\u6574\\u4f53'; // current category

var llmChartInstances = [];

function switchLlmDim(el, dim) {
  llmDim = dim;
  var btns = el.parentNode.querySelectorAll('.llm-fbtn');
  for (var i = 0; i < btns.length; i++) btns[i].className = 'llm-fbtn';
  el.className = 'llm-fbtn active';
  renderLlmDashboard();
}

function switchLlmCat(el, cat) {
  llmCat = cat;
  var btns = el.parentNode.querySelectorAll('.llm-fbtn');
  for (var i = 0; i < btns.length; i++) btns[i].className = 'llm-fbtn';
  el.className = 'llm-fbtn active';
  renderLlmDashboard();
}

function initLlmCatFilter() {
  var wrap = document.getElementById('llmCatFilter');
  var cats = Object.keys(LLM_DATA.sections);
  for (var i = 0; i < cats.length; i++) {
    var b = document.createElement('button');
    b.className = 'llm-fbtn' + (cats[i] === llmCat ? ' active' : '');
    b.textContent = cats[i];
    b.setAttribute('data-cat', cats[i]);
    b.onclick = (function(c) { return function() { switchLlmCat(this, c); }; })(cats[i]);
    wrap.appendChild(b);
  }
}

function renderLlmWordCount() {
  var el = document.getElementById('llmWordCount');
  var wc = LLM_DATA.wordcount[llmCat] || LLM_DATA.wordcount['\\u6574\\u4f53'] || {};
  var comps = ['\\u8c46\\u5305', '\\u5343\\u95ee', 'Gemini', 'GPT'];
  var colors = ['#165dff', '#f77234', '#0fc6c2', '#722ed1'];
  var h = '';
  for (var i = 0; i < comps.length; i++) {
    var v = wc[comps[i]] || 0;
    h += '<div class="llm-ov-card" style="border-top:3px solid ' + colors[i] + '">';
    h += '<div class="ov-name">' + comps[i] + '</div>';
    h += '<div class="ov-val">' + v + '</div>';
    h += '<div class="ov-sub">\\u5e73\\u5747\\u56de\\u590d\\u5b57\\u6570</div>';
    h += '</div>';
  }
  el.innerHTML = h;
}

function renderLlmVolume() {
  var el = document.getElementById('llmVolume');
  var vol = LLM_DATA.volume;
  var cats = Object.keys(vol);
  var maxV = 0;
  for (var i = 0; i < cats.length; i++) { if (vol[cats[i]] > maxV) maxV = vol[cats[i]]; }
  var colors = ['#165dff', '#36cfc9', '#f7ba1e', '#f77234', '#722ed1'];
  var h = '';
  for (var i = 0; i < cats.length; i++) {
    var pct = maxV > 0 ? Math.round(vol[cats[i]] / maxV * 100) : 0;
    h += '<div class="llm-vol-bar">';
    h += '<span class="llm-vol-label">' + cats[i] + '</span>';
    h += '<div class="llm-vol-track">';
    h += '<div class="llm-vol-fill" style="width:' + pct + '%;background:' + colors[i % colors.length] + '">' + vol[cats[i]] + '</div>';
    h += '</div></div>';
  }
  el.innerHTML = h;
}

function fmtVal(v) {
  if (!v || v === '-' || v === '#ERROR' || v.indexOf('#') === 0) return '-';
  return v;
}

function valClass(v, metric) {
  if (!v || v === '-' || v.indexOf('#') === 0) return 'val-neutral';
  /* For GSB: positive is good for 豆包 */
  if (metric === 'GSB') {
    var f = parseFloat(v);
    if (isNaN(f)) return 'val-neutral';
    return f > 0 ? 'val-good' : (f < 0 ? 'val-bad' : 'val-neutral');
  }
  return 'val-neutral';
}

function renderLlmMetrics() {
  var el = document.getElementById('llmMetrics');
  var sec = LLM_DATA.sections[llmCat];
  if (!sec || !sec.metrics) { el.innerHTML = '<div style="padding:20px;color:#86909c">\\u65e0\\u6570\\u636e</div>'; return; }
  var m = sec.metrics;
  var suffix = llmDim === 'obj' ? '_\\u5ba2\\u89c2' : '_\\u4e3b\\u5ba2\\u89c2';
  var metrics = ['GSB', 'p-value', '\\u53ef\\u7528\\u7387', '\\u6ee1\\u5206\\u7387', '\\u52dd\\u9000\\u7387', '\\u5747\\u5206'];
  var comps = ['\\u8c46\\u5305', '\\u5343\\u95ee', 'Gemini', 'GPT'];
  var h = '';

  for (var mi = 0; mi < metrics.length; mi++) {
    var mName = metrics[mi];
    var mKey = mName === '\\u52dd\\u9000\\u7387' ? '\\u529d\\u9000\\u7387' : mName;
    var mData = m[mKey];
    if (!mData) continue;
    h += '<div class="llm-card">';
    h += '<div class="card-title">' + mName + '</div>';
    h += '<table class="llm-metric-table"><thead><tr><th>\\u7ade\\u54c1</th><th>\\u6570\\u503c</th></tr></thead><tbody>';
    for (var ci = 0; ci < comps.length; ci++) {
      var key = comps[ci] + suffix;
      var v = fmtVal(mData[key] || '-');
      var cls = valClass(v, mName);
      h += '<tr><td>' + comps[ci] + '</td><td class="' + cls + '">' + v + '</td></tr>';
    }
    h += '</tbody></table></div>';
  }

  /* Word count card */
  var wcData = m['\\u56de\\u590d\\u5b57\\u6570'];
  if (wcData) {
    h += '<div class="llm-card">';
    h += '<div class="card-title">\\u56de\\u590d\\u5b57\\u6570</div>';
    h += '<table class="llm-metric-table"><thead><tr><th>\\u7ade\\u54c1</th><th>\\u5b57\\u6570</th></tr></thead><tbody>';
    for (var ci = 0; ci < comps.length; ci++) {
      var key = comps[ci] + suffix;
      var v = fmtVal(wcData[key] || '-');
      h += '<tr><td>' + comps[ci] + '</td><td>' + v + '</td></tr>';
    }
    h += '</tbody></table></div>';
  }

  el.innerHTML = h;
}

function renderLlmCharts() {
  var el = document.getElementById('llmCharts');
  /* Destroy old charts */
  for (var i = 0; i < llmChartInstances.length; i++) {
    try { llmChartInstances[i].destroy(); } catch(e) {}
  }
  llmChartInstances = [];

  var sec = LLM_DATA.sections[llmCat];
  if (!sec || !sec.metrics) { el.innerHTML = ''; return; }
  var m = sec.metrics;
  var suffix = llmDim === 'obj' ? '_\\u5ba2\\u89c2' : '_\\u4e3b\\u5ba2\\u89c2';
  var chartMetrics = ['\\u53ef\\u7528\\u7387', '\\u6ee1\\u5206\\u7387', '\\u529d\\u9000\\u7387', '\\u5747\\u5206'];
  var comps = ['\\u8c46\\u5305', '\\u5343\\u95ee', 'Gemini', 'GPT'];
  var colors = ['#165dff', '#f77234', '#0fc6c2', '#722ed1'];

  var h = '';
  for (var mi = 0; mi < chartMetrics.length; mi++) {
    h += '<div class="chart-container-llm">';
    h += '<div class="chart-title">' + chartMetrics[mi] + '</div>';
    h += '<canvas id="llmChart_' + mi + '" height="200"></canvas>';
    h += '</div>';
  }
  el.innerHTML = h;

  /* Render charts using Chart.js */
  if (typeof Chart === 'undefined') return;

  for (var mi = 0; mi < chartMetrics.length; mi++) {
    var mKey = chartMetrics[mi];
    var mData = m[mKey];
    if (!mData) continue;
    var vals = [];
    for (var ci = 0; ci < comps.length; ci++) {
      var raw = mData[comps[ci] + suffix] || '';
      var fv = parseFloat(raw);
      vals.push(isNaN(fv) ? null : fv * (raw.indexOf('%') >= 0 ? 1 : 100));
    }
    var canvas = document.getElementById('llmChart_' + mi);
    if (!canvas) continue;
    var ctx = canvas.getContext('2d');
    var chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: comps,
        datasets: [{
          data: vals,
          backgroundColor: colors,
          borderRadius: 6,
          barPercentage: 0.5
        }]
      },
      plugins: [ChartDataLabels],
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          datalabels: {
            anchor: 'end', align: 'end', font: { size: 11, weight: 'bold' },
            formatter: function(v) { return v !== null ? v.toFixed(1) + '%' : '-'; }
          }
        },
        scales: {
          y: { beginAtZero: true, ticks: { callback: function(v) { return v + '%'; } } },
          x: { grid: { display: false } }
        }
      }
    });
    llmChartInstances.push(chart);
  }

  /* GSB chart (grouped bar: 豆包 vs each competitor) */
  var gsbData = m['GSB'];
  if (gsbData) {
    var gsbH = '<div class="chart-container-llm">';
    gsbH += '<div class="chart-title">GSB (\\u8c46\\u5305 vs \\u5404\\u7ade\\u54c1)</div>';
    gsbH += '<canvas id="llmChart_gsb" height="200"></canvas>';
    gsbH += '</div>';
    el.innerHTML += gsbH;

    var gsbLabels = ['vs \\u5343\\u95ee', 'vs Gemini', 'vs GPT'];
    var gsbComps = ['\\u5343\\u95ee', 'Gemini', 'GPT'];
    var gsbVals = [];
    for (var gi = 0; gi < gsbComps.length; gi++) {
      var raw = gsbData[gsbComps[gi] + suffix] || '';
      var fv = parseFloat(raw);
      gsbVals.push(isNaN(fv) ? null : fv * (raw.indexOf('%') >= 0 ? 1 : 100));
    }
    var gsbCanvas = document.getElementById('llmChart_gsb');
    if (gsbCanvas) {
      var gsbCtx = gsbCanvas.getContext('2d');
      var gsbChart = new Chart(gsbCtx, {
        type: 'bar',
        data: {
          labels: gsbLabels,
          datasets: [{
            label: 'GSB',
            data: gsbVals,
            backgroundColor: gsbVals.map(function(v) { return v !== null && v >= 0 ? '#00b42a' : '#f53f3f'; }),
            borderRadius: 6,
            barPercentage: 0.4
          }]
        },
        plugins: [ChartDataLabels],
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            datalabels: {
              anchor: 'end', align: 'end', font: { size: 11, weight: 'bold' },
              formatter: function(v) { return v !== null ? (v > 0 ? '+' : '') + v.toFixed(2) + '%' : '-'; }
            }
          },
          scales: {
            y: { ticks: { callback: function(v) { return v + '%'; } } },
            x: { grid: { display: false } }
          }
        }
      });
      llmChartInstances.push(gsbChart);
    }
  }
}

function renderLlmDashboard() {
  renderLlmWordCount();
  renderLlmVolume();
  renderLlmMetrics();
  renderLlmCharts();
}

initLlmCatFilter();
renderLlmDashboard();
</script>
"""

# Insert before </body>
body_end = html.rfind('</body>')
html = html[:body_end] + llm_js + '\n' + html[body_end:]

# ============================================================
# 6. Write output
# ============================================================
output = 'viz_final_v10.html'
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(output)
print('Built: %s (%d bytes, %.1f MB)' % (output, size, size/1024/1024))
print('Done!')
