#!/usr/bin/env python3
"""
Generate dual-axis plot:
- X-axis: Number of methods finding a fusion
- Left Y-axis: Count of validated fusions (bar chart)
- Right Y-axis: Percentage of total predicted fusions (line chart)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import csv

# Configuration
OUTPUT_DIR = "/data6/mark/Project/chimericRNA_detection/datasets_and_results/real_data/r1"

# ============================================================================
# Calculate Method Consensus
# ============================================================================
def calculate_method_consensus(method_results, known_fusions_set):
    """
    Calculate how many methods find each fusion
    Separate validated vs total predictions
    """
    # Count how many methods find each fusion
    fusion_method_count = Counter()
    
    # Get all unique fusions across all methods
    all_fusions = set()
    for predictions in method_results.values():
        all_fusions.update(predictions)
    
    # Count methods for each fusion
    for fusion in all_fusions:
        count = sum(1 for predictions in method_results.values() if fusion in predictions)
        fusion_method_count[fusion] = count
    
    # Separate validated vs all
    validated_counts = Counter()
    total_counts = Counter()
    
    for fusion, method_count in fusion_method_count.items():
        total_counts[method_count] += 1
        if fusion in known_fusions_set:
            validated_counts[method_count] += 1
    
    return validated_counts, total_counts, fusion_method_count


# ============================================================================
# Generate Dual-Axis Plot
# ============================================================================
def generate_consensus_plot(validated_counts, total_counts, n_methods, output_prefix):
    """
    Generate dual-axis plot showing:
    - Bar chart: validated fusion counts by number of methods
    - Line chart: percentage of total predictions
    """
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # X-axis: number of methods (1 to n_methods)
    x = np.arange(1, n_methods + 1)
    
    # Get counts for each x value
    validated = [validated_counts.get(i, 0) for i in x]
    total = [total_counts.get(i, 0) for i in x]
    
    # Calculate percentages
    total_sum = sum(total)
    percentages = [total[i] / total_sum * 100 if total_sum > 0 else 0 for i in range(len(x))]
    
    # Left Y-axis: Bar chart for validated fusions
    bars = ax1.bar(x, validated, width=0.6, color='#3498db', alpha=0.7, 
                   edgecolor='black', linewidth=1.5, label='Validated Fusions')
    
    ax1.set_xlabel('Number of Methods Detecting Fusion', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Count of Validated Fusions', fontsize=14, fontweight='bold', color='#3498db')
    ax1.tick_params(axis='y', labelcolor='#3498db', labelsize=12)
    ax1.tick_params(axis='x', labelsize=12)
    ax1.set_xticks(x)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar, val in zip(bars, validated):
        if val > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(validated)*0.02,
                    str(int(val)), ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Right Y-axis: Line chart for percentage of total predictions
    ax2 = ax1.twinx()
    line = ax2.plot(x, percentages, color='#e74c3c', linewidth=3, marker='o', 
                    markersize=10, label='% of Total Predictions', linestyle='-', 
                    markerfacecolor='white', markeredgewidth=2, markeredgecolor='#e74c3c')
    
    ax2.set_ylabel('Total Predicted Fusions (%)', fontsize=14, fontweight='bold', color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c', labelsize=12)
    ax2.set_ylim(0, max(percentages) * 1.2 if max(percentages) > 0 else 10)
    
    # Add value labels on line
    for xi, pct in zip(x, percentages):
        if pct > 0:
            ax2.text(xi, pct + max(percentages)*0.05, f'{pct:.1f}%', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='#e74c3c')
    
    # Title and legends
    plt.title('Method Consensus: Validated Fusions vs Total Predictions', 
             fontsize=16, fontweight='bold', pad=20)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=12, framealpha=0.9)
    
    # Styling
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    plt.savefig(f"{output_prefix}_consensus_plot.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_consensus_plot.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_consensus_plot.pdf/png")
    
    # Save data to CSV
    with open(f"{output_prefix}_consensus_data.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['N_Methods', 'Validated_Count', 'Total_Count', 'Percentage'])
        for i, xi in enumerate(x):
            writer.writerow([xi, validated[i], total[i], percentages[i]])
    
    print(f"  Saved: {output_prefix}_consensus_data.csv")
    
    # Print summary
    print("\n  Summary:")
    print(f"  {'N_Methods':<12} {'Validated':<12} {'Total':<12} {'Percentage'}")
    print("  " + "-"*50)
    for i, xi in enumerate(x):
        print(f"  {xi:<12} {validated[i]:<12} {total[i]:<12} {percentages[i]:.2f}%")


# ============================================================================
# Generate Additional Consensus Visualizations
# ============================================================================
def generate_fusion_heatmap(fusion_method_count, method_results, known_fusions_set, output_prefix):
    """
    Generate heatmap showing which methods detect which fusions
    Focus on fusions found by multiple methods
    """
    # Filter fusions found by at least 2 methods
    multi_method_fusions = [f for f, count in fusion_method_count.items() if count >= 2]
    
    if len(multi_method_fusions) == 0:
        print("  No fusions found by multiple methods")
        return
    
    # Sort by number of methods (descending) and fusion name
    multi_method_fusions.sort(key=lambda f: (-fusion_method_count[f], f))
    
    # Take top 50 for visualization
    top_fusions = multi_method_fusions[:min(50, len(multi_method_fusions))]
    
    # Create binary matrix
    methods = list(method_results.keys())
    matrix = np.zeros((len(top_fusions), len(methods)))
    
    for i, fusion in enumerate(top_fusions):
        for j, method in enumerate(methods):
            if fusion in method_results[method]:
                matrix[i, j] = 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, max(8, len(top_fusions) * 0.3)))
    
    # Color map: green for validated, blue for non-validated
    colors = []
    for fusion in top_fusions:
        if fusion in known_fusions_set:
            colors.append('green')
        else:
            colors.append('gray')
    
    # Plot heatmap
    im = ax.imshow(matrix, cmap='Blues', aspect='auto', interpolation='nearest')
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(methods)))
    ax.set_yticks(np.arange(len(top_fusions)))
    ax.set_xticklabels(methods, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels([f"{fusion_method_count[f]}x: {f[:40]}" for f in top_fusions], 
                       fontsize=8)
    
    # Color y-tick labels by validation status
    for i, (tick, color) in enumerate(zip(ax.get_yticklabels(), colors)):
        tick.set_color(color)
        if color == 'green':
            tick.set_fontweight('bold')
    
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Fusion (sorted by method count)', fontsize=12, fontweight='bold')
    ax.set_title('Fusion Detection Heatmap (Multi-Method Fusions)', 
                fontsize=14, fontweight='bold', pad=15)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label='Detected (1) / Not Detected (0)')
    
    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Validated Fusion'),
        Patch(facecolor='gray', label='Unvalidated Fusion')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.15, 1), fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_fusion_heatmap.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_fusion_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_fusion_heatmap.pdf/png")


# ============================================================================
# Main Function
# ============================================================================
def main():
    """Generate method consensus plots"""
    print("="*80)
    print("Generating Method Consensus Plots")
    print("="*80)
    
    # This would normally load data from the data loader
    # For now, we'll create placeholder functionality
    print("\nNote: This script should be run after data loading")
    print("It will be integrated into the main analysis pipeline")
    

if __name__ == '__main__':
    main()
