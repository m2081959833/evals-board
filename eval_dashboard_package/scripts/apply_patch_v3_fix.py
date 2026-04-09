#!/usr/bin/env python3
"""Fix v3: correct renderOverview to use proper element IDs and render data correctly"""
import re

with open('viz_final_v2.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add toggle buttons to 评估指标 section header
old_eval = '<div class="section-title">评估指标</div>'
new_eval = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">评估指标</div>
    <div class="ov-dim-toggle" id="ovDimToggle1">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session维度</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt维度</button>
    </div>
    </div>'''
html = html.replace(old_eval, new_eval, 1)

# 2. Add toggle buttons to 统计指标 section header
old_stat = '<div class="section-title">统计指标</div>'
new_stat = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">统计指标</div>
    <div class="ov-dim-toggle" id="ovDimToggle2">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session维度</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt维度</button>
    </div>
    </div>'''
html = html.replace(old_stat, new_stat, 1)

# 3. Add toggle button CSS
toggle_css = '.ov-dim-toggle{display:flex;gap:6px}\n.ov-dim-toggle .fbtn{font-size:12px;padding:2px 10px}\n'
html = html.replace('.section-title{', toggle_css + '.section-title{', 1)

# 4. Remove volStrip div
html = html.replace('<div class="vol-strip" id="volStrip"></div>', '')
html = re.sub(r'\.vol-strip\{[^}]*\}', '', html)

# 5. Find and replace renderOverview function
ov_match = re.search(r'function renderOverview\(\)\s*\{', html)
start = ov_match.start()
brace_count = 0
pos = ov_match.end() - 1
for i in range(pos, len(html)):
    if html[i] == '{':
        brace_count += 1
    elif html[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end = i + 1
            break

new_fn = """var ovDim = 'session';
function switchOvDim(btn, dim) {
  ovDim = dim;
  var toggles = document.querySelectorAll('.ov-dim-toggle .fbtn');
  for (var i = 0; i < toggles.length; i++) {
    if (toggles[i].dataset.v === dim) toggles[i].classList.add('active');
    else toggles[i].classList.remove('active');
  }
  renderOverview();
}
function renderOverview() {
  var base = safeGet(S, ['\\u53cc\\u7aef\\u6574\\u4f53', ovDim, '\\u6574\\u4f53']) || {};

  function fmtPct(d, kDb, kQw) {
    var a = pv(d[kDb]), b = pv(d[kQw]);
    if (a===null && b===null) return '\\u65e0\\u6570\\u636e';
    return (a!==null?a.toFixed(1)+'%':'-') + ' / ' + (b!==null?b.toFixed(1)+'%':'-');
  }
  function fmtGsb(d, kQw) {
    var v = pv(d[kQw]);
    if (v===null) return '\\u65e0\\u6570\\u636e';
    var neg = -v;
    return (neg>0?'+':'')+neg.toFixed(2)+'%';
  }
  function gsbClass(d, kQw) {
    var v = pv(d[kQw]);
    if (v===null) return '';
    return (-v)>=0?'green':'red';
  }

  var objHtml = '';
  var objItems = [
    {t:'GSB',s:'\\u8c46\\u5305 vs Qwen',v:fmtGsb(base.GSB||{},'Qwen_\\u5ba2\\u89c2'),c:gsbClass(base.GSB||{},'Qwen_\\u5ba2\\u89c2')},
    {t:'\\u53ef\\u7528\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u53ef\\u7528\\u7387']||{},'\\u8c46\\u5305_\\u5ba2\\u89c2','Qwen_\\u5ba2\\u89c2'),c:''},
    {t:'\\u52dd\\u9000\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u52dd\\u9000\\u7387']||{},'\\u8c46\\u5305_\\u5ba2\\u89c2','Qwen_\\u5ba2\\u89c2'),c:''},
    {t:'\\u6ee1\\u5206\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u6ee1\\u5206\\u7387']||{},'\\u8c46\\u5305_\\u5ba2\\u89c2','Qwen_\\u5ba2\\u89c2'),c:''}
  ];
  for(var i=0;i<objItems.length;i++){
    var it=objItems[i];
    objHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('objMetrics').innerHTML=objHtml;

  var subHtml='';
  var subItems = [
    {t:'GSB',s:'\\u8c46\\u5305 vs Qwen',v:fmtGsb(base.GSB||{},'Qwen_\\u4e3b\\u5ba2\\u89c2'),c:gsbClass(base.GSB||{},'Qwen_\\u4e3b\\u5ba2\\u89c2')},
    {t:'\\u53ef\\u7528\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u53ef\\u7528\\u7387']||{},'\\u8c46\\u5305_\\u4e3b\\u5ba2\\u89c2','Qwen_\\u4e3b\\u5ba2\\u89c2'),c:''},
    {t:'\\u52dd\\u9000\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u52dd\\u9000\\u7387']||{},'\\u8c46\\u5305_\\u4e3b\\u5ba2\\u89c2','Qwen_\\u4e3b\\u5ba2\\u89c2'),c:''},
    {t:'\\u6ee1\\u5206\\u7387',s:'\\u8c46\\u5305 vs Qwen',v:fmtPct(base['\\u6ee1\\u5206\\u7387']||{},'\\u8c46\\u5305_\\u4e3b\\u5ba2\\u89c2','Qwen_\\u4e3b\\u5ba2\\u89c2'),c:''}
  ];
  for(var i=0;i<subItems.length;i++){
    var it=subItems[i];
    subHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('subMetrics').innerHTML=subHtml;

  var wordD = base['\\u56de\\u590d\\u5b57\\u6570']||{};
  var dbW = wordD['\\u8c46\\u5305']||0, qwW = wordD['Qwen']||0;
  var ratio = qwW>0?(qwW/dbW).toFixed(1)+'x':'';
  var statHtml='';
  statHtml+='<div class="mc"><div class="mc-title">\\u5b57\\u6570</div><div class="mc-sub">\\u8c46\\u5305 vs Qwen</div><div class="mc-val">'+dbW+' / '+qwW+(ratio?' ('+ratio+')':'')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">\\u5747\\u5206(\\u5ba2\\u89c2)</div><div class="mc-sub">\\u8c46\\u5305 vs Qwen</div><div class="mc-val">'+fmtPct(base['\\u5747\\u5206']||{},'\\u8c46\\u5305_\\u5ba2\\u89c2','Qwen_\\u5ba2\\u89c2')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">\\u5747\\u5206(\\u4e3b\\u5ba2\\u89c2)</div><div class="mc-sub">\\u8c46\\u5305 vs Qwen</div><div class="mc-val">'+fmtPct(base['\\u5747\\u5206']||{},'\\u8c46\\u5305_\\u4e3b\\u5ba2\\u89c2','Qwen_\\u4e3b\\u5ba2\\u89c2')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Session\\u9898\\u91cf</div><div class="mc-sub">\\u53cc\\u7aef/APP/Web</div><div class="mc-val">'+(safeGet(V,['session\\u7ef4\\u5ea6','\\u53cc\\u7aef\\u6574\\u4f53'])||0)+' / '+(safeGet(V,['session\\u7ef4\\u5ea6','APP'])||0)+' / '+(safeGet(V,['session\\u7ef4\\u5ea6','Web'])||0)+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Prompt\\u9898\\u91cf</div><div class="mc-sub">\\u53cc\\u7aef/APP/Web</div><div class="mc-val">'+(safeGet(V,['prompt\\u7ef4\\u5ea6','\\u6574\\u4f53','\\u53cc\\u7aef\\u6574\\u4f53'])||0)+' / '+(safeGet(V,['prompt\\u7ef4\\u5ea6','\\u6574\\u4f53','APP'])||0)+' / '+(safeGet(V,['prompt\\u7ef4\\u5ea6','\\u6574\\u4f53','Web'])||0)+'</div></div>';
  document.getElementById('statMetrics').innerHTML=statHtml;
}"""

html = html[:start] + new_fn + html[end:]

# 6. Fix 劝退率 character: replace 勝退率 with 劝退率
html = html.replace('\u52dd\u9000\u7387', '\u529d\u9000\u7387')

# 7. Remove any remaining volStrip references
lines = html.split('\n')
cleaned = [l for l in lines if 'volStrip' not in l and 'vol-strip' not in l]
html = '\n'.join(cleaned)

with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_final_v3.html:", len(html), "bytes")
print("volStrip refs:", html.count('volStrip') + html.count('vol-strip'))
print("ovDimToggle refs:", html.count('ovDimToggle'))
print("objMetrics refs:", html.count('objMetrics'))
print("subMetrics refs:", html.count('subMetrics'))
print("statMetrics refs:", html.count('statMetrics'))
