import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

# Load model PhoBERT-v2
model_name = "vinai/phobert-base-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"Device: {device}")

# Config
dataset_file = r'D:\MGEEMS\ViConSim_Dataset_with_glosses.xlsx'
embedding_output = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Language_Models_Using_Glosses\Embedding_phobert.txt'
similarity_output = r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Language_Models_Using_Glosses\SimPhoBert.txt'
col_g1 = 'Gloss 1 (Sentence 1)'
col_g2 = 'Gloss 2 (Sentence 2)'

def get_embedding(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze(0).cpu().numpy()

df = pd.read_excel(dataset_file)
print(f"Total pairs: {len(df)}")
# Compute embeddings and similarity for each gloss pair
similarities = []
emb_lines = []

for idx, row in df.iterrows():
    g1 = str(row[col_g1]) if pd.notna(row[col_g1]) else ''
    g2 = str(row[col_g2]) if pd.notna(row[col_g2]) else ''

    vec1 = get_embedding(g1) if g1 else np.zeros(768)
    vec2 = get_embedding(g2) if g2 else np.zeros(768)

    sim = cosine_similarity([vec1], [vec2])[0][0]
    sim = (sim + 1) / 2 * 4  # scale to [0, 4]
    similarities.append(sim)

    emb_lines.append(" ".join(map(str, vec1)))
    emb_lines.append(" ".join(map(str, vec2)))

    if (idx + 1) % 50 == 0:
        print(f"[{idx + 1}/{len(df)}]")

# Save embeddings
with open(embedding_output, 'w', encoding='utf-8') as f:
    for line in emb_lines:
        f.write(line + "\n")

# Save similarities
with open(similarity_output, 'w', encoding='utf-8') as f:
    for sim in similarities:
        f.write(f"{sim}\n")

df['phobert_similarity'] = similarities
print(f"\nDone! Computed {len(similarities)} PhoBERT similarity scores")
print(f"Saved to {similarity_output}")
print(f"\nSample results:")
print(df[[col_g1, col_g2, 'phobert_similarity']].head(10).to_string(index=False))