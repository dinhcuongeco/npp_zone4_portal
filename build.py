#!/usr/bin/env python3
"""
build.py — Doc allocation.xlsx (sheet 'vdo' va 'allocation') va sinh ra
NPP_Portal.html tu npp_portal_template.html.

Cach dung:
    python build.py

Yeu cau file trong cung thu muc:
    - allocation.xlsx
    - npp_portal_template.html
Output:
    - NPP_Portal.html
"""
import sys
import json
import re
import pandas as pd
import numpy as np

XLSX = "allocation.xlsx"
TEMPLATE = "npp_portal_template.html"
OUTPUT = "NPP_Portal.html"


def split_prefix(s):
    """'80702671-Pham Hoang Phi' -> 'Pham Hoang Phi'
       'BD8-CTY TNHH MTV Nguyen Truong Ngan' -> 'CTY TNHH MTV Nguyen Truong Ngan'"""
    if pd.isna(s):
        return ""
    s = str(s)
    if "-" in s:
        return s.split("-", 1)[1].strip()
    return s.strip()


def num(v, default=0):
    if pd.isna(v):
        return default
    try:
        f = float(v)
        if f == int(f):
            return int(f)
        return f
    except (TypeError, ValueError):
        return default


def build_data(vdo):
    records = []
    for _, row in vdo.iterrows():
        target = num(row["Target"])
        actual = num(row["Actual"])
        balance = num(row["Balance"])
        # Recompute balance/pct consistently (Excel may leave these blank)
        if target:
            pct = actual / target
            if balance == 0 and pd.isna(row["Balance"]):
                balance = target - actual
        else:
            pct = 0.0

        rec = {
            "id": int(row["MAAN8"]),
            "name": str(row["Customer_Name"]),
            "addr": str(row["Outlet_Address"]),
            "area": str(row["Area_Name"]),
            "nppCode": str(row["code npp"]),
            "npp": split_prefix(row["ParentName"]),
            "terr": str(row["TerritoryName"]),
            "ss": split_prefix(row["SS_FullName"]),
            "sr": split_prefix(row["SR_FullName"]),
            "type": row["Type"] if pd.notna(row["Type"]) else "(Chưa phân loại)",
            "program": row["Program"] if pd.notna(row["Program"]) else "(Không có)",
            "target": target,
            "actual": actual,
            "pct": pct,
            "balance": balance,
        }
        records.append(rec)
    return records


def build_alloc_and_creds(alloc_raw):
    # Header rows occupy rows 0-2 (0-indexed); data starts row 3
    df = alloc_raw.iloc[3:].reset_index(drop=True)
    # Column positions (0-indexed) per fixed template layout:
    # 0 Week | 1 Item code | 2 Item | 8 Sold to | 9 code npp
    # 15 Final(Batch1) | 16 Final(Batch2) | 17 Final Allocation
    cols = df[[0, 1, 2, 8, 9, 15, 16, 17]].copy()
    cols.columns = ["week", "itemCode", "item", "soldto", "npp", "b1", "b2", "total"]
    cols = cols.dropna(subset=["week", "npp"], how="any")

    def to_num(v):
        if pd.isna(v):
            return 0
        if isinstance(v, str):
            v = v.strip()
            if v in ("", "-", "—"):
                return 0
            v = v.replace(",", "")
        try:
            f = float(v)
            return int(f) if f == int(f) else f
        except (TypeError, ValueError):
            return 0

    alloc_records = []
    creds = {}
    for _, row in cols.iterrows():
        b1 = to_num(row["b1"])
        b2 = to_num(row["b2"])
        total = to_num(row["total"])
        alloc_records.append({
            "week": str(row["week"]),
            "npp": str(row["npp"]),
            "item": str(row["item"]),
            "itemCode": int(row["itemCode"]),
            "b1": b1,
            "b2": b2,
            "total": total if total else (b1 + b2),
        })
        npp = str(row["npp"])
        soldto = row["soldto"]
        if pd.notna(soldto):
            soldto_str = str(int(soldto)) if isinstance(soldto, (int, float)) else str(soldto).strip()
            creds[npp] = soldto_str

    return alloc_records, creds


def main():
    try:
        xl = pd.ExcelFile(XLSX)
    except FileNotFoundError:
        print(f"LOI: Khong tim thay file '{XLSX}' trong thu muc nay.")
        sys.exit(1)

    if "vdo" not in xl.sheet_names:
        print("LOI: Khong tim thay sheet 'vdo' trong allocation.xlsx")
        sys.exit(1)
    if "allocation" not in xl.sheet_names:
        print("LOI: Khong tim thay sheet 'allocation' trong allocation.xlsx")
        sys.exit(1)

    vdo = pd.read_excel(xl, sheet_name="vdo")
    required_cols = ["Geography", "Region_Name", "Area_Name", "ParentName", "TerritoryName",
                      "SS_FullName", "SR_FullName", "MAAN8", "Customer_Name", "Outlet_Address",
                      "code npp", "Type", "Program", "Target", "Actual", "%", "Balance"]
    missing = [c for c in required_cols if c not in vdo.columns]
    if missing:
        print(f"LOI: Sheet 'vdo' thieu cot: {missing}")
        print("Kiem tra lai ten cot trong Excel - khong duoc doi ten cot.")
        sys.exit(1)

    alloc_raw = pd.read_excel(xl, sheet_name="allocation", header=None)
    if alloc_raw.shape[0] < 4 or alloc_raw.shape[1] < 18:
        print("LOI: Sheet 'allocation' khong dung cau truc (it hon 4 dong hoac 18 cot).")
        sys.exit(1)

    data = build_data(vdo)
    alloc, creds = build_alloc_and_creds(alloc_raw)

    print(f"DATA: {len(data)} outlets")
    print(f"ALLOC: {len(alloc)} dong allocation")
    print(f"CREDS: {len(creds)} NPP -> {list(creds.keys())}")

    try:
        template = open(TEMPLATE, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"LOI: Khong tim thay file '{TEMPLATE}'")
        sys.exit(1)

    for ph in ["__DATA__", "__CREDS__", "__ALLOC__"]:
        if ph not in template:
            print(f"LOI: Template thieu placeholder {ph}")
            sys.exit(1)

    out = template.replace("__DATA__", "const DATA=" + json.dumps(data, ensure_ascii=False) + ";")
    out = out.replace("__CREDS__", "const CREDS=" + json.dumps(creds, ensure_ascii=False) + ";")
    out = out.replace("__ALLOC__", "const ALLOC=" + json.dumps(alloc, ensure_ascii=False) + ";")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"\nDA TAO XONG: {OUTPUT} ({len(out)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
