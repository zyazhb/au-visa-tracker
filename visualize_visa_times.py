#!/usr/bin/env python3
"""
Lightweight Visa Processing Times Visualization
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def main():
    # Load data
    data = []
    with open("visa_processing_times.csv", 'r', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            if row['timestamp']:
                timestamp = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
                row['datetime'] = timestamp
                data.append(row)
    
    data.sort(key=lambda x: x['datetime'])
    
    if not data:
        print("No data found!")
        return
    
    # Setup chart
    fig, ax = plt.subplots(figsize=(16, 10))
    dates = [row['datetime'] for row in data]
    
    # Plot trend lines
    percentiles = [
        ('25%', [int(row['percent_25']) for row in data], '#2E8B57'),
        ('50%', [int(row['percent_50']) for row in data], '#4682B4'),
        ('75%', [int(row['percent_75']) for row in data], '#DAA520'),
        ('90%', [int(row['percent_90']) for row in data], '#CD853F'),
        ('Max Guide', [int(row['process_guide_max_days']) for row in data], '#8B0000')
    ]
    
    for label, values, color in percentiles:
        ax.plot(dates, values, marker='o', linewidth=3, markersize=8, 
                color=color, alpha=0.8, label=f'{label} Percentile')
        
        # Add value labels
        for date, value in zip(dates, values):
            ax.annotate(f'{value}d', xy=(date, value), xytext=(5, 10), 
                       textcoords='offset points', ha='left', va='bottom', 
                       fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.3))
    
    # Reference lines
    target_date = datetime.strptime("2025-07-22", "%Y-%m-%d")
    today = datetime.now()
    days_to_target = (target_date - today).days
    days_difference = abs(days_to_target)
    
    chart_start = datetime.strptime("2025-07-22", "%Y-%m-%d")
    chart_end = today
    if chart_end < chart_start:
        chart_start, chart_end = chart_end, chart_start
    
    # Target date line (red dashed)
    if days_to_target >= 0:
        ax.plot([chart_start, chart_end], [days_to_target, days_to_target], 
                color='red', linewidth=3, linestyle='--', alpha=0.8,
                label=f'Days to 2025-07-22: {days_to_target} days')
        ax.axvline(x=target_date, color='red', linestyle=':', linewidth=2, alpha=0.5)
    
    # Absolute difference line (orange solid)
    ax.plot([chart_start, chart_end], [days_difference, days_difference], 
            color='orange', linewidth=3, linestyle='-', alpha=0.8,
            label=f'Days difference: {days_difference} days')
    
    # Chart formatting
    ax.set_xlim(chart_start, chart_end)
    ax.set_ylim(0, max([max(vals) for _, vals, _ in percentiles] + [days_difference, days_to_target if days_to_target >= 0 else 0]) * 1.1)
    
    ax.set_ylabel('Processing Time (Days)', fontweight='bold', fontsize=12)
    ax.set_xlabel('Data Collection Date', fontweight='bold', fontsize=12)
    
    visa_info = f"{data[0]['visa_subclass_text']} - {data[0]['stream_text']}"
    ax.set_title(f'Visa Processing Times Trend\n{visa_info}\nChart Range: 2025-07-22 to {today.strftime("%Y-%m-%d")}', 
                 fontweight='bold', fontsize=14, pad=20)
    
    # Date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    date_span = (chart_end - chart_start).days
    interval = 1 if date_span <= 7 else 3 if date_span <= 30 else 7
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    plt.xticks(rotation=45)
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    
    # Info box
    latest = data[-1]
    info_text = f"""Latest Processing Times ({latest['datetime'].date()}):
• 25%: {latest['percent_25']} days • 50%: {latest['percent_50']} days
• 75%: {latest['percent_75']} days • 90%: {latest['percent_90']} days
• Max: {latest['process_guide_max_days']} days • Target: {days_to_target} days"""
    
    plt.figtext(0.02, 0.02, info_text, fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    # Save and display
    plt.savefig("visa_processing_times_trend.png", dpi=300, bbox_inches='tight')
    print("Trend chart saved as: visa_processing_times_trend.png")
    plt.show()

if __name__ == "__main__":
    print("Generating visa processing times trend visualization...")
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")