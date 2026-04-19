import pandas as pd

df = pd.read_excel("ViConSim_Dataset copy.xlsx", sheet_name="ViConSim")
s = df["Score"]

print(f"count = {len(s)}")
print(f"mean  = {s.mean():.2f}")
print(f"std   = {s.std():.2f}")
print(f"min   = {s.min()}, max = {s.max()}")
