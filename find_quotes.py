import os

with open('data/few_shot_lib.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Chinese left quote: \u201c (8220)
# Chinese right quote: \u201d (8221)
for i, line in enumerate(lines, 1):
    if '\u201c' in line or '\u201d' in line:
        print(f'Line {i}: {line.strip()[:120]}')
