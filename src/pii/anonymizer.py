# src/pii/anonymizer.py
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        """
        Anonymize text với strategy được chọn.

        Strategies:
        - "mask"    : Nguyen Van A → N****** V** A
        - "replace" : thay bằng fake data (dùng Faker)
        - "hash"    : SHA-256 one-way hash
        """
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", 
                          {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", 
                                 {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", 
                           {"new_value": f"{fake.random_number(digits=12, fix_len=True)}"}),
                "VN_PHONE": OperatorConfig("replace", 
                            {"new_value": f"09{fake.random_number(digits=8, fix_len=True)}"}),
            }
        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask", {"chars_to_mask": 6, "masking_char": "*", "from_end": True}),
                "EMAIL_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 10, "masking_char": "*", "from_end": True}),
                "VN_CCCD": OperatorConfig("mask", {"chars_to_mask": 8, "masking_char": "*", "from_end": True}),
                "VN_PHONE": OperatorConfig("mask", {"chars_to_mask": 6, "masking_char": "*", "from_end": True}),
            }
        elif strategy == "hash":
            import hashlib
            def hash_func(x): return hashlib.sha256(x.encode()).hexdigest()[:12]
            operators = {
                "PERSON": OperatorConfig("custom", {"lambda": hash_func}),
                "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": hash_func}),
                "VN_CCCD": OperatorConfig("custom", {"lambda": hash_func}),
                "VN_PHONE": OperatorConfig("custom", {"lambda": hash_func}),
            }

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize toàn bộ DataFrame.
        - Cột text (ho_ten, dia_chi, email): dùng anonymize_text()
        - Cột cccd, so_dien_thoai: replace trực tiếp bằng fake data
        - Cột benh, ket_qua_xet_nghiem: GIỮ NGUYÊN (cần cho model training)
        - Cột patient_id: GIỮ NGUYÊN (pseudonym đã đủ an toàn)
        """
        df_anon = df.copy()

        # Xử lý các cột PII bằng cách gọi anonymize_text
        for col in ["ho_ten", "dia_chi", "email"]:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].apply(lambda x: self.anonymize_text(str(x)))

        # Xử lý cccd và so_dien_thoai riêng bằng fake data trực tiếp (vì format cố định)
        if "cccd" in df_anon.columns:
            df_anon["cccd"] = df_anon["cccd"].apply(lambda _: f"{fake.random_number(digits=12, fix_len=True)}")
        
        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = df_anon["so_dien_thoai"].apply(lambda _: f"09{fake.random_number(digits=8, fix_len=True)}")

        return df_anon

    def calculate_detection_rate(self, 
                                  original_df: pd.DataFrame,
                                  pii_columns: list) -> float:
        """
        Tính % PII được detect thành công.
        Mục tiêu: > 95%
        """
        total = 0
        detected = 0

        for col in pii_columns:
            if col not in original_df.columns:
                continue
            for value in original_df[col].astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
