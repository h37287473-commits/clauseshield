import sys
sys.path.insert(0, r'C:\Users\PC\.openclaw\workspace\projects\clauseshield')

from utils.code_generator import generate_batch, export_to_json, export_plain_list

# Generate 50 redemption codes
codes = generate_batch(count=50, prefix='CLAUS', max_uses=1, expiry_days=365)

# Save to JSON
export_to_json(codes, 'data/redemption_codes_50.json', append=False)

# Export plain list for easy sharing
export_plain_list(codes, 'data/redemption_codes_50.txt')

print(f'Generated {len(codes)} redemption codes')
print('First 5 codes:')
for c in codes[:5]:
    print(f"  {c['code']}")
