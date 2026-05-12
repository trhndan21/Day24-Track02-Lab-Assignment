import pandas as pd
import os
import json
from src.encryption.vault import SimpleVault
from src.quality.validation import validate_anonymized_data
from src.pii.anonymizer import MedVietAnonymizer

# 1. Test Encryption
print("--- Testing Encryption ---")
vault = SimpleVault()
original_text = "Bệnh nhân Nguyễn Văn A - CCCD: 123456789012"
encrypted = vault.encrypt_data(original_text)
print(f"Encrypted payload: {json.dumps(encrypted, indent=2)}")

decrypted = vault.decrypt_data(encrypted)
print(f"Decrypted text: {decrypted}")
assert decrypted == original_text
print("✅ Encryption round-trip successful!")

# 2. Test Anonymization & Quality
print("\n--- Testing Anonymization & Quality ---")
raw_path = "data/raw/patients_raw.csv"
anon_path = "data/processed/patients_anonymized.csv"

# Load original data
df_raw = pd.read_csv(raw_path)

# Anonymize
anonymizer = MedVietAnonymizer()
df_anon = anonymizer.anonymize_dataframe(df_raw.head(10))

# Ensure directory exists
os.makedirs("data/processed", exist_ok=True)
df_anon.to_csv(anon_path, index=False)
print(f"Saved anonymized data to {anon_path}")

# Validate
validation_results = validate_anonymized_data(anon_path, original_df=df_raw.head(10))
print(f"Validation Results: {json.dumps(validation_results, indent=2)}")

if validation_results["success"]:
    print("✅ Data quality validation passed!")
else:
    print("❌ Data quality validation FAILED!")
    for failure in validation_results["failed_checks"]:
        print(f"  - {failure}")
