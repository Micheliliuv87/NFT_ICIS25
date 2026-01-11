#!/usr/bin/env python3
import os
import time
import json
import requests
import pandas as pd
import datetime
from itertools import cycle

# ─── CONFIG ─────────────────────────────────────────────────────────
DF5_PATH      = r"your_\Model\Analysis_NFT_Sales\df_tables"         # your df_table5.csv
OUTPUT_DIR    = "Address_Data"
API_KEYS      = [
    "your_api_key_1",
    "your_api_key_2",
    "your_api_key_3"
]
RATE_LIMIT    = 4    # requests per second
MAX_RETRIES   = 3
PAGE_SIZE     = 100
BASE_URL      = "https://api.etherscan.io/api"
# ────────────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_txlist(address, api_keys):
    """Fetch all txs for `address` using pagination. Rotates keys on API errors."""
    all_txs = []
    page = 1
    key_cycle = cycle(api_keys)

    while True:
        apikey = next(key_cycle)
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": PAGE_SIZE,
            "sort": "asc",
            "apikey": apikey
        }
        for attempt in range(1, MAX_RETRIES+1):
            try:
                r = requests.get(BASE_URL, params=params, timeout=15)
                r.raise_for_status()
                data = r.json()
                if data.get("status") == "1" and isinstance(data.get("result"), list):
                    txs = data["result"]
                    all_txs.extend(txs)
                    print(f"{address}: page {page} → {len(txs)} txs")
                    break
                else:
                    msg = data.get("message") or data.get("result")
                    print(f"{address}: API error on page {page} (attempt {attempt}): {msg}")
            except Exception as e:
                print(f"{address}: HTTP error on page {page} (attempt {attempt}): {e}")
            time.sleep(1)  # back‐off
        else:
            print(f"{address}: giving up after {MAX_RETRIES} retries on page {page}")
            break

        if len(txs) < PAGE_SIZE:
            # last page
            break
        page += 1
        time.sleep(1.0 / RATE_LIMIT)

    return all_txs

def save_json(address, txs):
    """Atomically write out the JSON file for `address`."""
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    payload = {
        "address": address,
        "transaction_count": len(txs),
        "timestamp": timestamp,
        "transactions": txs
    }
    fname = os.path.join(OUTPUT_DIR, f"{address}.json")
    tmp   = fname + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, fname)
    print(f"→ saved {address}.json with {len(txs)} txs")

def main():
    # 1) load df_table5 and pick zero‐tx addresses
    df5 = pd.read_csv(DF5_PATH, usecols=["seller_n-1_address","transaction_count"])
    zeros = (
        df5
        .loc[df5["transaction_count"] == 0, "seller_n-1_address"]
        .dropna()
        .unique()
        .tolist()
    )
    print(f"Found {len(zeros)} addresses with transaction_count == 0")

    # 2) re‐fetch each one
    for addr in zeros:
        try:
            print(f"\nFetching {addr} …")
            txs = get_txlist(addr, API_KEYS)
            save_json(addr, txs)
        except Exception as e:
            print(f"!!! failed for {addr}: {e}")

if __name__ == "__main__":
    main()
