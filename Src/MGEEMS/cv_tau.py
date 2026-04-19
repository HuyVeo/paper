"""5-fold cross-validation for tau-tuning in M-GEEMS.

Goal: measure the Pearson-r gap between full-dataset tuning and held-out
      cross-validation, i.e.  Delta_r  =  r_cv - r_full
      (reported in the paper as  Delta_r = -a).
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.model_selection import KFold
from sklearn.preprocessing import MinMaxScaler

FILES = {
    "simfasttext":  r"D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\Simfasttext.txt",
    "simlcs":       r"D:\MGEEMS\Test\Similarity\Similarity_Based_on_Lexical_Overlap\SimLCS.txt",
    "simcrossword": r"D:\MGEEMS\Test\Similarity\Similarity_Cross_Word_Gloss\SimCrossWord.txt",
    "simphobert":   r"D:\MGEEMS\Test\Similarity\Similarity_Based_on_Language_Models_Using_Glosses\SimPhoBert.txt",
    "human":        r"D:\MGEEMS\ViConSim_Dataset copy.xlsx",
}

TAU_GRID = np.arange(0.1, 10.01, 0.1)   # candidate values of tau
N_FOLDS  = 5
SEED     = 42


def mgeems(S, tau):
    e = np.exp(tau * S)
    alpha = e / e.sum(axis=1, keepdims=True)
    return (alpha * S).sum(axis=1)


def best_tau(S, y):
    best_r, best_t = -1.0, TAU_GRID[0]
    for t in TAU_GRID:
        r, _ = pearsonr(mgeems(S, t), y)
        if r > best_r:
            best_r, best_t = r, t
    return best_t, best_r


# ---- load ---------------------------------------------------------------
sigs = [np.loadtxt(FILES[k]) for k in ["simfasttext", "simlcs", "simcrossword", "simphobert"]]
y = pd.read_excel(FILES["human"], sheet_name="ViConSim")["Score"].to_numpy(float)
n = min(min(len(s) for s in sigs), len(y))
S_raw = np.column_stack([s[:n] for s in sigs])
y = y[:n]

S = MinMaxScaler().fit_transform(S_raw)

# ---- full-dataset tuning ------------------------------------------------
tau_full, r_full = best_tau(S, y)
print(f"Full-dataset : tau*={tau_full:.2f}, Pearson r = {r_full:.4f}")

# ---- 5-fold CV ----------------------------------------------------------
kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
preds = np.zeros(n)

for fold, (tr, te) in enumerate(kf.split(S), 1):
    tau_tr, r_tr = best_tau(S[tr], y[tr])
    preds[te] = mgeems(S[te], tau_tr)
    r_te, _ = pearsonr(preds[te], y[te])
    print(f"  Fold {fold}: tau*={tau_tr:.2f}, train r={r_tr:.4f}, test r={r_te:.4f}")

r_cv, _ = pearsonr(preds, y)
delta_r = r_cv - r_full          # paper reports -a, so a = -delta_r
print(f"\nCV (held-out): Pearson r = {r_cv:.4f}")
print(f"Delta r = r_cv - r_full = {delta_r:+.4f}")
print(f"=> a = {abs(delta_r):.4f}")
