with open('viz_final_v3.html', 'r') as f:
    html = f.read()

# Replace JS unicode escape \u52dd (勝) with \u529d (劝) 
old = '\\u52dd\\u9000\\u7387'
new = '\\u529d\\u9000\\u7387'
count = html.count(old)
print(f"Found {count} occurrences of \\u52dd\\u9000\\u7387")
html = html.replace(old, new)

with open('viz_final_v3.html', 'w') as f:
    f.write(html)

# Verify
with open('viz_final_v3.html', 'rb') as f:
    raw = f.read()
old_bytes = b'\\u52dd'
new_bytes = b'\\u529d'
print("Remaining \\u52dd:", raw.count(old_bytes))
print("New \\u529d:", raw.count(new_bytes))
