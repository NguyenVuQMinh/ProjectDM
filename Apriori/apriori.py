"""Apriori thuần Python, không dùng thư viện khai phá luật."""

import ast
import csv
import itertools
from collections import Counter
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "Data" / "cleaned_transactions.csv"
RESULT_FILE = Path(__file__).resolve().parent.parent / "result" / "apriori_result.csv"
MIN_SUPPORT = 0.1
MIN_CONFIDENCE = 0.5


def doc_giao_dich():
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        return [set(ast.literal_eval(row["Items"])) for row in csv.DictReader(file)]


def dem_tap_muc(tap_muc, giao_dich):
    return sum(tap_muc.issubset(giao_dich) for giao_dich in giao_dich)


def tim_tap_pho_bien(giao_dich):
    so_giao_dich = len(giao_dich)
    tap_pho_bien = {}
    muc_hien_tai = {frozenset([muc]) for gd in giao_dich for muc in gd}

    while muc_hien_tai:
        muc_ke_tiep = set()
        for tap_muc in muc_hien_tai:
            so_lan = dem_tap_muc(set(tap_muc), giao_dich)
            do_ho_tro = so_lan / so_giao_dich
            if do_ho_tro >= MIN_SUPPORT:
                tap_pho_bien[tap_muc] = do_ho_tro

        tap_dat = set(tap_pho_bien)
        kich_thuoc = len(next(iter(muc_hien_tai)))
        for tap_a, tap_b in itertools.combinations(tap_dat, 2):
            tap_moi = tap_a | tap_b
            if len(tap_moi) == kich_thuoc + 1:
                muc_ke_tiep.add(frozenset(tap_moi))
        muc_hien_tai = muc_ke_tiep

    return tap_pho_bien


def tao_luat(tap_pho_bien):
    luat = []
    for tap_muc, support in tap_pho_bien.items():
        if len(tap_muc) < 2:
            continue
        for kich_thuoc in range(1, len(tap_muc)):
            for trai in itertools.combinations(tap_muc, kich_thuoc):
                trai = frozenset(trai)
                phai = tap_muc - trai
                confidence = support / tap_pho_bien[trai]
                if confidence >= MIN_CONFIDENCE:
                    lift = confidence / tap_pho_bien[phai]
                    luat.append((trai, phai, support, confidence, lift))
    return luat


def ghi_ket_qua(tap_pho_bien, luat):
    RESULT_FILE.parent.mkdir(exist_ok=True)
    cot = ["loai", "tap_muc", "ve_trai", "ve_phai", "support", "confidence", "lift"]
    with RESULT_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=cot)
        writer.writeheader()
        for tap_muc, support in sorted(tap_pho_bien.items(), key=lambda x: (-x[1], len(x[0]))):
            writer.writerow({
                "loai": "tap_pho_bien",
                "tap_muc": ", ".join(sorted(tap_muc)),
                "ve_trai": "",
                "ve_phai": "",
                "support": round(support, 4),
                "confidence": "",
                "lift": "",
            })
        for trai, phai, support, confidence, lift in sorted(luat, key=lambda x: -x[3]):
            writer.writerow({
                "loai": "luat_ket_hop",
                "tap_muc": "",
                "ve_trai": ", ".join(sorted(trai)),
                "ve_phai": ", ".join(sorted(phai)),
                "support": round(support, 4),
                "confidence": round(confidence, 4),
                "lift": round(lift, 4),
            })


def main():
    tap_pho_bien = tim_tap_pho_bien(doc_giao_dich())
    luat = tao_luat(tap_pho_bien)
    ghi_ket_qua(tap_pho_bien, luat)
    print(f"Da luu {len(tap_pho_bien)} tap pho bien va {len(luat)} luat vao {RESULT_FILE}")


if __name__ == "__main__":
    main()