import numpy as np
import sys
from scipy.spatial.distance import cdist
import pandas as pd

W2V_PATH = r"D:\MGEEMS\Test\Similarity\Similarity_Cross_Word_Gloss\word2vec_vi_words_100dims.txt"
DATASET_PATH = r"D:\MGEEMS\ViConSim_Dataset_with_glosses.xlsx"
OUTPUT_PATH = r"D:\MGEEMS\Test\Similarity\Similarity_Cross_Word_Gloss\SimCrossWord.txt"
EMBEDDING_DIM = 100

col_g1 = 'Gloss 1 (Sentence 1)'
col_g2 = 'Gloss 2 (Sentence 2)'
def load_w2v_model(path, dim):
    mapping = {}
    try:
        with open(path, 'r', encoding="utf-8") as f:
            first_line = f.readline().strip().split()
            if len(first_line) > 2:
                f.seek(0)
            count = 0
            for line in f:
                parts = line.strip().split()
                if len(parts) != dim + 1:
                    continue
                word = parts[0].replace(" ", "_")
                try:
                    vec = np.array(parts[1:], dtype=float)
                    mapping[word] = vec
                    count += 1
                except ValueError:
                    continue
        return mapping
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file tại {path}")
        sys.exit(1)

def get_word_vector(word, model, dim):
    word = word.replace("-", "_")
    if word in model:
        return model[word]
    sub_words = word.split("_")
    combined_vec = np.zeros(dim)
    found = False
    for sub in sub_words:
        if sub in model:
            combined_vec += model[sub]
            found = True

    if found:
        return combined_vec
    return np.repeat(0.0001, dim)

def sentence_to_matrix(sentence, model, dim):
    words = sentence.strip().split()
    if not words: return None
    return np.array([get_word_vector(w, model, dim) for w in words])

def compute_cross_word_similarity(sen1, sen2, model, dim):
    V1 = sentence_to_matrix(sen1, model, dim) # Shape: (n, 100)
    V2 = sentence_to_matrix(sen2, model, dim) # Shape: (m, 100)
    if V1 is None or V2 is None: return 0.0
    try:
        dists = cdist(V1, V2, 'cosine')
    except Exception:
        return 0.0
    sim_matrix = (2 - dists) / 2
    score_1 = np.mean(np.max(sim_matrix, axis=1))
    score_2 = np.mean(np.max(sim_matrix, axis=0))
    return (score_1 + score_2) / 2
def main():
    model = load_w2v_model(W2V_PATH, EMBEDDING_DIM)
    df = pd.read_excel(DATASET_PATH)
    print(f"Total pairs: {len(df)}")

    similarities = []
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for idx, row in df.iterrows():
            g1 = str(row[col_g1]) if pd.notna(row[col_g1]) else ''
            g2 = str(row[col_g2]) if pd.notna(row[col_g2]) else ''
            score = compute_cross_word_similarity(g1, g2, model, EMBEDDING_DIM)
            score = score * 4  # scale to [0, 4]
            similarities.append(score)
            f.write(f"{score}\n")

    df['crossword_similarity'] = similarities
    print(f"Done! Computed {len(similarities)} CrossWord similarity scores")
    print(f"Saved to {OUTPUT_PATH}")
    print(f"\nSample results:")
    print(df[[col_g1, col_g2, 'crossword_similarity']].head(10).to_string(index=False))

main()