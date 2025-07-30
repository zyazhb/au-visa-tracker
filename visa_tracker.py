#!/usr/bin/env python3
"""
Visa Processing Time Tracker

This script automatically requests Australian immigration visa processing times
once a day and saves unique results to a CSV file.
"""

import csv
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import schedule


class VisaTracker:
    def __init__(self, csv_file: str = "visa_processing_times.csv"):
        self.csv_file = Path(csv_file)
        self.url = "https://immi.homeaffairs.gov.au/_layouts/15/api/GPT.aspx/GetProcessGuideInfo"
        self.headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.payload = {
            "gptRequest": {
                "VisaSubclassCode": "500",
                "StreamCode": "45"
            }
        }
        self.seen_hashes = set()
        self._load_existing_hashes()

    def _load_existing_hashes(self) -> None:
        """Load existing MD5 hashes from CSV to avoid duplicates"""
        if not self.csv_file.exists():
            return
        
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'response_hash' in row:
                        self.seen_hashes.add(row['response_hash'])
            print(f"Loaded {len(self.seen_hashes)} existing hashes")
        except Exception as e:
            print(f"Error loading existing hashes: {e}")

    def _calculate_md5(self, data: str) -> str:
        """Calculate MD5 hash of the response data"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist"""
        if self.csv_file.exists():
            return
        
        headers = [
            'timestamp',
            'response_hash',
            'visa_subclass_text',
            'visa_subclass_code',
            'stream_code',
            'stream_text',
            'visa_url',
            'percent_25',
            'percent_50',
            'percent_75',
            'percent_90',
            'percent_25_text',
            'percent_50_text',
            'percent_75_text',
            'percent_90_text',
            'process_guide_max_days',
            'process_guide_info'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"Initialized CSV file: {self.csv_file}")

    def fetch_visa_data(self) -> Optional[Dict]:
        """Fetch visa processing data from the API"""
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=self.payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('d', {}).get('success'):
                return data
            else:
                print(f"API returned success=false: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            return None

    def save_to_csv(self, data: Dict, response_hash: str) -> None:
        """Save visa data to CSV file"""
        self._initialize_csv()
        
        # Extract the first item from the data array
        visa_info = data['d']['data'][0] if data['d']['data'] else {}
        
        row = [
            datetime.now().isoformat(),
            response_hash,
            visa_info.get('VisaSubclassText', ''),
            visa_info.get('VisaSubclassCode', ''),
            visa_info.get('StreamCode', ''),
            visa_info.get('StreamText', ''),
            visa_info.get('VisaUrl', ''),
            visa_info.get('Percent25', ''),
            visa_info.get('Percent50', ''),
            visa_info.get('Percent75', ''),
            visa_info.get('Percent90', ''),
            visa_info.get('Percent25Text', ''),
            visa_info.get('Percent50Text', ''),
            visa_info.get('Percent75Text', ''),
            visa_info.get('Percent90Text', ''),
            visa_info.get('ProcessGuideMaxDays', ''),
            visa_info.get('ProcessGuideInfo', '')
        ]
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def check_and_save(self) -> None:
        """Main method to check for new data and save if unique"""
        print(f"[{datetime.now()}] Checking for visa processing updates...")
        
        data = self.fetch_visa_data()
        if not data:
            print("Failed to fetch data")
            return
        
        # Calculate hash of the response data
        response_str = json.dumps(data['d']['data'], sort_keys=True)
        response_hash = self._calculate_md5(response_str)
        
        if response_hash in self.seen_hashes:
            print(f"Data unchanged (hash: {response_hash[:8]}...)")
            return
        
        # New data found, save it
        self.seen_hashes.add(response_hash)
        self.save_to_csv(data, response_hash)
        print(f"New data saved! Hash: {response_hash[:8]}...")
        
        # Print summary of the data
        if data['d']['data']:
            info = data['d']['data'][0]
            print(f"  Visa: {info.get('VisaSubclassText', 'N/A')}")
            print(f"  75th percentile: {info.get('Percent75Text', 'N/A')}")
            print(f"  90th percentile: {info.get('Percent90Text', 'N/A')}")

    def run_scheduler(self) -> None:
        """Run the daily scheduler"""
        print("Starting Visa Tracker - Daily monitoring active")
        print(f"CSV file: {self.csv_file.absolute()}")
        
        # Schedule daily check at 9 AM
        schedule.every().day.at("09:00").do(self.check_and_save)
        
        # Run once immediately
        self.check_and_save()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_once(self) -> None:
        """Run a single check (useful for testing)"""
        self.check_and_save()


def main():
    """Main entry point"""
    import sys
    
    tracker = VisaTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("Running single check...")
        tracker.run_once()
    else:
        print("Starting daily scheduler...")
        tracker.run_scheduler()


if __name__ == "__main__":
    main() 