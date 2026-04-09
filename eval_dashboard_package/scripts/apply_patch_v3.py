#!/usr/bin/env python3
"""Apply v3 patches to viz_final_v2.html:
1. Add Session/Prompt toggle to 评估指标 and 统计指标
2. Remove volStrip
"""
import re

with open('viz_final_v2.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add toggle buttons to 评估指标 section header
old_eval = '<div class="section-title">\u8bc4\u4f30\u6307\u6807</div>'
new_eval = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">\u8bc4\u4f30\u6307\u6807</div>
    <div class="ov-dim-toggle" id="ovDimToggle1">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session\u7ef4\u5ea6</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt\u7ef4\u5ea6</button>
    </div>
    </div>'''
assert old_eval in html, "Cannot find 评估指标 header!"
html = html.replace(old_eval, new_eval, 1)

# 2. Add toggle buttons to 统计指标 section header
old_stat = '<div class="section-title">\u7edf\u8ba1\u6307\u6807</div>'
new_stat = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div class="section-title" style="margin-bottom:0">\u7edf\u8ba1\u6307\u6807</div>
    <div class="ov-dim-toggle" id="ovDimToggle2">
      <button class="fbtn active" data-v="session" onclick="switchOvDim(this,'session')">Session\u7ef4\u5ea6</button>
      <button class="fbtn" data-v="prompt" onclick="switchOvDim(this,'prompt')">Prompt\u7ef4\u5ea6</button>
    </div>
    </div>'''
assert old_stat in html, "Cannot find 统计指标 header!"
html = html.replace(old_stat, new_stat, 1)

# 3. Add toggle button CSS before .section-title
toggle_css = '.ov-dim-toggle{display:flex;gap:6px}\n.ov-dim-toggle .fbtn{font-size:12px;padding:2px 10px}\n'
html = html.replace('.section-title{', toggle_css + '.section-title{', 1)

# 4. Remove volStrip div from HTML
html = html.replace('<div class="vol-strip" id="volStrip"></div>', '')

# 5. Remove .vol-strip CSS
html = re.sub(r'\.vol-strip\{[^}]*\}', '', html)

# 6. Replace renderOverview function with dimension-aware version + add switchOvDim
# Find the renderOverview function
ov_match = re.search(r'function renderOverview\(\)\s*\{', html)
assert ov_match, "Cannot find renderOverview function!"

# Find the closing brace of renderOverview
start = ov_match.start()
brace_count = 0
pos = ov_match.end() - 1  # position of opening {
for i in range(pos, len(html)):
    if html[i] == '{':
        brace_count += 1
    elif html[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end = i + 1
            break

old_fn = html[start:end]

new_fn = r"""var ovDim = 'session';
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
  var base = safeGet(S, ['\u53cc\u7aef\u6574\u4f53', ovDim, '\u6574\u4f53']) || {};
  var evalEl = document.getElementById('overviewEval');
  if (evalEl) {
    var gsb = safeGet(base, ['GSB']) || {};
    var pv  = safeGet(base, ['p-value']) || {};
    var evalHtml = '<div class="ov-grid">';
    evalHtml += '<div class="ov-card"><div class="ov-label">GSB (\u5ba2\u89c2)</div><div class="ov-value">' + (gsb['Qwen_\u5ba2\u89c2'] || '-') + '</div></div>';
    evalHtml += '<div class="ov-card"><div class="ov-label">GSB (\u4e3b\u5ba2\u89c2)</div><div class="ov-value">' + (gsb['Qwen_\u4e3b\u5ba2\u89c2'] || '-') + '</div></div>';
    evalHtml += '<div class="ov-card"><div class="ov-label">p-value (\u5ba2\u89c2)</div><div class="ov-value">' + (pv['Qwen_\u5ba2\u89c2'] || '-') + '</div></div>';
    evalHtml += '<div class="ov-card"><div class="ov-label">p-value (\u4e3b\u5ba2\u89c2)</div><div class="ov-value">' + (pv['Qwen_\u4e3b\u5ba2\u89c2'] || '-') + '</div></div>';
    evalHtml += '</div>';
    evalEl.innerHTML = evalHtml;
  }
  var statEl = document.getElementById('overviewStat');
  if (statEl) {
    var ky  = safeGet(base, ['\u53ef\u7528\u7387']) || {};
    var mf  = safeGet(base, ['\u6ee1\u5206\u7387']) || {};
    var qt  = safeGet(base, ['\u52dd\u9000\u7387']) || {};
    var jf  = safeGet(base, ['\u5747\u5206']) || {};
    var zs  = safeGet(base, ['\u56de\u590d\u5b57\u6570']) || {};
    var statHtml = '<div class="ov-grid">';
    statHtml += '<div class="ov-card"><div class="ov-label">\u53ef\u7528\u7387 (\u8c46\u5305/Qwen \u5ba2\u89c2)</div><div class="ov-value">' + (ky['\u8c46\u5305_\u5ba2\u89c2']||'-') + ' / ' + (ky['Qwen_\u5ba2\u89c2']||'-') + '</div></div>';
    statHtml += '<div class="ov-card"><div class="ov-label">\u6ee1\u5206\u7387 (\u8c46\u5305/Qwen \u4e3b\u5ba2\u89c2)</div><div class="ov-value">' + (mf['\u8c46\u5305_\u4e3b\u5ba2\u89c2']||'-') + ' / ' + (mf['Qwen_\u4e3b\u5ba2\u89c2']||'-') + '</div></div>';
    statHtml += '<div class="ov-card"><div class="ov-label">\u52dd\u9000\u7387 (\u8c46\u5305/Qwen \u5ba2\u89c2)</div><div class="ov-value">' + (qt['\u8c46\u5305_\u5ba2\u89c2']||'-') + ' / ' + (qt['Qwen_\u5ba2\u89c2']||'-') + '</div></div>';
    statHtml += '<div class="ov-card"><div class="ov-label">\u5747\u5206 (\u8c46\u5305/Qwen \u5ba2\u89c2)</div><div class="ov-value">' + (jf['\u8c46\u5305_\u5ba2\u89c2']||'-') + ' / ' + (jf['Qwen_\u5ba2\u89c2']||'-') + '</div></div>';
    statHtml += '<div class="ov-card"><div class="ov-label">\u56de\u590d\u5b57\u6570 (\u8c46\u5305/Qwen)</div><div class="ov-value">' + (zs['\u8c46\u5305']||'-') + ' / ' + (zs['Qwen']||'-') + '</div></div>';
    statHtml += '</div>';
    statEl.innerHTML = statHtml;
  }
}"""

html = html[:start] + new_fn + html[end:]

# 7. Remove volStrip rendering from render() function
# Remove lines containing volStrip
lines = html.split('\n')
cleaned = []
skip_vol = False
for line in lines:
    if 'volStrip' in line or 'vol-strip' in line:
        continue
    cleaned.append(line)
html = '\n'.join(cleaned)

# 8. Fix: the 劝退率 key uses correct character
# Check if we accidentally put 勝退率 instead of 劝退率
html = html.replace('\u52dd\u9000\u7387', '\u529d\u9000\u7387')

with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_final_v3.html:", len(html), "bytes")
print("volStrip refs:", html.count('volStrip') + html.count('vol-strip'))
print("ovDimToggle refs:", html.count('ovDimToggle'))
print("switchOvDim refs:", html.count('switchOvDim'))
print("劝退率 refs:", html.count('\u529d\u9000\u7387'))
