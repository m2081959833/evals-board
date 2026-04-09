import re

with open('viz_final_v3.html', 'r') as f:
    html = f.read()

# Find the renderOverview function area and replace all \uXXXX with actual characters
def replace_unicode_escapes(match):
    code = int(match.group(1), 16)
    return chr(code)

# Only replace in the new code section (between switchOvDim and end of renderOverview)
start_marker = "var ovDim = 'session';"
end_marker = "document.getElementById('statMetrics').innerHTML=statHtml;\n}"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx) + len(end_marker)

if start_idx >= 0 and end_idx > start_idx:
    section = html[start_idx:end_idx]
    # Replace \uXXXX patterns
    fixed = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode_escapes, section)
    html = html[:start_idx] + fixed + html[end_idx:]
    print(f"Replaced unicode escapes in {end_idx - start_idx} char section")
else:
    print("Could not find section markers!")

with open('viz_final_v3.html', 'w') as f:
    f.write(html)

# Verify
with open('viz_final_v3.html', 'rb') as f:
    raw = f.read()
remaining = raw.count(b'\\u')
# Note: chart.js library has lots of \u patterns, that's fine
# Check specifically in our code section
with open('viz_final_v3.html', 'r') as f:
    html2 = f.read()
s = html2.find("var ovDim = 'session';")
e = html2.find("document.getElementById('statMetrics').innerHTML=statHtml;\n}", s) + 50
our_code = html2[s:e]
our_escapes = re.findall(r'\\u[0-9a-fA-F]{4}', our_code)
print(f"Remaining unicode escapes in our code: {len(our_escapes)}")
if our_escapes:
    print("  Examples:", our_escapes[:5])
print("劝退率 in our code:", our_code.count('劝退率'))
print("Done!")
