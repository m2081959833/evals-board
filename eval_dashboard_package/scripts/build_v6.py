#!/usr/bin/env python3
"""Build viz_page_v6.html - completely clean ES5-compatible version."""
import json

# Load data
with open('viz_data_v5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix known corrupted cells
data['stats']['双端整体']['session']['整体']['均分'] = {
    '豆包_客观': '61.13%', '豆包_主客观': '66.80%',
    'Qwen_客观': '55.07%', 'Qwen_主客观': '59.93%'
}
data['stats']['双端整体']['session']['整体']['回复字数'] = {'豆包': 371, 'Qwen': 612}

data_json = json.dumps(data, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>3月流式竞对【豆包 vs Qwen3.5】[v6]</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
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
.filter-row .label{font-size:13px;color:#86909c;min-width:60px}
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
</style>
</head>
<body>
<div class="header">
<h1>3月流式竞对【豆包 vs Qwen3.5】[v6]</h1>
<p>数据来源: 数据统计 Sheet · 生成时间: 2026-04-02</p>
</div>

<div class="top-nav" id="topNav">
<div class="top-nav-item active" data-tab="tabCharts">数据看板</div>
<div class="top-nav-item" data-tab="tabCases">案例探查</div>
</div>

<div id="tabCharts" class="tab-panel active">
<div class="filter-row" id="fPlatform">
<span class="label">数据端</span>
<button class="fbtn active" data-v="双端整体">双端整体</button>
<button class="fbtn" data-v="APP">APP</button>
<button class="fbtn" data-v="Web">Web</button>
</div>
<div class="filter-row" id="fScores">
<span class="label">评分维度</span>
<button class="fbtn active" data-v="主客观">主观+客观</button>
<button class="fbtn active" data-v="客观">客观</button>
</div>
<div class="filter-row" id="fDim">
<span class="label">统计维度</span>
<button class="fbtn active" data-v="session">Session维度</button>
<button class="fbtn" data-v="prompt">Prompt维度</button>
</div>
<div class="filter-row" id="fCat">
<span class="label">题目类型</span>
</div>
<div class="vol-strip" id="volStrip"></div>
<div class="charts-grid" id="chartsGrid"></div>
</div>

<div id="tabCases" class="tab-panel">
<div style="padding:40px;text-align:center;color:#86909c">案例探查模块 (待接入评估数据 Sheet)</div>
</div>

<script>
var DATA = __DATA_PLACEHOLDER__;
var S = DATA.stats;
var V = DATA.volume || {};
var C = {db:'rgba(22,93,255,0.85)', qw:'rgba(255,125,0,0.85)'};
var charts = {};

var st = {
  plat: '双端整体',
  scores: ['主客观','客观'],
  dim: 'session',
  cat: '整体'
};

/* --- helpers --- */
function pv(s) {
  if (!s || s === '-' || s === '#DIV/0!' || s === '#N/A') return null;
  var n = parseFloat(String(s).replace('%',''));
  return isNaN(n) ? null : n;
}

function safeGet(obj, keys) {
  var cur = obj;
  for (var i = 0; i < keys.length; i++) {
    if (cur == null) return undefined;
    cur = cur[keys[i]];
  }
  return cur;
}

function barOpts(metric, showLegend) {
  var isPercent = (metric !== '回复字数' && metric !== 'p-value');
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
      x: {
        ticks: { font: { size: 11 } },
        grid: { display: false }
      }
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
        anchor: 'end',
        align: function(context) {
          return context.dataset.data[context.dataIndex] >= 0 ? 'end' : 'start';
        },
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
      x: {
        ticks: { font: { size: 11 } },
        grid: { display: false }
      }
    }
  };
}

/* --- top nav --- */
var topNavItems = document.querySelectorAll('#topNav .top-nav-item');
for (var ti = 0; ti < topNavItems.length; ti++) {
  (function(el) {
    el.onclick = function() {
      for (var j = 0; j < topNavItems.length; j++) {
        topNavItems[j].classList.remove('active');
      }
      var panels = document.querySelectorAll('.tab-panel');
      for (var j = 0; j < panels.length; j++) {
        panels[j].classList.remove('active');
      }
      el.classList.add('active');
      document.getElementById(el.dataset.tab).classList.add('active');
    };
  })(topNavItems[ti]);
}

/* --- filter binding --- */
function bindSingle(containerId, stateKey, callback) {
  var btns = document.querySelectorAll('#' + containerId + ' .fbtn');
  for (var i = 0; i < btns.length; i++) {
    (function(b) {
      b.onclick = function() {
        var siblings = document.querySelectorAll('#' + containerId + ' .fbtn');
        for (var j = 0; j < siblings.length; j++) siblings[j].classList.remove('active');
        b.classList.add('active');
        st[stateKey] = b.dataset.v;
        callback();
      };
    })(btns[i]);
  }
}

function bindMulti(containerId, stateKey, callback) {
  var btns = document.querySelectorAll('#' + containerId + ' .fbtn');
  for (var i = 0; i < btns.length; i++) {
    (function(b) {
      b.onclick = function() {
        b.classList.toggle('active');
        var activeArr = [];
        var activeBtns = document.querySelectorAll('#' + containerId + ' .fbtn.active');
        for (var j = 0; j < activeBtns.length; j++) activeArr.push(activeBtns[j].dataset.v);
        if (activeArr.length === 0) {
          b.classList.add('active');
          activeArr = [b.dataset.v];
        }
        st[stateKey] = activeArr;
        callback();
      };
    })(btns[i]);
  }
}

bindSingle('fPlatform', 'plat', function() { updateCats(); render(); });
bindMulti('fScores', 'scores', function() { render(); });
bindSingle('fDim', 'dim', function() { updateCats(); render(); });

/* --- category update --- */
function updateCats() {
  var dimData = safeGet(S, [st.plat, st.dim]);
  var cats = dimData ? Object.keys(dimData) : ['整体'];
  var c = document.getElementById('fCat');
  var btnsHtml = '';
  for (var i = 0; i < cats.length; i++) {
    btnsHtml += '<button class="fbtn ' + (i === 0 ? 'active' : '') + '" data-v="' + cats[i] + '">' + cats[i] + '</button>';
  }
  c.innerHTML = '<span class="label">题目类型</span>' + btnsHtml;
  st.cat = cats[0];
  bindSingle('fCat', 'cat', function() { render(); });
}

/* --- destroy charts --- */
function destroyCharts() {
  var keys = Object.keys(charts);
  for (var i = 0; i < keys.length; i++) {
    charts[keys[i]].destroy();
  }
  charts = {};
}

/* --- main render --- */
function render() {
  destroyCharts();
  var pd = safeGet(S, [st.plat, st.dim, st.cat]);
  if (!pd) {
    document.getElementById('chartsGrid').innerHTML = '<div style="padding:40px;text-align:center;color:#999;grid-column:1/-1">暂无该维度数据</div>';
    return;
  }

  // Volume strip
  var pk = st.plat;
  var sCount = safeGet(V, ['session维度', pk]) || 0;
  var pCountObj = safeGet(V, ['prompt维度', st.cat, pk]);
  if (pCountObj == null) pCountObj = safeGet(V, ['prompt维度', '整体', pk]);
  var pCount = pCountObj || '-';
  document.getElementById('volStrip').innerHTML =
    '<div class="vol-chip"><div class="vol-num">' + sCount + '</div><div class="vol-lbl">Session 题量</div></div>' +
    '<div class="vol-chip c2"><div class="vol-num">' + pCount + '</div><div class="vol-lbl">' + st.cat + ' Prompt 题量</div></div>';

  var showSub = st.scores.indexOf('主客观') >= 0;
  var showObj = st.scores.indexOf('客观') >= 0;
  var metricList = ['GSB', 'p-value', '可用率', '满分率', '劝退率', '均分', '回复字数'];

  // Build chart card HTML
  var html = '';
  for (var mi = 0; mi < metricList.length; mi++) {
    var m = metricList[mi];
    var cid = 'ch_' + m.replace(/[^a-zA-Z0-9]/g, '');
    html += '<div class="chart-card"><div class="chart-title">' + m + '</div>' +
      '<div class="chart-subtitle">' + st.plat + ' / ' + (st.dim === 'session' ? 'Session维度' : 'Prompt维度') + ' / ' + st.cat + '</div>' +
      '<div class="chart-wrap"><canvas id="' + cid + '"></canvas></div></div>';
  }
  document.getElementById('chartsGrid').innerHTML = html;

  // Create charts
  for (var mi = 0; mi < metricList.length; mi++) {
    var m = metricList[mi];
    var cid = 'ch_' + m.replace(/[^a-zA-Z0-9]/g, '');
    var ctx = document.getElementById(cid);
    if (!ctx) continue;
    var d = pd[m];
    if (!d) continue;

    if (m === '回复字数') {
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['豆包', 'Qwen3.5'],
          datasets: [{
            data: [d['豆包'] || 0, d['Qwen'] || 0],
            backgroundColor: [C.db, C.qw],
            borderRadius: 4,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: barOpts(m, false)
      });
      continue;
    }

    if (m === 'GSB') {
      var gLabels = [];
      var gData = [];
      var gColors = [];
      if (showSub) {
        gLabels.push('主观+客观');
        var v1 = pv(d['Qwen_主客观']);
        var negV1 = (v1 !== null) ? -v1 : null;
        gData.push(negV1);
        gColors.push(negV1 !== null && negV1 > 0 ? 'rgba(52,199,89,0.85)' : negV1 !== null && negV1 < 0 ? 'rgba(255,59,48,0.85)' : 'rgba(200,200,200,0.5)');
      }
      if (showObj) {
        gLabels.push('客观');
        var v2 = pv(d['Qwen_客观']);
        var negV2 = (v2 !== null) ? -v2 : null;
        gData.push(negV2);
        gColors.push(negV2 !== null && negV2 > 0 ? 'rgba(52,199,89,0.85)' : negV2 !== null && negV2 < 0 ? 'rgba(255,59,48,0.85)' : 'rgba(200,200,200,0.5)');
      }
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: gLabels,
          datasets: [{
            label: 'GSB (正=豆包领先)',
            data: gData,
            backgroundColor: gColors,
            borderRadius: 4,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: gsbOpts()
      });
      continue;
    }

    if (m === 'p-value') {
      var pLabels = [];
      var pData = [];
      if (showSub) { pLabels.push('主观+客观'); pData.push(pv(d['Qwen_主客观'])); }
      if (showObj) { pLabels.push('客观'); pData.push(pv(d['Qwen_客观'])); }
      charts[cid] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: pLabels,
          datasets: [{
            label: 'p-value',
            data: pData,
            backgroundColor: 'rgba(134,144,156,0.7)',
            borderRadius: 4,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: barOpts(m, false)
      });
      continue;
    }

    // Standard metrics: 可用率, 满分率, 劝退率, 均分
    var sLabels = [];
    var dbData = [];
    var qwData = [];
    if (showSub) {
      sLabels.push('主观+客观');
      dbData.push(pv(d['豆包_主客观']));
      qwData.push(pv(d['Qwen_主客观']));
    }
    if (showObj) {
      sLabels.push('客观');
      dbData.push(pv(d['豆包_客观']));
      qwData.push(pv(d['Qwen_客观']));
    }
    charts[cid] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: sLabels,
        datasets: [
          { label: '豆包', data: dbData, backgroundColor: C.db, borderRadius: 4, barPercentage: 0.6 },
          { label: 'Qwen3.5', data: qwData, backgroundColor: C.qw, borderRadius: 4, barPercentage: 0.6 }
        ]
      },
      plugins: [ChartDataLabels],
      options: barOpts(m, true)
    });
  }
}

/* --- init --- */
updateCats();
render();
</script>
</body>
</html>
'''

# Inject data
html = html.replace('__DATA_PLACEHOLDER__', data_json)

# Verify
assert 'DATA' in html
assert '__DATA_PLACEHOLDER__' not in html
assert '=>' not in html.split('<script>')[1].split('</script>')[0], "Arrow functions found!"

with open('viz_page_v6.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_page_v6.html: {} bytes".format(len(html)))

# Balanced brace check
script = html.split('<script>')[1].split('</script>')[0]
opens_b = script.count('{')
close_b = script.count('}')
opens_p = script.count('(')
close_p = script.count(')')
opens_s = script.count('[')
close_s = script.count(']')
print("Braces: {{ {} }} {}  {} {}".format(opens_b, close_b, 'OK' if opens_b == close_b else 'MISMATCH!', ''))
print("Parens: ( {} ) {}  {}".format(opens_p, close_p, 'OK' if opens_p == close_p else 'MISMATCH!'))
print("Brackets: [ {} ] {}  {}".format(opens_s, close_s, 'OK' if opens_s == close_s else 'MISMATCH!'))
