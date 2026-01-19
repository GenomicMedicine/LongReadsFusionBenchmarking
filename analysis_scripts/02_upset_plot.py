#!/usr/bin/env python3
"""
Generate UpSet Plot showing method intersections and recall metrics
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
import seaborn as sns
from itertools import combinations
import csv

# Import data loader
import sys
sys.path.insert(0, os.path.dirname(__file__))
from data_loader_module import load_known_fusions, scan_all_datasets, normalize_fusion_name, METHODS, OUTPUT_DIR

# ============================================================================
# Configuration
# ============================================================================
METHOD_COLORS = {
    'CTAT-LR-Fusion': '#E64B35',
    'JAFFAL': '#8491B4',
    'LongGF': '#91D1C2',
    'genion': '#3C5488',
    'pbfusion': '#DC91A3',
    'FusionSeeker': '#00A087',
    'IFDlong': '#F39B7F',
    'FLAIR_fusion': '#4DBBD5'
}

# ============================================================================
# Calculate Method Performance
# ============================================================================
def calculate_method_metrics(method_results, known_fusions_set):
    """Calculate TP, FP, FN, Precision, Recall for each method"""
    metrics = {}
    
    for method, predictions in method_results.items():
        if not predictions:
            continue
        
        # Calculate metrics
        tp = len(predictions & known_fusions_set)
        fp = len(predictions - known_fusions_set)
        fn = len(known_fusions_set - predictions)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metrics[method] = {
            'TP': tp,
            'FP': fp,
            'FN': fn,
            'Precision': precision,
            'Recall': recall,
            'F1': f1,
            'Total_Predictions': len(predictions),
            'Total_TruthSet': len(known_fusions_set)
        }
    
    return metrics


# ============================================================================
# Generate UpSet Plot
# ============================================================================
def generate_upset_plot(method_results, known_fusions_set, output_prefix):
    """
    Generate UpSet plot showing intersections between methods
    Also display recall for each method
    """
    # Get methods that have results
    available_methods = [m for m in METHODS if m in method_results and len(method_results[m]) > 0]
    
    if len(available_methods) < 2:
        print("  Warning: Need at least 2 methods with results")
        return
    
    print(f"  Generating UpSet plot with {len(available_methods)} methods")
    
    # Calculate all possible intersections
    intersection_data = []
    
    # Single method sets
    for method in available_methods:
        fusions = method_results[method]
        intersection_data.append({
            'methods': frozenset([method]),
            'count': len(fusions),
            'fusions': fusions
        })
    
    # Pairwise intersections
    for method1, method2 in combinations(available_methods, 2):
        intersection = method_results[method1] & method_results[method2]
        intersection_data.append({
            'methods': frozenset([method1, method2]),
            'count': len(intersection),
            'fusions': intersection
        })
    
    # Triple intersections (if enough methods)
    if len(available_methods) >= 3:
        for combo in combinations(available_methods, 3):
            intersection = set.intersection(*[method_results[m] for m in combo])
            intersection_data.append({
                'methods': frozenset(combo),
                'count': len(intersection),
                'fusions': intersection
            })
    
    # Sort by count
    intersection_data.sort(key=lambda x: x['count'], reverse=True)
    
    # Take top intersections for visualization
    top_intersections = intersection_data[:min(30, len(intersection_data))]
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 1, height_ratios=[2, 3, 1], hspace=0.05)
    
    # Top panel: Bar chart of intersection sizes
    ax_bar = fig.add_subplot(gs[0])
    
    x_pos = np.arange(len(top_intersections))
    counts = [item['count'] for item in top_intersections]
    colors_bar = ['#E64B35' if len(item['methods']) == 1 else '#3C5488' if len(item['methods']) == 2 else '#00A087' 
                  for item in top_intersections]
    
    bars = ax_bar.bar(x_pos, counts, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax_bar.set_ylabel('Intersection Size', fontsize=12, fontweight='bold')
    ax_bar.set_xticks([])
    ax_bar.spines['bottom'].set_visible(False)
    ax_bar.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add counts on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.02,
                       str(count), ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Middle panel: Dot matrix showing which methods are in each intersection
    ax_matrix = fig.add_subplot(gs[1])
    
    for i, item in enumerate(top_intersections):
        methods_in_set = item['methods']
        for j, method in enumerate(available_methods):
            if method in methods_in_set:
                ax_matrix.scatter(i, j, s=500, c=METHOD_COLORS.get(method, '#666666'), 
                                marker='o', edgecolors='black', linewidth=1.5, zorder=10)
        
        # Draw connecting lines
        methods_indices = [j for j, method in enumerate(available_methods) if method in methods_in_set]
        if len(methods_indices) > 1:
            for k in range(len(methods_indices)-1):
                ax_matrix.plot([i, i], [methods_indices[k], methods_indices[k+1]], 
                             'k-', linewidth=3, zorder=5)
    
    ax_matrix.set_yticks(range(len(available_methods)))
    ax_matrix.set_yticklabels(available_methods, fontsize=11, fontweight='bold')
    ax_matrix.set_xticks([])
    ax_matrix.set_xlim(-0.5, len(top_intersections)-0.5)
    ax_matrix.set_ylim(-0.5, len(available_methods)-0.5)
    ax_matrix.invert_yaxis()
    ax_matrix.grid(axis='y', alpha=0.2, linestyle=':')
    ax_matrix.set_ylabel('Methods', fontsize=12, fontweight='bold')
    
    # Remove spines
    for spine in ax_matrix.spines.values():
        spine.set_visible(False)
    
    # Bottom panel: Recall for each method
    ax_recall = fig.add_subplot(gs[2])
    
    # Calculate recall for each method
    recalls = []
    for method in available_methods:
        predictions = method_results[method]
        tp = len(predictions & known_fusions_set)
        fn = len(known_fusions_set - predictions)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        recalls.append(recall)
    
    y_pos = np.arange(len(available_methods))
    bars_recall = ax_recall.barh(y_pos, recalls, 
                                  color=[METHOD_COLORS.get(m, '#666666') for m in available_methods],
                                  alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax_recall.set_xlabel('Recall (Sensitivity)', fontsize=12, fontweight='bold')
    ax_recall.set_yticks(y_pos)
    ax_recall.set_yticklabels(available_methods, fontsize=11, fontweight='bold')
    ax_recall.set_xlim(0, 1.0)
    ax_recall.invert_yaxis()
    ax_recall.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add recall values
    for bar, recall in zip(bars_recall, recalls):
        ax_recall.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                      f'{recall:.3f}', va='center', fontsize=10, fontweight='bold')
    
    # Overall title
    fig.suptitle('UpSet Plot: Method Intersections and Recall Metrics', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_upset_plot.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_upset_plot.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_upset_plot.pdf/png")
    
    # Save intersection data to CSV
    with open(f"{output_prefix}_intersections.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Methods', 'Count', 'FusionList'])
        for item in top_intersections:
            methods_str = ';'.join(sorted(item['methods']))
            fusions_str = ';'.join(sorted(item['fusions']))
            writer.writerow([methods_str, item['count'], fusions_str])
    
    print(f"  Saved: {output_prefix}_intersections.csv")


# ============================================================================
# Select Best Dataset for UpSet Plot
# ============================================================================
def select_best_dataset_for_upset(results, known_fusions):
    """
    Select the dataset with most cell lines and methods for UpSet plot
    Prioritize datasets with more complete method results
    """
    best_score = -1
    best_dataset = None
    best_key = None
    
    for cell_line, platforms in results.items():
        for platform, datasets in platforms.items():
            for dataset_key, dataset_info in datasets.items():
                method_results = dataset_info.get('method_results', {})
                
                # Count methods with results
                n_methods = sum(1 for m in METHODS if m in method_results and len(method_results[m]) > 0)
                
                # Calculate total fusions across all methods
                total_fusions = sum(len(fusions) for fusions in method_results.values())
                
                # Score: prioritize number of methods, then total fusions
                score = n_methods * 1000 + total_fusions
                
                if score > best_score:
                    best_score = score
                    best_dataset = dataset_info
                    best_key = dataset_key
    
    return best_dataset, best_key


# ============================================================================
# Main Function
# ============================================================================
def main():
    """Generate UpSet plots"""
    print("="*80)
    print("Generating UpSet Plots")
    print("="*80)
    
    # Load data
    print("\n1. Loading data...")
    results = scan_all_datasets()
    known_fusions = load_known_fusions()
    
    # Select best dataset
    print("\n2. Selecting best dataset for UpSet plot...")
    best_dataset, best_key = select_best_dataset_for_upset(results, known_fusions)
    
    if best_dataset:
        print(f"   Selected dataset: {best_key}")
        method_results = best_dataset.get('method_results', {})
        
        # Use general known fusions as ground truth
        known_fusions_set = known_fusions.get('ChimerKB_general', set())
        if not known_fusions_set:
            # Combine all known fusions
            known_fusions_set = set()
            for fusions in known_fusions.values():
                known_fusions_set.update(fusions)
        
        print(f"   Ground truth: {len(known_fusions_set)} known fusions")
        print(f"   Methods with results: {sum(1 for m in METHODS if m in method_results and len(method_results[m]) > 0)}")
        
        # Calculate metrics
        print("\n3. Calculating metrics...")
        metrics = calculate_method_metrics(method_results, known_fusions_set)
        
        # Print metrics
        print("\n   Method Performance:")
        print("   " + "-"*70)
        print(f"   {'Method':<20} {'Recall':<10} {'Precision':<10} {'F1':<10} {'Count'}")
        print("   " + "-"*70)
        for method in METHODS:
            if method in metrics:
                m = metrics[method]
                print(f"   {method:<20} {m['Recall']:<10.3f} {m['Precision']:<10.3f} "
                      f"{m['F1']:<10.3f} {m['Total_Predictions']}")
        
        # Generate UpSet plot
        print("\n4. Generating UpSet plot...")
        output_prefix = os.path.join(OUTPUT_DIR, "01_method_intersection")
        generate_upset_plot(method_results, known_fusions_set, output_prefix)
    
    print("\n✓ UpSet plot generation complete!")


if __name__ == '__main__':
    # First need to create a standalone data loader module
    print("Note: This script requires data_loader_module.py")
    print("Running data loader first...")
    
    # Import and run data loader
    exec(open(os.path.join(os.path.dirname(__file__), '01_data_loader.py')).read())
