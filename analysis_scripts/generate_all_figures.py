#!/usr/bin/env python3
"""
Master Script: Generate All Figures and Analysis
Runs complete analysis pipeline and generates all visualizations
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import gridspec
from matplotlib.patches import Rectangle
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Import from main_analysis
from main_analysis import (
    BASE_DIR, OUTPUT_DIR, METHODS, METHOD_COLORS,
    load_known_fusions, scan_all_datasets, load_runtime_memory,
    calculate_all_metrics, setup_plot_style, save_figure
)

# ============================================================================
# Figure 1: UpSet Plot with Recall
# ============================================================================
def generate_upset_plot(metrics_df, results_df, known_fusions, output_prefix):
    """Generate UpSet plot showing method intersections"""
    print("\nGenerating Figure 1: UpSet Plot...")
    
    # Select best dataset (most methods with results)
    best_dataset = None
    max_methods = 0
    
    for idx, row in results_df.iterrows():
        n_methods = sum(1 for m in METHODS if f'{m}_fusions' in row and row[f'{m}_fusions'] is not None)
        if n_methods > max_methods:
            max_methods = n_methods
            best_dataset = row
    
    if best_dataset is None:
        print("  No suitable dataset found")
        return
    
    # Get method results for this dataset
    method_results = {}
    for method in METHODS:
        fusion_col = f'{method}_fusions'
        if fusion_col in best_dataset and best_dataset[fusion_col] is not None:
            method_results[method] = best_dataset[fusion_col]
    
    # Calculate intersections
    intersection_data = []
    
    # Single methods
    for method in method_results:
        intersection_data.append({
            'methods': frozenset([method]),
            'count': len(method_results[method]),
            'fusions': method_results[method]
        })
    
    # Pairs
    for m1, m2 in combinations(method_results.keys(), 2):
        intersection = method_results[m1] & method_results[m2]
        intersection_data.append({
            'methods': frozenset([m1, m2]),
            'count': len(intersection),
            'fusions': intersection
        })
    
    # Sort by count
    intersection_data.sort(key=lambda x: x['count'], reverse=True)
    top_intersections = intersection_data[:min(25, len(intersection_data))]
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 1, height_ratios=[2, 3, 1], hspace=0.05)
    
    # Top: Bar chart
    ax_bar = fig.add_subplot(gs[0])
    x_pos = np.arange(len(top_intersections))
    counts = [item['count'] for item in top_intersections]
    colors = ['#E64B35' if len(item['methods'])==1 else '#3C5488' if len(item['methods'])==2 else '#00A087' 
              for item in top_intersections]
    
    bars = ax_bar.bar(x_pos, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax_bar.set_ylabel('Intersection Size', fontsize=12, fontweight='bold')
    ax_bar.set_xticks([])
    ax_bar.spines['bottom'].set_visible(False)
    ax_bar.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, count in zip(bars, counts):
        if count > 0:
            ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.02,
                       str(count), ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Middle: Dot matrix
    ax_matrix = fig.add_subplot(gs[1])
    available_methods = list(method_results.keys())
    
    for i, item in enumerate(top_intersections):
        methods_in_set = item['methods']
        for j, method in enumerate(available_methods):
            if method in methods_in_set:
                ax_matrix.scatter(i, j, s=500, c=METHOD_COLORS.get(method, '#666666'),
                                marker='o', edgecolors='black', linewidth=1.5, zorder=10)
        
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
    
    for spine in ax_matrix.spines.values():
        spine.set_visible(False)
    
    # Bottom: Recall
    ax_recall = fig.add_subplot(gs[2])
    recalls = []
    for method in available_methods:
        predictions = method_results[method]
        tp = len(predictions & known_fusions)
        fn = len(known_fusions - predictions)
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
    
    for bar, recall in zip(bars_recall, recalls):
        ax_recall.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                      f'{recall:.3f}', va='center', fontsize=10, fontweight='bold')
    
    fig.suptitle('Method Intersections and Recall Metrics', fontsize=16, fontweight='bold', y=0.98)
    
    save_figure(fig, f"{output_prefix}_upset_plot")
    print("  ✓ UpSet plot complete")


# ============================================================================
# Figure 2: Method Consensus
# ============================================================================
def generate_consensus_plot(results_df, known_fusions, output_prefix):
    """Generate method consensus plot"""
    print("\nGenerating Figure 2: Method Consensus...")
    
    # Aggregate across all datasets
    fusion_method_count = {}
    
    for idx, row in results_df.iterrows():
        for method in METHODS:
            fusion_col = f'{method}_fusions'
            if fusion_col in row and row[fusion_col] is not None:
                fusions = row[fusion_col]
                # Skip if not a set or is empty
                if not isinstance(fusions, set) or len(fusions) == 0:
                    continue
                for fusion in fusions:
                    if fusion not in fusion_method_count:
                        fusion_method_count[fusion] = set()
                    fusion_method_count[fusion].add(method)
    
    # Count by number of methods
    validated_counts = {}
    total_counts = {}
    
    for fusion, methods in fusion_method_count.items():
        n_methods = len(methods)
        total_counts[n_methods] = total_counts.get(n_methods, 0) + 1
        if fusion in known_fusions:
            validated_counts[n_methods] = validated_counts.get(n_methods, 0) + 1
    
    # Create plot
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    x = np.arange(1, 9)
    validated = [validated_counts.get(i, 0) for i in x]
    total = [total_counts.get(i, 0) for i in x]
    
    total_sum = sum(total)
    percentages = [t / total_sum * 100 if total_sum > 0 else 0 for t in total]
    
    bars = ax1.bar(x, validated, width=0.6, color='#3498db', alpha=0.7,
                   edgecolor='black', linewidth=1.5, label='Validated Fusions')
    
    ax1.set_xlabel('Number of Methods Detecting Fusion', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Count of Validated Fusions', fontsize=14, fontweight='bold', color='#3498db')
    ax1.tick_params(axis='y', labelcolor='#3498db', labelsize=12)
    ax1.set_xticks(x)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, val in zip(bars, validated):
        if val > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(validated)*0.02,
                    str(int(val)), ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2 = ax1.twinx()
    line = ax2.plot(x, percentages, color='#e74c3c', linewidth=3, marker='o',
                    markersize=10, label='% of Total Predictions',
                    markerfacecolor='white', markeredgewidth=2, markeredgecolor='#e74c3c')
    
    ax2.set_ylabel('Total Predicted Fusions (%)', fontsize=14, fontweight='bold', color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c', labelsize=12)
    
    for xi, pct in zip(x, percentages):
        if pct > 0:
            ax2.text(xi, pct + max(percentages)*0.05, f'{pct:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='#e74c3c')
    
    plt.title('Method Consensus: Validated Fusions vs Total Predictions',
             fontsize=16, fontweight='bold', pad=20)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=12)
    
    save_figure(fig, f"{output_prefix}_consensus")
    print("  ✓ Consensus plot complete")


# ============================================================================
# Figure 3: Leaderboard Ranking
# ============================================================================
def generate_leaderboard(metrics_df, output_prefix):
    """Generate leaderboard ranking plot"""
    print("\nGenerating Figure 3: Leaderboard Ranking...")
    
    # Calculate rankings per dataset
    rankings = []
    for dataset, group in metrics_df.groupby('dataset'):
        sorted_group = group.sort_values('F1', ascending=False)
        for rank, (idx, row) in enumerate(sorted_group.iterrows(), 1):
            rankings.append({
                'dataset': dataset,
                'method': row['method'],
                'rank': rank,
                'F1': row['F1']
            })
    
    rankings_df = pd.DataFrame(rankings)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    methods = sorted(METHODS)
    
    # Box plot
    ax1 = axes[0]
    ranking_data = [rankings_df[rankings_df['method'] == m]['rank'].values for m in methods]
    
    bp = ax1.boxplot(ranking_data, labels=methods, patch_artist=True,
                     showmeans=True, medianprops=dict(color='red', linewidth=2),
                     meanprops=dict(marker='D', markerfacecolor='yellow',
                                  markeredgecolor='black', markersize=8))
    
    for patch, method in zip(bp['boxes'], methods):
        patch.set_facecolor(METHOD_COLORS.get(method, '#666666'))
        patch.set_alpha(0.7)
    
    ax1.set_xlabel('Method', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Rank (1 = Best)', fontsize=13, fontweight='bold')
    ax1.set_title('Leaderboard Ranking Distribution', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Average rank
    ax2 = axes[1]
    mean_ranks = [rankings_df[rankings_df['method'] == m]['rank'].mean() for m in methods]
    std_ranks = [rankings_df[rankings_df['method'] == m]['rank'].std() for m in methods]
    
    x_pos = np.arange(len(methods))
    colors = [METHOD_COLORS.get(m, '#666666') for m in methods]
    
    bars = ax2.barh(x_pos, mean_ranks, xerr=std_ranks,
                    color=colors, alpha=0.8, edgecolor='black', linewidth=1.5,
                    capsize=5)
    
    ax2.set_yticks(x_pos)
    ax2.set_yticklabels(methods, fontsize=11, fontweight='bold')
    ax2.invert_yaxis()
    ax2.set_xlabel('Average Rank ± SD', fontsize=13, fontweight='bold')
    ax2.set_title('Average Ranking Across Datasets', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    for bar, mean_val, std_val in zip(bars, mean_ranks, std_ranks):
        ax2.text(bar.get_width() + std_val + 0.1, bar.get_y() + bar.get_height()/2,
                f'{mean_val:.2f}±{std_val:.2f}',
                va='center', fontsize=10, fontweight='bold')
    
    save_figure(fig, f"{output_prefix}_leaderboard")
    print("  ✓ Leaderboard plot complete")


# ============================================================================
# Figure 4-5: Runtime and Memory
# ============================================================================
def generate_runtime_memory_plots(runtime_df, output_prefix):
    """Generate runtime and memory analysis plots"""
    print("\nGenerating Figures 4-5: Runtime and Memory Analysis...")
    
    if len(runtime_df) == 0:
        print("  No runtime data available")
        return
    
    methods = sorted(runtime_df['Method'].unique())
    
    # Scatter plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for method in methods:
        method_data = runtime_df[runtime_df['Method'] == method]
        if len(method_data) > 0:
            runtime = method_data['Runtime_sec'].values
            memory = method_data['Memory_MB'].values
            
            ax.scatter(runtime, memory, s=150, alpha=0.7,
                      c=METHOD_COLORS.get(method, '#666666'),
                      label=method, edgecolors='black', linewidth=1.5)
            
            mean_runtime = np.mean(runtime)
            mean_memory = np.mean(memory)
            ax.scatter(mean_runtime, mean_memory, s=400, alpha=1.0,
                      c=METHOD_COLORS.get(method, '#666666'),
                      marker='*', edgecolors='black', linewidth=2)
    
    ax.set_xlabel('Runtime (seconds)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)', fontsize=14, fontweight='bold')
    ax.set_title('Runtime vs Memory Usage by Method', fontsize=16, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Log scale if needed
    if runtime_df['Runtime_sec'].max() / max(runtime_df['Runtime_sec'].min(), 1) > 100:
        ax.set_xscale('log')
    if runtime_df['Memory_MB'].max() / max(runtime_df['Memory_MB'].min(), 1) > 100:
        ax.set_yscale('log')
    
    save_figure(fig, f"{output_prefix}_runtime_memory_scatter")
    
    # Box plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    runtime_data = [runtime_df[runtime_df['Method'] == m]['Runtime_sec'].values for m in methods]
    memory_data = [runtime_df[runtime_df['Method'] == m]['Memory_MB'].values for m in methods]
    
    bp1 = ax1.boxplot(runtime_data, labels=methods, patch_artist=True,
                      showmeans=True, medianprops=dict(color='red', linewidth=2))
    
    for patch, method in zip(bp1['boxes'], methods):
        patch.set_facecolor(METHOD_COLORS.get(method, '#666666'))
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Runtime (seconds)', fontsize=13, fontweight='bold')
    ax1.set_title('Runtime Distribution by Method', fontsize=14, fontweight='bold')
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    bp2 = ax2.boxplot(memory_data, labels=methods, patch_artist=True,
                      showmeans=True, medianprops=dict(color='red', linewidth=2))
    
    for patch, method in zip(bp2['boxes'], methods):
        patch.set_facecolor(METHOD_COLORS.get(method, '#666666'))
        patch.set_alpha(0.7)
    
    ax2.set_ylabel('Memory Usage (MB)', fontsize=13, fontweight='bold')
    ax2.set_title('Memory Distribution by Method', fontsize=14, fontweight='bold')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    save_figure(fig, f"{output_prefix}_performance_boxplots")
    print("  ✓ Runtime/memory plots complete")


# ============================================================================
# Figure 6: PPV vs TPR
# ============================================================================
def generate_ppv_tpr_plot(metrics_df, output_prefix):
    """Generate PPV vs TPR plot"""
    print("\nGenerating Figure 6: PPV vs TPR...")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    methods = sorted(metrics_df['method'].unique())
    
    for method in methods:
        method_data = metrics_df[metrics_df['method'] == method]
        
        if len(method_data) > 0:
            ppv = method_data['Precision'].values
            tpr = method_data['Recall'].values
            
            ax.scatter(tpr, ppv, s=80, alpha=0.4,
                      c=METHOD_COLORS.get(method, '#666666'),
                      edgecolors='none', zorder=2)
            
            mean_tpr = np.mean(tpr)
            mean_ppv = np.mean(ppv)
            std_tpr = np.std(tpr)
            std_ppv = np.std(ppv)
            
            ax.errorbar(mean_tpr, mean_ppv,
                       xerr=std_tpr, yerr=std_ppv,
                       fmt='o', markersize=15,
                       color=METHOD_COLORS.get(method, '#666666'),
                       markeredgecolor='black', markeredgewidth=2,
                       elinewidth=2, capsize=5,
                       label=method, zorder=3, alpha=0.9)
            
            ax.text(mean_tpr + 0.02, mean_ppv + 0.02, method,
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3',
                           facecolor=METHOD_COLORS.get(method, '#666666'),
                           alpha=0.7),
                   color='white', zorder=4)
    
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, linewidth=1)
    
    # F1 contours
    for f1 in [0.3, 0.5, 0.7, 0.9]:
        tpr_range = np.linspace(0.01, 1, 100)
        ppv_range = f1 * tpr_range / (2 * tpr_range - f1)
        ppv_range = np.clip(ppv_range, 0, 1)
        ax.plot(tpr_range, ppv_range, ':', alpha=0.3, linewidth=1, color='gray')
    
    rect = Rectangle((0.5, 0.5), 0.5, 0.5, alpha=0.05, facecolor='green')
    ax.add_patch(rect)
    ax.text(0.75, 0.95, 'Ideal', fontsize=12, fontweight='bold',
           color='green', alpha=0.3, ha='center')
    
    ax.set_xlabel('TPR (Recall / Sensitivity)', fontsize=14, fontweight='bold')
    ax.set_ylabel('PPV (Precision)', fontsize=14, fontweight='bold')
    ax.set_title('PPV vs TPR: Method Performance Comparison',
                fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    save_figure(fig, f"{output_prefix}_ppv_tpr")
    print("  ✓ PPV vs TPR plot complete")


# ============================================================================
# Main Function
# ============================================================================
def main():
    """Generate all figures"""
    print("="*80)
    print("Real Data Analysis: Complete Figure Generation")
    print("="*80)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    setup_plot_style()
    
    # Load data
    print("\nLoading data...")
    known_fusions_all, _ = load_known_fusions()
    all_results = scan_all_datasets()
    results_df = pd.DataFrame(all_results)
    metrics_df = calculate_all_metrics(results_df, known_fusions_all)
    runtime_df = load_runtime_memory()
    
    # Generate figures
    output_prefix = os.path.join(OUTPUT_DIR, "01")
    
    generate_upset_plot(metrics_df, results_df, known_fusions_all, 
                       os.path.join(OUTPUT_DIR, "01_method_intersection"))
    
    generate_consensus_plot(results_df, known_fusions_all,
                           os.path.join(OUTPUT_DIR, "02_method"))
    
    generate_leaderboard(metrics_df,
                        os.path.join(OUTPUT_DIR, "03"))
    
    generate_runtime_memory_plots(runtime_df,
                                  os.path.join(OUTPUT_DIR, "04"))
    
    generate_ppv_tpr_plot(metrics_df,
                         os.path.join(OUTPUT_DIR, "07"))
    
    print("\n" + "="*80)
    print("All figures generated successfully!")
    print("="*80)
    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
