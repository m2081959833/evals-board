#!/usr/bin/env python3
"""
Parse Excel data and debug why charts are empty.
The issue is likely that the JS pv() function receives data in a format it can't parse,
OR the data keys don't match what the JS code expects.
Let's dump the exact data for APP/prompt/整体 to see what's happening.
"""
import json, openpyxl

wb = openpyxl.load_workbook('source_data2.xlsx', data_only=True)
ws = wb['Sheet1']

# Let's look at the exact raw cell values for APP/prompt/整体
# That section starts at row 13 (title), data at row 16
# APP columns: 12-16 (L:label, M:豆包客观, N:豆包主客观, O:Qwen客观, P:Qwen主客观)

print("=== APP / prompt / 整体 ===")
metrics = ['GSB', 'p-value', '可用率', '满分率', '劝退率', '均分', '回复字数']
for i, metric in enumerate(metrics):
    r = 16 + i  # rows 16-22
    label = ws.cell(r, 12).value
    db_obj = ws.cell(r, 13).value
    db_sub = ws.cell(r, 14).value
    qw_obj = ws.cell(r, 15).value
    qw_sub = ws.cell(r, 16).value
    print(f"R{r} [{label}]: 豆包客观={repr(db_obj)} 豆包主客观={repr(db_sub)} Qwen客观={repr(qw_obj)} Qwen主客观={repr(qw_sub)}")

print("\n=== 双端整体 / session / 整体 ===")
for i, metric in enumerate(metrics):
    r = 4 + i  # rows 4-10
    label = ws.cell(r, 6).value
    db_obj = ws.cell(r, 7).value
    db_sub = ws.cell(r, 8).value
    qw_obj = ws.cell(r, 9).value
    qw_sub = ws.cell(r, 10).value
    print(f"R{r} [{label}]: 豆包客观={repr(db_obj)} 豆包主客观={repr(db_sub)} Qwen客观={repr(qw_obj)} Qwen主客观={repr(qw_sub)}")

# Now load the data we generated and check
with open('viz_data_final.json') as f:
    data = json.load(f)

print("\n=== Generated JSON: APP/prompt/整体 ===")
app_prompt = data['stats']['APP']['prompt']['整体']
for m in metrics:
    print(f"{m}: {json.dumps(app_prompt[m], ensure_ascii=False)}")

print("\n=== Generated JSON: 双端整体/prompt/整体 ===")
dual_prompt = data['stats']['双端整体']['prompt']['整体']
for m in metrics:
    print(f"{m}: {json.dumps(dual_prompt[m], ensure_ascii=False)}")
