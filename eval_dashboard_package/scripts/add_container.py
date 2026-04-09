#!/usr/bin/env python3
"""Add centered container with max-width to match reference design"""
import re

with open('viz_final_v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Modify body CSS: remove padding, add centered background
old_body = 'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d2129;padding:20px}'
new_body = 'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d2129;padding:20px 0;margin:0}\n.page-container{max-width:1200px;margin:0 auto;padding:0 24px}'

html = html.replace(old_body, new_body)

# 2. Wrap all body content in a .page-container div
# Find <body> opening and the first content after scripts
# The structure is: <body> ... <div class="header"> ... </body>
html = html.replace('<div class="header">', '<div class="page-container">\n<div class="header">', 1)

# Close .page-container before </body>
html = html.replace('</body>', '</div><!-- /page-container -->\n</body>', 1)

# But we need to make sure the scripts are NOT inside the container
# Actually, the scripts are inside <script> tags in the body, they should be inside the container - that's fine
# Let me check: the last </script> should be followed by </div></body>

with open('viz_final_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Updated viz_final_v3.html: {len(html)} bytes")
print(f"page-container count: {html.count('page-container')}")
