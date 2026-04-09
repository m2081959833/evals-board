#!/usr/bin/env python3
"""Fix arrow functions and const/let in viz_page_v5.html for ES5 compatibility."""

import re

with open('viz_page_v5.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace const/let with var in script sections
# Find the script section
script_match = re.search(r'(<script>)(.*?)(</script>)', html, re.DOTALL)
if not script_match:
    print("ERROR: no script section found")
    exit(1)

script = script_match.group(2)

# Replace const and let with var
script = re.sub(r'\bconst\b', 'var', script)
script = re.sub(r'\blet\b', 'var', script)

# 2. Replace arrow functions
# Pattern: (args) => { ... }  or  (args) => expr
# and: arg => { ... }  or  arg => expr

# Simple cases like: el => { ... } or () => { ... } or (a,b) => { ... }
# We need to handle these carefully

# Replace: identifier => { with function(identifier) {
# Replace: (args) => { with function(args) {
# Replace: () => { with function() {

# Multi-arg or no-arg arrow: (args) => 
script = re.sub(r'\(([^)]*)\)\s*=>\s*\{', r'function(\1){', script)
# Single-arg arrow with block: word => {
script = re.sub(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>\s*\{', r'function(\1){', script)

# Arrow with expression (no braces): (args) => expr  -- these are trickier
# e.g., .map(x => x.dataset.v)  -->  .map(function(x){ return x.dataset.v; })
# Pattern: word => expression (up to closing paren or semicolon)
# Let's handle the common patterns:

# .forEach(n=>n.classList...) - single expression
# .map(x=>x.dataset.v) - single expression  
# We need: function(n){ return n.classList...; }

# For expression arrows after => (no opening brace), we need to find the expression end
# This is tricky with regex. Let's use a more targeted approach.

# Actually, let's check if any arrow functions remain
remaining = re.findall(r'=>', script)
if remaining:
    print(f"Still {len(remaining)} arrow functions remaining, applying expression arrow fix...")
    
    # Handle: identifier => expression (no braces)
    # These typically appear inside .map(), .forEach(), etc.
    # Pattern: word => expression-until-closing-context
    
    # Strategy: find all => that aren't followed by { and wrap them
    lines = script.split('\n')
    new_lines = []
    for line in lines:
        # Keep replacing until no more arrows
        max_iters = 20
        while '=>' in line and max_iters > 0:
            max_iters -= 1
            # Try to match: (word)=>expr or word=>expr where expr doesn't start with {
            # Single arg expression arrow: word=>expr
            m = re.search(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>\s*([^{])', line)
            if m:
                # Need to find the full expression - it ends at ) or ; or , at the right nesting level
                start = m.start()
                arg = m.group(1)
                # Find where the expression starts
                expr_start = m.start(2)
                # Parse forward to find the end of expression
                depth = 0
                i = expr_start
                while i < len(line):
                    ch = line[i]
                    if ch in '([{':
                        depth += 1
                    elif ch in ')]}':
                        if depth == 0:
                            break
                        depth -= 1
                    elif ch == ',' and depth == 0:
                        break
                    elif ch == ';' and depth == 0:
                        break
                    i += 1
                expr = line[expr_start:i]
                replacement = 'function(' + arg + '){ return ' + expr + '; }'
                line = line[:start] + replacement + line[i:]
            else:
                break
        new_lines.append(line)
    script = '\n'.join(new_lines)

# Final check
remaining = re.findall(r'=>', script)
print(f"Arrow functions after fix: {len(remaining)}")

# Reassemble
html = html[:script_match.start(2)] + script + html[script_match.end(2):]

with open('viz_page_v5.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Fixed viz_page_v5.html: {len(html)} bytes")

# Verify
with open('viz_page_v5.html', 'r') as f:
    content = f.read()
    
script2 = re.search(r'<script>(.*?)</script>', content, re.DOTALL).group(1)
if 'const ' in script2 or 'let ' in script2:
    print("WARNING: const/let still present!")
else:
    print("✓ No const/let in script")
    
arrows2 = re.findall(r'=>', script2)
print(f"✓ Arrow functions in final: {len(arrows2)}")
