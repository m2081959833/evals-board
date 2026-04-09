#!/usr/bin/env python3
"""Trim reply texts to reduce JSON size while keeping useful content"""
import json

with open('cases_data_v2.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Trim replies to 500 chars max
for c in cases:
    if c.get('db_r') and len(c['db_r']) > 500:
        c['db_r'] = c['db_r'][:500]
    if c.get('qw_r') and len(c['qw_r']) > 500:
        c['qw_r'] = c['qw_r'][:500]

j = json.dumps(cases, ensure_ascii=False, separators=(',', ':'))
print(f"Trimmed to 500 chars: {len(j)} bytes ({len(j)/1024:.0f} KB)")

# Try 300 chars
for c in cases:
    if c.get('db_r') and len(c['db_r']) > 300:
        c['db_r'] = c['db_r'][:300]
    if c.get('qw_r') and len(c['qw_r']) > 300:
        c['qw_r'] = c['qw_r'][:300]

j = json.dumps(cases, ensure_ascii=False, separators=(',', ':'))
print(f"Trimmed to 300 chars: {len(j)} bytes ({len(j)/1024:.0f} KB)")
