import openpyxl, json, re, os

wb = openpyxl.load_workbook('cases_excel.xlsx', data_only=True)
ws = wb['评估数据']

def safe_str(v):
    if v is None:
        return ''
    return str(v)

def safe_num(v):
    if v is None:
        return ''
    try:
        return float(v)
    except:
        return ''

def parse_prompt(raw):
    """Parse prompt text, extract images from JSON entities."""
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
    """Remove script tags that would break HTML embedding."""
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

    # --- DCG scores (use safe_str to preserve 0) ---
    db_obj_p = safe_str(vals[11])
    db_obj_s = safe_str(vals[14])
    db_sub_p = safe_str(vals[17])
    db_sub_s = safe_str(vals[20])

    qw_obj_p = safe_str(vals[29])
    qw_obj_s = safe_str(vals[32])
    qw_sub_p = safe_str(vals[35])
    qw_sub_s = safe_str(vals[38])

    # --- GSB scores: NEGATE all values ---
    def negate_gsb(v):
        if v is None:
            return ''
        try:
            n = float(v)
            if n == 0:
                return '0'
            return safe_str(-n)
        except:
            return safe_str(v)

    gsb_obj_p = negate_gsb(vals[44])
    gsb_obj_s = negate_gsb(vals[47])
    gsb_sub_p = negate_gsb(vals[50])
    gsb_sub_s = negate_gsb(vals[53])

    # --- GSB label/class (based on gsb_obj_p after negation) ---
    gsb_label = ''
    gsb_cls = 'gsb-tie'
    try:
        gv = float(gsb_obj_p) if gsb_obj_p != '' else None
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
    qw_cot = sanitize_html(vals[27])
    qw_attach = sanitize_html(vals[28])

    # --- Word counts ---
    db_w = safe_str(vals[56])
    qw_w = safe_str(vals[57])

    # --- 富媒体意图 ---
    rich_intent = safe_str(vals[8])

    # --- 豆包 annotation fields ---
    db_obj_p_qtype = safe_str(vals[12])
    db_obj_p_note = safe_str(vals[13])
    db_obj_s_qtype = safe_str(vals[15])
    db_obj_s_note = safe_str(vals[16])
    db_sub_p_qtype = safe_str(vals[18])
    db_sub_p_note = safe_str(vals[19])
    db_sub_s_qtype = safe_str(vals[21])
    db_sub_s_note = safe_str(vals[22])
    db_rich_score = safe_str(vals[23])
    db_rich_type = safe_str(vals[24])
    db_rich_note = safe_str(vals[25])

    # --- Qwen annotation fields ---
    qw_obj_p_qtype = safe_str(vals[30])
    qw_obj_p_note = safe_str(vals[31])
    qw_obj_s_qtype = safe_str(vals[33])
    qw_obj_s_note = safe_str(vals[34])
    qw_sub_p_qtype = safe_str(vals[36])
    qw_sub_p_note = safe_str(vals[37])
    qw_sub_s_qtype = safe_str(vals[39])
    qw_sub_s_note = safe_str(vals[40])
    qw_rich_score = safe_str(vals[41])
    qw_rich_type = safe_str(vals[42])
    qw_rich_note = safe_str(vals[43])

    # --- GSB annotation fields ---
    gsb_obj_p_dtype = safe_str(vals[45])
    gsb_obj_p_note = safe_str(vals[46])
    gsb_obj_s_dtype = safe_str(vals[48])
    gsb_obj_s_note = safe_str(vals[49])
    gsb_sub_p_dtype = safe_str(vals[51])
    gsb_sub_p_note = safe_str(vals[52])
    gsb_sub_s_dtype = safe_str(vals[54])
    gsb_sub_s_note = safe_str(vals[55])

    case_id = str(sid) + '-' + str(pid) if sid and pid else 'R' + str(ri)

    rec = {
        'id': case_id,
        'sid': safe_str(sid),
        'r': ri - 3,
        'q': prompt_text,
        'cat': cat,
        'src': src,
        'turn': turn,
        'rich_intent': rich_intent,

        # DCG scores
        'db_obj_p': db_obj_p, 'db_obj_s': db_obj_s,
        'db_sub_p': db_sub_p, 'db_sub_s': db_sub_s,
        'qw_obj_p': qw_obj_p, 'qw_obj_s': qw_obj_s,
        'qw_sub_p': qw_sub_p, 'qw_sub_s': qw_sub_s,

        # GSB scores (negated)
        'gsb_obj_p': gsb_obj_p, 'gsb_obj_s': gsb_obj_s,
        'gsb_sub_p': gsb_sub_p, 'gsb_sub_s': gsb_sub_s,

        'gsb_label': gsb_label, 'gsb_cls': gsb_cls,

        # Word counts
        'db_w': db_w, 'qw_w': qw_w,

        # Reply texts
        'db_r': db_reply, 'qw_r': qw_reply,
        'qw_cot': qw_cot, 'qw_attach': qw_attach,

        # Images
        'imgs': imgs,

        # 豆包 annotations
        'db_obj_p_qtype': db_obj_p_qtype, 'db_obj_p_note': db_obj_p_note,
        'db_obj_s_qtype': db_obj_s_qtype, 'db_obj_s_note': db_obj_s_note,
        'db_sub_p_qtype': db_sub_p_qtype, 'db_sub_p_note': db_sub_p_note,
        'db_sub_s_qtype': db_sub_s_qtype, 'db_sub_s_note': db_sub_s_note,
        'db_rich_score': db_rich_score, 'db_rich_type': db_rich_type, 'db_rich_note': db_rich_note,

        # Qwen annotations
        'qw_obj_p_qtype': qw_obj_p_qtype, 'qw_obj_p_note': qw_obj_p_note,
        'qw_obj_s_qtype': qw_obj_s_qtype, 'qw_obj_s_note': qw_obj_s_note,
        'qw_sub_p_qtype': qw_sub_p_qtype, 'qw_sub_p_note': qw_sub_p_note,
        'qw_sub_s_qtype': qw_sub_s_qtype, 'qw_sub_s_note': qw_sub_s_note,
        'qw_rich_score': qw_rich_score, 'qw_rich_type': qw_rich_type, 'qw_rich_note': qw_rich_note,

        # GSB annotations
        'gsb_obj_p_dtype': gsb_obj_p_dtype, 'gsb_obj_p_note': gsb_obj_p_note,
        'gsb_obj_s_dtype': gsb_obj_s_dtype, 'gsb_obj_s_note': gsb_obj_s_note,
        'gsb_sub_p_dtype': gsb_sub_p_dtype, 'gsb_sub_p_note': gsb_sub_p_note,
        'gsb_sub_s_dtype': gsb_sub_s_dtype, 'gsb_sub_s_note': gsb_sub_s_note,
    }
    cases.append(rec)

