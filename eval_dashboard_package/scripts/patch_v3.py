#!/usr/bin/env python3
"""Patch viz_final_v2.html:
1. renderOverview => accept dim parameter, add session/prompt toggle buttons
2. Remove volStrip from render()
"""
import re

with open('viz_final_v2.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============ Fix 1: Replace overview HTML section ============
old_overview_html = '''<!-- 评估背景 -->
<div class="section-card">
  <div class="section-title">评估背景</div>
  <div class="info-row">
    <div class="info-chip"><div class="ic-label">🎯 评估对象</div><div class="ic-value">豆包 vs Qwen3.5</div></div>
    <div class="info-chip"><div class="ic-label">📋 评估范围</div><div class="ic-value">文字、图文、视频</div></div>
    <div class="info-chip"><div class="ic-label">📦 评估题库</div><div class="ic-value">Session 215题 / Prompt 657题</div></div>
    <div class="info-chip"><div class="ic-label">📊 对比基准</div><div class="ic-value">3月流式竞对数据</div></div>
  </div>
</div>

<!-- 评估指标 -->
<div class="section-card" id="overviewMetrics">
  <div class="section-title">评估指标</div>
  <div class="metric-row-label">客观指标</div>
  <div class="metric-row" id="objMetrics"></div>
  <div class="metric-row-label">整体指标（主观+客观）</div>
  <div class="metric-row" id="subMetrics"></div>
</div>

<!-- 统计指标 -->
<div class="section-card">
  <div class="section-title">统计指标</div>
  <div class="metric-row" id="statMetrics"></div>
</div>'''

new_overview_html = '''<!-- 评估背景 -->
<div class="section-card">
  <div class="section-title">评估背景</div>
  <div class="info-row">
    <div class="info-chip"><div class="ic-label">🎯 评估对象</div><div class="ic-value">豆包 vs Qwen3.5</div></div>
    <div class="info-chip"><div class="ic-label">📋 评估范围</div><div class="ic-value">文字、图文、视频</div></div>
    <div class="info-chip"><div class="ic-label">📦 评估题库</div><div class="ic-value">Session 215题 / Prompt 657题</div></div>
    <div class="info-chip"><div class="ic-label">📊 对比基准</div><div class="ic-value">3月流式竞对数据</div></div>
  </div>
</div>

<!-- 评估指标 -->
<div class="section-card" id="overviewMetrics">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">评估指标</div>
    <div class="ov-dim-toggle" id="ovDimToggle1">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session维度</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt维度</button>
    </div>
  </div>
  <div class="metric-row-label">客观指标</div>
  <div class="metric-row" id="objMetrics"></div>
  <div class="metric-row-label">整体指标（主观+客观）</div>
  <div class="metric-row" id="subMetrics"></div>
</div>

<!-- 统计指标 -->
<div class="section-card">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">统计指标</div>
    <div class="ov-dim-toggle" id="ovDimToggle2">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session维度</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt维度</button>
    </div>
  </div>
  <div class="metric-row" id="statMetrics"></div>
</div>'''

assert old_overview_html in html, "Old overview HTML not found!"
html = html.replace(old_overview_html, new_overview_html)

# ============ Fix 2: Replace volStrip in render and remove vol-strip div ============
# Remove the volStrip HTML div
html = html.replace('<div class="vol-strip" id="volStrip"></div>', '')

# ============ Fix 3: Replace renderOverview and add switchOvDim in JS ============
scripts = re.findall(r'(<script>)(.*?)(</script>)', html, re.DOTALL)
# Third script block is our app code
app_script_match = None
count = 0
for m in re.finditer(r'(<script>)(.*?)(</script>)', html, re.DOTALL):
    count += 1
    if count == 3:
        app_script_match = m
        break

app_code = app_script_match.group(2)

# Replace the old renderOverview function
old_render_overview_start = app_code.index('function renderOverview()')
old_render_overview_end = app_code.index('/* ---- chart options ----')

old_render_overview = app_code[old_render_overview_start:old_render_overview_end]

new_render_overview = '''var ovDim = 'session';

function switchOvDim(btn, dim) {
  ovDim = dim;
  /* sync both toggle groups */
  var toggles = document.querySelectorAll('.ov-dim-toggle .fbtn');
  for (var i = 0; i < toggles.length; i++) {
    if (toggles[i].dataset.v === dim) toggles[i].classList.add('active');
    else toggles[i].classList.remove('active');
  }
  renderOverview();
}

function renderOverview() {
  var base = safeGet(S, ['双端整体', ovDim, '整体']) || {};

  function fmtPct(d, kDb, kQw) {
    if (!d) return '无数据';
    var a = pv(d[kDb]), b = pv(d[kQw]);
    if (a===null && b===null) return '无数据';
    return (a!==null?a.toFixed(1)+'%':'-') + ' / ' + (b!==null?b.toFixed(1)+'%':'-');
  }
  function fmtGsb(d, kQw) {
    if (!d) return '无数据';
    var v = pv(d[kQw]);
    if (v===null) return '无数据';
    var neg = -v;
    return (neg>0?'+':'')+neg.toFixed(2)+'%';
  }
  function gsbClass(d, kQw) {
    if (!d) return '';
    var v = pv(d[kQw]);
    if (v===null) return '';
    return (-v)>=0?'green':'red';
  }

  var dimLabel = ovDim==='session'?'Session维度':'Prompt维度';

  /* 客观指标 */
  var objHtml = '';
  var objItems = [
    {t:'GSB',s:'豆包 vs Qwen · '+dimLabel,v:fmtGsb(base.GSB,'Qwen_客观'),c:gsbClass(base.GSB,'Qwen_客观')},
    {t:'可用率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['可用率'],'豆包_客观','Qwen_客观'),c:''},
    {t:'劝退率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['劝退率'],'豆包_客观','Qwen_客观'),c:''},
    {t:'满分率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['满分率'],'豆包_客观','Qwen_客观'),c:''}
  ];
  for(var i=0;i<objItems.length;i++){
    var it=objItems[i];
    objHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('objMetrics').innerHTML=objHtml;

  /* 主观+客观 */
  var subHtml='';
  var subItems = [
    {t:'GSB',s:'豆包 vs Qwen · '+dimLabel,v:fmtGsb(base.GSB,'Qwen_主客观'),c:gsbClass(base.GSB,'Qwen_主客观')},
    {t:'可用率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['可用率'],'豆包_主客观','Qwen_主客观'),c:''},
    {t:'劝退率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['劝退率'],'豆包_主客观','Qwen_主客观'),c:''},
    {t:'满分率',s:'豆包 vs Qwen · '+dimLabel,v:fmtPct(base['满分率'],'豆包_主客观','Qwen_主客观'),c:''}
  ];
  for(var i=0;i<subItems.length;i++){
    var it=subItems[i];
    subHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('subMetrics').innerHTML=subHtml;

  /* 统计指标 */
  var wordD = base['回复字数']||{};
  var dbW = wordD['豆包']||0, qwW = wordD['Qwen']||0;
  var ratio = (dbW>0&&qwW>0)?(qwW/dbW).toFixed(1)+'x':'';
  var statHtml='';
  statHtml+='<div class="mc"><div class="mc-title">字数</div><div class="mc-sub">豆包 vs Qwen · '+dimLabel+'</div><div class="mc-val">'+dbW+' / '+qwW+(ratio?' ('+ratio+')':'')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">均分(客观)</div><div class="mc-sub">豆包 vs Qwen · '+dimLabel+'</div><div class="mc-val">'+fmtPct(base['均分'],'豆包_客观','Qwen_客观')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">均分(主客观)</div><div class="mc-sub">豆包 vs Qwen · '+dimLabel+'</div><div class="mc-val">'+fmtPct(base['均分'],'豆包_主客观','Qwen_主客观')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Session题量</div><div class="mc-sub">双端/APP/Web</div><div class="mc-val">'+(safeGet(V,['session维度','双端整体'])||0)+' / '+(safeGet(V,['session维度','APP'])||0)+' / '+(safeGet(V,['session维度','Web'])||0)+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Prompt题量</div><div class="mc-sub">双端/APP/Web</div><div class="mc-val">'+(safeGet(V,['prompt维度','整体','双端整体'])||0)+' / '+(safeGet(V,['prompt维度','整体','APP'])||0)+' / '+(safeGet(V,['prompt维度','整体','Web'])||0)+'</div></div>';
  document.getElementById('statMetrics').innerHTML=statHtml;
}

'''

app_code = app_code[:old_render_overview_start] + new_render_overview + app_code[old_render_overview_end:]

# Remove volStrip lines from render() function
# Remove: var pk=st.plat; ... volStrip innerHTML assignment
# Find and remove the volStrip block
vol_block_start = app_code.index("var pk=st.plat;")
vol_block_end = app_code.index("var showSub=")
vol_block = app_code[vol_block_start:vol_block_end]
app_code = app_code.replace(vol_block, '')

# Also remove the volStrip empty line at the start of render when pd is null
app_code = app_code.replace("document.getElementById('volStrip').innerHTML='';return;", "return;")

# Reconstruct the HTML
html = html[:app_script_match.start(2)] + app_code + html[app_script_match.end(2):]

# Verify
assert 'switchOvDim' in html
assert 'ovDimToggle1' in html
assert 'volStrip' not in html or html.count('volStrip') == 0
assert '=>' not in re.findall(r'<script>(.*?)</script>', html, re.DOTALL)[2]

with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_final_v3.html: {} bytes".format(len(html)))
print("volStrip references remaining: {}".format(html.count('volStrip')))
PYEOF