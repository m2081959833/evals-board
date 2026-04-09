#!/usr/bin/env python3
"""
Patch viz_final_v8.html to add front-end Excel import feature.
Inlines SheetJS + data_import.js, adds upload button CSS.
"""
import os

# Read all components
with open('viz_final_v8.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('xlsx.full.min.js', 'r', encoding='utf-8') as f:
    sheetjs = f.read()
with open('data_import.js', 'r', encoding='utf-8') as f:
    import_js = f.read()

# 1. Add upload button CSS before </head>
upload_css = """<style>
.upload-btn{display:inline-flex;align-items:center;gap:6px;padding:6px 16px;background:#165dff;color:#fff;border-radius:6px;cursor:pointer;font-size:13px;font-weight:500;transition:background .2s;user-select:none}
.upload-btn:hover{background:#0e42d2}
.upload-icon{font-size:16px;line-height:1}
#uploadWrap{display:inline-flex;align-items:center;gap:8px}
</style>"""
html = html.replace('</head>', upload_css + '\n</head>')

# 2. Add SheetJS library as a new script block before the closing </body>
# Find the last </script> before </body>
body_end = html.rfind('</body>')
insert_point = body_end

sheetjs_block = '\n<script>/* SheetJS xlsx.full.min.js */\n' + sheetjs + '\n</script>\n'
import_block = '<script>/* Data Import Module */\n' + import_js + '\n</script>\n'

html = html[:insert_point] + sheetjs_block + import_block + html[insert_point:]

# Write output
output = 'viz_final_v9.html'
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(output)
print('Built: %s (%d bytes, %.1f MB)' % (output, size, size/1024/1024))

# Verify
assert 'upload-btn' in html, 'upload CSS missing'
assert 'handleExcelUpload' in html, 'import JS missing'
assert 'SheetJS' in html, 'SheetJS missing'
assert 'initUploadUI' in html, 'initUploadUI missing'
print('All verifications passed!')
