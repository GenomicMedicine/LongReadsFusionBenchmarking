#!/usr/bin/env python3
"""
Generate PPV (Precision) vs TPR (Recall) Plot
Classic ROC-style visualization showing method performance
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle

OUTPUT_DIR = "/data6/mark/Project/chimericRNA_detection/datasets_and_results/real_data/r1"

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
# Generate PPV vs TPR Scatter Plot
# ============================================================================
def generate_ppv_tpr_plot(metrics_df, output_prefix):
    """
    Generate PPV (Precision) vs TPR (Recall) scatter plot
    Each point represents one method on one dataset
    Show mean ± SD for each method
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    methods = sorted(metrics_df['method'].unique())
    
    # Plot individual points and means
    for method in methods:
        method_data = metrics_df[metrics_df['method'] == method]
        
        if len(method_data) > 0:
            ppv = method_data['Precision'].values
            tpr = method_data['Recall'].values
            
            # Plot individual points (semi-transparent)
            ax.scatter(tpr, ppv, s=80, alpha=0.4, 
                      c=METHOD_COLORS.get(method, '#666666'),
                      edgecolors='none', zorder=2)
            
            # Calculate and plot mean
            mean_tpr = np.mean(tpr)
            mean_ppv = np.mean(ppv)
            std_tpr = np.std(tpr)
            std_ppv = np.std(ppv)
            
            # Plot mean with error bars
            ax.errorbar(mean_tpr, mean_ppv, 
                       xerr=std_tpr, yerr=std_ppv,
                       fmt='o', markersize=15, 
                       color=METHOD_COLORS.get(method, '#666666'),
                       markerfacecolor=METHOD_COLORS.get(method, '#666666'),
                       markeredgecolor='black', markeredgewidth=2,
                       ecolor=METHOD_COLORS.get(method, '#666666'),
                       elinewidth=2, capsize=5, capthick=2,
                       label=method, zorder=3, alpha=0.9)
            
            # Add method name label
            ax.text(mean_tpr + 0.02, mean_ppv + 0.02, method, 
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', 
                           facecolor=METHOD_COLORS.get(method, '#666666'),
                           edgecolor='black', alpha=0.7),
                   color='white', zorder=4)
    
    # Add diagonal line (F1-score contours could be added)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, linewidth=1, label='PPV = TPR', zorder=1)
    
    # Add F1-score contours
    for f1 in [0.3, 0.5, 0.7, 0.9]:
        tpr_range = np.linspace(0.01, 1, 100)
        ppv_range = f1 * tpr_range / (2 * tpr_range - f1)
        ppv_range = np.clip(ppv_range, 0, 1)
        ax.plot(tpr_range, ppv_range, ':', alpha=0.3, linewidth=1, color='gray', zorder=1)
        # Add F1 label
        if f1 < 0.95:
            idx = int(len(tpr_range) * 0.7)
            ax.text(tpr_range[idx], ppv_range[idx], f'F1={f1}', 
                   fontsize=8, alpha=0.5, rotation=45, color='gray')
    
    # Highlight quadrants
    # Top-right quadrant (high PPV, high TPR) - ideal
    rect = Rectangle((0.5, 0.5), 0.5, 0.5, alpha=0.05, facecolor='green', zorder=0)
    ax.add_patch(rect)
    ax.text(0.75, 0.95, 'Ideal', fontsize=12, fontweight='bold', 
           color='green', alpha=0.3, ha='center')
    
    # Bottom-left quadrant (low PPV, low TPR) - poor
    rect = Rectangle((0, 0), 0.5, 0.5, alpha=0.05, facecolor='red', zorder=0)
    ax.add_patch(rect)
    ax.text(0.25, 0.05, 'Poor', fontsize=12, fontweight='bold', 
           color='red', alpha=0.3, ha='center')
    
    ax.set_xlabel('TPR (Recall / Sensitivity)', fontsize=14, fontweight='bold')
    ax.set_ylabel('PPV (Precision)', fontsize=14, fontweight='bold')
    ax.set_title('PPV vs TPR: Method Performance Comparison', 
                fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    
    # Legend (only show mean markers)
    handles, labels = ax.get_legend_handles_labels()
    # Filter out diagonal line from legend if present
    filtered = [(h, l) for h, l in zip(handles, labels) if l != 'PPV = TPR']
    if filtered:
        handles, labels = zip(*filtered)
        ax.legend(handles, labels, loc='lower left', fontsize=10, 
                 framealpha=0.9, ncol=2, bbox_to_anchor=(0, 0))
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_ppv_tpr_plot.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_ppv_tpr_plot.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_ppv_tpr_plot.pdf/png")
    
    # Print summary statistics
    print("\n  PPV-TPR Summary:")
    print("  " + "="*80)
    print(f"  {'Method':<20} {'Mean TPR':<15} {'Mean PPV':<15} {'Mean F1':<15}")
    print("  " + "="*80)
    for method in methods:
        method_data = metrics_df[metrics_df['method'] == method]
        if len(method_data) > 0:
            mean_tpr = np.mean(method_data['Recall'])
            mean_ppv = np.mean(method_data['Precision'])
            mean_f1 = np.mean(method_data['F1'])
            print(f"  {method:<20} {mean_tpr:<15.3f} {mean_ppv:<15.3f} {mean_f1:<15.3f}")


# ============================================================================
# Generate Performance Space Heat Map
# ============================================================================
def generate_performance_heatmap(metrics_df, output_prefix):
    """
    Generate 2D heatmap showing density of method performance in PPV-TPR space
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    methods = sorted(metrics_df['method'].unique())
    
    # Create 2D histogram
    all_tpr = metrics_df['Recall'].values
    all_ppv = metrics_df['Precision'].values
    
    # Plot hexbin
    hexbin = ax.hexbin(all_tpr, all_ppv, gridsize=20, cmap='YlOrRd', 
                      alpha=0.6, edgecolors='black', linewidths=0.2, mincnt=1)
    
    # Overlay method means
    for method in methods:
        method_data = metrics_df[metrics_df['method'] == method]
        if len(method_data) > 0:
            mean_tpr = np.mean(method_data['Recall'])
            mean_ppv = np.mean(method_data['Precision'])
            
            ax.scatter(mean_tpr, mean_ppv, s=300, 
                      color=METHOD_COLORS.get(method, '#666666'),
                      marker='*', edgecolors='black', linewidth=2,
                      zorder=10)
            
            ax.text(mean_tpr + 0.02, mean_ppv, method, 
                   fontsize=10, fontweight='bold', zorder=11)
    
    # Add F1-score contours
    for f1 in [0.3, 0.5, 0.7, 0.9]:
        tpr_range = np.linspace(0.01, 1, 100)
        ppv_range = f1 * tpr_range / (2 * tpr_range - f1)
        ppv_range = np.clip(ppv_range, 0, 1)
        ax.plot(tpr_range, ppv_range, '--', alpha=0.5, linewidth=2, 
               color='blue', label=f'F1={f1}' if f1 == 0.5 else '')
    
    ax.set_xlabel('TPR (Recall)', fontsize=14, fontweight='bold')
    ax.set_ylabel('PPV (Precision)', fontsize=14, fontweight='bold')
    ax.set_title('Performance Density Heatmap', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Colorbar
    cbar = plt.colorbar(hexbin, ax=ax, label='Number of Observations')
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_performance_heatmap.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_performance_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_performance_heatmap.pdf/png")


# ============================================================================
# Generate Method Trajectory Plot
# ============================================================================
def generate_method_trajectory_plot(metrics_df, output_prefix):
    """
    Show how method performance varies across different datasets
    Each method gets a trajectory line connecting its performances
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    
    methods = sorted(metrics_df['method'].unique())
    
    for method in methods:
        method_data = metrics_df[metrics_df['method'] == method]
        
        if len(method_data) > 1:
            tpr = method_data['Recall'].values
            ppv = method_data['Precision'].values
            
            # Sort by F1-score for nice trajectory
            f1 = 2 * tpr * ppv / (tpr + ppv + 1e-10)
            sorted_idx = np.argsort(f1)
            
            tpr_sorted = tpr[sorted_idx]
            ppv_sorted = ppv[sorted_idx]
            
            # Plot trajectory
            ax.plot(tpr_sorted, ppv_sorted, '-', 
                   color=METHOD_COLORS.get(method, '#666666'),
                   linewidth=2, alpha=0.6, zorder=2)
            
            # Plot points
            ax.scatter(tpr, ppv, s=100, 
                      color=METHOD_COLORS.get(method, '#666666'),
                      edgecolors='black', linewidth=1.5,
                      alpha=0.8, zorder=3)
            
            # Add method label at mean position
            mean_tpr = np.mean(tpr)
            mean_ppv = np.mean(ppv)
            ax.text(mean_tpr, mean_ppv + 0.03, method, 
                   fontsize=10, fontweight='bold',
                   ha='center', color=METHOD_COLORS.get(method, '#666666'),
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor=METHOD_COLORS.get(method, '#666666'),
                           linewidth=2, alpha=0.9),
                   zorder=4)
    
    # Add reference lines
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, linewidth=1)
    
    # F1 contours
    for f1 in [0.5, 0.7, 0.9]:
        tpr_range = np.linspace(0.01, 1, 100)
        ppv_range = f1 * tpr_range / (2 * tpr_range - f1)
        ppv_range = np.clip(ppv_range, 0, 1)
        ax.plot(tpr_range, ppv_range, ':', alpha=0.3, linewidth=1.5, 
               color='gray', label=f'F1={f1}' if f1 == 0.7 else '')
    
    ax.set_xlabel('TPR (Recall)', fontsize=14, fontweight='bold')
    ax.set_ylabel('PPV (Precision)', fontsize=14, fontweight='bold')
    ax.set_title('Method Performance Trajectories Across Datasets', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_trajectory_plot.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_trajectory_plot.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_prefix}_trajectory_plot.pdf/png")


# ============================================================================
# Main Function
# ============================================================================
def main():
    """Generate PPV vs TPR plots"""
    print("="*80)
    print("Generating PPV vs TPR Plots")
    print("="*80)
    
    print("\nNote: This script will be integrated into the main analysis pipeline")


if __name__ == '__main__':
    main()
