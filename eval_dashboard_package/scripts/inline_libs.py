#!/usr/bin/env python3
"""Inline Chart.js and ChartDataLabels into viz_page_v6.html to eliminate CDN dependency."""

with open('viz_page_v6.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('chart.umd.min.js', 'r', encoding='utf-8') as f:
    chartjs = f.read()

with open('chartjs-plugin-datalabels.min.js', 'r', encoding='utf-8') as f:
    datalabels = f.read()

# Replace CDN script tags with inline scripts
html = html.replace(
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>',
    '<script>\n' + chartjs + '\n</script>'
)

html = html.replace(
    '<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>',
    '<script>\n' + datalabels + '\n</script>'
)

# Verify no external script tags remain
assert 'cdn.jsdelivr.net' not in html, "CDN references still present!"

with open('viz_page_v6_inline.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_page_v6_inline.html: {} bytes".format(len(html)))
print("No external CDN dependencies - fully self-contained!")
