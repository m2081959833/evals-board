#!/usr/bin/env python3
"""Parse Excel into JSON - full reply texts, image support, per-prompt view."""
import json, re, openpyxl

wb = openpyxl.load_workbook('cases_excel.xlsx', data_only=True)
ws = wb['评估数据']

def clean_cat(c):
    if not c: return ''
    c = c.strip().replace('\uff08','(').replace('\uff09',')')
    c = re.sub(r'\(.*?\)','',c).strip()
    return c

def gsb_label(v):
    try: v = float(v)
    except: return ('','')
    if v > 0: return ('Qwen\u80dc (+' + str(int(v)) + ')', 'gsb-lose')
    elif v < 0: return ('\u8c46\u5305\u80dc (' + str(int(v)) + ')', 'gsb-win')
    else: return ('\u5e73\u5c40 (0)', 'gsb-tie')

def parse_prompt(raw):
    if not raw: return '', []
    raw = str(raw)
    if raw.startswith('{') and '"entities"' in raw:
        try:
            d = json.loads(raw)
            text = d.get('text','').strip()
            images = []
            for e in d.get('entities',[]):
                if e.get('entity_type') == 2:
                    url = e.get('entity_content',{}).get('image',{}).get('image_ori',{}).get('url','')
                    if url: images.append(url)
            return text, images
        except: return raw, []
    return raw, []

cases = []
for row in ws.iter_rows(min_row=4, max_row=753):
    session = str(row[1].value or '').strip()
    prompt_no = str(row[2].value or '').strip()
    raw_prompt = str(row[3].value or '')
    cat = clean_cat(str(row[4].value or ''))
    turn = str(row[5].value or '').strip()
    src = str(row[6].value or '').strip()
    prompt_text, prompt_images = parse_prompt(raw_prompt)
    # Full reply texts - no truncation
    db_reply = str(row[10].value or '')
    qw_reply = str(row[26].value or '')
    db_obj = str(row[11].value or '')
    db_sub = str(row[17].value or '')
    qw_obj = str(row[29].value or '')
    qw_sub = str(row[35].value or '')
    gsb_obj = str(row[44].value or '')
    gsb_sub = str(row[50].value or '')
    db_w = str(row[56].value or '')
    qw_w = str(row[57].value or '')
    if not session: continue
    r_match = re.search(r'-(\d+)$', prompt_no)
    r_val = int(r_match.group(1)) if r_match else 1
    label, cls = gsb_label(gsb_obj)
    rec = {
        'id': prompt_no, 'sid': session, 'r': r_val,
        'q': prompt_text, 'cat': cat, 'src': src, 'turn': turn,
        'db_obj': db_obj, 'db_sub': db_sub,
        'qw_obj': qw_obj, 'qw_sub': qw_sub,
        'gsb_obj': gsb_obj, 'gsb_sub': gsb_sub,
        'db_w': db_w, 'qw_w': qw_w,
        'db_r': db_reply, 'qw_r': qw_reply,
        'gsb_label': label, 'gsb_cls': cls,
    }
    if prompt_images:
        rec['imgs'] = prompt_images
    cases.append(rec)

print('Total cases:', len(cases))
print('Cases with images:', sum(1 for c in cases if c.get('imgs')))

# Check reply text sizes
db_lens = [len(c['db_r']) for c in cases if c['db_r']]
qw_lens = [len(c['qw_r']) for c in cases if c['qw_r']]
print('DB reply: avg=%d, max=%d' % (sum(db_lens)//len(db_lens), max(db_lens)))
print('QW reply: avg=%d, max=%d' % (sum(qw_lens)//len(qw_lens), max(qw_lens)))

out = json.dumps(cases, ensure_ascii=False, separators=(',',':'))
print('JSON size: %d bytes (%.1f MB)' % (len(out), len(out)/1024/1024))

# If too large, truncate replies to 2000 chars
if len(out) > 3*1024*1024:
    for c in cases:
        if len(c.get('db_r','')) > 2000: c['db_r'] = c['db_r'][:2000]
        if len(c.get('qw_r','')) > 2000: c['qw_r'] = c['qw_r'][:2000]
    out = json.dumps(cases, ensure_ascii=False, separators=(',',':'))
    print('After 2000-char trim: %d bytes (%.1f MB)' % (len(out), len(out)/1024/1024))

with open('cases_data_full.json','w',encoding='utf-8') as f:
    f.write(out)
print('Saved cases_data_full.json')
