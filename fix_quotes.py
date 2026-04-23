import json

# Read the file
with open('data/few_shot_lib.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all Chinese quotes with English single quotes
# Left double quote: \u201c
# Right double quote: \u201d
content = content.replace('\u201c', "'")
content = content.replace('\u201d', "'")

# Also replace any other problematic quotes if present
content = content.replace('\u2018', "'")  # Left single quote
content = content.replace('\u2019', "'")  # Right single quote

# Try to parse and rewrite
try:
    data = json.loads(content)
    with open('data/few_shot_lib.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('SUCCESS: All Chinese quotes replaced and JSON rewritten')
    print(f'Total examples: {len(data["examples"])}')
except json.JSONDecodeError as e:
    print(f'ERROR: {e}')
    print(f'Location: line {e.lineno}, col {e.colno}')
    
    # Show surrounding context
    lines = content.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    print('\nContext:')
    for i in range(start, end):
        marker = ' >>> ' if i == e.lineno - 1 else '     '
        print(f'{marker}{i+1}: {lines[i][:100]}')
