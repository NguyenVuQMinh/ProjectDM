"""FP-Growth thuần Python, không dùng thư viện khai phá luật."""

import ast
import csv
import itertools
from collections import Counter
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "Data" / "basket_data.csv"
RESULT_FILE = Path(__file__).resolve().parent.parent / "result" / "fpgrowth_result.csv"
MIN_SUPPORT = 0.1
MIN_CONFIDENCE = 0.5


class Node:
    def __init__(self, item, count=0, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None


def doc_giao_dich():
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        giao_dich = [set(ast.literal_eval(row["Items"])) for row in csv.DictReader(file)]
    print(f"So giao dich: {len(giao_dich)}")
    assert len(giao_dich) == 165, (
        f"Loi: doc {len(giao_dich)} giao dich, khong phai 165. "
        f"Hay kiem tra file {DATA_FILE}"
    )
    return giao_dich


def tao_cay(giao_dich, min_count):
    dem = Counter(muc for gd in giao_dich for muc in gd)
    dem = {muc: so_lan for muc, so_lan in dem.items() if so_lan >= min_count}
    goc = Node(None)
    header = {}

    for gd in giao_dich:
        muc = sorted((muc for muc in gd if muc in dem), key=lambda x: (-dem[x], x))
        nut = goc
        for item in muc:
            if item not in nut.children:
                nut.children[item] = Node(item, parent=nut)
                nut_moi = nut.children[item]
                if item in header:
                    cuoi = header[item]
                    while cuoi.link:
                        cuoi = cuoi.link
                    cuoi.link = nut_moi
                else:
                    header[item] = nut_moi
            nut = nut.children[item]
            nut.count += 1
    return goc, header, dem


def tao_co_so_dieu_kien(nut):
    ket_qua = []
    while nut:
        duong_dan = []
        cha = nut.parent
        while cha and cha.item is not None:
            duong_dan.append(cha.item)
            cha = cha.parent
        if duong_dan:
            ket_qua.append((duong_dan, nut.count))
        nut = nut.link
    return ket_qua


def fp_growth(giao_dich, min_count, tap_hien_tai=frozenset(), ket_qua=None):
    if ket_qua is None:
        ket_qua = {}
    _, header, dem = tao_cay(giao_dich, min_count)

    for item in sorted(header, key=lambda x: (dem[x], x)):
        tap_moi = tap_hien_tai | frozenset([item])
        ket_qua[tap_moi] = dem[item]
        co_so = tao_co_so_dieu_kien(header[item])
        giao_dich_moi = []
        for duong_dan, so_lan in co_so:
            giao_dich_moi.extend([set(duong_dan)] * so_lan)
        if giao_dich_moi:
            fp_growth(giao_dich_moi, min_count, tap_moi, ket_qua)
    return ket_qua


def tao_luat(tap_pho_bien, so_giao_dich):
    luat = []
    for tap_muc, so_lan in tap_pho_bien.items():
        if len(tap_muc) < 2:
            continue
        support = so_lan / so_giao_dich
        for kich_thuoc in range(1, len(tap_muc)):
            for trai_tuple in itertools.combinations(tap_muc, kich_thuoc):
                trai = frozenset(trai_tuple)
                phai = tap_muc - trai
                if phai in tap_pho_bien:
                    confidence = support / (tap_pho_bien[trai] / so_giao_dich)
                    if confidence >= MIN_CONFIDENCE:
                        lift = confidence / (tap_pho_bien[phai] / so_giao_dich)
                        luat.append((trai, phai, support, confidence, lift))
    return luat


def ghi_ket_qua(tap_pho_bien, luat, so_giao_dich):
    RESULT_FILE.parent.mkdir(exist_ok=True)
    cot = ["loai", "tap_muc", "ve_trai", "ve_phai", "support", "confidence", "lift"]
    with RESULT_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=cot)
        writer.writeheader()
        for tap_muc, so_lan in sorted(tap_pho_bien.items(), key=lambda x: -x[1]):
            writer.writerow({
                "loai": "tap_pho_bien",
                "tap_muc": ", ".join(sorted(tap_muc)),
                "ve_trai": "",
                "ve_phai": "",
                "support": round(so_lan / so_giao_dich, 4),
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
    giao_dich = doc_giao_dich()
    min_count = int(MIN_SUPPORT * len(giao_dich) + 0.999999)
    tap_pho_bien = fp_growth(giao_dich, min_count)
    luat = tao_luat(tap_pho_bien, len(giao_dich))
    ghi_ket_qua(tap_pho_bien, luat, len(giao_dich))
    print(f"Da luu {len(tap_pho_bien)} tap pho bien va {len(luat)} luat vao {RESULT_FILE}")


if __name__ == "__main__":
    main()