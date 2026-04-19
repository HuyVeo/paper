import numpy as np
import pandas as pd
from itertools import combinations
from scipy.stats import spearmanr, f

df = pd.read_excel("ViConSim_Dataset copy.xlsx", sheet_name="ViConSim")
cols = ["Human1", "Human2", "Human3", "Human4", "Human5"]
M = df[cols].to_numpy(dtype=float)          # n_items x k_raters
n, k = M.shape

# --- Average pairwise Spearman's rho ------------------------------------
rhos = [spearmanr(M[:, i], M[:, j]).correlation
        for i, j in combinations(range(k), 2)]
rho_avg = float(np.mean(rhos))

print("Pairwise Spearman's rho:")
for (i, j), r in zip(combinations(cols, 2), rhos):
    print(f"  {i:7s} - {j:7s}: {r:.4f}")
print(f"Average Spearman's rho = {rho_avg:.4f}")

# --- ICC(2,1) and ICC(2,k)  (two-way random, absolute agreement) --------
grand_mean = M.mean()
row_means  = M.mean(axis=1)
col_means  = M.mean(axis=0)

SS_total   = ((M - grand_mean) ** 2).sum()
SS_rows    = k * ((row_means - grand_mean) ** 2).sum()
SS_cols    = n * ((col_means - grand_mean) ** 2).sum()
SS_err     = SS_total - SS_rows - SS_cols

MS_rows = SS_rows / (n - 1)
MS_cols = SS_cols / (k - 1)
MS_err  = SS_err  / ((n - 1) * (k - 1))

ICC_2_1 = (MS_rows - MS_err) / (MS_rows + (k - 1) * MS_err + k * (MS_cols - MS_err) / n)
ICC_2_k = (MS_rows - MS_err) / (MS_rows + (MS_cols - MS_err) / n)

# ICC(3,1) and ICC(3,k): two-way mixed, consistency
ICC_3_1 = (MS_rows - MS_err) / (MS_rows + (k - 1) * MS_err)
ICC_3_k = (MS_rows - MS_err) / MS_rows

print(f"\nICC(2,1) single rater    (absolute)    = {ICC_2_1:.4f}")
print(f"ICC(2,k) average raters  (absolute)    = {ICC_2_k:.4f}")
print(f"ICC(3,1) single rater    (consistency) = {ICC_3_1:.4f}")
print(f"ICC(3,k) average raters  (consistency) = {ICC_3_k:.4f}")
