import json, re, os

with open('viz_final_v6.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('cases_data_v8.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)
with open('case_explorer_v8.js', 'r', encoding='utf-8') as f:
    case_logic_js = f.read()

print('Base HTML size:', len(html))
print('Cases:', len(cases))

# ============================================================
# STEP 1: Fix GSB display in dashboard
# ============================================================
html = html.replace(
    'var neg = -v;\n    return (neg>0?\'+\':\'\')+neg.toFixed(2)+\'%\';',
    'return (v>0?\'+\':\'\')+v.toFixed(2)+\'%\';'
)
html = html.replace(
    'return (-v)>=0?\'green\':\'red\';',
    'return v>=0?\'green\':\'red\';'
)
print('Step 1: Fixed fmtGsb/gsbClass')

# ============================================================
# STEP 2: Negate GSB values in DATA.stats
# ============================================================
data_start = html.find('var DATA = {')
obj_start = html.index('{', data_start)
depth = 0
pos = obj_start
while pos < len(html):
    ch = html[pos]
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            obj_end = pos + 1
            break
    pos += 1

data_obj = json.loads(html[obj_start:obj_end])
gsb_count = 0
stats = data_obj.get('stats', {})
for platform in stats:
    for scope in stats[platform]:
        for dim in stats[platform][scope]:
            if 'GSB' in stats[platform][scope][dim]:
                gsb = stats[platform][scope][dim]['GSB']
                for key in gsb:
                    val = gsb[key]
                    if val and val != '-':
                        try:
                            v = float(val.replace('%', ''))
                            gsb[key] = str(round(-v, 2)) + '%'
                            gsb_count += 1
                        except:
                            pass

new_data_str = json.dumps(data_obj, ensure_ascii=False)
html = html[:obj_start] + new_data_str + html[obj_end:]
print('Step 2: Negated %d GSB values' % gsb_count)

# ============================================================
# STEP 3: Add annotation CSS
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
print('Step 3: Added CSS')

# ============================================================
# STEP 4: Replace CASES data + case logic (robust search)
# ============================================================
cases_start = html.find('var CASES = [')
assert cases_start >= 0, 'CASES not found'

# Find the last filterCases(); call followed by whitespace and </script>
# Use regex for robustness
m = re.search(r'filterCases\(\);\s*</script>', html[cases_start:])
assert m, 'filterCases end not found'
replace_end = cases_start + m.start() + len('filterCases();')

print('Replacing %d chars (offset %d to %d)' % (replace_end - cases_start, cases_start, replace_end))

cases_json_str = json.dumps(cases, ensure_ascii=False)
cases_json_str = cases_json_str.replace('</script', '<\\/script').replace('</Script', '<\\/Script')
new_block = 'var CASES = ' + cases_json_str + ';\n' + case_logic_js

html = html[:cases_start] + new_block + html[replace_end:]
print('Step 4: Replaced CASES + case logic')

# ============================================================
# STEP 5: Verify everything
# ============================================================
open_c = html.count('<script>')
close_c = html.count('</script>')
print('\nScript tags: open=%d close=%d' % (open_c, close_c))

checks = {
    'filterCases': html.count('function filterCases'),
    'renderCase': html.count('function renderCase'),
    'annHtml': html.count('function annHtml'),
    'fmtGsb': html.count('function fmtGsb'),
    'gsbClass': html.count('function gsbClass'),
    'var CASES': html.count('var CASES'),
    'var DATA': html.count('var DATA'),
    'new Chart(': html.count('new Chart('),
}
all_ok = True
for k, v in checks.items():
    status = 'OK (%d)' % v if v > 0 else 'MISSING'
    print('  %s: %s' % (k, status))
    if v == 0: all_ok = False

assert all_ok, 'Missing required elements!'
assert open_c == close_c, 'Script tag mismatch!'

out = 'viz_final_v8.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('\nSaved:', out, 'size:', os.path.getsize(out))
