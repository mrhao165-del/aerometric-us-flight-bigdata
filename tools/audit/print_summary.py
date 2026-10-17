import json

data = json.load(open('tools/audit/candidate_key_audit_summary.json'))
print(f"{'Year':<6} | {'Total Rows':<12} | {'Distinct Keys':<14} | {'Dup Keys':<10} | {'Dup Rows':<10} | {'Dup Rate (%)':<12} | {'Component Nulls'}")
print("-" * 90)
total_r, total_k, total_dk, total_dr = 0, 0, 0, 0
for d in data:
    r, k, dk, dr = d['total_rows'], d['distinct_candidate_keys'], d['duplicate_keys_count'], d['duplicate_rows_count']
    rate = d['duplicate_row_percentage']
    nulls = sum(d['component_nulls'].values())
    total_r += r
    total_k += k
    total_dk += dk
    total_dr += dr
    print(f"{d['year']:<6} | {r:<12,} | {k:<14,} | {dk:<10} | {dr:<10} | {rate:<12.6f} | {nulls}")
print("=" * 90)
print(f"{'TOTAL':<6} | {total_r:<12,} | {total_k:<14,} | {total_dk:<10} | {total_dr:<10} | {(total_dr/total_r)*100:<12.6f} | 0")
