import json
import re

# Read the evaluation data sheet
with open('./_mira_py__read_lark_content_f218d1863bc4.json', 'r') as f:
    data = json.load(f)

text = data[0]['text']
parsed = json.loads(text)
content = parsed['content']
lines = content.split('\n')

# The data is messy because response text contains newlines
# We need to identify rows that start with a message_id pattern (hash)
# or specific known headers

# Find actual data rows - they start with | followed by a 64-char hex hash
cases = []
current_case = None

hash_pattern = re.compile(r'^\| [a-f0-9]{30,64}')
# Also match the continued data pattern with pipe-separated columns

for i, line in enumerate(lines):
    if hash_pattern.match(line):
        # This is the start of a new case
        if current_case:
            cases.append(current_case)
        
        cols = line.split(' | ')
        if len(cols) >= 8:
            # Extract basic info
            msg_id = cols[0].lstrip('| ').strip()
            eval_round = cols[1].strip() if len(cols) > 1 else ''
            session_id = cols[2].strip() if len(cols) > 2 else ''
            prompt_id = cols[3].strip() if len(cols) > 3 else ''
            prompt_text = cols[4].strip() if len(cols) > 4 else ''
            eval_direction = cols[5].strip() if len(cols) > 5 else ''
            single_multi = cols[6].strip() if len(cols) > 6 else ''
            source = cols[7].strip() if len(cols) > 7 else ''
            
            current_case = {
                'message_id': msg_id[:20] + '...',
                'eval_round': eval_round,
                'session_id': session_id,
                'prompt_id': prompt_id,
                'prompt': prompt_text[:200],
                'eval_direction': eval_direction,
                'single_multi': single_multi,
                'source': source,
                'full_line': line
            }

if current_case:
    cases.append(current_case)

print(f"Total cases found: {len(cases)}")

# Show first 5 cases
for i, c in enumerate(cases[:10]):
    print(f"\n--- Case {i+1} ---")
    print(f"  Session: {c['session_id']}, Prompt: {c['prompt_id']}")
    print(f"  Direction: {c['eval_direction']}, Source: {c['source']}")
    print(f"  Prompt: {c['prompt'][:100]}...")

# Get unique eval directions
directions = set(c['eval_direction'] for c in cases)
print(f"\n\nEval directions: {directions}")

# Get unique sources
sources = set(c['source'] for c in cases)
print(f"Sources: {sources}")

# Count by source
from collections import Counter
source_counts = Counter(c['source'] for c in cases)
print(f"Source counts: {source_counts}")

direction_counts = Counter(c['eval_direction'] for c in cases)
print(f"Direction counts: {direction_counts}")

# Save parsed cases
with open('parsed_cases.json', 'w') as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)

print("\nSaved parsed_cases.json")
