"""Tìm luật kết hợp bằng FP-Growth (sử dụng thư viện mlxtend)."""

import ast
import sys
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder


DATA_FILE = Path(__file__).resolve().parent.parent / "Data" / "cleaned_transactions.csv"
RESULT_FILE = Path(__file__).resolve().parent.parent / "result" / "fpgrowth_lib_result.csv"
MIN_SUPPORT = 0.1
MIN_CONFIDENCE = 0.5


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def doc_giao_dich(file_path):
    data = pd.read_csv(file_path)
    return data["Items"].apply(ast.literal_eval).tolist()


def tim_luat_fpgrowth(transactions):
    encoder = TransactionEncoder()
    encoded_data = encoder.fit(transactions).transform(transactions)
    one_hot_data = pd.DataFrame(encoded_data, columns=encoder.columns_)

    frequent_itemsets = fpgrowth(
        one_hot_data,
        min_support=MIN_SUPPORT,
        use_colnames=True,
    )
    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=MIN_CONFIDENCE,
    )
    return frequent_itemsets, rules


def ghi_ket_qua(frequent_itemsets, rules):
    RESULT_FILE.parent.mkdir(exist_ok=True)
    ket_qua = []

    for _, row in frequent_itemsets.iterrows():
        ket_qua.append({
            "loai": "tap_pho_bien",
            "tap_muc": ", ".join(sorted(row["itemsets"])),
            "ve_trai": "",
            "ve_phai": "",
            "support": round(row["support"], 4),
            "confidence": "",
            "lift": "",
        })

    for _, row in rules.iterrows():
        ket_qua.append({
            "loai": "luat_ket_hop",
            "tap_muc": "",
            "ve_trai": ", ".join(sorted(row["antecedents"])),
            "ve_phai": ", ".join(sorted(row["consequents"])),
            "support": round(row["support"], 4),
            "confidence": round(row["confidence"], 4),
            "lift": round(row["lift"], 4),
        })

    pd.DataFrame(ket_qua).to_csv(RESULT_FILE, index=False, encoding="utf-8-sig")


def main():
    transactions = doc_giao_dich(DATA_FILE)
    frequent_itemsets, rules = tim_luat_fpgrowth(transactions)
    ghi_ket_qua(frequent_itemsets, rules)

    print("=== CÁC TẬP MẶT HÀNG PHỔ BIẾN ===")
    print(frequent_itemsets.sort_values("support", ascending=False).to_string(index=False))

    print("\n=== CÁC LUẬT KẾT HỢP ===")
    if rules.empty:
        print("Không tìm thấy luật phù hợp với ngưỡng đã chọn.")
        return

    rules = rules.sort_values(["confidence", "lift"], ascending=False)
    ket_qua = rules[["antecedents", "consequents", "support", "confidence", "lift"]]
    print(ket_qua.to_string(index=False))
    print(f"\nDa luu ket qua vao {RESULT_FILE}")


if __name__ == "__main__":
    main()