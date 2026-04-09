#!/usr/bin/env python3
"""Build the final visualization HTML with data from Excel."""
import json

with open('viz_data_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('chart.umd.min.js', 'r', encoding='utf-8') as f:
    chartjs = f.read()

with open('chartjs-plugin-datalabels.min.js', 'r', encoding='utf-8') as f:
    datalabels = f.read()

data_json = json.dumps(data, ensure_ascii=False)

# Build the complete HTML
html_top = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>3月流式竞对【豆包 vs Qwen3.5】</title>
<script>
'''

html_after_chartjs = '''
</script>
<script>
'''

html_after_datalabels = '''
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f5f6fa;color:#1d2129;padding:20px}
.header{text-align:center;margin-bottom:24px}
.header h1{font-size:22px;font-weight:700;color:#1d2129}
.header p{font-size:13px;color:#86909c;margin-top:4px}
.top-nav{display:flex;gap:12px;margin-bottom:16px;border-bottom:2px solid #e5e6eb;padding-bottom:0}
.top-nav-item{padding:8px 18px;cursor:pointer;font-size:14px;font-weight:500;color:#4e5969;border-bottom:2px solid transparent;margin-bottom:-2px;transition:.2s}
.top-nav-item.active{color:#165dff;border-bottom-color:#165dff}
.top-nav-item:hover{color:#165dff}
.tab-panel{display:none}
.tab-panel.active{display:block}
.filter-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:12px}
.filter-row .label{font-size:13px;color:#86909c;min-width:70px}
.fbtn{padding:4px 14px;border:1px solid #e5e6eb;border-radius:16px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969;transition:.2s}
.fbtn.active{background:#165dff;color:#fff;border-color:#165dff}
.fbtn:hover{border-color:#165dff}
.vol-strip{display:flex;gap:16px;margin-bottom:16px}
.vol-chip{background:#fff;border-radius:8px;padding:12px 20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.vol-chip.c2{background:#f0f5ff}
.vol-num{font-size:22px;font-weight:700;color:#165dff}
.vol-lbl{font-size:12px;color:#86909c;margin-top:2px}
.charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}
.chart-subtitle{font-size:11px;color:#86909c;margin-bottom:8px}
.chart-wrap{position:relative;height:220px}
.legend-note{text-align:center;font-size:12px;color:#86909c;margin-top:4px}
@media(max-width:900px){.charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.charts-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="header">
<h1>3\u6708\u6d41\u5f0f\u7ade\u5bf9\u3010\u8c46\u5305 vs Qwen3.5\u3011</h1>
<p>\u6570\u636e\u6765\u6e90: 3\u6708\u6d41\u5f0f\u7ade\u5bf9 Excel \u00b7 \u751f\u6210\u65f6\u95f4: 2026-04-02</p>
</div>

<div class="top-nav" id="topNav">
<div class="top-nav-item active" data-tab="tabCharts">\u6570\u636e\u770b\u677f</div>
<div class="top-nav-item" data-tab="tabCases">\u6848\u4f8b\u63a2\u67e5</div>
</div>

<div id="tabCharts" class="tab-panel active">
<div class="filter-row" id="fPlatform">
<span class="label">\u6570\u636e\u7aef</span>
<button class="fbtn active" data-v="\u53cc\u7aef\u6574\u4f53">\u53cc\u7aef\u6574\u4f53</button>
<button class="fbtn" data-v="APP">APP</button>
<button class="fbtn" data-v="Web">Web</button>
</div>
<div class="filter-row" id="fScores">
<span class="label">\u8bc4\u5206\u7ef4\u5ea6</span>
<button class="fbtn active" data-v="\u4e3b\u5ba2\u89c2">\u4e3b\u89c2+\u5ba2\u89c2</button>
<button class="fbtn active" data-v="\u5ba2\u89c2">\u5ba2\u89c2</button>
</div>
<div class="filter-row" id="fDim">
<span class="label">\u7edf\u8ba1\u7ef4\u5ea6</span>
<button class="fbtn active" data-v="session">Session\u7ef4\u5ea6</button>
<button class="fbtn" data-v="prompt">Prompt\u7ef4\u5ea6</button>
</div>
<div class="filter-row" id="fCat">
<span class="label">\u9898\u76ee\u7c7b\u578b</span>
</div>
<div class="vol-strip" id="volStrip"></div>
<div class="charts-grid" id="chartsGrid"></div>
</div>

<div id="tabCases" class="tab-panel">
<div style="padding:40px;text-align:center;color:#86909c">\u6848\u4f8b\u63a2\u67e5\u6a21\u5757 (\u5f85\u63a5\u5165\u8bc4\u4f30\u6570\u636e Sheet)</div>
</div>

<script>
'''

html_script = r'''
var DATA = __DATA_PLACEHOLDER__;
var S = DATA.stats;
var V = DATA.volume || {};
var C = {db:'rgba(22,93,255,0.85)', qw:'rgba(255,125,0,0.85)'};
var charts = {};

var st = {
  plat: '\u53cc\u7aef\u6574\u4f53',
  scores: ['\u4e3b\u5ba2\u89c2','\u5ba2\u89c2'],
  dim: 'session',
  cat: '\u6574\u4f53'
};

function pv(s) {
  if (!s || s === '-' || s === '#DIV/0!' || s === '#N/A' || s === '#CALC!' || s === 'None') return null;
  var n = parseFloat(String(s).replace('%',''));
  return isNaN(n) ? null : n;
}

function safeGet(obj, keys) {
  var cur = obj;
  for (var i = 0; i < keys.length; i++) {
    if (cur == null || typeof cur !== 'object') return undefined;
    cur = cur[keys[i]];
  }
  return cur;
}

function barOpts(metric, showLegend) {
  var isPercent = (metric !== '\u56de\u590d\u5b57\u6570' && metric !== 'p-value');
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: !!showLegend, position: 'top', labels: { font: { size: 11 } } },
      datalabels: {
        anchor: 'end',
        align: 'end',
        font: { size: 11, weight: 600 },
        formatter: function(value) {
          if (value === null || value === undefined) return '';
          if (isPercent) return value.toFixed(2) + '%';
          if (metric === 'p-value') return value.toFixed(4);
          return String(value);
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(v) {
            if (isPercent) return v + '%';
            return v;
          },
          font: { size: 11 }
        },
        grid: { color: 'rgba(0,0,0,.06)' }
      },
      x: { ticks: { font: { size: 11 } }, grid: { display: false } }
    }
  };
}

function gsbOpts() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      datalabels: {
        anchor: function(ctx) { return ctx.dataset.data[ctx.dataIndex] >= 0 ? 'end' : 'start'; },
        align: function(ctx) { return ctx.dataset.data[ctx.dataIndex] >= 0 ? 'end' : 'start'; },
        font: { size: 11, weight: 600 },
        formatter: function(value) {
          if (value === null || value === undefined) return '';
          return value.toFixed(2) + '%';
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: function(v) { return v + '%'; },
          font: { size: 11 }
        },
        grid: { color: 'rgba(0,0,0,.06)' }
      },
      x: { ticks: { font: { size: 11 } }, grid: { display: false } }
    }
  };
}

/* top nav */
var topNavItems = document.querySelectorAll('#topNav .top-nav-item');
for (var ti = 0; ti < topNavItems.length; ti++) {
  (function(el) {
    el.onclick = function() {
      for (var j = 0; j < topNavItems.length; j++) topNavItems[j].classList.remove('active');
      var panels = document.querySelectorAll('.tab-panel');
      for (var j = 0; j < panels.length; j++) panels[j].classList.remove('active');
      el.classList.add('active');
      document.getElementById(el.dataset.tab).classList.add('active');
    };
  })(topNavItems[ti]);
}

/* filter binding */
function bindSingle(cid, sk, cb) {
  var btns = document.querySelectorAll('#' + cid + ' .fbtn');
  for (var i = 0; i < btns.length; i++) {
    (function(b) {
      b.onclick = function() {
        var sibs = document.querySelectorAll('#' + cid + ' .fbtn');
        for (var j = 0; j < sibs.length; j++) sibs[j].classList.remove('active');
        b.classList.add('active');
        st[sk] = b.dataset.v;
        cb();
      };
    })(btns[i]);
  }
}

function bindMulti(cid, sk, cb) {
  var btns = document.querySelectorAll('#' + cid + ' .fbtn');
  for (var i = 0; i < btns.length; i++) {
    (function(b) {
      b.onclick = function() {
        b.classList.toggle('active');
        var arr = [];
        var actives = document.querySelectorAll('#' + cid + ' .fbtn.active');
        for (var j = 0; j < actives.length; j++) arr.push(actives[j].dataset.v);
        if (arr.length === 0) { b.classList.add('active'); arr = [b.dataset.v]; }
        st[sk] = arr;
        cb();
      };
    })(btns[i]);
  }
}

bindSingle('fPlatform', 'plat', function() { updateCats(); render(); });
bindMulti('fScores', 'scores', function() { render(); });
bindSingle('fDim', 'dim', function() { updateCats(); render(); });

function updateCats() {
  var dimData = safeGet(S, [st.plat, st.dim]);
  var cats = dimData ? Object.keys(dimData) : ['\u6574\u4f53'];
  var c = document.getElementById('fCat');
  var btnsHtml = '<span class="label">\u9898\u76ee\u7c7b\u578b</span>';
  for (var i = 0; i < cats.length; i++) {
    btnsHtml += '<button class="fbtn ' + (i === 0 ? 'active' : '') + '" data-v="' + cats[i] + '">' + cats[i] + '</button>';
  }
  c.innerHTML = btnsHtml;
  st.cat = cats[0];
  bindSingle('fCat', 'cat', function() { render(); });
}

function destroyCharts() {
  var keys = Object.keys(charts);
  for (var i = 0; i < keys.length; i++) charts[keys[i]].destroy();
  charts = {};
}

function render() {
  destroyCharts();
  var pd = safeGet(S, [st.plat, st.dim, st.cat]);
  if (!pd) {
    document.getElementById('chartsGrid').innerHTML = '<div style="padding:40px;text-align:center;color:#999;grid-column:1/-1">\u6682\u65e0\u8be5\u7ef4\u5ea6\u6570\u636e</div>';
    document.getElementById('volStrip').innerHTML = '';
    return;
  }

  /* volume */
  var pk = st.plat;
  var sCount = safeGet(V, ['session\u7ef4\u5ea6', pk]) || 0;
  var pCountObj = safeGet(V, ['prompt\u7ef4\u5ea6', st.cat, pk]);
  if (pCountObj == null) pCountObj = safeGet(V, ['prompt\u7ef4\u5ea6', '\u6574\u4f53', pk]);
  var pCount = pCountObj || '-';
  document.getElementById('volStrip').innerHTML =
    '<div class="vol-chip"><div class="vol-num">' + sCount + '</div><div class="vol-lbl">Session \u9898\u91cf</div></div>' +
    '<div class="vol-chip c2"><div class="vol-num">' + pCount + '</div><div class="vol-lbl">' + st.cat + ' Prompt \u9898\u91cf</div></div>';

  var showSub = st.scores.indexOf('\u4e3b\u5ba2\u89c2') >= 0;
  var showObj = st.scores.indexOf('\u5ba2\u89c2') >= 0;
  var metricList = ['GSB', 'p-value', '\u53ef\u7528\u7387', '\u6ee1\u5206\u7387', '\u52dd\u9000\u7387', '\u5747\u5206', '\u56de\u590d\u5b57\u6570'];

  var html = '';
  for (var mi = 0; mi < metricList.length; mi++) {
    var m = metricList[mi];
    var cid = 'ch_' + m.replace(/[^a-zA-Z0-9]/g, '');
    html += '<div class="chart-card"><div class="chart-title">' + m + '</div>' +
      '<div class="chart-subtitle">' + st.plat + ' / ' + (st.dim === 'session' ? 'Session\u7ef4\u5ea6' : 'Prompt\u7ef4\u5ea6') + ' / ' + st.cat + '</div>' +
      '<div class="chart-wrap"><canvas id="' + cid + '"></canvas></div>';
    if (m === 'GSB') html += '<div class="legend-note">\u2191 \u6b63\u503c=\u8c46\u5305\u9886\u5148(\u7eff) \u00b7 \u8d1f\u503c=Qwen\u9886\u5148(\u7ea2)</div>';
    html += '</div>';
  }
  document.getElementById('chartsGrid').innerHTML = html;

  for (var mi = 0; mi < metricList.length; mi++) {
    var m = metricList[mi];
    var cid = 'ch_' + m.replace(/[^a-zA-Z0-9]/g, '');
    var ctx = document.getElementById(cid);
    if (!ctx) continue;
    var d = pd[m];
    if (!d) continue;

    if (m === '\u56de\u590d\u5b57\u6570') {
      var dbW = d['\u8c46\u5305'];
      var qwW = d['Qwen'];
      if (dbW == null && qwW == null) continue;
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['\u8c46\u5305', 'Qwen3.5'],
          datasets: [{data: [dbW || 0, qwW || 0], backgroundColor: [C.db, C.qw], borderRadius: 4, barPercentage: 0.5}]
        },
        plugins: [ChartDataLabels],
        options: barOpts(m, false)
      });
      continue;
    }

    if (m === 'GSB') {
      var gL = [], gD = [], gC = [];
      if (showSub) {
        gL.push('\u4e3b\u89c2+\u5ba2\u89c2');
        var v1 = pv(d['Qwen_\u4e3b\u5ba2\u89c2']);
        var nv1 = (v1 !== null) ? -v1 : null;
        gD.push(nv1);
        gC.push(nv1 !== null && nv1 > 0 ? 'rgba(52,199,89,0.85)' : nv1 !== null && nv1 < 0 ? 'rgba(255,59,48,0.85)' : 'rgba(200,200,200,0.5)');
      }
      if (showObj) {
        gL.push('\u5ba2\u89c2');
        var v2 = pv(d['Qwen_\u5ba2\u89c2']);
        var nv2 = (v2 !== null) ? -v2 : null;
        gD.push(nv2);
        gC.push(nv2 !== null && nv2 > 0 ? 'rgba(52,199,89,0.85)' : nv2 !== null && nv2 < 0 ? 'rgba(255,59,48,0.85)' : 'rgba(200,200,200,0.5)');
      }
      if (gL.length === 0) continue;
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: { labels: gL, datasets: [{ label: 'GSB (\u6b63=\u8c46\u5305\u9886\u5148)', data: gD, backgroundColor: gC, borderRadius: 4, barPercentage: 0.5 }] },
        plugins: [ChartDataLabels],
        options: gsbOpts()
      });
      continue;
    }

    if (m === 'p-value') {
      var pL = [], pD = [];
      if (showSub) { pL.push('\u4e3b\u89c2+\u5ba2\u89c2'); pD.push(pv(d['Qwen_\u4e3b\u5ba2\u89c2'])); }
      if (showObj) { pL.push('\u5ba2\u89c2'); pD.push(pv(d['Qwen_\u5ba2\u89c2'])); }
      if (pL.length === 0) continue;
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: { labels: pL, datasets: [{ label: 'p-value', data: pD, backgroundColor: 'rgba(134,144,156,0.7)', borderRadius: 4, barPercentage: 0.5 }] },
        plugins: [ChartDataLabels],
        options: barOpts(m, false)
      });
      continue;
    }

    /* standard metrics */
    var sL = [], dbD = [], qwD = [];
    if (showSub) {
      sL.push('\u4e3b\u89c2+\u5ba2\u89c2');
      dbD.push(pv(d['\u8c46\u5305_\u4e3b\u5ba2\u89c2']));
      qwD.push(pv(d['Qwen_\u4e3b\u5ba2\u89c2']));
    }
    if (showObj) {
      sL.push('\u5ba2\u89c2');
      dbD.push(pv(d['\u8c46\u5305_\u5ba2\u89c2']));
      qwD.push(pv(d['Qwen_\u5ba2\u89c2']));
    }
    if (sL.length === 0) continue;
    charts[cid] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: sL,
        datasets: [
          { label: '\u8c46\u5305', data: dbD, backgroundColor: C.db, borderRadius: 4, barPercentage: 0.6 },
          { label: 'Qwen3.5', data: qwD, backgroundColor: C.qw, borderRadius: 4, barPercentage: 0.6 }
        ]
      },
      plugins: [ChartDataLabels],
      options: barOpts(m, true)
    });
  }
}

updateCats();
render();
'''

html_end = '''
</script>
</body>
</html>
'''

# Assemble
full_html = html_top + chartjs + html_after_chartjs + datalabels + html_after_datalabels
full_html += html_script.replace('__DATA_PLACEHOLDER__', data_json)
full_html += html_end

# Fix metric name: 劝退率 in metricList uses Unicode but data keys use Chinese
# Actually the Unicode escapes in the template strings are just for the HTML display text,
# the actual JS will work with the Unicode characters. Let me verify the metric names match.

with open('viz_final.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Generated viz_final.html: {} bytes".format(len(full_html)))
print("Contains {} script blocks".format(full_html.count('<script>')))

# Verify
import re
scripts = re.findall(r'<script>(.*?)</script>', full_html, re.DOTALL)
app_code = scripts[2]
assert '=>' not in app_code, "Arrow functions found in app code!"
assert 'const ' not in app_code, "const found in app code!"
assert 'let ' not in app_code, "let found in app code!"
assert '__DATA_PLACEHOLDER__' not in app_code, "Placeholder still present!"
print("All checks passed!")