print('Total cases:', len(cases))

# Verify GSB negation
pos_count = 0
neg_count = 0
zero_count = 0
for c in cases:
    for k in ['gsb_obj_p', 'gsb_obj_s', 'gsb_sub_p', 'gsb_sub_s']:
        v = c[k]
        if v == '':
            continue
        try:
            fv = float(v)
            if fv > 0:
                pos_count += 1
            elif fv < 0:
                neg_count += 1
            else:
                zero_count += 1
        except:
            pass
print('GSB after negation - positive:', pos_count, 'negative:', neg_count, 'zero:', zero_count)

# Check annotation field counts
ann_fields = [
    'db_obj_p_qtype', 'db_obj_p_note', 'db_sub_p_qtype', 'db_sub_p_note',
    'db_rich_score', 'db_rich_type', 'db_rich_note',
    'qw_obj_p_qtype', 'qw_obj_p_note', 'qw_sub_p_qtype', 'qw_sub_p_note',
    'qw_rich_score', 'qw_rich_type', 'qw_rich_note',
    'gsb_obj_p_dtype', 'gsb_obj_p_note', 'gsb_sub_p_dtype', 'gsb_sub_p_note',
]
for f in ann_fields:
    cnt = sum(1 for c in cases if c[f] != '')
    print('  ', f, ':', cnt)

# Save JSON
with open('cases_data_v7.json', 'w', encoding='utf-8') as fp:
    json.dump(cases, fp, ensure_ascii=False)
print('Saved cases_data_v7.json, size:', os.path.getsize('cases_data_v7.json'))
