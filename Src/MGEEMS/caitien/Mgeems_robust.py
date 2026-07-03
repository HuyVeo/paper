import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer
from sklearn.model_selection import KFold

FILES = {
    'simfasttext':  r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Word_Embeddings\Simfasttext.txt',
    'simlcs':       r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Lexical_Overlap\SimLCS.txt',
    'simcrossword': r'D:\MGEEMS\Test\Similarity\Similarity_Cross_Word_Gloss\SimCrossWord.txt',
    'simphobert':   r'D:\MGEEMS\Test\Similarity\Similarity_Based_on_Language_Models_Using_Glosses\SimPhoBert.txt',
    "simbamibert":   r'D:\MGEEMS\Test\Similarity\Sim_BamiBert\SimBamiBERT_test.txt'
}
METRIC_NAMES = ['SimFasttext', 'SimLCS', 'SimCrossWord', 'SimPhoBert', 'SimBamiBERT']
OUTPUT_DIR = r'D:\MGEEMS\Test\MGEEMS\caitien'

# Doc du lieu
sims_raw = np.column_stack([np.loadtxt(f) for f in FILES.values()])
human = pd.read_excel(r'D:\MGEEMS\ViConSim_Dataset copy.xlsx',
                       sheet_name='ViConSim')['Score'].values.astype(float)


def normalize_minmax(X):
    """Min-Max Normalization ve [0, 1]."""
    return MinMaxScaler().fit_transform(X)

def normalize_zscore(X):
    """Z-score Normalization roi clip ve [0, 1]."""
    mu = X.mean(axis=0)
    sigma = X.std(axis=0)
    Z = (X - mu) / sigma
    # Clip ve [0, 1] bang sigmoid-style min-max tren Z
    Z_min = Z.min(axis=0)
    Z_max = Z.max(axis=0)
    return (Z - Z_min) / (Z_max - Z_min)

def normalize_quantile(X):
    """Quantile Normalization ve uniform [0, 1]."""
    qt = QuantileTransformer(output_distribution='uniform', random_state=42)
    return qt.fit_transform(X)

NORMALIZERS = {
    'MinMax': normalize_minmax,
    'Z-score': normalize_zscore,
    'Quantile': normalize_quantile,
}


def compute_mgeems(S, tau):
    exp_s = np.exp(tau * S)
    alpha = exp_s / exp_s.sum(axis=1, keepdims=True)
    return (alpha * S).sum(axis=1)

def find_best_tau(S, y, tau_range):
    """Tim tau cho Pearson cao nhat tren tap (S, y)."""
    best_tau, best_r = tau_range[0], -1
    for t in tau_range:
        mg = compute_mgeems(S, t)
        r, _ = pearsonr(mg, y)
        if r > best_r:
            best_r = r
            best_tau = t
    return best_tau, best_r

TAU_RANGE = np.arange(0.01, 50.01, 0.01)


K = 10
kf = KFold(n_splits=K, shuffle=True, random_state=42)

all_results = []  # bang tong hop
cv_details = []   # chi tiet tung fold

print("=" * 70)
print("K-FOLD CROSS-VALIDATION (K={})".format(K))
print("=" * 70)

for norm_name, norm_fn in NORMALIZERS.items():
    print(f"\n>>> Normalization: {norm_name}")
    print(f"{'Method':<20} {'Pearson':>10} {'Spearman':>10}")
    print("-" * 42)

    # Normalize toan bo de tinh metric rieng le
    S_full = norm_fn(sims_raw)

    # Tuong quan tung metric rieng le (tren toan bo dataset - khong can CV)
    for i, mname in enumerate(METRIC_NAMES):
        r, _ = pearsonr(S_full[:, i], human)
        rho, _ = spearmanr(S_full[:, i], human)
        print(f"{mname:<20} {r:>10.4f} {rho:>10.4f}")
        all_results.append({
            'Normalization': norm_name,
            'Method': mname,
            'Pearson': round(r, 4),
            'Spearman': round(rho, 4),
            'Type': 'Individual'
        })

    # K-fold CV cho M-GEEMS
    fold_pearsons = []
    fold_spearmans = []
    fold_taus = []

    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(sims_raw)):
        # Normalize rieng tren train, transform test
        if norm_name == 'MinMax':
            scaler = MinMaxScaler()
            S_train = scaler.fit_transform(sims_raw[train_idx])
            S_test = scaler.transform(sims_raw[test_idx])
            # Clip test ve [0,1] phong truong hop ngoai khoang train
            S_test = np.clip(S_test, 0, 1)
        elif norm_name == 'Z-score':
            mu = sims_raw[train_idx].mean(axis=0)
            sigma = sims_raw[train_idx].std(axis=0)
            Z_train = (sims_raw[train_idx] - mu) / sigma
            Z_test = (sims_raw[test_idx] - mu) / sigma
            # Min-max tren Z_train, ap dung cho Z_test
            z_min = Z_train.min(axis=0)
            z_max = Z_train.max(axis=0)
            S_train = (Z_train - z_min) / (z_max - z_min)
            S_test = (Z_test - z_min) / (z_max - z_min)
            S_test = np.clip(S_test, 0, 1)
        elif norm_name == 'Quantile':
            qt = QuantileTransformer(output_distribution='uniform', random_state=42)
            S_train = qt.fit_transform(sims_raw[train_idx])
            S_test = qt.transform(sims_raw[test_idx])
            S_test = np.clip(S_test, 0, 1)

        # Tim tau toi uu tren train
        best_tau, _ = find_best_tau(S_train, human[train_idx], TAU_RANGE)
        fold_taus.append(best_tau)

        # Evaluate tren test
        mg_test = compute_mgeems(S_test, best_tau)
        r_test, _ = pearsonr(mg_test, human[test_idx])
        rho_test, _ = spearmanr(mg_test, human[test_idx])
        fold_pearsons.append(r_test)
        fold_spearmans.append(rho_test)

        cv_details.append({
            'Normalization': norm_name,
            'Fold': fold_idx + 1,
            'Tau': round(best_tau, 2),
            'Pearson': round(r_test, 4),
            'Spearman': round(rho_test, 4),
        })

    mean_p = np.mean(fold_pearsons)
    std_p = np.std(fold_pearsons)
    mean_s = np.mean(fold_spearmans)
    std_s = np.std(fold_spearmans)
    mean_tau = np.mean(fold_taus)
    std_tau = np.std(fold_taus)

    print("-" * 42)
    print(f"{'M-GEEMS (CV)':<20} {mean_p:>7.4f}±{std_p:.4f} {mean_s:>7.4f}±{std_s:.4f}")
    print(f"  Tau trung binh: {mean_tau:.2f} ± {std_tau:.2f}")

    all_results.append({
        'Normalization': norm_name,
        'Method': f'M-GEEMS (CV, tau={mean_tau:.2f}±{std_tau:.2f})',
        'Pearson': f'{mean_p:.4f}±{std_p:.4f}',
        'Spearman': f'{mean_s:.4f}±{std_s:.4f}',
        'Type': 'M-GEEMS CV'
    })



