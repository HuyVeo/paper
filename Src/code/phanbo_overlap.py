"""
Gloss Overlap bằng Jaccard Similarity - Chọn 250 cặp theo phân bố điểm
========================================================================

Input:
    - concepts.txt  : mỗi dòng 1 concept (dòng i ứng với gloss dòng i)
    - glosses.txt   : mỗi dòng 1 gloss (định nghĩa) của concept tương ứng

Output:
    - gloss_pairs_250.txt  : 250 cặp với score 0-4
    - gloss_pairs_250.csv  : file CSV tương ứng

Phân bố:
    Score 0: 15.0%  =  38 cặp
    Score 1: 18.3%  =  46 cặp
    Score 2: 19.3%  =  48 cặp
    Score 3: 27.2%  =  68 cặp
    Score 4: 20.2%  =  50 cặp
    Tổng:            250 cặp

Cách dùng:
    python gloss_overlap.py
    python gloss_overlap.py --concepts concepts.txt --glosses glosses.txt
"""

import csv
import sys
import os
import random
from itertools import combinations

# ============================================================
# CẤU HÌNH
# ============================================================
CONCEPT_FILE = r'.\dataset\concept.txt'
GLOSS_FILE = r'.\dataset\gloss.txt'
TOTAL_PAIRS = 250

# Phân bố mong muốn
DISTRIBUTION = {
    0: int(TOTAL_PAIRS * 0.150),   # 38 cặp
    1: int(TOTAL_PAIRS * 0.183),   # 46 cặp
    2: int(TOTAL_PAIRS * 0.193),   # 48 cặp
    3: int(TOTAL_PAIRS * 0.272),   # 68 cặp
    4: TOTAL_PAIRS,                # phần còn lại -> score 4
}
# Tính lại score 4 = tổng - (0+1+2+3)
DISTRIBUTION[4] = TOTAL_PAIRS - sum(DISTRIBUTION[s] for s in range(4))

# ============================================================
# PARSE ARGUMENTS
# ============================================================
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == '--concepts' and i + 1 < len(args):
        CONCEPT_FILE = args[i + 1]; i += 2
    elif args[i] == '--glosses' and i + 1 < len(args):
        GLOSS_FILE = args[i + 1]; i += 2
    else:
        i += 1

# ============================================================
# ĐỌC FILE
# ============================================================
def read_lines(filepath):
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file: {filepath}")
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

concepts = read_lines(CONCEPT_FILE)
glosses = read_lines(GLOSS_FILE)

if len(concepts) != len(glosses):
    print(f"❌ Số concept ({len(concepts)}) != số gloss ({len(glosses)})")
    sys.exit(1)

print(f"Đọc được {len(concepts)} concepts + glosses")

# ============================================================
# JACCARD SIMILARITY
# ============================================================
def tokenize(text):
    """Tách từ đơn giản, chuyển thường, bỏ dấu câu."""
    import re
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    return set(tokens)

def jaccard_similarity(text1, text2):
    """Tính Jaccard = |A ∩ B| / |A ∪ B|"""
    set1 = tokenize(text1)
    set2 = tokenize(text2)
    if not set1 and not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)

def jaccard_to_score(sim):
    """
    Chuyển Jaccard similarity (0.0 - 1.0) thành score (0 - 4).
    
    Ngưỡng:
        0.00 - 0.05  -> Score 0 (không liên quan)
        0.05 - 0.15  -> Score 1 (rất ít liên quan)
        0.15 - 0.30  -> Score 2 (liên quan một phần)
        0.30 - 0.50  -> Score 3 (khá tương đồng)
        0.50 - 1.00  -> Score 4 (rất tương đồng)
    """
    if sim < 0.05:
        return 0
    elif sim < 0.15:
        return 1
    elif sim < 0.30:
        return 2
    elif sim < 0.50:
        return 3
    else:
        return 4

# ============================================================
# TÍNH JACCARD CHO TẤT CẢ CÁC CẶP
# ============================================================
print(f"\nĐang tính Jaccard cho tất cả các cặp...")

n = len(concepts)
all_pairs = []

for i, j in combinations(range(n), 2):
    sim = jaccard_similarity(glosses[i], glosses[j])
    score = jaccard_to_score(sim)
    all_pairs.append({
        'idx_i': i,
        'idx_j': j,
        'concept1': concepts[i],
        'concept2': concepts[j],
        'gloss1': glosses[i],
        'gloss2': glosses[j],
        'jaccard': sim,
        'score': score,
    })

print(f"Tổng số cặp khả dụng: {len(all_pairs)}")

# Thống kê phân bố thực tế
print(f"\nPhân bố thực tế của tất cả các cặp:")
for s in range(5):
    count = sum(1 for p in all_pairs if p['score'] == s)
    pct = count / len(all_pairs) * 100 if all_pairs else 0
    print(f"  Score {s}: {count:>6} cặp ({pct:.1f}%)")

