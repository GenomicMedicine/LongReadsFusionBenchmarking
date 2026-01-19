#!/usr/bin/env python3
"""
生成Figure S2 (A-E)：补充图表
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from pathlib import Path

# 设置
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

BASE_DIR = Path('/data6/mark/Project/chimericRNA_detection/datasets_and_results')
OUTPUT_DIR = BASE_DIR / 'script/sim_data/figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 读取数据
df = pd.read_csv(BASE_DIR / 'script/sim_data/tables/simulated_benchmark.csv')

# 工具列表
TOOLS = ['CTAT-LR-Fusion', 'FLAIR_fusion', 'FusionSeeker', 'genion', 
         'IFDlong', 'JAFFAL', 'LongGF', 'pbfusion']

# 颜色映射
TOOL_COLORS = {
    'CTAT-LR-Fusion': '#1f77b4',
    'FLAIR_fusion': '#ff7f0e',
    'FusionSeeker': '#2ca02c',
    'genion': '#d62728',
    'IFDlong': '#9467bd',
    'JAFFAL': '#8c564b',
    'LongGF': '#e377c2',
    'pbfusion': '#7f7f7f'
}

def parse_dataset_params(dataset):
    """解析数据集参数"""
    import re
    pattern = r'(nanopore|pacbio)(\d+)_(\d+)x_(\d+\.\d+)_(\d+)'
    match = re.match(pattern, dataset)
    if match:
        platform, year, depth, identity, readlen = match.groups()
        return {
            'platform': 'ONT' if platform == 'nanopore' else 'PacBio',
            'year': year,
            'depth': int(depth),
            'identity': float(identity),
            'read_length': int(readlen)
        }
    return None

# 添加参数列
df['params'] = df['dataset'].apply(parse_dataset_params)
df = df[df['params'].notna()].copy()
df['platform'] = df['params'].apply(lambda x: x['platform'])
df['year'] = df['params'].apply(lambda x: x['year'])
df['depth'] = df['params'].apply(lambda x: x['depth'])
df['identity'] = df['params'].apply(lambda x: x['identity'])
df['read_length'] = df['params'].apply(lambda x: x['read_length'])

# ============================================================================
# Figure S2A: Tool-wise Distribution Across All Datasets
# ============================================================================
def plot_S2A():
    """工具检测融合数量的整体分布"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 准备数据
    plot_data = []
    for tool in TOOLS:
        tool_data = df[df['tool'] == tool]
        for count in tool_data['fusion_count']:
            plot_data.append({'Tool': tool, 'Count': count})
    
    plot_df = pd.DataFrame(plot_data)
    
    # 绘制小提琴图
    sns.violinplot(data=plot_df, x='Tool', y='Count', ax=ax, 
                   palette=TOOL_COLORS, inner='box')
    
    ax.set_ylabel('Fusion Count')
    ax.set_xlabel('')
    ax.set_title('(A) Distribution of Fusion Detection Across All Simulated Datasets', 
                 fontweight='bold', fontsize=12)
    ax.set_yscale('log')
    ax.grid(axis='y', alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'FigureS2_A_distribution.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'FigureS2_A_distribution.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure S2A")

# ============================================================================
# Figure S2B: Platform-specific Year Comparison
# ============================================================================
def plot_S2B():
    """不同测序技术版本的对比"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # ONT版本对比
    ont_data = df[df['platform'] == 'ONT']
    ont_years = sorted(ont_data['year'].unique())
    
    year_data_ont = []
    for year in ont_years:
        for tool in TOOLS:
            data = ont_data[(ont_data['year'] == year) & (ont_data['tool'] == tool)]
            if len(data) > 0:
                year_data_ont.append({
                    'Year': f'ONT {year}',
                    'Tool': tool,
                    'Fusions': data['fusion_count'].mean()
                })
    
    ydf_ont = pd.DataFrame(year_data_ont)
    ydf_ont_pivot = ydf_ont.pivot(index='Tool', columns='Year', values='Fusions')
    ydf_ont_pivot.plot(kind='bar', ax=ax1, width=0.7)
    ax1.set_ylabel('Mean Fusion Count')
    ax1.set_xlabel('')
    ax1.set_title('(B1) ONT Platform Version Comparison', fontweight='bold')
    ax1.legend(frameon=False, fontsize=8)
    ax1.grid(axis='y', alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # PacBio版本对比
    pb_data = df[df['platform'] == 'PacBio']
    pb_years = sorted(pb_data['year'].unique())
    
    year_data_pb = []
    for year in pb_years:
        for tool in TOOLS:
            data = pb_data[(pb_data['year'] == year) & (pb_data['tool'] == tool)]
            if len(data) > 0:
                year_data_pb.append({
                    'Year': f'PacBio {year}',
                    'Tool': tool,
                    'Fusions': data['fusion_count'].mean()
                })
    
    ydf_pb = pd.DataFrame(year_data_pb)
    ydf_pb_pivot = ydf_pb.pivot(index='Tool', columns='Year', values='Fusions')
    ydf_pb_pivot.plot(kind='bar', ax=ax2, width=0.7)
    ax2.set_ylabel('Mean Fusion Count')
    ax2.set_xlabel('')
    ax2.set_title('(B2) PacBio Platform Version Comparison', fontweight='bold')
    ax2.legend(frameon=False, fontsize=8)
    ax2.grid(axis='y', alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'FigureS2_B_platform_versions.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'FigureS2_B_platform_versions.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure S2B")

# ============================================================================
# Figure S2C: Correlation Between Tools
# ============================================================================
def plot_S2C():
    """工具间检测结果的相关性"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 创建相关性矩阵
    # 对于每个数据集，统计各工具的融合数量
    datasets = df['dataset'].unique()
    correlation_data = {}
    
    for tool in TOOLS:
        tool_counts = []
        for dataset in datasets:
            data = df[(df['dataset'] == dataset) & (df['tool'] == tool)]
            if len(data) > 0:
                tool_counts.append(data['fusion_count'].iloc[0])
            else:
                tool_counts.append(0)
        correlation_data[tool] = tool_counts
    
    corr_df = pd.DataFrame(correlation_data)
    correlation_matrix = corr_df.corr()
    
    # 绘制热图
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1, square=True, ax=ax,
                cbar_kws={'label': 'Pearson Correlation'})
    
    ax.set_title('(C) Tool Correlation Matrix', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'FigureS2_C_correlation.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'FigureS2_C_correlation.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure S2C")

# ============================================================================
# Figure S2D: Resource Usage vs Performance
# ============================================================================
def plot_S2D():
    """资源使用与性能的权衡"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 左图：运行时间 vs 融合数量
    for tool in TOOLS:
        tool_data = df[df['tool'] == tool]
        if len(tool_data) > 0:
            ax1.scatter(tool_data['runtime_minutes'], tool_data['fusion_count'],
                       label=tool, color=TOOL_COLORS.get(tool, 'gray'), 
                       alpha=0.6, s=50)
    
    ax1.set_xlabel('Runtime (minutes)')
    ax1.set_ylabel('Fusion Count')
    ax1.set_title('(D1) Runtime vs Detection Count', fontweight='bold')
    ax1.legend(frameon=False, fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # 右图：内存使用 vs 融合数量
    for tool in TOOLS:
        tool_data = df[df['tool'] == tool]
        if len(tool_data) > 0:
            ax2.scatter(tool_data['memory_gb'], tool_data['fusion_count'],
                       label=tool, color=TOOL_COLORS.get(tool, 'gray'), 
                       alpha=0.6, s=50)
    
    ax2.set_xlabel('Memory Usage (GB)')
    ax2.set_ylabel('Fusion Count')
    ax2.set_title('(D2) Memory vs Detection Count', fontweight='bold')
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'FigureS2_D_resources.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'FigureS2_D_resources.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure S2D")

# ============================================================================
# Figure S2E: Parameter Sensitivity Heatmap
# ============================================================================
def plot_S2E():
    """参数敏感性热图"""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    # 为每个工具创建深度-一致性热图
    depths = sorted([d for d in df['depth'].unique() if d in [1, 5, 10, 50, 100]])
    identities = sorted([i for i in df['identity'].unique() if i in [0.8, 0.85, 0.9, 0.95, 0.998]])
    
    for idx, tool in enumerate(TOOLS):
        ax = axes[idx]
        
        # 创建数据矩阵
        heatmap_data = np.zeros((len(identities), len(depths)))
        
        for i, identity in enumerate(identities):
            for j, depth in enumerate(depths):
                data = df[(df['tool'] == tool) & 
                         (df['depth'] == depth) & 
                         (df['identity'] == identity) &
                         (df['read_length'] == 15000)]
                if len(data) > 0:
                    heatmap_data[i, j] = data['fusion_count'].mean()
        
        # 绘制热图
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd',
                   xticklabels=[f'{d}x' for d in depths],
                   yticklabels=[f'{i:.2f}' for i in identities],
                   ax=ax, cbar_kws={'label': 'Fusion Count'})
        
        ax.set_title(tool, fontweight='bold')
        ax.set_xlabel('Depth')
        ax.set_ylabel('Identity')
    
    fig.suptitle('(E) Parameter Sensitivity: Depth vs Identity', 
                 fontweight='bold', fontsize=14, y=0.995)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'FigureS2_E_sensitivity.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'FigureS2_E_sensitivity.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure S2E")

# ============================================================================
# 主函数
# ============================================================================
def main():
    print("="*80)
    print("Generating Figure S2 (A-E)")
    print("="*80)
    
    plot_S2A()
    plot_S2B()
    plot_S2C()
    plot_S2D()
    plot_S2E()
    
    print("\n✓ All Figure S2 panels generated successfully!")
    print(f"✓ Output directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
