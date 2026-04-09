import openpyxl, json, re, os

wb = openpyxl.load_workbook('cases_excel.xlsx', data_only=True)
ws = wb['评估数据']

def safe_str(v):
    if v is None:
        return ''
    return str(v)

def negate_gsb(v):
    if v is None:
        return ''
    try:
        n = float(v)
        if n == 0:
            return '0'
        # Remove trailing .0 for integers
        neg = -n
        if neg == int(neg):
            return str(int(neg))
        return str(neg)
    except:
        return safe_str(v)

def parse_prompt(raw):
    if not raw:
        return '', []
    s = str(raw)
    imgs = []
    try:
        obj = json.loads(s)
        if isinstance(obj, dict) and 'entities' in obj:
            text = obj.get('text', '')
            for ent in obj.get('entities', []):
                if ent.get('entity_type') == 2:
                    ec = ent.get('entity_content', {})
                    img = ec.get('image', {})
                    ori = img.get('image_ori', {})
                    url = ori.get('url', '')
                    if url:
                        imgs.append(url)
            return text, imgs
    except:
        pass
    return s, []

def sanitize_html(s):
    if not s:
        return ''
    s = str(s)
    s = s.replace('<script', '<scr ipt').replace('</script', '</scr ipt')
    s = s.replace('</Script', '</Scr ipt').replace('<Script', '<Scr ipt')
    return s

cases = []
for ri, row in enumerate(ws.iter_rows(min_row=4, values_only=False), start=4):
    vals = [c.value for c in row]
    prompt_raw = vals[3]
    if not prompt_raw:
        continue

    prompt_text, imgs = parse_prompt(prompt_raw)
    if not prompt_text and not imgs:
        continue

    cat = safe_str(vals[4])
    turn = safe_str(vals[5])
    src = safe_str(vals[6])
    sid = safe_str(vals[1])
    pid = safe_str(vals[2])

    # Use pid as case_id (it already contains session prefix)
    case_id = pid if pid else 'R' + str(ri)

    # --- DCG scores (keep v6-compatible field names: db_obj, db_sub, qw_obj, qw_sub) ---
    # Use prompt-level as the primary display score (same as v6)
    db_obj = safe_str(vals[11])   # 客观dcg(prompt)
    db_sub = safe_str(vals[17])   # 主客观dcg(prompt)
    qw_obj = safe_str(vals[29])   # 客观dcg(prompt)
    qw_sub = safe_str(vals[35])   # 主客观dcg(prompt)

    # --- GSB scores: NEGATE all values ---
    gsb_obj = negate_gsb(vals[44])  # 客观gsb(prompt)
    gsb_sub = negate_gsb(vals[50])  # 主客观gsb(prompt)

    # GSB label/class based on gsb_obj after negation
    gsb_label = ''
    gsb_cls = 'gsb-tie'
    try:
        gv = float(gsb_obj) if gsb_obj != '' else None
        if gv is not None:
            if gv > 0:
                gsb_label = '\u8c46\u5305\u80dc (+' + str(gv) + ')'
                gsb_cls = 'gsb-win'
            elif gv < 0:
                gsb_label = 'Qwen\u80dc (' + str(gv) + ')'
                gsb_cls = 'gsb-lose'
            else:
                gsb_label = '\u5e73\u5c40 (0)'
                gsb_cls = 'gsb-tie'
    except:
        pass

    # --- Reply texts ---
    db_reply = sanitize_html(vals[10])
    qw_reply = sanitize_html(vals[26])

    # --- Word counts ---
    db_w = safe_str(vals[56])
    qw_w = safe_str(vals[57])

    # === NEW ANNOTATION FIELDS ===
    # 豆包 annotations
    db_obj_qt = safe_str(vals[12])    # 客观 问题类型
    db_obj_note = safe_str(vals[13])  # 客观 打分备注
    db_sub_qt = safe_str(vals[18])    # 主客观 问题类型
    db_sub_note = safe_str(vals[19])  # 主客观 打分备注
    db_rich_s = safe_str(vals[23])    # 富媒体得分
    db_rich_t = safe_str(vals[24])    # 富媒体类型
    db_rich_n = safe_str(vals[25])    # 富媒体备注

    # Qwen annotations
    qw_obj_qt = safe_str(vals[30])
    qw_obj_note = safe_str(vals[31])
    qw_sub_qt = safe_str(vals[36])
    qw_sub_note = safe_str(vals[37])
    qw_rich_s = safe_str(vals[41])
    qw_rich_t = safe_str(vals[42])
    qw_rich_n = safe_str(vals[43])

    # GSB annotations
    gsb_obj_dt = safe_str(vals[45])   # diff问题类型
    gsb_obj_note = safe_str(vals[46]) # GSB备注
    gsb_sub_dt = safe_str(vals[51])
    gsb_sub_note = safe_str(vals[52])

    rec = {
        'id': case_id, 'sid': sid, 'r': ri - 3,
        'q': prompt_text, 'cat': cat, 'src': src, 'turn': turn,
        'db_obj': db_obj, 'db_sub': db_sub,
        'qw_obj': qw_obj, 'qw_sub': qw_sub,
        'gsb_obj': gsb_obj, 'gsb_sub': gsb_sub,
        'gsb_label': gsb_label, 'gsb_cls': gsb_cls,
        'db_w': db_w, 'qw_w': qw_w,
        'db_r': db_reply, 'qw_r': qw_reply,
        'imgs': imgs,
        # Annotations
        'db_oq': db_obj_qt, 'db_on': db_obj_note,
        'db_sq': db_sub_qt, 'db_sn': db_sub_note,
        'db_rs': db_rich_s, 'db_rt': db_rich_t, 'db_rn': db_rich_n,
        'qw_oq': qw_obj_qt, 'qw_on': qw_obj_note,
        'qw_sq': qw_sub_qt, 'qw_sn': qw_sub_note,
        'qw_rs': qw_rich_s, 'qw_rt': qw_rich_t, 'qw_rn': qw_rich_n,
        'go_dt': gsb_obj_dt, 'go_n': gsb_obj_note,
        'gs_dt': gsb_sub_dt, 'gs_n': gsb_sub_note,
    }
    cases.append(rec)

print('Total cases:', len(cases))

# Verify GSB negation
pos = sum(1 for c in cases if c['gsb_obj'] and c['gsb_obj'] != '' and float(c['gsb_obj']) > 0)
neg = sum(1 for c in cases if c['gsb_obj'] and c['gsb_obj'] != '' and float(c['gsb_obj']) < 0)
zero = sum(1 for c in cases if c['gsb_obj'] == '0')
print('GSB obj after negation - pos:%d neg:%d zero:%d' % (pos, neg, zero))

# Annotation stats
print('db_on (客观备注):', sum(1 for c in cases if c['db_on']))
print('db_sn (主客观备注):', sum(1 for c in cases if c['db_sn']))
print('go_n (GSB客观备注):', sum(1 for c in cases if c['go_n']))
print('db_rs (富媒体得分):', sum(1 for c in cases if c['db_rs']))

with open('cases_data_v8.json', 'w', encoding='utf-8') as fp:
    json.dump(cases, fp, ensure_ascii=False)
print('Saved cases_data_v8.json, size:', os.path.getsize('cases_data_v8.json'))
