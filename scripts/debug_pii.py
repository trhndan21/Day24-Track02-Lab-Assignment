import pandas as pd
from src.pii.detector import build_vietnamese_analyzer, detect_pii

analyzer = build_vietnamese_analyzer()
df = pd.read_csv("data/raw/patients_raw.csv").head(1)
row = df.iloc[0]

for col in ["ho_ten", "cccd", "so_dien_thoai", "email"]:
    val = str(row[col])
    results = detect_pii(val, analyzer)
    print(f"Col: {col}, Value: {val}, Detected: {[r.entity_type for r in results]}")
