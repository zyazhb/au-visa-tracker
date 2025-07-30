#!/usr/bin/env python3
"""
Visa Processing Times Visualization Script
Displays trends of processing times over multiple dates with reference line.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

def calculate_days_to_target(target_date_str="2025-07-22"):
    """Calculate days from now to target date"""
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    today = datetime.now()
    days_diff = (target_date - today).days
    return days_diff, target_date

def calculate_days_difference(target_date_str="2025-07-22"):
    """Calculate absolute days difference between today and target date"""
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    today = datetime.now()
    days_diff = abs((target_date - today).days)
    return days_diff

def load_and_process_data(csv_file="visa_processing_times.csv"):
    """Load and process all visa processing times CSV data"""
    df = pd.read_csv(csv_file)
    
    # Convert timestamp to datetime
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Sort by date
    df = df.sort_values('date')
    
    return df

def create_visualization():
    """Create the visa processing times trend visualization"""
    # Load data
    df = load_and_process_data()
    
    # Calculate days to target date
    days_to_target, target_date = calculate_days_to_target()
    
    # Calculate absolute days difference (always positive)
    days_difference = calculate_days_difference()
    
    # Get today's date
    today = datetime.now().date()
    
    # Prepare data for plotting
    dates = [datetime.combine(date, datetime.min.time()) for date in df['date']]
    
    # Processing times data for trend lines (using only numeric values)
    processing_data = {
        '25%': {'values': df['percent_25'].astype(int).tolist(), 'color': '#2E8B57'},
        '50%': {'values': df['percent_50'].astype(int).tolist(), 'color': '#4682B4'},
        '75%': {'values': df['percent_75'].astype(int).tolist(), 'color': '#DAA520'},
        '90%': {'values': df['percent_90'].astype(int).tolist(), 'color': '#CD853F'},
        'Max Guide': {'values': df['process_guide_max_days'].astype(int).tolist(), 'color': '#8B0000'}
    }
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Draw trend lines for each percentile
    for label, data in processing_data.items():
        ax.plot(dates, data['values'], 
                marker='o', linewidth=3, markersize=8, 
                color=data['color'], alpha=0.8,
                label=f'{label} Percentile')
        
        # Add value annotations for each point (only showing numeric days)
        for i, (date, value) in enumerate(zip(dates, data['values'])):
            ax.annotate(f'{value}d', 
                       xy=(date, value), 
                       xytext=(5, 10), textcoords='offset points',
                       ha='left', va='bottom', fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor=data['color'], alpha=0.3))
    
    # Define chart date range (from 2025-07-22 to today)
    chart_start_date = datetime.strptime("2025-07-22", "%Y-%m-%d")
    chart_end_date = datetime.now()
    chart_date_range = [chart_start_date, chart_end_date]
    
    # Add horizontal line for target date
    if days_to_target >= 0:
        # Horizontal line across the entire chart width
        ax.plot(chart_date_range, [days_to_target, days_to_target], 
                color='red', linewidth=3, linestyle='--', alpha=0.8,
                label=f'Days to 2025-07-22: {days_to_target} days')
        
        # Add text annotation for the horizontal line
        mid_date = chart_start_date + (chart_end_date - chart_start_date) / 2
        ax.annotate(f'Target: 2025-07-22\n{days_to_target} days from now', 
                   xy=(mid_date, days_to_target), 
                   xytext=(20, 20), textcoords='offset points',
                   ha='left', va='bottom', color='red', fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='red'))
        
        # Add vertical line to target date
        ax.axvline(x=target_date, color='red', linestyle=':', linewidth=2, alpha=0.5)
    
    # Add horizontal line for absolute days difference (today - 2025-07-22)
    ax.plot(chart_date_range, [days_difference, days_difference], 
            color='orange', linewidth=3, linestyle='-', alpha=0.8,
            label=f'Days difference (today - 2025-07-22): {days_difference} days')
    
    # Add text annotation for the horizontal difference line
    mid_date = chart_start_date + (chart_end_date - chart_start_date) / 2
    ax.annotate(f'Absolute difference: {days_difference} days\n(today vs 2025-07-22)', 
               xy=(mid_date, days_difference), 
               xytext=(-50, -30), textcoords='offset points',
               ha='center', va='top', color='orange', fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
               arrowprops=dict(arrowstyle='->', color='orange'))
    
    # Customize the plot
    ax.set_ylabel('Processing Time (Days)', fontweight='bold', fontsize=12)
    ax.set_xlabel('Data Collection Date', fontweight='bold', fontsize=12)
    
    # Create title with visa info from first row
    visa_info = f"{df.iloc[0]['visa_subclass_text']} - {df.iloc[0]['stream_text']}"
    ax.set_title(f'Visa Processing Times Trend\n{visa_info}\nChart Range: 2025-07-22 to {datetime.now().strftime("%Y-%m-%d")}', 
                 fontweight='bold', fontsize=14, pad=20)
    
    # Set x-axis range from 2025-07-22 to today
    start_date = datetime.strptime("2025-07-22", "%Y-%m-%d")
    end_date = datetime.now()
    ax.set_xlim(start_date, end_date)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # Calculate appropriate interval based on date range
    date_span = (chart_end_date - chart_start_date).days
    if date_span <= 7:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    elif date_span <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    
    plt.xticks(rotation=45)
    
    # Set axis limits
    all_values = []
    for data in processing_data.values():
        all_values.extend(data['values'])
    max_days = max(all_values)
    
    # Include both reference lines in max calculation
    if days_to_target >= 0:
        max_days = max(max_days, days_to_target)
    max_days = max(max_days, days_difference)
    
    ax.set_ylim(0, max_days * 1.1)
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Add additional information as text box (using only numeric values)
    latest_data = df.iloc[-1]  # Most recent data
    info_text = f"""Latest Processing Times ({latest_data['date']}):
• 25% processed within: {latest_data['percent_25']} days
• 50% processed within: {latest_data['percent_50']} days
• 75% processed within: {latest_data['percent_75']} days
• 90% processed within: {latest_data['percent_90']} days
• Max guide time: {latest_data['process_guide_max_days']} days
• Target date: 2025-07-22 ({days_to_target} days from today)
• Absolute difference (today vs 2025-07-22): {days_difference} days"""
    
    plt.figtext(0.02, 0.02, info_text, fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    return fig

def main():
    """Main function to generate and display the visualization"""
    print("Generating visa processing times trend visualization...")
    
    try:
        fig = create_visualization()
        
        # Save the plot
        output_file = "visa_processing_times_trend.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Trend chart saved as: {output_file}")
        
        # Display the plot
        plt.show()
        
    except FileNotFoundError:
        print("Error: visa_processing_times.csv file not found!")
        print("Please ensure the CSV file is in the current directory.")
    except Exception as e:
        print(f"Error generating visualization: {e}")

if __name__ == "__main__":
    main() 