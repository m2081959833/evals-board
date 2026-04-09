import json
import re

# Read the evaluation data sheet - parse more thoroughly to get scores
with open('./_mira_py__read_lark_content_f218d1863bc4.json', 'r') as f:
    data = json.load(f)

text = data[0]['text']
parsed = json.loads(text)
content = parsed['content']
lines = content.split('\n')

# We need to find the last pipe-separated line for each case to get the scores
# Strategy: collect all lines between hash-starts, find the one with score data

hash_pattern = re.compile(r'^\| [a-f0-9]{30,64}')
case_blocks = []
current_block = []

for i, line in enumerate(lines):
    if hash_pattern.match(line):
        if current_block:
            case_blocks.append(current_block)
        current_block = [line]
    elif current_block:
        current_block.append(line)

if current_block:
    case_blocks.append(current_block)

print(f"Total case blocks: {len(case_blocks)}")

# For each case block, find the main data line (the one starting with hash)
# and parse the score-containing line (last line with many pipe columns)
cases_with_scores = []

for block in case_blocks[:5]:
    main_line = block[0]
    cols = main_line.split(' | ')
    print(f"\n=== Block with {len(block)} lines ===")
    print(f"Main cols count: {len(cols)}")
    
    # Find the last line that has score data (numbers and pipe)
    last_data_line = None
    for line in block:
        pipe_count = line.count('|')
        if pipe_count > 40:
            last_data_line = line
    
    if last_data_line:
        score_cols = last_data_line.split(' | ')
        print(f"Score line cols count: {len(score_cols)}")
        # The last two cols should be 豆包 and Qwen3.5 word counts
        if len(score_cols) >= 2:
            print(f"Last cols: ...{score_cols[-3:]}")

print("\n\n--- Examining first block in detail ---")
for i, line in enumerate(case_blocks[0]):
    pipe_count = line.count('|')
    print(f"  Line {i} ({pipe_count} pipes): {line[:120]}...")
