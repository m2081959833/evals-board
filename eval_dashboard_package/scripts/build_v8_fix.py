import json, re, os

# Load ORIGINAL v6 HTML as base (untouched)
with open('viz_final_v6.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('cases_data_v8.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

with open('case_explorer_v8.js', 'r', encoding='utf-8') as f:
    case_logic_js = f.read()

print('Base HTML size:', len(html))
print('Cases:', len(cases))

# ============================================================
# STEP 1: Fix fmtGsb/gsbClass - ONLY remove the negation
#          DO NOT touch DATA values (they are already correct)
# ============================================================
html = html.replace(
    'var neg = -v;\n    return (neg>0?\'+\':\'\')+neg.toFixed(2)+\'%\';',
    'return (v>0?\'+\':\'\')+v.toFixed(2)+\'%\';'
)
html = html.replace(
    'return (-v)>=0?\'green\':\'red\';',
    'return v>=0?\'green\':\'red\';'
)
assert 'var neg = -v' not in html
assert '(-v)>=0' not in html
print('Step 1: Removed negation in fmtGsb/gsbClass (DATA values untouched)')

# ============================================================
# STEP 2: Add annotation CSS
# ============================================================
ann_css = """<style>
.ann-block{padding:6px 14px 10px;font-size:12px;line-height:1.7;color:#4e5969;border-bottom:1px dashed #e5e6eb}
.ann-line{margin-bottom:2px}
.ann-lbl{color:#86909c;font-weight:500}
.ann-rich{margin-top:4px;padding:6px 10px;background:#fffbe6;border-radius:6px;border:1px solid #ffe58f}
.gsb-ann{padding:8px 20px 10px;font-size:12px;line-height:1.7;color:#4e5969;background:#fafbfc}
.gsb-ann .ann-lbl{color:#86909c;font-weight:500}
</style>"""
html = html.replace('</head>', ann_css + '\n</head>')
print('Step 2: Added CSS')

# ============================================================
# STEP 3: Replace CASES data + case logic
# ============================================================
cases_start = html.find('var CASES = [')
assert cases_start >= 0
m = re.search(r'filterCases\(\);\s*</script>', html[cases_start:])
assert m
replace_end = cases_start + m.start() + len('filterCases();')

cases_json_str = json.dumps(cases, ensure_ascii=False)
cases_json_str = cases_json_str.replace('</script', '<\\/script').replace('</Script', '<\\/Script')
new_block = 'var CASES = ' + cases_json_str + ';\n' + case_logic_js

html = html[:cases_start] + new_block + html[replace_end:]
print('Step 3: Replaced CASES + case logic (%d cases)' % len(cases))

# ============================================================
# STEP 4: Verify
# ============================================================
open_c = html.count('<script>')
close_c = html.count('</script>')
print('Script tags: open=%d close=%d' % (open_c, close_c))
assert open_c == close_c

checks = ['filterCases', 'renderCase', 'annHtml', 'fmtGsb', 'gsbClass', 'var CASES', 'var DATA', 'new Chart(']
for fn in checks:
    status = 'OK' if fn in html else 'MISSING'
    print('  %s: %s' % (fn, status))
    assert fn in html, fn + ' missing!'

# Verify GSB in DATA is ORIGINAL (not negated)
data_start = html.find('var DATA = {')
obj_start = html.index('{', data_start)
depth = 0
pos = obj_start
while pos < len(html):
    if html[pos] == '{': depth += 1
    elif html[pos] == '}':
        depth -= 1
        if depth == 0: break
    pos += 1
dobj = json.loads(html[obj_start:pos+1])
sample_gsb = dobj['stats']['双端整体']['prompt']['整体']['GSB']
print('\nDashboard GSB sample (should be POSITIVE = 豆包赢):')
for k, v in sample_gsb.items():
    print('  %s: %s' % (k, v))

out = 'viz_final_v8.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('\nSaved:', out, 'size:', os.path.getsize(out))
