#!/usr/bin/env python3
"""
Script to add new visa processing data to CSV
"""

import json
import hashlib
import html
from datetime import datetime

def parse_json_data(json_file="0723"):
    """Parse JSON data from the file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Extract the visa data from the JSON structure
    visa_data = data['d']['data'][0]
    return visa_data

def create_response_hash(data):
    """Create a hash from the data for tracking"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()

def decode_html_entities(text):
    """Decode HTML entities in the text"""
    return html.unescape(text)

def add_to_csv(csv_file="visa_processing_times.csv", date_str="2025-07-23"):
    """Add new data to the CSV file"""
    
    # Parse the JSON data
    json_data = parse_json_data()
    
    # Create timestamp for the specified date
    timestamp = f"{date_str}T13:40:43.720628"  # Using same time format as existing
    
    # Create response hash
    response_hash = create_response_hash(json_data)
    
    # Map JSON fields to CSV format
    csv_row = [
        timestamp,
        response_hash,
        json_data['VisaSubclassText'],
        json_data['VisaSubclassCode'],
        json_data['StreamCode'],
        json_data['StreamText'],
        json_data['VisaUrl'],
        json_data['Percent25'],
        json_data['Percent50'],
        json_data['Percent75'],
        json_data['Percent90'],
        json_data['Percent25Text'],
        json_data['Percent50Text'],
        json_data['Percent75Text'],
        json_data['Percent90Text'],
        json_data['ProcessGuideMaxDays'],
        decode_html_entities(json_data['ProcessGuideInfo'])
    ]
    
    # Convert to CSV line
    csv_line = ','.join([f'"{field}"' if ',' in str(field) or '"' in str(field) else str(field) for field in csv_row])
    
    # Append to CSV file
    with open(csv_file, 'a') as f:
        f.write(csv_line + '\n')
    
    print(f"Added new data for {date_str} to {csv_file}")
    print(f"New values:")
    print(f"  25%: {json_data['Percent25']} days ({json_data['Percent25Text']})")
    print(f"  50%: {json_data['Percent50']} days ({json_data['Percent50Text']})")
    print(f"  75%: {json_data['Percent75']} days ({json_data['Percent75Text']})")
    print(f"  90%: {json_data['Percent90']} days ({json_data['Percent90Text']})")
    print(f"  Max: {json_data['ProcessGuideMaxDays']} days")

if __name__ == "__main__":
    add_to_csv() 