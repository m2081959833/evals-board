#!/usr/bin/env python3
"""
Parse LLM evaluation data (4-model comparison) from the markdown table.
Column mapping (0-indexed):
  0: Session题号, 1: Prompt题号, 2: Prompt
  8: 一级分类, 11: 单/多轮, 12: 渠道
  
  豆包: 24=回复, 26=客观dcg(prompt), 27=问题类型, 28=打分备注
        29=客观dcg(session), 32=主客观dcg(prompt), 33=问题类型, 34=打分备注
        35=主客观dcg(session)
  千问: 40=回复, 42=客观dcg(p), 43=问题类型, 44=打分备注
        45=客观dcg(s), 48=主客观dcg(p), 49=问题类型, 50=打分备注, 51=主客观dcg(s)
  豆包vs千问 GSB: 54=客观gsb(p), 55=diff问题类型, 56=GSB备注
                   57=客观gsb(s), 60=主客观gsb(p), 61=diff问题类型, 62=gsb备注, 63=主客观gsb(s)
  
  Gemini: 70=回复, 72=客观dcg(p), 73=问题类型, 74=打分备注
          75=客观dcg(s), 78=主客观dcg(p), 79=问题类型, 80=打分备注, 81=主客观dcg(s)
  豆包vsGemini GSB: 84=客观gsb(p), 85=diff问题, 86=GSB备注
                     87=客观gsb(s), 90=主客观gsb(p), 91=diff问题, 92=gsb备注, 93=主客观gsb(s)
  
  GPT: 98=回复, 100=客观dcg(p), 101=问题类型, 102=打分备注
       103=客观dcg(s), 106=主客观dcg(p), 107=问题类型, 108=打分备注, 109=主客观dcg(s)
  豆包vsGPT GSB: 112=客观gsb(p), 113=diff问题, 114=GSB备注
                  115=客观gsb(s), 118=主客观gsb(p), 119=diff问题, 120=gsb备注, 121=主客观gsb(s)
  
  回复字数: 124=豆包, 125=千问, 126=Gemini, 127=GPT
"""

import json, re

with open('_mira_lark__read_lark_content_3d2e5f26dd9e.json', 'r') as f:
    raw = json.load(f)

text = json.loads(raw[0]['text'])['content']
lines = text.strip().split('\n')

def parse_row(line):
    parts = line.split('|')
    if len(parts) > 2:
        return [p.strip() for p in parts[1:-1]]
    return []

def g(cells, idx):
    """Get cell value safely."""
    if idx >= len(cells): return ''
    v = cells[idx]
    if not v or v == '(null)': return ''
    return v

def sanitize(s):
    if not s: return ''
    s = str(s)
    s = s.replace('<script', '<scr ipt').replace('</script', '</scr ipt')
    return s

def gsb_label(val):
    """Generate GSB label from value. Positive = 豆包胜."""
    if not val or val == '-': return '', 'gsb-tie'
    try:
        f = float(val)
        fi = int(f) if f == int(f) else f
        if f > 0: return '豆包胜 (+%s)' % fi, 'gsb-win'
        elif f < 0: return '竞品胜 (%s)' % fi, 'gsb-lose'
        else: return '平局 (0)', 'gsb-tie'
    except:
        return '', 'gsb-tie'

