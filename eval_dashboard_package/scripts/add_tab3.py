#!/usr/bin/env python3
"""
Add Tab3: 历次评估趋势 - showing how competitors perform relative to 豆包 across evaluations.
"""
import re, json

with open('viz_final_v10_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Original size: {len(html):,} bytes")

# =====================================================
# Step 1: Add Tab3 button in the tab bar
# =====================================================
# Find existing tab buttons
tab2_btn = 'LLM竞品评估｜豆包 vs 千问3 vs Gemini 3 Pro vs GPT5.2｜26年1月</div>'
tab3_btn = tab2_btn + '\n  <div class="project-tab" data-project="proj3" onclick="switchProject(this)">历次评估趋势</div>'
html = html.replace(tab2_btn, tab3_btn, 1)
print("[OK] Added Tab3 button")

# =====================================================
# Step 2: Add Tab3 CSS to <head>
# =====================================================
first_style_end = html.find('</style>')
tab3_css = """
/* === Tab3: Trend Dashboard === */
.trend-header{text-align:center;margin-bottom:32px}
.trend-header h2{font-size:22px;font-weight:700;color:#1d2129;margin:0 0 6px 0}
.trend-header .trend-subtitle{font-size:14px;color:#86909c}
.trend-filters{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;align-items:center}
.trend-filter-label{font-size:13px;color:#4e5969;font-weight:500;margin-right:4px}
.trend-filter-btn{padding:5px 14px;font-size:13px;border-radius:6px;border:1px solid #e5e6eb;background:#fff;color:#4e5969;cursor:pointer;transition:all .15s}
.trend-filter-btn.active{background:#165dff;color:#fff;border-color:#165dff}
.trend-charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:32px}
.trend-chart-card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.06);border:1px solid #e5e6eb}
.trend-chart-card .tc-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:4px}
.trend-chart-card .tc-desc{font-size:12px;color:#86909c;margin-bottom:12px}
.trend-chart-card .tc-wrap{position:relative;height:260px}
.trend-summary{background:#f7f8fa;border-radius:12px;padding:24px;margin-bottom:32px}
.trend-summary h3{font-size:16px;font-weight:600;color:#1d2129;margin:0 0 16px 0}
.trend-summary table{width:100%;border-collapse:collapse;font-size:13px}
.trend-summary th{text-align:left;padding:8px 12px;background:#e8f3ff;color:#1d2129;font-weight:600;border-bottom:2px solid #165dff}
.trend-summary td{padding:8px 12px;border-bottom:1px solid #e5e6eb}
.trend-summary .val-up{color:#00b42a;font-weight:600}
.trend-summary .val-down{color:#f53f3f;font-weight:600}
.trend-summary .val-neutral{color:#86909c}
@media(max-width:900px){.trend-charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.trend-charts-grid{grid-template-columns:1fr}}
"""
html = html[:first_style_end] + tab3_css + html[first_style_end:]
print("[OK] Added Tab3 CSS")

# =====================================================
# Step 3: Add Tab3 panel HTML (before the last </body>)
# =====================================================
tab3_html = '''
<div id="proj3" class="project-panel">
  <div style="max-width:1200px;margin:0 auto;padding:32px 48px">
    <div class="trend-header">
      <h2>历次评估趋势 · 以豆包为基准</h2>
      <div class="trend-subtitle">对比不同评估批次中，各竞品模型相对豆包的核心指标表现变化</div>
    </div>

    <div class="trend-filters">
      <span class="trend-filter-label">评分维度：</span>
      <button class="trend-filter-btn active" onclick="trendSetDim(this,'主客观')">主观+客观</button>
      <button class="trend-filter-btn" onclick="trendSetDim(this,'客观')">客观</button>
    </div>

    <div class="trend-summary" id="trend-summary"></div>

    <div class="trend-charts-grid" id="trend-charts-grid"></div>
  </div>
</div>
'''

# Insert before the LAST </body>
last_body = html.rfind('</body>')
html = html[:last_body] + tab3_html + '\n' + html[last_body:]
print("[OK] Inserted Tab3 panel HTML")

# =====================================================
# Step 4: Add Tab3 JS data and rendering logic
# =====================================================

# Build the trend data from existing data
# We need to extract both datasets programmatically
scripts = re.findall(r'<script[\s>](.*?)</script>', html, re.DOTALL)

# Tab1 DATA
s2 = scripts[2]
data_start = s2.find('var DATA = ')
data_json_start = s2.find('{', data_start)
depth = 0
for i in range(data_json_start, len(s2)):
    if s2[i] == '{': depth += 1
    elif s2[i] == '}':
        depth -= 1
        if depth == 0:
            data_end = i + 1
            break
tab1 = json.loads(s2[data_json_start:data_end])

# Tab2 LLM_DATA
s5_idx = html.find('var LLM_DATA = ')
llm_json_start = html.find('{', s5_idx)
depth = 0
for i in range(llm_json_start, len(html)):
    if html[i] == '{': depth += 1
    elif html[i] == '}':
        depth -= 1
        if depth == 0:
            llm_end = i + 1
            break
tab2 = json.loads(html[llm_json_start:llm_end])

# Build trend data structure
# Eval 1 (Tab2): 26年1月 LLM竞品评估 - 4 models
# Eval 2 (Tab1): 26年3月 流式竞对 - 2 models (豆包 vs Qwen)
# Common competitor: Qwen/千问

def parse_pct(v):
    if v is None or v == '-' or v == '': return None
    v = str(v).replace('%','').strip()
    try: return float(v)
    except: return None

# Build: for each metric, each eval round, extract 豆包 and competitor values
trend_data = {
    "evals": [
        {"id": "eval1", "name": "26年1月 LLM竞品评估", "short": "26年1月",
         "models": ["千问3", "Gemini 3 Pro", "GPT 5.2"]},
        {"id": "eval2", "name": "26年3月 流式竞对", "short": "26年3月",
         "models": ["Qwen3.5"]}
    ],
    "metrics": {}
}

# Metrics to track
core_metrics = ["GSB", "可用率", "满分率", "劝退率", "均分"]

for dim in ["客观", "主客观"]:
    trend_data["metrics"][dim] = {}
    for metric in core_metrics:
        trend_data["metrics"][dim][metric] = {}

        # Eval1 (Tab2): LLM_DATA
        e1_section = tab2["sections"].get("整体", {}).get("metrics", {}).get(metric, {})
        db_e1 = parse_pct(e1_section.get("豆包_" + dim))
        qw3_e1 = parse_pct(e1_section.get("千问_" + dim))
        gm_e1 = parse_pct(e1_section.get("Gemini_" + dim))
        gpt_e1 = parse_pct(e1_section.get("GPT_" + dim))

        # Eval2 (Tab1): DATA, 双端整体 > session > 整体
        e2_section = tab1["stats"]["双端整体"]["session"]["整体"].get(metric, {})
        db_e2 = parse_pct(e2_section.get("豆包_" + dim))
        qw_e2 = parse_pct(e2_section.get("Qwen_" + dim))

        trend_data["metrics"][dim][metric] = {
            "豆包": {"26年1月": db_e1, "26年3月": db_e2},
            "千问": {"26年1月": qw3_e1, "26年3月": qw_e2},
            "Gemini": {"26年1月": gm_e1, "26年3月": None},
            "GPT": {"26年1月": gpt_e1, "26年3月": None}
        }

    # Add 回复字数 separately (no dim suffix distinction)
    wc_metric = "回复字数"
    e1_wc = tab2["sections"].get("整体", {}).get("metrics", {}).get(wc_metric, {})
    e2_wc = tab1["stats"]["双端整体"]["session"]["整体"].get(wc_metric, {})

    trend_data["metrics"][dim][wc_metric] = {
        "豆包": {"26年1月": parse_pct(e1_wc.get("豆包_" + dim, e1_wc.get("豆包"))),
                 "26年3月": parse_pct(e2_wc.get("豆包_" + dim, e2_wc.get("豆包")))},
        "千问": {"26年1月": parse_pct(e1_wc.get("千问_" + dim, e1_wc.get("千问"))),
                 "26年3月": parse_pct(e2_wc.get("Qwen_" + dim, e2_wc.get("Qwen")))},
        "Gemini": {"26年1月": parse_pct(e1_wc.get("Gemini_" + dim, e1_wc.get("Gemini"))),
                   "26年3月": None},
        "GPT": {"26年1月": parse_pct(e1_wc.get("GPT_" + dim, e1_wc.get("GPT"))),
                "26年3月": None}
    }

trend_json = json.dumps(trend_data, ensure_ascii=False)
print(f"Trend data JSON size: {len(trend_json)} chars")

# Now build the JS
trend_js = '''
<script>
/* === Tab3: Trend Dashboard === */
var TREND_DATA = ''' + trend_json + ''';
var trendDim = "主客观";

function trendSetDim(btn, dim) {
  trendDim = dim;
  var btns = btn.parentNode.querySelectorAll(".trend-filter-btn");
  for (var i = 0; i < btns.length; i++) btns[i].className = "trend-filter-btn";
  btn.className = "trend-filter-btn active";
  renderTrendDashboard();
}

function renderTrendDashboard() {
  renderTrendSummary();
  renderTrendCharts();
}

function renderTrendSummary() {
  var el = document.getElementById("trend-summary");
  if (!el) return;
  var metrics = TREND_DATA.metrics[trendDim];
  var periods = ["26年1月", "26年3月"];
  var models = ["豆包", "千问", "Gemini", "GPT"];
  var modelLabels = {"豆包": "豆包(基准)", "千问": "千问(Qwen)", "Gemini": "Gemini", "GPT": "GPT"};
  var coreMetrics = ["均分", "可用率", "满分率", "劝退率", "GSB"];
  
  var h = "<h3>核心指标汇总（整体 · " + trendDim + "）</h3>";
  h += "<table><thead><tr><th>指标</th><th>模型</th>";
  for (var p = 0; p < periods.length; p++) h += "<th>" + periods[p] + "</th>";
  h += "<th>变化</th></tr></thead><tbody>";

  for (var mi = 0; mi < coreMetrics.length; mi++) {
    var mName = coreMetrics[mi];
    var mData = metrics[mName];
    if (!mData) continue;
    var first = true;
    for (var m = 0; m < models.length; m++) {
      var model = models[m];
      var md = mData[model];
      if (!md) continue;
      h += "<tr>";
      if (first) {
        h += "<td rowspan='" + models.length + "' style='font-weight:600;vertical-align:middle'>" + mName + "</td>";
        first = false;
      }
      h += "<td>" + (modelLabels[model] || model) + "</td>";
      for (var p = 0; p < periods.length; p++) {
        var val = md[periods[p]];
        if (val === null || val === undefined) {
          h += "<td style='color:#c9cdd4'>-</td>";
        } else if (mName === "回复字数") {
          h += "<td>" + Math.round(val) + "</td>";
        } else {
          h += "<td>" + val.toFixed(1) + "%</td>";
        }
      }
      // Change column
      var v1 = md["26年1月"];
      var v2 = md["26年3月"];
      if (v1 !== null && v1 !== undefined && v2 !== null && v2 !== undefined) {
        var diff = v2 - v1;
        var arrow = diff > 0 ? "↑" : (diff < 0 ? "↓" : "→");
        var cls = diff > 0 ? "val-up" : (diff < 0 ? "val-down" : "val-neutral");
        // For 劝退率, lower is better, so flip colors
        if (mName === "劝退率") {
          cls = diff < 0 ? "val-up" : (diff > 0 ? "val-down" : "val-neutral");
        }
        if (mName === "回复字数") {
          h += "<td class='" + cls + "'>" + arrow + Math.abs(Math.round(diff)) + "</td>";
        } else {
          h += "<td class='" + cls + "'>" + arrow + Math.abs(diff).toFixed(1) + "%</td>";
        }
      } else {
        h += "<td style='color:#c9cdd4'>仅1期</td>";
      }
      h += "</tr>";
    }
  }
  h += "</tbody></table>";
  el.innerHTML = h;
}

var trendChartInstances = [];
function renderTrendCharts() {
  var el = document.getElementById("trend-charts-grid");
  if (!el) return;
  // Destroy old charts
  for (var i = 0; i < trendChartInstances.length; i++) {
    trendChartInstances[i].destroy();
  }
  trendChartInstances = [];

  var metrics = TREND_DATA.metrics[trendDim];
  var chartMetrics = ["均分", "可用率", "满分率", "劝退率", "GSB", "回复字数"];
  var chartDescs = {
    "均分": "各模型平均分变化",
    "可用率": "各模型可用率变化",
    "满分率": "各模型满分率变化",
    "劝退率": "越低越好",
    "GSB": "相对豆包的GSB胜率",
    "回复字数": "平均回复字数变化"
  };
  var modelColors = {
    "豆包": "#3370ff",
    "千问": "#f77234",
    "Gemini": "#00b42a",
    "GPT": "#9c5eff"
  };
  var periods = ["26年1月", "26年3月"];
  var models = ["豆包", "千问", "Gemini", "GPT"];

  var h = "";
  for (var ci = 0; ci < chartMetrics.length; ci++) {
    var mName = chartMetrics[ci];
    h += "<div class='trend-chart-card'>";
    h += "<div class='tc-title'>" + mName + "</div>";
    h += "<div class='tc-desc'>" + (chartDescs[mName] || "") + "</div>";
    h += "<div class='tc-wrap'><canvas id='trend-chart-" + ci + "'></canvas></div>";
    h += "</div>";
  }
  el.innerHTML = h;

  // Render charts
  for (var ci = 0; ci < chartMetrics.length; ci++) {
    var mName = chartMetrics[ci];
    var mData = metrics[mName];
    if (!mData) continue;

    var datasets = [];
    for (var m = 0; m < models.length; m++) {
      var model = models[m];
      var md = mData[model];
      if (!md) continue;
      var vals = [];
      var hasAny = false;
      for (var p = 0; p < periods.length; p++) {
        var v = md[periods[p]];
        vals.push(v);
        if (v !== null && v !== undefined) hasAny = true;
      }
      if (!hasAny) continue;
      datasets.push({
        label: model,
        data: vals,
        borderColor: modelColors[model] || "#999",
        backgroundColor: modelColors[model] || "#999",
        borderWidth: 2.5,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.1,
        spanGaps: false
      });
    }

    var canvas = document.getElementById("trend-chart-" + ci);
    if (!canvas) continue;
    var ctx = canvas.getContext("2d");
    var isInteger = (mName === "回复字数");

    var chart = new Chart(ctx, {
      type: "line",
      data: { labels: periods, datasets: datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { usePointStyle: true, padding: 16, font: { size: 12 } } },
          datalabels: {
            display: true,
            anchor: "end",
            align: "top",
            font: { size: 11, weight: "bold" },
            formatter: function(value) {
              if (value === null || value === undefined) return "";
              return isInteger ? Math.round(value) : value.toFixed(1) + "%";
            }
          }
        },
        scales: {
          y: {
            beginAtZero: mName !== "回复字数" && mName !== "GSB",
            grid: { color: "rgba(0,0,0,0.05)" },
            ticks: {
              callback: function(v) { return isInteger ? v : v + "%"; },
              font: { size: 11 }
            }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 12, weight: "600" } }
          }
        }
      },
      plugins: [ChartDataLabels]
    });
    trendChartInstances.push(chart);
  }
}
</script>
'''

# Insert the trend JS before last </body>
last_body = html.rfind('</body>')
html = html[:last_body] + trend_js + '\n' + html[last_body:]
print("[OK] Inserted Tab3 JS")

# =====================================================
# Step 5: Update switchProject to handle proj3
# =====================================================
# Add trend rendering on proj3 switch
old_switch = "if (target === 'proj2' && typeof renderLlmDashboard === 'function') {"
new_switch = """if (target === 'proj2' && typeof renderLlmDashboard === 'function') {
    setTimeout(function() { renderLlmDashboard(); }, 50);
  }
  if (target === 'proj3' && typeof renderTrendDashboard === 'function') {
    setTimeout(function() { renderTrendDashboard(); }, 50);
  }
  if (false) {"""
html = html.replace(old_switch, new_switch, 1)
print("[OK] Updated switchProject for proj3")

# =====================================================
# Verification
# =====================================================
print(f"\nFinal size: {len(html):,} bytes")

# Check proj3 exists
if 'id="proj3"' in html:
    print("[OK] proj3 panel exists")
if 'renderTrendDashboard' in html:
    print("[OK] renderTrendDashboard function exists")
if 'TREND_DATA' in html:
    print("[OK] TREND_DATA exists")

# Brace balance
scripts = re.findall(r'<script[\s>](.*?)</script>', html, re.DOTALL)
print(f"\nScript blocks: {len(scripts)}")
for i, s in enumerate(scripts):
    opens = s.count('{')
    closes = s.count('}')
    diff = opens - closes
    if diff != 0:
        if i == 3:
            print(f"  Block {i}: diff={diff} (SheetJS, expected)")
        else:
            print(f"  Block {i}: diff={diff} *** CHECK ***")

with open('viz_final_v10_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\n[DONE] Saved viz_final_v10_full.html")