print("\n" + "=" * 70)
print("SENSITIVITY ANALYSIS")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

sensitivity_data = {}

for idx, (norm_name, norm_fn) in enumerate(NORMALIZERS.items()):
    S_full = norm_fn(sims_raw)
    taus = np.arange(0.1, 50.1, 0.1)
    pearsons = []
    spearmans = []
    for t in taus:
        mg = compute_mgeems(S_full, t)
        r, _ = pearsonr(mg, human)
        rho, _ = spearmanr(mg, human)
        pearsons.append(r)
        spearmans.append(rho)

    pearsons = np.array(pearsons)
    spearmans = np.array(spearmans)

    # Tim peak va plateau
    best_idx = np.argmax(pearsons)
    best_t = taus[best_idx]
    best_p = pearsons[best_idx]
    # Plateau: vung ma Pearson > 0.99 * peak
    threshold = 0.99 * best_p
    plateau_mask = pearsons >= threshold
    plateau_start = taus[plateau_mask][0]
    plateau_end = taus[plateau_mask][-1]

    print(f"\n{norm_name}:")
    print(f"  Peak Pearson = {best_p:.4f} tai tau = {best_t:.1f}")
    print(f"  Plateau (>99% peak): tau in [{plateau_start:.1f}, {plateau_end:.1f}]")

    sensitivity_data[norm_name] = {
        'taus': taus, 'pearsons': pearsons, 'spearmans': spearmans,
        'best_t': best_t, 'best_p': best_p,
        'plateau_start': plateau_start, 'plateau_end': plateau_end,
    }

    ax = axes[idx]
    ax.plot(taus, pearsons, label='Pearson', color='#2196F3', linewidth=1.5)
    ax.plot(taus, spearmans, label='Spearman', color='#FF5722', linewidth=1.5)
    ax.axvline(best_t, color='gray', linestyle='--', alpha=0.7, label=f'Best τ={best_t:.1f}')
    ax.axhspan(threshold, 1.0, alpha=0.08, color='green', label='99% plateau')
    ax.set_xlabel('τ (temperature)', fontsize=12)
    if idx == 0:
        ax.set_ylabel('Correlation', fontsize=12)
    ax.set_title(f'{norm_name} Normalization', fontsize=13)
    ax.legend(fontsize=9, loc='lower right')
    ax.set_xlim(0, 50)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plot_path = f'{OUTPUT_DIR}\\sensitivity_analysis.png'
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nDa luu bieu do: {plot_path}")


output_excel = f'{OUTPUT_DIR}\\mgeems_robust_results.xlsx'
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # Sheet 1: Tong hop
    pd.DataFrame(all_results).to_excel(writer, sheet_name='Summary', index=False)

    # Sheet 2: Chi tiet CV tung fold
    pd.DataFrame(cv_details).to_excel(writer, sheet_name='CV_Details', index=False)

    # Sheet 3: Sensitivity data
    sens_rows = []
    for norm_name, data in sensitivity_data.items():
        for i, t in enumerate(data['taus']):
            sens_rows.append({
                'Normalization': norm_name,
                'Tau': round(t, 2),
                'Pearson': round(data['pearsons'][i], 4),
                'Spearman': round(data['spearmans'][i], 4),
            })
    pd.DataFrame(sens_rows).to_excel(writer, sheet_name='Sensitivity', index=False)

print(f"Da xuat ket qua: {output_excel}")


print("\n" + "=" * 70)
print("BANG SO SANH TONG HOP")
print("=" * 70)
summary_df = pd.DataFrame(all_results)
print(summary_df.to_string(index=False))