# ============================================================
# CHỌN 250 CẶP THEO PHÂN BỐ MONG MUỐN
# Quy tắc: trong cùng 1 mức score, mỗi concept chỉ xuất hiện 1 lần
#           giữa các mức score khác nhau, concept có thể xuất hiện lại
# ============================================================
print(f"\nChọn {TOTAL_PAIRS} cặp theo phân bố mong muốn...")
print(f"  (Không lặp concept trong cùng mức score)\n")

# Nhóm theo score
by_score = {s: [] for s in range(5)}
for p in all_pairs:
    by_score[p['score']].append(p)

# Xáo trộn mỗi nhóm
for s in range(5):
    random.shuffle(by_score[s])

selected = []
global_used_pairs = set()  # Tránh trùng cặp giữa các mức

for s in range(5):
    needed = DISTRIBUTION[s]
    picked = []
    used_concepts_this_score = set()  # Mỗi concept chỉ xuất hiện 1 lần trong mức này

    for p in by_score[s]:
        pair_key = (p['idx_i'], p['idx_j'])

        # Bỏ qua nếu cặp đã chọn ở mức khác
        if pair_key in global_used_pairs:
            continue

        # Bỏ qua nếu concept đã xuất hiện trong mức score này
        if p['idx_i'] in used_concepts_this_score or p['idx_j'] in used_concepts_this_score:
            continue

        picked.append(p)
        used_concepts_this_score.add(p['idx_i'])
        used_concepts_this_score.add(p['idx_j'])
        global_used_pairs.add(pair_key)

        if len(picked) >= needed:
            break

    selected.extend(picked)

    if len(picked) < needed:
        print(f"  ⚠ Score {s}: cần {needed} nhưng chỉ chọn được {len(picked)} cặp (không đủ concept không trùng)")
    else:
        print(f"  ✓ Score {s}: chọn {len(picked)} cặp")

print(f"\nTổng số cặp đã chọn: {len(selected)}")

# Nếu thiếu, bù từ các mức có dư (vẫn giữ quy tắc không trùng cặp)
if len(selected) < TOTAL_PAIRS:
    deficit = TOTAL_PAIRS - len(selected)
    print(f"  Thiếu {deficit} cặp, bù từ các mức có dư...")
    for s in range(5):
        for p in by_score[s]:
            pair_key = (p['idx_i'], p['idx_j'])
            if pair_key not in global_used_pairs:
                selected.append(p)
                global_used_pairs.add(pair_key)
                if len(selected) >= TOTAL_PAIRS:
                    break
        if len(selected) >= TOTAL_PAIRS:
            break

# ============================================================
# THỐNG KÊ CUỐI CÙNG
# ============================================================
print(f"\n{'='*60}")
print(f"PHÂN BỐ CUỐI CÙNG ({len(selected)} cặp)")
print(f"{'='*60}")
for s in range(5):
    count = sum(1 for p in selected if p['score'] == s)
    pct = count / len(selected) * 100 if selected else 0
    target_pct = DISTRIBUTION[s] / TOTAL_PAIRS * 100
    print(f"  Score {s}: {count:>4} cặp ({pct:>5.1f}%)  [mục tiêu: {target_pct:.1f}%]")

# ============================================================
# XUẤT FILE TXT
# ============================================================
selected_sorted = sorted(selected, key=lambda p: p['score'])

with open('gloss_pairs_250.txt', 'w', encoding='utf-8') as f:
    # Header cách nhau bằng tab
    f.write('\t'.join(['STT', 'concept1', 'concept2', 'gloss1', 'gloss2', 'jaccard', 'score']) + '\n')
    for i, p in enumerate(selected_sorted, 1):
        row = [
            str(i),
            p['concept1'],
            p['concept2'],
            p['gloss1'],
            p['gloss2'],
            f"{p['jaccard']:.4f}",
            str(p['score']),
        ]
        f.write('\t'.join(row) + '\n')

print(f"\n✓ Đã xuất: gloss_pairs_250.txt (tab-separated)")

# ============================================================
# XUẤT FILE CSV (tab-separated, có cả gloss)
# ============================================================
with open('gloss_pairs_250.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['stt', 'concept1', 'concept2', 'gloss1', 'gloss2', 'jaccard', 'score'])
    for i, p in enumerate(selected_sorted, 1):
        writer.writerow([
            i,
            p['concept1'],
            p['concept2'],
            p['gloss1'],
            p['gloss2'],
            round(p['jaccard'], 4),
            p['score'],
        ])

print(f"✓ Đã xuất: gloss_pairs_250.csv (tab-separated)")

# ============================================================
# IN MẪU MỖI MỨC SCORE
# ============================================================
print(f"\n{'='*60}")
print(f"VÍ DỤ MỖI MỨC SCORE")
print(f"{'='*60}")
for s in range(5):
    examples = [p for p in selected_sorted if p['score'] == s][:2]
    print(f"\n--- Score {s} ---")
    for p in examples:
        print(f"  {p['concept1']} <-> {p['concept2']}")
        print(f"    Gloss 1: {p['gloss1'][:80]}...")
        print(f"    Gloss 2: {p['gloss2'][:80]}...")
        print(f"    Jaccard: {p['jaccard']:.4f}")