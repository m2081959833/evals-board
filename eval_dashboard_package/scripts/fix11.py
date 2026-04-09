#!/usr/bin/env python3
"""fix11.py - Add p-value significance note and coloring in Tab2 LLM metrics."""

path = 'viz_final_v10_full.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Change p-value card title to include significance note
old_title = "h += '<div class=\"card-title\">' + mName + '</div>';"
# This is generic for all metrics. We need to make it conditional for p-value.
# Instead, let's replace the card-title line to add note for p-value
new_title = "h += '<div class=\"card-title\">' + mName + (mName === 'p-value' ? ' (<0.1\\u663e\\u8457)' : '') + '</div>';"

if old_title in html:
    # Only replace the one inside renderLlmMetrics (first occurrence)
    html = html.replace(old_title, new_title, 1)
    print("OK: Added p-value significance note to card title")
else:
    print("WARN: Could not find card-title line")

# 2. Update the p-value row rendering to use GSB-based coloring
# Current code in the loop:
#   var cls = valClass(v, mName);
# For p-value, we need to check GSB value for the same model to determine color
# Replace the inner loop section to handle p-value specially

old_loop = """    for (var ci = 0; ci < comps.length; ci++) {
      if ((mName === 'GSB' || mName === 'p-value') && comps[ci] === '\\u8c46\\u5305') continue;
      var key = comps[ci] + suffix;
      var v = fmtVal(mData[key] || '-');
      var cls = valClass(v, mName);
      var dispName = (mName === 'GSB' || mName === 'p-value') ? '\\u8c46\\u5305 vs ' + comps[ci] : comps[ci];
      h += '<tr><td>' + dispName + '</td><td class=\"' + cls + '\">' + v + '</td></tr>';
    }"""

new_loop = """    for (var ci = 0; ci < comps.length; ci++) {
      if ((mName === 'GSB' || mName === 'p-value') && comps[ci] === '\\u8c46\\u5305') continue;
      var key = comps[ci] + suffix;
      var v = fmtVal(mData[key] || '-');
      var cls = valClass(v, mName);
      if (mName === 'p-value' && v !== '-') {
        var pf = parseFloat(v);
        if (!isNaN(pf) && pf < 0.1) {
          var gsbData = m['GSB'];
          var gsbVal = gsbData ? parseFloat(gsbData[comps[ci] + suffix] || '') : NaN;
          if (!isNaN(gsbVal)) { cls = gsbVal > 0 ? 'val-good' : 'val-bad'; }
        }
      }
      var dispName = (mName === 'GSB' || mName === 'p-value') ? '\\u8c46\\u5305 vs ' + comps[ci] : comps[ci];
      h += '<tr><td>' + dispName + '</td><td class=\"' + cls + '\">' + v + '</td></tr>';
    }"""

if old_loop in html:
    html = html.replace(old_loop, new_loop, 1)
    print("OK: Updated p-value coloring logic with GSB-based green/red")
else:
    print("WARN: Could not find inner loop code")
    # Debug
    idx = html.find("if ((mName === 'GSB' || mName === 'p-value') && comps[ci]")
    if idx >= 0:
        print(f"  Found partial match at {idx}")
        print(repr(html[idx:idx+300]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Done!")

# Verify
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
if 'gsbVal' in c:
    print("Verify: gsbVal logic found")
if '<0.1' in c:
    idx = c.find('<0.1')
    print(f"Verify: <0.1 note found at pos {idx}")
