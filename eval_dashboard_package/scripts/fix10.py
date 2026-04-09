#!/usr/bin/env python3
"""fix10.py - Change GSB rows in Tab3 trend summary to '豆包 vs X' format."""

path = 'viz_final_v10_full.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# In renderTrendSummary, the inner loop renders each model row for each metric.
# For GSB, we want to:
# 1. Skip 豆包 row (always null/null)
# 2. Show "豆包 vs 千问(Qwen)" etc. instead of just model name
#
# Current code (line ~2237):
#   var first = true;
#   for (var m = 0; m < models.length; m++) {
#     var model = models[m];
#     var md = mData[model];
#     if (!md) continue;
#     h += "<tr>";
#     if (first) {
#       h += "<td rowspan='" + models.length + "' ...>" + mName + "</td>";
#       first = false;
#     }
#     h += "<td>" + (modelLabels[model] || model) + "</td>";
#
# Need to: for GSB, skip 豆包, use different labels, and adjust rowspan

# Strategy: Replace the inner model loop to handle GSB specially

old_inner = """    var first = true;
    for (var m = 0; m < models.length; m++) {
      var model = models[m];
      var md = mData[model];
      if (!md) continue;
      h += "<tr>";
      if (first) {
        h += "<td rowspan='" + models.length + "' style='font-weight:600;vertical-align:middle'>" + mName + "</td>";
        first = false;
      }
      h += "<td>" + (modelLabels[model] || model) + "</td>";"""

new_inner = """    var isGSB = (mName === 'GSB');
    var loopModels = isGSB ? models.filter(function(x){return x !== '\\u8c46\\u5305';}) : models;
    var gsbLabels = {"\\u5343\\u95ee": "\\u8c46\\u5305 vs \\u5343\\u95ee(Qwen)", "Gemini": "\\u8c46\\u5305 vs Gemini", "GPT": "\\u8c46\\u5305 vs GPT"};
    var first = true;
    for (var m = 0; m < loopModels.length; m++) {
      var model = loopModels[m];
      var md = mData[model];
      if (!md) continue;
      h += "<tr>";
      if (first) {
        h += "<td rowspan='" + loopModels.length + "' style='font-weight:600;vertical-align:middle'>" + mName + "</td>";
        first = false;
      }
      var cellLabel = isGSB ? (gsbLabels[model] || '\\u8c46\\u5305 vs ' + model) : (modelLabels[model] || model);
      h += "<td>" + cellLabel + "</td>";"""

count = html.count(old_inner)
print(f"Found {count} occurrence(s) of inner loop code")

if old_inner in html:
    html = html.replace(old_inner, new_inner, 1)
    print("OK: Updated renderTrendSummary GSB rows to '豆包 vs X' format")
else:
    print("WARN: Could not find exact inner loop code")
    # Debug: find nearby code
    idx = html.find("var first = true;")
    while idx >= 0:
        snippet = html[idx:idx+200]
        if 'modelLabels' in snippet:
            print(f"  Found at pos {idx}: {snippet[:100]}...")
            break
        idx = html.find("var first = true;", idx + 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('gsbLabels')
if idx >= 0:
    print(f"Verify: gsbLabels found at pos {idx}")
    print(content[idx:idx+200])
else:
    print("WARN: gsbLabels not found")
