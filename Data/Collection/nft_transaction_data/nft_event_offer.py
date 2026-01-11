import os
import time
import json
import requests
from collections import deque
from typing import Dict, Any, List
from urllib.parse import urlencode
from tqdm import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
OUTPUT_DIR = "NFT_Event_Offer"
os.makedirs(OUTPUT_DIR, exist_ok=True)
INPUT_JSON = "data/final_collection.json"
API_RATE_LIMIT = 4  # Requests per second

# API Configuration (This is for Offer events specifically, but for other event types please modify according to the API document)
# in this case, the offer data is the largest chunk of the whole data that was collected. Therefore, you see this example. 
EVENTS_BASE_URL = ("https://api.opensea.io/api/v2/events/chain/ethereum/"
                   "contract/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/nfts/{token_id}"
                   "?event_type=offer")
# If you have multiple API keys, list them here.
API_KEYS = deque([
    "your_api_key_1",
    "your_api_key_2",
    "your_api_key_3"
])
HEADERS = {"accept": "application/json"}

class EventScraper:
    def __init__(self):
        self.current_key = API_KEYS[0]
        self.failed_tokens = []
        self.processed = self._load_progress()
        self.lock = threading.Lock()  # Protects shared data (processed, failed_tokens)
    
    def _load_progress(self) -> set:
        """Load processed token IDs from disk."""
        progress_path = os.path.join(OUTPUT_DIR, "progress.json")
        try:
            if os.path.exists(progress_path):
                with open(progress_path) as f:
                    return set(json.load(f))
        except Exception as e:
            print(f"Error loading progress: {str(e)}")
        return set()
    
    def _save_progress(self):
        """Atomically save processing progress."""
        progress_path = os.path.join(OUTPUT_DIR, "progress.json")
        temp_path = f"{progress_path}.tmp"
        try:
            with self.lock:
                with open(temp_path, "w") as f:
                    json.dump(list(self.processed), f)
                os.replace(temp_path, progress_path)
        except Exception as e:
            print(f"Failed to save progress: {str(e)}")
    
    def _rotate_key(self):
        """Cycle through available API keys."""
        with self.lock:
            API_KEYS.rotate(-1)
            self.current_key = API_KEYS[0]
        print(f"Rotated to new key ending with: ...{self.current_key[-6:]}")
    
    def _save_nft_file(self, token_id: str, nft_name: str, events: List[Any]):
        """Save events for a single NFT into its own file using an atomic write."""
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in nft_name).strip().replace(" ", "_")
        filename = os.path.join(OUTPUT_DIR, f"NFT_{safe_name}_{token_id}.json")
        temp_path = f"{filename}.tmp"
        
        data_to_save = {
            "metadata": {
                "token_id": token_id,
                "nft_name": nft_name,
                "event_count": len(events),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "events": events
        }
        
        try:
            with open(temp_path, "w") as f:
                json.dump(data_to_save, f, indent=2)
            os.replace(temp_path, filename)
            print(f"Saved NFT {nft_name} (Token ID: {token_id}) with {len(events)} events.")
        except Exception as e:
            print(f"Failed to save NFT {nft_name} (Token ID: {token_id}): {str(e)}")
    
    def _handle_pagination(self, token_id: str, token_index: int, total: int) -> List[Any]:
        """
        Process all pages for a single token ID and return collected events.
        This method includes a retry mechanism and prints progress including token index info.
        """
        events_for_nft = []
        cursor = None
        page_count = 0
        while True:
            page_count += 1
            params = {"limit": 50}
            if cursor:
                params["next"] = cursor
            
            # Retry logic for each page request
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    url = EVENTS_BASE_URL.format(token_id=token_id)
                    response = requests.get(
                        url,
                        headers={**HEADERS, "x-api-key": self.current_key},
                        params=params,
                        timeout=15
                    )
                    break  # Got a response, exit retry loop
                except Exception as e:
                    retry_count += 1
                    print(f"Token {token_id} ({token_index}/{total}): Request error: {e}. "
                          f"Retrying {retry_count}/{max_retries} after delay...")
                    time.sleep(5)
            
            if retry_count == max_retries:
                print(f"Token {token_id} ({token_index}/{total}): Max retries reached for page {page_count}. Aborting token.")
                with self.lock:
                    self.failed_tokens.append(token_id)
                break
            
            if response.status_code == 401:
                self._rotate_key()
                continue
                
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 30))
                print(f"Token {token_id} ({token_index}/{total}): Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            if response.status_code != 200:
                print(f"Token {token_id} ({token_index}/{total}): Request failed: HTTP {response.status_code}")
                with self.lock:
                    self.failed_tokens.append(token_id)
                break
            
            data = response.json()
            events = data.get("asset_events", [])
            events_for_nft.extend(events)
            
            print(f"Token {token_id} ({token_index}/{total}): Processed page {page_count}. "
                  f"Received {len(events)} events, total so far: {len(events_for_nft)}.")
            
            # If no events are returned, assume no more pages.
            if len(events) == 0:
                print(f"Token {token_id} ({token_index}/{total}): Received 0 events on page {page_count}. Stopping further requests.")
                break
            
            cursor = data.get("next")
            if not cursor:
                print(f"Token {token_id} ({token_index}/{total}): No more pages. Finished collection.")
                break
            else:
                print(f"Token {token_id} ({token_index}/{total}): More pages to fetch...")
            
            time.sleep(1 / API_RATE_LIMIT)
        
        return events_for_nft
    
    def process_token(self, token: Dict[str, Any], token_index: int, total: int):
        """
        Process events for a single NFT.
        """
        token_id = str(token["token_id"])
        nft_name = token.get("name", token_id)
        
        with self.lock:
            if token_id in self.processed:
                print(f"Skipping token {token_id} ({token_index}/{total}) - already processed.")
                return

        print(f"\nProcessing NFT {nft_name} (Token ID: {token_id}) ({token_index}/{total})")
        events = self._handle_pagination(token_id, token_index, total)
        self._save_nft_file(token_id, nft_name, events)
        with self.lock:
            self.processed.add(token_id)
        self._save_progress()
    
    def finalize_operation(self):
        """Finalize operation by saving the list of failed tokens."""
        failed_path = os.path.join(OUTPUT_DIR, "failed_tokens.json")
        try:
            with open(failed_path, "w") as f:
                json.dump(self.failed_tokens, f, indent=2)
            print("Finalized operation. Failed tokens saved.")
        except Exception as e:
            print(f"Failed to save failed tokens: {str(e)}")

def main():
    with open(INPUT_JSON) as f:
        token_data = json.load(f)
        tokens = token_data["nfts"]
    
    total_tokens = len(tokens)
    scraper = EventScraper()
    
    # Use ThreadPoolExecutor to process multiple NFTs concurrently.
    # Adjust max_workers according to your allowed concurrency.
    max_workers = 5  # For example, 5 concurrent threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each token
        futures = [executor.submit(scraper.process_token, token, idx, total_tokens)
                   for idx, token in enumerate(tokens, 1)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing token: {e}")
    
    scraper.finalize_operation()
    print("\nOperation completed successfully!")
    print(f"Total tokens processed: {len(scraper.processed)}")
    print(f"Failed token count: {len(scraper.failed_tokens)}")

if __name__ == "__main__":
    main()
