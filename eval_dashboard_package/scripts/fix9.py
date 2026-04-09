#!/usr/bin/env python3
"""fix9.py - Change GSB metric card in Tab2 to show '豆包 vs X' format instead of model names."""

path = 'viz_final_v10_full.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find renderLlmMetrics function and modify the GSB card rendering
# Currently it loops over comps = ['豆包', '千问', 'Gemini', 'GPT'] and shows each as a row
# For GSB and p-value, we want to skip 豆包 and show "豆包 vs 千问" etc.

# The current loop in renderLlmMetrics:
#   for (var ci = 0; ci < comps.length; ci++) {
#     var key = comps[ci] + suffix;
#     var v = fmtVal(mData[key] || '-');
#     var cls = valClass(v, mName);
#     h += '<tr><td>' + comps[ci] + '</td><td class="' + cls + '">' + v + '</td></tr>';
#   }

# We need to change this so for GSB and p-value metrics, it shows:
#   - Skip 豆包 row (since it's always '-')
#   - Show "豆包 vs 千问", "豆包 vs Gemini", "豆包 vs GPT"

old_loop = """    for (var ci = 0; ci < comps.length; ci++) {
      var key = comps[ci] + suffix;
      var v = fmtVal(mData[key] || '-');
      var cls = valClass(v, mName);
      h += '<tr><td>' + comps[ci] + '</td><td class="' + cls + '">' + v + '</td></tr>';
    }"""

new_loop = """    for (var ci = 0; ci < comps.length; ci++) {
      if ((mName === 'GSB' || mName === 'p-value') && comps[ci] === '\\u8c46\\u5305') continue;
      var key = comps[ci] + suffix;
      var v = fmtVal(mData[key] || '-');
      var cls = valClass(v, mName);
      var dispName = (mName === 'GSB' || mName === 'p-value') ? '\\u8c46\\u5305 vs ' + comps[ci] : comps[ci];
      h += '<tr><td>' + dispName + '</td><td class="' + cls + '">' + v + '</td></tr>';
    }"""

if old_loop in html:
    html = html.replace(old_loop, new_loop, 1)
    print("OK: Updated GSB/p-value rows in renderLlmMetrics to show '豆包 vs X' format")
else:
    print("WARN: Could not find the exact loop code")
    # Try to find it with different whitespace
    import re
    pattern = r"for \(var ci = 0; ci < comps\.length; ci\+\+\) \{\s*var key = comps\[ci\] \+ suffix;\s*var v = fmtVal\(mData\[key\] \|\| '-'\);\s*var cls = valClass\(v, mName\);\s*h \+= '<tr><td>' \+ comps\[ci\] \+ '</td><td class=\"' \+ cls \+ '\">' \+ v \+ '</td></tr>';\s*\}"
    m = re.search(pattern, html)
    if m:
        print("Found with regex at position", m.start())
        print("Matched text:", repr(m.group()[:200]))
    else:
        print("Could not find even with regex")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('dispName')
if idx >= 0:
    print("Verify: found dispName at pos", idx)
    print(content[idx-100:idx+200])
else:
    print("WARN: dispName not found in output")
