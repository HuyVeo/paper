from gensim.models.fasttext import load_facebook_model
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

dataset_file = r'D:\MGEEMS\ViConSim_Dataset_with_glosses.xlsx'
embedding_output = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\Embedding_fasttext.txt'
similarity_output = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\Simfasttext.txt'
model_path = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\cc.vi.300.bin'

print("Loading fasttext model...")
model = load_facebook_model(model_path)
print("Model loaded!")

df = pd.read_excel(dataset_file)
print(f"Columns: {list(df.columns)}")
print(f"Total pairs: {len(df)}")
# Get concept columns
col_c1 = df.columns[1]  # Concept 1
col_c2 = df.columns[2]  # Concept 2
print(f"Concept 1 column: '{col_c1}'")
print(f"Concept 2 column: '{col_c2}'")

# Compute embeddings for all unique concepts
all_concepts = set(df[col_c1].astype(str).tolist() + df[col_c2].astype(str).tolist())
print(f"Unique concepts: {len(all_concepts)}")

concept_vectors = {}
for cp in all_concepts:
    concept_vectors[cp] = model.wv[cp.replace(' ', '_')]

# Save embeddings
with open(embedding_output, 'w', encoding='utf-8') as f:
    for cp, vec in concept_vectors.items():
        vector_str = " ".join(map(str, vec))
        f.write(f"{cp}\t{vector_str}\n")

print(f"Saved embeddings to {embedding_output}")
# Compute cosine similarity for each concept pair
similarities = []
with open(similarity_output, 'w', encoding='utf-8') as f:
    for idx, row in df.iterrows():
        c1 = str(row[col_c1])
        c2 = str(row[col_c2])
        v1 = concept_vectors[c1].reshape(1, -1)
        v2 = concept_vectors[c2].reshape(1, -1)
        sim = cosine_similarity(v1, v2)[0][0]
        sim = (sim + 1) / 2 * 4  # scale from [-1,1] to [0,4]
        similarities.append(sim)
        f.write(f"{sim}\n")

df['fasttext_similarity'] = similarities
print(f"Done! Computed {len(similarities)} similarity scores")
print(f"Saved to {similarity_output}")
print(f"\nSample results:")
print(df[[col_c1, col_c2, 'fasttext_similarity']].head(10).to_string(index=False))