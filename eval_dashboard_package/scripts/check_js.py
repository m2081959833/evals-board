import re

with open('viz_page_v6.html') as f:
    html = f.read()

script = html.split('<script>')[1].split('</script>')[0]

# Remove data JSON to focus on code
data_start = script.index('var DATA = ') + len('var DATA = ')
depth = 0
i = data_start
while i < len(script):
    if script[i] == '{': depth += 1
    elif script[i] == '}':
        depth -= 1
        if depth == 0: break
    i += 1
data_end = i + 1

code = script[:script.index('var DATA = ')] + script[data_end:]

# Check for obvious syntax issues
lines = code.strip().split('\n')
print('Total code lines (excl data):', len(lines))

# Check function definitions
funcs = re.findall(r'function\s+(\w+)', code)
print('Functions defined:', funcs)

# Check for variable declarations
var_count = len(re.findall(r'\bvar\b', code))
print('var declarations:', var_count)

# Check for ES6+ features
es6_features = {
    'Arrow function': '=>',
    'Template literal': '`',
    'Optional chaining': '?.',
    'Nullish coalescing': '??',
}

for name, pattern in es6_features.items():
    matches = re.findall(re.escape(pattern) if '.' in pattern or '?' in pattern else pattern, code)
    if matches:
        print('X Found', name, ':', len(matches), 'occurrences')
    else:
        print('OK No', name)

# Show the render function
render_start = code.index('function render()')
print('\n--- render() first 500 chars ---')
print(code[render_start:render_start+500])
