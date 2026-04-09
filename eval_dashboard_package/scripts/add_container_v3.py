#!/usr/bin/env python3
"""Add page-container wrapper to viz_final_v3.html for centered 1200px layout"""

with open('viz_final_v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix body CSS: change padding:20px to padding:20px 0;margin:0
html = html.replace(
    'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d2129;padding:20px}',
    'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d2129;padding:20px 0;margin:0}'
)

# 2. Add page-container CSS before </style>
container_css = '\n.page-container{max-width:1200px;margin:0 auto;padding:0 24px}\n'
html = html.replace('</style>', container_css + '</style>', 1)

# 3. Wrap body content in page-container div
# Find <body> tag
body_start = html.find('<body>')
if body_start >= 0:
    body_content_start = body_start + len('<body>')
    body_end = html.find('</body>')
    body_content = html[body_content_start:body_end]
    html = html[:body_content_start] + '\n<div class="page-container">\n' + body_content + '\n</div>\n' + html[body_end:]
    print("Added page-container wrapper")

with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Final size:", len(html), "bytes")
