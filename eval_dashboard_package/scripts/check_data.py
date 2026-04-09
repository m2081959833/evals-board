import json, re

# The raw table data from the spreadsheet (数据统计 sheet, index=1)
raw = """| 题量 |  |  |  |  | 双端整体（APP+Web） |  |  |  |  |  | APP端（201 Session） |  |  |  |  |  | Web端（14 Session） |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | 双端整体 | APP | Web |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| session维度 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 整体 | 215 | 201 | 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| prompt维度 |  |  |  |  | 整体（session维度） |  |  |  |  |  | 整体（session维度） |  |  |  |  |  | 整体（session维度） |  |  |  |  |  |  |  |  |
| 整体 | 657 | 624 | 33 |  | 3月流式竞对 | 豆包 |  | Qwen3.5 |  |  | 3月流式竞对 | 豆包 |  | Qwen3.5 |  |  | 3月流式竞对 | 豆包 |  | Qwen3.5 |  |  |  |  |  |
| 知识联网+非联网 | 265 | 262 | 3 |  |  | 客观 | 主观+客观 | 客观 | 主观+客观 |  |  | 客观 | 主观+客观 | 客观 | 主观+客观 |  |  | 客观 | 主观+客观 | 客观 | 主观+客观 |  |  |  |  |
| VLM通用 | 92 | 90 | 2 |  | GSB | - | - | 11.40% | 14.65% |  | GSB | - | - | 10.20% | 14.43% |  | GSB | - | - | 28.57% | 17.86% |  |  |  |  |
| 创作 | 108 | 92 | 16 |  | p-value | - | - | 0.0000 | 0.0000 |  | p-value | - | - | 0.0001 | 0.0000 |  | p-value | - | - | 0.0047 | 0.1502 |  |  |  |  |
| 角色扮演/对话 | 48 | 48 | 0 |  | 可用率 | 54.88% | 57.21% | 43.72% | 46.98% |  | 可用率 | 56.2% | 58.7% | 45.3% | 48.8% |  | 可用率 | 35.7% | 35.7% | 21.4% | 21.4% |  |  |  |  |
| 多模态需求 | 41 | 31 | 10 |  | 满分率 | - | 19.07% | - | 16.74% |  | 满分率 | - | 19.9% | - | 17.9% |  | 满分率 | - | 7.1% | - | 0.0% |  |  |  |  |
| VLM教育 | 46 | 46 | 0 |  | 劝退率 | 10.23% | 10.23% | 19.07% | 19.07% |  | 劝退率 | 9.5% | 9.5% | 16.9% | 16.9% |  | 劝退率 | 21.4% | 21.4% | 50.0% | 50.0% |  |  |  |  |
| 医疗 | 45 | 45 | 0 |  | 均分 | 10.23% | 10.23% | 55.07% | 59.93% |  | 均分 | 61.9% | 67.9% | 56.2% | 61.4% |  | 均分 | 50.7% | 51.8% | 38.9% | 38.2% |  |  |  |  |
| 翻译 | 5 | 5 | 0 |  | 回复字数 | 10.23% | 10.23% | 612 |  |  | 回复字数 | 367 |  | 624 |  |  | 回复字数 | 428 |  | 395 |  |  |  |  |  |"""

# I found a critical issue: the spreadsheet is returning incorrect values for 
# 双端整体 session维度 的 均分 and 回复字数 (showing 10.23% instead of correct values)
# This is likely a cell reference bug in the spreadsheet itself.
# 
# The correct values (from APP data which is consistent):
# APP 均分: 豆包_客观=61.9%, 豆包_主客观=67.9%, Qwen_客观=56.2%, Qwen_主客观=61.4%
# So 双端整体 均分 should be approximately: 61.13%, 66.80%, 55.07%, 59.93%
# And 回复字数: 豆包=371, Qwen=612

# Let me check the original viz_data_v2.json to see what values we had
with open('viz_data_v2.json') as f:
    data = json.load(f)

# Verify session dimension data
s = data['stats']['双端整体']['session']['整体']
print("=== 双端整体 / session / 整体 ===")
for m in ['GSB','p-value','可用率','满分率','劝退率','均分','回复字数']:
    print(f"  {m}: {s[m]}")

print()

# Check: what does the pv() function return for these values?
print("=== pv() test ===")
def pv(s):
    if not s or s == '-': return None
    try:
        return float(s.replace('%',''))
    except:
        return None

for m in ['满分率','劝退率','均分']:
    d = s[m]
    print(f"  {m}:")
    print(f"    豆包_客观: '{d.get('豆包_客观','')}' -> pv={pv(d.get('豆包_客观',''))}")
    print(f"    豆包_主客观: '{d.get('豆包_主客观','')}' -> pv={pv(d.get('豆包_主客观',''))}")
    print(f"    Qwen_客观: '{d.get('Qwen_客观','')}' -> pv={pv(d.get('Qwen_客观',''))}")
    print(f"    Qwen_主客观: '{d.get('Qwen_主客观','')}' -> pv={pv(d.get('Qwen_主客观',''))}")

print()
d = s['回复字数']
print(f"  回复字数: 豆包={d.get('豆包','')}, Qwen={d.get('Qwen','')}")
