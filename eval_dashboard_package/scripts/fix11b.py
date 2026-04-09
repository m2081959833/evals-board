#!/usr/bin/env python3
"""fix11b.py - Update p-value chart: threshold 0.05->0.1 and GSB-based coloring."""

path = 'viz_final_v10_full.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update chart comment
html = html.replace(
    "/* p-value: bar per competitor, highlight <0.05 */",
    "/* p-value: bar per competitor, highlight <0.1 with GSB-based coloring */",
    1
)

# 2. Update backgroundColor: need GSB data for coloring
# Current: backgroundColor: pvVals.map(function(v) { return v !== null && v < 0.05 ? '#00b42a' : '#c9cdd4'; }),
# Need: check GSB for each competitor to determine green vs red

old_bg = "backgroundColor: pvVals.map(function(v) { return v !== null && v < 0.05 ? '#00b42a' : '#c9cdd4'; }),"

# We need access to GSB data and suffix inside the map. Let's build the colors array before the chart creation.
new_bg_block = """backgroundColor: (function() {
              var gsbD = m['GSB'];
              return pvVals.map(function(v, idx) {
                if (v === null || v >= 0.1) return '#c9cdd4';
                var gv = gsbD ? parseFloat(gsbD[pvComps[idx] + suffix] || '') : NaN;
                if (isNaN(gv)) return '#c9cdd4';
                return gv > 0 ? '#00b42a' : '#f53f3f';
              });
            })(),"""

if old_bg in html:
    html = html.replace(old_bg, new_bg_block, 1)
    print("OK: Updated p-value chart backgroundColor with GSB-based coloring and 0.1 threshold")
else:
    print("WARN: Could not find backgroundColor line")

# 3. Update datalabels color function
old_dl_color = "color: function(ctx2) { var v = ctx2.dataset.data[ctx2.dataIndex]; return v !== null && v < 0.05 ? '#00b42a' : '#4e5969'; },"

new_dl_color = """color: function(ctx2) {
                var v = ctx2.dataset.data[ctx2.dataIndex];
                if (v === null || v >= 0.1) return '#4e5969';
                var gsbD = m['GSB'];
                var gv = gsbD ? parseFloat(gsbD[pvComps[ctx2.dataIndex] + suffix] || '') : NaN;
                if (isNaN(gv)) return '#4e5969';
                return gv > 0 ? '#00b42a' : '#f53f3f';
              },"""

if old_dl_color in html:
    html = html.replace(old_dl_color, new_dl_color, 1)
    print("OK: Updated p-value chart datalabels color with GSB-based logic")
else:
    print("WARN: Could not find datalabels color line")

# 4. Add significance line to chart subtitle or add annotation
# The chart card title is built generically. Let's add a note in the chart card for p-value
old_legend_note = "if (mKey === 'GSB') h += '<div class=\"legend-note\">\\u2191 正值=豆包领先(绿) \\u00b7 负值=竞品领先(红)</div>';"
new_legend_note = old_legend_note + "\n    if (mKey === 'p-value') h += '<div class=\"legend-note\"><0.1\\u663e\\u8457: \\u8c46\\u5305\\u9886\\u5148=\\u7eff \\u00b7 \\u8c46\\u5305\\u843d\\u540e=\\u7ea2</div>';"

if old_legend_note in html:
    html = html.replace(old_legend_note, new_legend_note, 1)
    print("OK: Added p-value legend note to chart")
else:
    print("WARN: Could not find legend-note line for GSB")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Done!")
