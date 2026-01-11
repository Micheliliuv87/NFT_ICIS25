import os
import time
import json
import requests
import itertools
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# === Configuration ===

OUTPUT_DIR = "Address_Data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_INPUT = r"df_table1.csv"  # Path to the df_table1.csv file, it is used to get the list of addresses for collection. 
API_RATE_LIMIT = 4  # maximum requests per second

# Etherscan API Base URL (for V2 endpoints)
BASE_URL = "https://api.etherscan.io/v2/api"

# Define a pool of API keys.
API_KEYS = deque([
    "your_api_key_1",
    "your_api_key_2",
    "your_api_key_3"
])
HEADERS = {"accept": "application/json"}

# === Class Definition ===

class EtherscanScraper:
    def __init__(self):
        self.current_key = API_KEYS[0]
        self.failed_addresses = []  # stores addresses that failed processing
        self.processed = self._load_progress()  # load addresses already processed
        self.lock = threading.Lock()  # to protect shared data

    def _load_progress(self) -> set:
        """Load processed addresses from disk."""
        progress_path = os.path.join(OUTPUT_DIR, "progress.json")
        if os.path.exists(progress_path):
            try:
                with open(progress_path, "r") as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"Error loading progress: {e}")
        return set()

    def _save_progress(self):
        """Atomically save processing progress to disk."""
        progress_path = os.path.join(OUTPUT_DIR, "progress.json")
        temp_path = f"{progress_path}.tmp"
        with self.lock:
            try:
                with open(temp_path, "w") as f:
                    json.dump(list(self.processed), f, indent=2)
                os.replace(temp_path, progress_path)
            except Exception as e:
                print(f"Error saving progress: {e}")

    def _rotate_key(self):
        """Cycle through available API keys."""
        with self.lock:
            API_KEYS.rotate(-1)
            self.current_key = API_KEYS[0]
        print(f"Rotated API key. New key ending with: ...{self.current_key[-6:]}")

    def _save_address_file(self, address: str, tx_data: list):
        """Save the buyer's transaction data to an atomic JSON file."""
        filename = os.path.join(OUTPUT_DIR, f"{address}.json")
        temp_path = f"{filename}.tmp"
        data_to_save = {
            "address": address,
            "transaction_count": len(tx_data),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "transactions": tx_data
        }
        try:
            with open(temp_path, "w") as f:
                json.dump(data_to_save, f, indent=2)
            os.replace(temp_path, filename)
            print(f"Saved data for address {address} with {len(tx_data)} transactions.")
        except Exception as e:
            print(f"Failed to save data for address {address}: {e}")

    def get_all_txlist_for_address(self, address: str) -> list:
        """
        Fetch all transactions for a given address using pagination.
        Implements a retry mechanism for each page request.
        Returns a list of transactions.
        """
        all_tx = []
        page = 1
        offset = 100  # Number of transactions per page; adjust as needed.
        max_retries = 3

        while True:
            success = False
            for attempt in range(1, max_retries + 1):
                apikey = self.current_key
                params = {
                    "chainid": 1,
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": page,
                    "offset": offset,
                    "sort": "asc",
                    "apikey": apikey
                }
                try:
                    response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    if data.get("status") == "1":
                        success = True
                        break
                    else:
                        print(f"API returned error for address {address} on page {page} (attempt {attempt}/{max_retries}): {data.get('message')}")
                except requests.RequestException as e:
                    print(f"HTTP error for address {address} on page {page} (attempt {attempt}/{max_retries}): {e}")
                time.sleep(5)  # Wait before retrying

            if not success:
                print(f"Max retries reached for address {address} on page {page}. Aborting retrieval for this address.")
                break

            tx_list = data.get("result", [])
            if not isinstance(tx_list, list):
                print(f"Unexpected result format for address {address} on page {page}.")
                break

            all_tx.extend(tx_list)
            print(f"Address {address}: Retrieved {len(tx_list)} transactions on page {page}. Total so far: {len(all_tx)}")
            if len(tx_list) < offset:
                break  # Last page reached

            page += 1
            time.sleep(1 / API_RATE_LIMIT)  # Respect the rate limit

        return all_tx

    def process_address(self, address: str, idx: int, total: int):
        """
        Process a single address:
         - Skip if already processed or if a buyer file already exists.
         - Retrieve all transactions via pagination with retries.
         - Save the result.
         - Update progress.
        """
        filename = os.path.join(OUTPUT_DIR, f"{address}.json")
        if os.path.exists(filename):
            print(f"Skipping {address} (file exists).")
            with self.lock:
                self.processed.add(address)
            return

        with self.lock:
            if address in self.processed:
                print(f"Skipping {address} (already processed).")
                return

        print(f"Processing address {address} ({idx}/{total})")
        tx_data = self.get_all_txlist_for_address(address)
        if tx_data is not None:
            self._save_address_file(address, tx_data)
            with self.lock:
                self.processed.add(address)
            self._save_progress()
        else:
            with self.lock:
                self.failed_addresses.append(address)
        time.sleep(1 / API_RATE_LIMIT)

    def finalize(self):
        """Save the failed addresses to a JSON file."""
        failed_path = os.path.join(OUTPUT_DIR, "failed_addresses.json")
        try:
            with open(failed_path, "w") as f:
                json.dump(self.failed_addresses, f, indent=2)
            print("Failed addresses saved.")
        except Exception as e:
            print(f"Failed to save failed addresses: {e}")

# === Main Routine ===

def main():
    # 1. Load CSV file and extract unique addresses from multiple columns.
    df = pd.read_csv(CSV_INPUT)
    # List the columns to include. Adjust these if the CSV column names differ.
    cols_to_check = ["buyer_n_sale", "seller_n_sale", "seller_n-1_sale", "buyer_n-1_sale"]
    all_addresses = set()
    for col in cols_to_check:
        if col in df.columns:
            addresses = df[col].dropna().unique()
            all_addresses.update(addresses)
    print(f"Found {len(all_addresses)} unique addresses from {cols_to_check}.")

    total = len(all_addresses)
    scraper = EtherscanScraper()

    # 2. Process addresses concurrently.
    max_workers = 5  # Adjust based on system and API constraints.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scraper.process_address, addr, idx, total)
                   for idx, addr in enumerate(all_addresses, 1)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception during processing: {e}")

    scraper.finalize()
    print(f"Total processed addresses: {len(scraper.processed)}")
    print(f"Total failed addresses: {len(scraper.failed_addresses)}")

if __name__ == "__main__":
    main()
