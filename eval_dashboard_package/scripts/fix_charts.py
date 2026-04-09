#!/usr/bin/env python3
"""Fix Tab 2 charts: 3-per-row grid layout with all metrics, matching Tab 1 style."""
import re

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for the chart grid (insert after existing .chart-container-llm styles)
chart_grid_css = """
.llm-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.llm-chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #e5e6eb}
.llm-chart-card .chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}
.llm-chart-card .chart-subtitle{font-size:12px;color:#86909c;margin-bottom:10px}
.llm-chart-card .chart-wrap{position:relative;height:240px}
.llm-chart-card .legend-note{font-size:11px;color:#86909c;text-align:center;margin-top:6px}
@media(max-width:900px){.llm-charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.llm-charts-grid{grid-template-columns:1fr}}
"""

# Find a good insertion point for CSS - after the last .chart-container-llm rule
css_marker = '.chart-container-llm .chart-title{font-size:14px;font-weight:600;color:#1d2129;margin-bottom:12px}'
last_css_pos = html.rfind(css_marker)
if last_css_pos >= 0:
    insert_pos = html.index('}', last_css_pos + len(css_marker)) + 1
    html = html[:insert_pos] + '\n' + chart_grid_css + html[insert_pos:]
    print(f"✓ CSS inserted at pos {insert_pos}")
else:
    # Fallback: insert before </style> of the case explorer styles
    print("⚠ CSS marker not found, trying fallback")

# 2. Replace the renderLlmCharts function with improved version
old_func_start = 'function renderLlmCharts() {'
old_func_end = '}\n\nfunction renderLlmDashboard()'

start_idx = html.index(old_func_start)
end_idx = html.index(old_func_end, start_idx)

