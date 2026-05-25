#!/usr/bin/env python3
"""Visa Processing Times Visualization"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def main():
    # Load data
    data = []
    with open("visa_processing_times.csv", "r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["timestamp"]:
                row["datetime"] = datetime.strptime(
                    row["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
                )
                data.append(row)
    data.sort(key=lambda x: x["datetime"])

    # Setup chart
    fig, ax = plt.subplots(figsize=(16, 10))
    dates = [row["datetime"] for row in data]

    # Plot trend lines
    percentiles = [
        ("25%", "percent_25", "#2E8B57"),
        ("50%", "percent_50", "#4682B4"),
        ("75%", "percent_75", "#DAA520"),
        ("90%", "percent_90", "#CD853F"),
        ("Max Guide", "process_guide_max_days", "#8B0000"),
    ]

    # Get today's date first
    start_date = datetime(2026, 5, 5)
    today = datetime.now()

    for label, key, color in percentiles:
        values = [int(row[key]) for row in data]
        ax.plot(
            dates,
            values,
            marker="o",
            linewidth=3,
            markersize=8,
            color=color,
            alpha=0.8,
            label=f"{label} Percentile",
        )
        for date, value in zip(dates, values):
            ax.annotate(
                f"{value}d",
                xy=(date, value),
                xytext=(5, 10),
                textcoords="offset points",
                ha="left",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.3),
            )
        # Draw horizontal line from last dot to today
        last_date = dates[-1]
        last_value = values[-1]
        ax.plot(
            [last_date, today],
            [last_value, last_value],
            color=color,
            linewidth=2,
            linestyle="--",
            alpha=0.5,
        )

    # Reference line
    days_diff = (today - start_date).days
    ax.plot(
        [start_date, today],
        [0, days_diff],
        color="orange",
        linewidth=3,
        alpha=0.8,
        label=f"Days difference: {days_diff} days",
    )

    # Formatting
    ax.set_xlabel("Data Collection Date", fontweight="bold", fontsize=12)
    ax.set_ylabel("Processing Time (Days)", fontweight="bold", fontsize=12)
    ax.set_xlim(start_date, today)
    max_val = max(max(int(row[key]) for row in data) for _, key, _ in percentiles)
    ax.set_ylim(0, max(max_val, days_diff) * 1.1)

    visa_info = f"{data[0]['visa_subclass_text']} - {data[0]['stream_text']}"
    ax.set_title(
        f"Visa Processing Times Trend\n{visa_info}\nChart Range: 2026-05-05 to {today.strftime('%Y-%m-%d')}",
        fontweight="bold",
        fontsize=14,
        pad=20,
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.xticks(rotation=45)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    plt.tight_layout()

    # Info box
    latest = data[-1]
    info_text = f"""Latest Processing Times ({latest["datetime"].date()}):
    • 25%: {latest["percent_25"]} days • 50%: {latest["percent_50"]} days
    • 75%: {latest["percent_75"]} days • 90%: {latest["percent_90"]} days
    • Max: {latest["process_guide_max_days"]} days • Target: {days_diff} days"""
    plt.figtext(
        0.02,
        0.02,
        info_text,
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
    )

    plt.savefig("visa_processing_times_trend.svg", bbox_inches="tight")
    print("Trend chart saved as: visa_processing_times_trend.svg")
    return plt
