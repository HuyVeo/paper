from underthesea import word_tokenize
import pandas as pd

dataset_file = r'D:\MGEEMS\ViConSim_Dataset_with_glosses.xlsx'
output_file = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Lexical_Overlap\SimLCS.txt'

df = pd.read_excel(dataset_file)
print(f"Columns: {list(df.columns)}")
print(f"Total pairs: {len(df)}")

# Find gloss columns
col_g1 = 'Gloss 1 (Sentence 1)'
col_g2 = 'Gloss 2 (Sentence 2)'

def tokenize_vi(text):
    return word_tokenize(text.lower(), format="text").split()

def lcs_length(s1, s2):
    n, m = len(s1), len(s2)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L[n][m]

def lcs_similarity(tokens1, tokens2):
    if not tokens1 or not tokens2:
        return 0.0
    return 4.0 * lcs_length(tokens1, tokens2) / max(len(tokens1), len(tokens2))
similarities = []
with open(output_file, "w", encoding="utf-8") as fout:
    for idx, row in df.iterrows():
        g1 = str(row[col_g1]) if pd.notna(row[col_g1]) else ''
        g2 = str(row[col_g2]) if pd.notna(row[col_g2]) else ''
        tokens1 = tokenize_vi(g1)
        tokens2 = tokenize_vi(g2)
        sim = lcs_similarity(tokens1, tokens2)
        similarities.append(sim)
        fout.write(f"{sim}\n")

df['lcs_similarity'] = similarities
print(f"Done! Computed {len(similarities)} LCS similarity scores")
print(f"Saved to {output_file}")
print(f"\nSample results:")
print(df[[col_g1, col_g2, 'lcs_similarity']].head(10).to_string(index=False))