# M-GEEMS: Multisource Gloss Extraction and Embedding-based Modeling for Semantic Concept Similarity

> A hybrid framework that combines **multisource gloss extraction** (BabelNet, WordNet, Wikipedia) with **distributional word embeddings** for measuring semantic similarity between Vietnamese concepts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Research-orange.svg)

---

## 📖 Overview

Measuring semantic similarity between concepts is a fundamental problem in NLP, powering applications such as information retrieval, question answering, semantic search, and knowledge graph construction. While English and other high-resource languages enjoy mature benchmarks and models, **Vietnamese remains under-explored at the concept level** — existing resources focus on word or sentence similarity and rarely align with lexical knowledge bases.

This repository contributes:

1. **ViConSim** — the first Vietnamese benchmark dataset for concept-level semantic similarity, annotated with human scores and aligned with BabelNet and Vietnamese WordNet.
2. **M-GEEMS** — a hybrid model that fuses knowledge-based gloss signals with distributional embeddings through a Multi-Layer Perceptron (MLP).

---

## 🏗️ Architecture

M-GEEMS is a two-stage framework.

### Stage 1 — Multisource Gloss Extraction

For each concept `c`, glosses are extracted from three complementary resources:

| Source | Notation | Characteristics |
|---|---|---|
| **WordNet** | `g_wn_c` | Concise, lexicographic, denotational |
| **BabelNet** | `g_bn_c` | Multilingual, aggregated, broad coverage |
| **Wikipedia** | `g_wiki_c` | Encyclopedic, contextual, world knowledge |

A **cascading strategy** selects the best available gloss per source, maximizing coverage for concepts with uneven Vietnamese support.

### Stage 2 — Similarity Feature Computation

For each concept pair `(c1, c2)`, **four families** of similarity features are computed at progressively deeper levels of abstraction:

| # | Feature Family | Method | What it captures |
|---|---|---|---|
| 1 | **Word embeddings** | fastText cosine similarity | Distributional similarity at the concept level (+ synonym/antonym variants) |
| 2 | **Lexical overlap** | Jaccard & LCS over glosses | Surface-level word overlap |
| 3 | **Cross-word gloss similarity** | Word2Vec best-match alignment | Soft token-level semantic alignment |
| 4 | **Sentence-level LM similarity** | PhoBERT mean-pooled embeddings | Compositional, contextual gloss semantics |

All features are concatenated into a unified feature vector and passed through an MLP trained with **mean squared error (MSE)** against gold human similarity annotations:

## 📊 ViConSim Dataset

`ViConSim_Dataset copy.xlsx` contains Vietnamese concept pairs annotated with human similarity scores and aligned with:

- **BabelNet** synsets (multilingual coverage)
- **Vietnamese WordNet** senses
- Gloss texts from BabelNet, WordNet, and Wikipedia

Dataset construction follows a rigorous pipeline with domain balancing, length filtering, and multi-annotator validation. Inter-annotator agreement: **Spearman's ρ = 0.848**, **Krippendorff's α = 0.846** (ordinal) — computed by `reliability.py`.

The dataset extends **ViSim-400** (Nguyen et al., 2018) by aligning each pair with BabelNet synsets and WordNet glosses.

### Utility scripts

| Script | Purpose |
|---|---|
| `reliability.py` | Computes Spearman, Fleiss' Kappa, and Krippendorff's Alpha to quantify inter-annotator agreement. |
| `score_stats.py` | Descriptive statistics: score distribution, sentence length, domain balance. Outputs figures to `visualization_output/`. |

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/HuyVeo/paper.git
cd MGEEMS
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Main libraries used:
- `requests`, `pandas`, `numpy`, `openpyxl`
- `wikipedia` (Python Wikipedia API)
- `gensim` (fastText, Word2Vec)
- `torch`, `transformers` (PhoBERT)
- `vncorenlp` (Vietnamese word segmentation)
- `scikit-learn` (MLP, evaluation metrics)
- `scipy`, `krippendorff` (for `reliability.py`)

### 3. Configure BabelNet API
Register at [https://babelnet.org](https://babelnet.org) to obtain a free API key (1,000 requests/day). Set it as an environment variable or edit the extractor config in `code/`:
```bash
export BABELNET_API_KEY="your_key_here"
```

---

## 🛠️ Usage

### Step 1 — Extract glosses
Run the gloss-extraction pipeline inside `code/` to collect definitions from BabelNet, WordNet, and Wikipedia for every concept listed in `dataset/`. Outputs are written back to `dataset/`.

### Step 2 — Compute similarity features
Scripts in `Similarity/` compute the four similarity families per concept pair and emit a unified feature matrix.

### Step 3 — Train M-GEEMS
Training and inference for the MLP predictor live in `MGEEMS/`. The model consumes the feature matrix from Step 2 and gold scores from `ViConSim_Dataset.xlsx`.

### Step 4 — Analyze reliability and statistics
```bash
python reliability.py        # Inter-annotator agreement
python score_stats.py        # Descriptive stats and plots
```
Plots are saved to `visualization_output/`.

---

## 📈 Evaluation Metrics

Following standard practice in Semantic Textual Similarity research:

- **Pearson Correlation (r)** — linear correlation between predicted and human scores
- **Spearman's Rank Correlation (ρ)** — rank-based correlation between predictions and gold

Both metrics enable direct comparison with prior STS work.

---

## 🧪 Results

M-GEEMS consistently outperforms strong lexical and embedding baselines on ViConSim, supporting the claim that **knowledge-enhanced multisource approaches are particularly beneficial for low-resource languages**.

Detailed experimental tables are reported in the accompanying paper.

---

## 🔧 Models & Resources

| Component | Resource |
|---|---|
| Static embeddings | Pretrained Vietnamese **fastText** |
| Cross-word alignment | Pretrained Vietnamese **Word2Vec** |
| Sentence encoder | **PhoBERT** (base) |
| Word segmentation | **VnCoreNLP** |
| Knowledge bases | **BabelNet** v6+, **Vietnamese WordNet**, **Wikipedia (vi)** |

---

## 📝 Citation

If you use M-GEEMS or ViConSim in your research, please cite:

```bibtex
@article{mgeems2025,
  title   = {M-GEEMS: Multisource Gloss Extraction and Embedding-based
             Modeling for Semantic Concept Similarity},
  author  = {...},
  year    = {2025}
}
```

---

## 📚 Key References

- Navigli, R. & Ponzetto, S. P. (2012). *BabelNet: The automatic construction, evaluation and application of a wide-coverage multilingual semantic network.* Artificial Intelligence.
- Miller, G. A. (1995). *WordNet: A lexical database for English.* Communications of the ACM.
- Mikolov, T. et al. (2013). *Efficient estimation of word representations in vector space.* ICLR.
- Nguyen, K. A. et al. (2018). *ViSim-400.*
- Formica, A., Mele, I., & Taglino, F. (2025). *Semantic similarity of words in a taxonomy: a fuzzy and multiple-context approach.* IEEE Access.

See the paper for the full reference list.

---

## 🤝 Contributing

Issues and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

Released under the MIT License. See `LICENSE` for details.

---

## 📬 Contact

For questions, please use the [GitHub Issues page](https://github.com/HuyVeo/MGEEMS/issues).