cases = []
for i in range(7, len(lines)):
    cells = parse_row(lines[i])
    if len(cells) < 30: continue
    pid = g(cells, 1)
    if not pid: continue
    prompt = g(cells, 2)
    if not prompt: continue

    sid = g(cells, 0)
    cat = g(cells, 8)
    turn = g(cells, 11)
    src = g(cells, 12)

    # Round number from prompt ID
    r_match = re.search(r'-(\d+)$', pid)
    r_num = int(r_match.group(1)) if r_match else 1

    # 豆包 DCG scores
    db_obj = g(cells, 26)
    db_sub = g(cells, 32)
    db_reply = sanitize(g(cells, 24))
    db_wc = g(cells, 124)

    # For each competitor, build GSB info
    # 千问
    qw_obj = g(cells, 42)
    qw_sub = g(cells, 48)
    qw_reply = sanitize(g(cells, 40))
    qw_wc = g(cells, 125)
    qw_gsb_obj = g(cells, 54)
    qw_gsb_sub = g(cells, 60)

    # Gemini
    gem_obj = g(cells, 72)
    gem_sub = g(cells, 78)
    gem_reply = sanitize(g(cells, 70))
    gem_wc = g(cells, 126)
    gem_gsb_obj = g(cells, 84)
    gem_gsb_sub = g(cells, 90)

    # GPT
    gpt_obj = g(cells, 100)
    gpt_sub = g(cells, 106)
    gpt_reply = sanitize(g(cells, 98))
    gpt_wc = g(cells, 127)
    gpt_gsb_obj = g(cells, 112)
    gpt_gsb_sub = g(cells, 118)

    # Primary GSB for sorting/filtering: use 千问 GSB as primary
    gsb_label_text, gsb_cls = gsb_label(qw_gsb_obj)

    rec = {
        'id': pid, 'sid': sid, 'r': r_num,
        'q': prompt, 'cat': cat, 'src': src, 'turn': turn,
        # 豆包
        'db_obj': db_obj, 'db_sub': db_sub, 'db_r': db_reply, 'db_w': db_wc,
        'db_oq': g(cells, 27), 'db_on': g(cells, 28),
        'db_sq': g(cells, 33), 'db_sn': g(cells, 34),
        # 千问
        'qw_obj': qw_obj, 'qw_sub': qw_sub, 'qw_r': qw_reply, 'qw_w': qw_wc,
        'qw_oq': g(cells, 43), 'qw_on': g(cells, 44),
        'qw_sq': g(cells, 49), 'qw_sn': g(cells, 50),
        'qw_gsb_obj': qw_gsb_obj, 'qw_gsb_sub': qw_gsb_sub,
        'qw_go_dt': g(cells, 55), 'qw_go_n': g(cells, 56),
        'qw_gs_dt': g(cells, 61), 'qw_gs_n': g(cells, 62),
        # Gemini
        'gem_obj': gem_obj, 'gem_sub': gem_sub, 'gem_r': gem_reply, 'gem_w': gem_wc,
        'gem_oq': g(cells, 73), 'gem_on': g(cells, 74),
        'gem_sq': g(cells, 79), 'gem_sn': g(cells, 80),
        'gem_gsb_obj': gem_gsb_obj, 'gem_gsb_sub': gem_gsb_sub,
        'gem_go_dt': g(cells, 85), 'gem_go_n': g(cells, 86),
        'gem_gs_dt': g(cells, 91), 'gem_gs_n': g(cells, 92),
        # GPT
        'gpt_obj': gpt_obj, 'gpt_sub': gpt_sub, 'gpt_r': gpt_reply, 'gpt_w': gpt_wc,
        'gpt_oq': g(cells, 101), 'gpt_on': g(cells, 102),
        'gpt_sq': g(cells, 107), 'gpt_sn': g(cells, 108),
        'gpt_gsb_obj': gpt_gsb_obj, 'gpt_gsb_sub': gpt_gsb_sub,
        'gpt_go_dt': g(cells, 113), 'gpt_go_n': g(cells, 114),
        'gpt_gs_dt': g(cells, 119), 'gpt_gs_n': g(cells, 120),
        # Primary GSB (vs千问)
        'gsb_label': gsb_label_text, 'gsb_cls': gsb_cls,
    }
    cases.append(rec)

print('Parsed %d cases' % len(cases))
print('Categories:', sorted(set(c['cat'] for c in cases if c['cat'])))
print('Sources:', sorted(set(c['src'] for c in cases if c['src'])))

# Sample
if cases:
    c = cases[0]
    print('\nFirst case:')
    print('  id=%s sid=%s cat=%s' % (c['id'], c['sid'], c['cat']))
    print('  q=%s...' % c['q'][:60])
    print('  db_obj=%s db_sub=%s db_r=%s...' % (c['db_obj'], c['db_sub'], c['db_r'][:40] if c['db_r'] else ''))
    print('  qw_obj=%s qw_sub=%s qw_gsb=%s' % (c['qw_obj'], c['qw_sub'], c['qw_gsb_obj']))

with open('llm_cases.json', 'w') as f:
    json.dump(cases, f, ensure_ascii=False)
print('\nSaved to llm_cases.json (%d bytes)' % len(json.dumps(cases, ensure_ascii=False)))
