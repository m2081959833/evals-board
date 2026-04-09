import json, re

# ========================================================================
# Step 1: Parse fresh data from the spreadsheet (数据统计 sheet, index=1)
# ========================================================================

raw_text = open('_mira_lark__read_lark_content_eeb4dd3ff31e.json').read()
# Extract the actual content field from JSON
content_obj = json.loads(raw_text)
if isinstance(content_obj, list):
    content_obj = content_obj[0]
if 'text' in content_obj:
    content_obj = json.loads(content_obj['text'])
content = content_obj.get('content','')

# Now re-read the stats sheet (index 1)
# We need to use the data we already fetched
# Let me just hardcode from the fresh spreadsheet read above

# Structure: stats[platform][dimension][category] = {metric: {key: value}}
stats = {}

# Parse table rows
lines = content.split('\n')
table_lines = [l for l in lines if l.startswith('|')]

# The 数据统计 sheet has a specific layout:
# Cols 0-4: volume info (left side)
# Cols 5-9: 双端整体 data (with empty col 10 as separator)
# Cols 11-15: APP data (with empty col 16 as separator)
# Cols 17-21: Web data

# Each metric block has format:
# | <metric_name> | val1 | val2 | val3 | val4 |
# where val1=豆包_客观, val2=豆包_主客观, val3=Qwen_客观, val4=Qwen_主客观

# For 回复字数: val1=豆包, val2=(empty), val3=Qwen, val4=(empty)

def parse_cell(v):
    """Clean cell value"""
    v = v.strip()
    if v in ('', '-', '#DIV/0!', '#N/A'):
        return '-'
    return v

def parse_section(rows, platform_col_offset):
    """Parse a section of metric rows for a specific platform.
    platform_col_offset: 5 for 双端整体, 11 for APP, 17 for Web
    """
    result = {}
    metrics = ['GSB', 'p-value', '可用率', '满分率', '劝退率', '均分', '回复字数']
    
    for row in rows:
        cells = [c.strip() for c in row.split('|')]
        # Remove empty first/last from pipe split
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        
        if len(cells) <= platform_col_offset + 4:
            continue
        
        metric_name = parse_cell(cells[platform_col_offset])
        if metric_name not in metrics:
            continue
        
        v1 = parse_cell(cells[platform_col_offset + 1])  # 豆包_客观
        v2 = parse_cell(cells[platform_col_offset + 2])  # 豆包_主客观  
        v3 = parse_cell(cells[platform_col_offset + 3])  # Qwen_客观
        v4 = parse_cell(cells[platform_col_offset + 4]) if len(cells) > platform_col_offset + 4 else '-'
        
        if metric_name == '回复字数':
            # Parse as integers
            def to_int(s):
                if s == '-':
                    return 0
                try:
                    return int(float(s.replace('%','')))
                except:
                    return 0
            result[metric_name] = {'豆包': to_int(v1), 'Qwen': to_int(v3)}
        else:
            result[metric_name] = {
                '豆包_客观': v1, '豆包_主客观': v2,
                'Qwen_客观': v3, 'Qwen_主客观': v4
            }
    
    return result

# Find the sections in the table
# Session维度 整体 starts right after the header rows
# Prompt维度 sections are separated by blank rows and have headers like "知识联网+非联网（prompt维度）"

platforms = {
    '双端整体': 5,
    'APP': 11,
    'Web': 17
}

# First, identify the row ranges for each section
sections = []  # list of (category, dimension, row_start, row_end)

current_section = None
section_start = 0

for i, line in enumerate(table_lines):
    cells = [c.strip() for c in line.split('|')]
    if cells and cells[0] == '':
        cells = cells[1:]
    
    # Check for section headers
    if len(cells) > 5:
        cell5 = cells[5].strip() if len(cells) > 5 else ''
        
        if '整体（session维度）' in cell5:
            if current_section:
                sections.append((current_section, section_start, i))
            current_section = ('session', '整体')
            section_start = i
        elif '整体（prompt维度）' in cell5:
            if current_section:
                sections.append((current_section, section_start, i))
            current_section = ('prompt', '整体')
            section_start = i
        elif '（prompt维度）' in cell5:
            if current_section:
                sections.append((current_section, section_start, i))
            cat_name = cell5.replace('（prompt维度）', '').strip()
            current_section = ('prompt', cat_name)
            section_start = i

if current_section:
    sections.append((current_section, section_start, len(table_lines)))

print(f"Found {len(sections)} sections:")
for sec, start, end in sections:
    print(f"  {sec} -> rows {start}-{end}")

# Now parse each section for each platform
stats = {'双端整体': {'session': {}, 'prompt': {}}, 
         'APP': {'session': {}, 'prompt': {}}, 
         'Web': {'session': {}, 'prompt': {}}}

for (dim, cat), start, end in sections:
    section_rows = table_lines[start:end]
    for plat_name, col_offset in platforms.items():
        parsed = parse_section(section_rows, col_offset)
        if parsed:
            stats[plat_name][dim][cat] = parsed

# Print summary
for plat in ['双端整体', 'APP', 'Web']:
    for dim in ['session', 'prompt']:
        cats = list(stats[plat][dim].keys())
        print(f"\n{plat}/{dim}: {cats}")
        if cats:
            first_cat = cats[0]
            metrics = stats[plat][dim][first_cat]
            for m, v in metrics.items():
                print(f"  {m}: {v}")

# ========================================================================
# Step 2: Parse volume data
# ========================================================================

volume = {
    'session维度': {'双端整体': 215, 'APP': 201, 'Web': 14},
    'prompt维度': {}
}

# Parse prompt volumes from left side columns
prompt_cats = {
    '整体': None, '知识联网+非联网': None, 'VLM通用': None, '创作': None,
    '角色扮演/对话': None, '多模态需求': None, 'VLM教育': None, '医疗': None,
    '翻译': None, '电商': None, '代码': None, '本地生活': None
}

for line in table_lines:
    cells = [c.strip() for c in line.split('|')]
    if cells and cells[0] == '':
        cells = cells[1:]
    if len(cells) >= 4:
        cat = cells[0].strip()
        if cat in prompt_cats:
            try:
                total = int(cells[1])
                app = int(cells[2])
                web = int(cells[3])
                volume['prompt维度'][cat] = {'双端整体': total, 'APP': app, 'Web': web}
            except:
                pass

print(f"\nVolume data: {json.dumps(volume, ensure_ascii=False, indent=2)}")

# ========================================================================
# Step 3: Fix category name mapping (写作 -> 创作)
# ========================================================================
# The spreadsheet uses "写作" but the filter uses "创作"
for plat in stats:
    for dim in stats[plat]:
        if '写作' in stats[plat][dim] and '创作' not in stats[plat][dim]:
            stats[plat][dim]['创作'] = stats[plat][dim].pop('写作')

# ========================================================================
# Step 4: Save the complete data JSON
# ========================================================================

# Get cases from old data
with open('viz_data_v2.json') as f:
    old_data = json.load(f)

output = {
    'stats': stats,
    'volume': volume,
    'cases': old_data.get('cases', [])
}

with open('viz_data_v5.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved viz_data_v5.json ({len(json.dumps(output))} bytes)")
print(f"Stats keys: {list(stats.keys())}")
print(f"双端整体/session: {list(stats['双端整体']['session'].keys())}")
print(f"双端整体/prompt: {list(stats['双端整体']['prompt'].keys())}")
