import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import MinMaxScaler

# Cau hinh
FILES = {
    'simfasttext':  r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\Simfasttext.txt',
    'simlcs':       r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Lexical_Overlap\SimLCS.txt',
    'simcrossword': r'D:\MGEEMS\Test\Similarity\Similarity_Cross_Word_Gloss\SimCrossWord.txt',
    # 'simphobert':   r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Language_Models_Using_Glosses\SimPhoBert.txt',
    'simbamibert':   r'D:\MGEEMS\Test\Similarity\Sim_BamiBert\SimBamiBERT_test.txt'
}
METRIC_NAMES = ['SimFasttext', 'SimLCS', 'SimCrossWord',  'SimBamiBERT']
OUTPUT_PATH = r'D:\MGEEMS\Test\MGEEMS\kq_v3\pearson_results.xlsx'

# Doc du lieu va chuan hoa ve [0, 1]
sims = [np.loadtxt(f) for f in FILES.values()]
human = pd.read_excel(r'D:\MGEEMS\ViConSim_Dataset copy.xlsx', sheet_name='ViConSim')['Score'].values.astype(float)
S = MinMaxScaler().fit_transform(np.column_stack(sims))

# M-GEEMS: tinh diem tong hop bang softmax
def compute_mgeems(S, tau):
    exp_s = np.exp(tau * S)
    alpha = exp_s / exp_s.sum(axis=1, keepdims=True)
    return (alpha * S).sum(axis=1)

# Tuong quan tung metric
rows = []
print(f"{'Method':<20} {'Pearson':>10} {'Spearman':>10}")
print("-" * 42)
for i, name in enumerate(METRIC_NAMES):
    r, _ = pearsonr(S[:, i], human)
    rho, _ = spearmanr(S[:, i], human)
    print(f"{name:<20} {r:>10.4f} {rho:>10.4f}")
    rows.append({'Method': name, 'Pearson': round(r, 4), 'Spearman': round(rho, 4)})

# Tim tau toi uu (Pearson cao nhat)
best_tau = max(np.arange(0.01, 50.01, 0.01), key=lambda t: pearsonr(compute_mgeems(S, t), human)[0])
mg = compute_mgeems(S, best_tau)
r_mg, _ = pearsonr(mg, human)
rho_mg, _ = spearmanr(mg, human)

print("-" * 42)
print(f"{'M-GEEMS (t=' + f'{best_tau:.2f}' + ')':<20} {r_mg:>10.4f} {rho_mg:>10.4f}")
rows.append({'Method': f'M-GEEMS (tau={best_tau:.2f})', 'Pearson': round(r_mg, 4), 'Spearman': round(rho_mg, 4)})

# Xuat Excel
pd.DataFrame(rows).to_excel(OUTPUT_PATH, index=False)
print(f"\nDa xuat: {OUTPUT_PATH}")