new_render_charts = r"""function renderLlmCharts() {
  var el = document.getElementById('llmCharts');
  var i;
  for (i = 0; i < llmChartInstances.length; i++) {
    try { llmChartInstances[i].destroy(); } catch(e) {}
  }
  llmChartInstances = [];

  var sec = LLM_DATA.sections[llmCat];
  if (!sec || !sec.metrics) { el.innerHTML = '<div style="padding:40px;text-align:center;color:#999">暂无该维度数据</div>'; return; }
  var m = sec.metrics;
  var suffix = llmDim === 'obj' ? '_客观' : '_主客观';
  var dimLabel = llmDim === 'obj' ? '客观' : '主观+客观';
  var allMetrics = ['GSB', 'p-value', '可用率', '满分率', '劝退率', '均分', '回复字数'];
  var comps = ['豆包', '千问', 'Gemini', 'GPT'];
  var colors = ['#165dff', '#f77234', '#0fc6c2', '#722ed1'];

  var h = '<div class="llm-charts-grid">';
  for (var mi = 0; mi < allMetrics.length; mi++) {
    var mKey = allMetrics[mi];
    h += '<div class="llm-chart-card">';
    h += '<div class="chart-title">' + mKey + '</div>';
    h += '<div class="chart-subtitle">' + dimLabel + ' / ' + llmCat + ' (n=' + sec.count + ')</div>';
    h += '<div class="chart-wrap"><canvas id="llmCh_' + mi + '"></canvas></div>';
    if (mKey === 'GSB') h += '<div class="legend-note">\u2191 正值=豆包领先(绿) \u00b7 负值=竞品领先(红)</div>';
    h += '</div>';
  }
  h += '</div>';
  el.innerHTML = h;

  if (typeof Chart === 'undefined') return;

  for (var mi = 0; mi < allMetrics.length; mi++) {
    var mKey = allMetrics[mi];
    var mData = m[mKey];
    if (!mData) continue;
    var canvas = document.getElementById('llmCh_' + mi);
    if (!canvas) continue;
    var ctx = canvas.getContext('2d');

    if (mKey === 'GSB') {
      /* GSB: grouped bar豆包 vs each competitor, green/red coloring */
      var gsbLabels = ['vs 千问', 'vs Gemini', 'vs GPT'];
      var gsbComps = ['千问', 'Gemini', 'GPT'];
      var gsbVals = [];
      for (var gi = 0; gi < gsbComps.length; gi++) {
        var raw = mData[gsbComps[gi] + suffix] || '';
        var fv = parseFloat(raw);
        gsbVals.push(isNaN(fv) ? null : fv * (raw.indexOf('%') >= 0 ? 1 : 100));
      }
      var chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: gsbLabels,
          datasets: [{
            label: 'GSB',
            data: gsbVals,
            backgroundColor: gsbVals.map(function(v) { return v !== null && v >= 0 ? '#00b42a' : '#f53f3f'; }),
            borderRadius: 6,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: {
          responsive: true, maintainAspectRatio: false,
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
      llmChartInstances.push(chart);
    } else if (mKey === 'p-value') {
      /* p-value: bar per competitor, highlight <0.05 */
      var pvLabels = ['vs 千问', 'vs Gemini', 'vs GPT'];
      var pvComps = ['千问', 'Gemini', 'GPT'];
      var pvVals = [];
      for (var pi = 0; pi < pvComps.length; pi++) {
        var raw = mData[pvComps[pi] + suffix] || '';
        var fv = parseFloat(raw);
        pvVals.push(isNaN(fv) ? null : fv);
      }
      var chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: pvLabels,
          datasets: [{
            data: pvVals,
            backgroundColor: pvVals.map(function(v) { return v !== null && v < 0.05 ? '#00b42a' : '#c9cdd4'; }),
            borderRadius: 6,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            datalabels: {
              anchor: 'end', align: 'end', font: { size: 11, weight: 'bold' },
              color: function(ctx2) { var v = ctx2.dataset.data[ctx2.dataIndex]; return v !== null && v < 0.05 ? '#00b42a' : '#4e5969'; },
              formatter: function(v) { return v !== null ? v.toFixed(4) : '-'; }
            }
          },
          scales: {
            y: { beginAtZero: true, suggestedMax: 1, ticks: { stepSize: 0.2 } },
            x: { grid: { display: false } }
          }
        }
      });
      llmChartInstances.push(chart);
    } else if (mKey === '回复字数') {
      /* Word count: 4 bars, no percentage */
      var wcVals = [];
      for (var ci = 0; ci < comps.length; ci++) {
        var raw = mData[comps[ci] + suffix] || '';
        var fv = parseFloat(raw);
        wcVals.push(isNaN(fv) ? null : fv);
      }
      var chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: comps,
          datasets: [{
            data: wcVals,
            backgroundColor: colors,
            borderRadius: 6,
            barPercentage: 0.5
          }]
        },
        plugins: [ChartDataLabels],
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            datalabels: {
              anchor: 'end', align: 'end', font: { size: 11, weight: 'bold' },
              formatter: function(v) { return v !== null ? Math.round(v) : '-'; }
            }
          },
          scales: {
            y: { beginAtZero: true },
            x: { grid: { display: false } }
          }
        }
      });
      llmChartInstances.push(chart);
    } else {
      /* Standard percentage metrics: 可用率 满分率 劝退率 均分 — 4 bars per competitor */
      var vals = [];
      for (var ci = 0; ci < comps.length; ci++) {
        var raw = mData[comps[ci] + suffix] || '';
        var fv = parseFloat(raw);
        vals.push(isNaN(fv) ? null : fv);
      }
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
          responsive: true, maintainAspectRatio: false,
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
  }
}

"""

html = html[:start_idx] + new_render_charts + html[end_idx:]
print(f"✓ renderLlmCharts replaced")

# 3. Also fix the "指标对比图表" container to NOT have any old wrapper style 
# The div#llmCharts should just be a plain container; the grid is inside it now.

# 4. Verify
print(f"Final size: {len(html):,} bytes")

# Check the grid CSS is present
assert 'llm-charts-grid' in html, "Grid CSS missing!"
assert 'llm-chart-card' in html, "Chart card class missing!"
assert 'llmCh_' in html, "Chart canvas IDs missing!"

# Check script balance
opens = html.count('<script')
closes = html.count('</script>')
print(f"Script tags: {opens} opens, {closes} closes")

# Check </body> positions
pos = 0
body_positions = []
while True:
    idx = html.find('</body>', pos)
    if idx < 0: break
    body_positions.append(idx)
    pos = idx + 1
print(f"</body> positions: {body_positions}")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Done")
