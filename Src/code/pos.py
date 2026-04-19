"""
Phân loại CỤM thuật ngữ: Cụm danh từ / Cụm động từ / Cụm tính từ bằng NLTK
=============================================================================

Cài đặt:
    pip install nltk
    python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng'); nltk.download('punkt_tab')"

Chạy:
    python classify_concepts.py
"""

import nltk
import csv

nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk import pos_tag, word_tokenize
from nltk import RegexpParser

# --- Grammar chunking để nhận diện cụm ---
grammar = r"""
    NP:  {<DT>?<JJ.*>*<NN.*>+}
    VP:  {<RB>?<VB.*>+<NN.*|JJ.*>*}
    ADJP: {<RB>?<JJ.*>+}
"""
chunker = RegexpParser(grammar)


def classify_phrase(concept):
    tokens = word_tokenize(concept)
    tagged = pos_tag(tokens)

    # Chi tiết từng từ
    chi_tiet = []
    for word, tag in tagged:
        if tag.startswith('NN'):
            chi_tiet.append(f"{word}(N)")
        elif tag.startswith('JJ'):
            chi_tiet.append(f"{word}(Adj)")
        elif tag.startswith('VB'):
            chi_tiet.append(f"{word}(V)")
        elif tag.startswith('RB'):
            chi_tiet.append(f"{word}(Adv)")
        else:
            chi_tiet.append(f"{word}({tag})")

    chi_tiet_str = ' + '.join(chi_tiet)

    # Chunk để xác định loại cụm
    tree = chunker.parse(tagged)

    chunk_label = None
    for subtree in tree.subtrees():
        if subtree.label() in ('NP', 'VP', 'ADJP'):
            chunk_label = subtree.label()
            break

    # Fallback: dùng head word (từ cuối)
    if not chunk_label:
        head_tag = tagged[-1][1]
        if head_tag.startswith('NN'):
            chunk_label = 'NP'
        elif head_tag.startswith('VB'):
            chunk_label = 'VP'
        elif head_tag.startswith('JJ'):
            chunk_label = 'ADJP'
        else:
            chunk_label = 'OTHER'

    loai_map = {
        'NP': 'Cụm danh từ',
        'VP': 'Cụm động từ',
        'ADJP': 'Cụm tính từ',
        'OTHER': 'Khác',
    }

    return loai_map.get(chunk_label, 'Khác'), chi_tiet_str


# === CHẠY ===
with open('D:\MGEEMS\dataset\concept.txt', 'r', encoding='utf-8') as f:
    concepts = [line.strip() for line in f if line.strip()]

print(f"Đọc được {len(concepts)} concepts\n")

results = []
for concept in concepts:
    loai, chi_tiet = classify_phrase(concept)
    results.append({'concept': concept, 'chi_tiet': chi_tiet, 'loai_cum': loai})
    print(f"{concept:<40} | {chi_tiet:<40} | {loai}")

# Xuất CSV
with open('concepts_result.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['concept', 'chi_tiet', 'loai_cum'])
    writer.writeheader()
    writer.writerows(results)

# Thống kê
print(f"\n{'='*50}")
for loai in ['Cụm danh từ', 'Cụm động từ', 'Cụm tính từ', 'Khác']:
    count = sum(1 for r in results if r['loai_cum'] == loai)
    if count > 0:
        print(f"  {loai:<15}: {count}")
print(f"  {'Tổng':<15}: {len(results)}")
print(f"\nĐã xuất ra: concepts_result.csv")