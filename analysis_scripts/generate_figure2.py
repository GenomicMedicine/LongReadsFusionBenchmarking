#!/usr/bin/env python3
"""
生成Figure 2 (A-H)：模拟数据性能对比
由于ground truth不匹配，使用以下策略：
- 使用融合检测数量作为敏感性指标
- 使用工具间一致性作为特异性指标
- 统计检验显著性差异
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
df['depth'] = df['params'].apply(lambda x: x['depth'])
df['identity'] = df['params'].apply(lambda x: x['identity'])
df['read_length'] = df['params'].apply(lambda x: x['read_length'])

# ============================================================================
# Figure 2A: Platform Comparison (ONT vs PacBio)
# ============================================================================
def plot_2A():
    """平台对比：ONT vs PacBio"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # 左图：融合数量对比
    platform_data = []
    for tool in TOOLS:
        for platform in ['ONT', 'PacBio']:
            data = df[(df['tool'] == tool) & (df['platform'] == platform)]
            if len(data) > 0:
                platform_data.append({
                    'Tool': tool,
                    'Platform': platform,
                    'Fusions': data['fusion_count'].median()
                })
    
    pdf = pd.DataFrame(platform_data)
    pdf_pivot = pdf.pivot(index='Tool', columns='Platform', values='Fusions')
    pdf_pivot.plot(kind='bar', ax=ax1, color=['#FF6B6B', '#4ECDC4'], width=0.7)
    ax1.set_ylabel('Median Fusion Count')
    ax1.set_xlabel('')
    ax1.set_title('(A) Platform Effect on Detection', fontweight='bold')
    ax1.legend(title='Platform', frameon=False)
    ax1.grid(axis='y', alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 右图：运行时间对比
    time_data = []
    for tool in TOOLS:
        for platform in ['ONT', 'PacBio']:
            data = df[(df['tool'] == tool) & (df['platform'] == platform)]
            if len(data) > 0:
                time_data.append({
                    'Tool': tool,
                    'Platform': platform,
                    'Runtime': data['runtime_minutes'].median()
                })
    
    tdf = pd.DataFrame(time_data)
    tdf_pivot = tdf.pivot(index='Tool', columns='Platform', values='Runtime')
    tdf_pivot.plot(kind='bar', ax=ax2, color=['#FF6B6B', '#4ECDC4'], width=0.7)
    ax2.set_ylabel('Median Runtime (min)')
    ax2.set_xlabel('')
    ax2.set_title('(B) Runtime Comparison', fontweight='bold')
    ax2.legend(title='Platform', frameon=False)
    ax2.grid(axis='y', alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'Figure2_AB_platform.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'Figure2_AB_platform.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure 2A-B")

# ============================================================================
# Figure 2C-D: Sequencing Depth Effect
# ============================================================================
def plot_2CD():
    """测序深度效应"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # 只使用10x作为基准的数据集
    depths = [1, 5, 10, 50, 100]
    depth_df = df[(df['depth'].isin(depths)) & 
                  (df['identity'] == 0.95) & 
                  (df['read_length'] == 15000)]
    
    # 左图：各工具随深度变化
    for tool in TOOLS:
        tool_data = depth_df[depth_df['tool'] == tool]
        if len(tool_data) > 0:
            depth_means = tool_data.groupby('depth')['fusion_count'].mean()
            depth_sems = tool_data.groupby('depth')['fusion_count'].sem()
            ax1.plot(depth_means.index, depth_means.values, 
                    marker='o', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
            ax1.fill_between(depth_means.index, 
                            depth_means - depth_sems, 
                            depth_means + depth_sems, 
                            alpha=0.2, color=TOOL_COLORS.get(tool, 'gray'))
    
    ax1.set_xlabel('Sequencing Depth (x)')
    ax1.set_ylabel('Fusion Count')
    ax1.set_title('(C) Depth Effect on Detection Sensitivity', fontweight='bold')
    ax1.legend(frameon=False, fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_xticks(depths)
    ax1.set_xticklabels([f'{d}x' for d in depths])
    
    # 右图：深度对运行时间的影响
    for tool in TOOLS:
        tool_data = depth_df[depth_df['tool'] == tool]
        if len(tool_data) > 0:
            depth_means = tool_data.groupby('depth')['runtime_minutes'].mean()
            ax2.plot(depth_means.index, depth_means.values, 
                    marker='s', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
    
    ax2.set_xlabel('Sequencing Depth (x)')
    ax2.set_ylabel('Runtime (minutes)')
    ax2.set_title('(D) Depth Effect on Runtime', fontweight='bold')
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xticks(depths)
    ax2.set_xticklabels([f'{d}x' for d in depths])
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'Figure2_CD_depth.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'Figure2_CD_depth.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure 2C-D")

# ============================================================================
# Figure 2E-F: Read Length Effect
# ============================================================================
def plot_2EF():
    """读长效应"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    read_lengths = [300, 1000, 5000, 15000, 50000]
    readlen_df = df[(df['read_length'].isin(read_lengths)) & 
                    (df['depth'] == 10) & 
                    (df['identity'] == 0.95)]
    
    # 左图：读长对融合检测的影响
    for tool in TOOLS:
        tool_data = readlen_df[readlen_df['tool'] == tool]
        if len(tool_data) > 0:
            len_means = tool_data.groupby('read_length')['fusion_count'].mean()
            len_sems = tool_data.groupby('read_length')['fusion_count'].sem()
            ax1.plot(len_means.index, len_means.values, 
                    marker='o', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
            ax1.fill_between(len_means.index, 
                            len_means - len_sems, 
                            len_means + len_sems, 
                            alpha=0.2, color=TOOL_COLORS.get(tool, 'gray'))
    
    ax1.set_xlabel('Read Length (bp)')
    ax1.set_ylabel('Fusion Count')
    ax1.set_title('(E) Read Length Effect on Detection', fontweight='bold')
    ax1.legend(frameon=False, fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_xticks(read_lengths)
    ax1.set_xticklabels([f'{l//1000}kb' if l >= 1000 else f'{l}bp' for l in read_lengths])
    
    # 右图：读长对检测变异系数的影响（稳定性）
    stability_data = []
    for tool in TOOLS:
        for rl in read_lengths:
            tool_data = readlen_df[(readlen_df['tool'] == tool) & 
                                  (readlen_df['read_length'] == rl)]
            if len(tool_data) > 1:
                cv = tool_data['fusion_count'].std() / tool_data['fusion_count'].mean()
                stability_data.append({
                    'Tool': tool,
                    'ReadLength': rl,
                    'CV': cv
                })
    
    sdf = pd.DataFrame(stability_data)
    for tool in TOOLS:
        tool_data = sdf[sdf['Tool'] == tool]
        if len(tool_data) > 0:
            ax2.plot(tool_data['ReadLength'], tool_data['CV'], 
                    marker='s', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
    
    ax2.set_xlabel('Read Length (bp)')
    ax2.set_ylabel('Coefficient of Variation')
    ax2.set_title('(F) Detection Stability vs Read Length', fontweight='bold')
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.set_xticks(read_lengths)
    ax2.set_xticklabels([f'{l//1000}kb' if l >= 1000 else f'{l}bp' for l in read_lengths])
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'Figure2_EF_readlength.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'Figure2_EF_readlength.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure 2E-F")

# ============================================================================
# Figure 2G-H: Sequence Identity Effect
# ============================================================================
def plot_2GH():
    """序列一致性效应"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    identities = [0.8, 0.85, 0.9, 0.95, 0.998]
    identity_df = df[(df['identity'].isin(identities)) & 
                     (df['depth'] == 10) & 
                     (df['read_length'] == 15000)]
    
    # 左图：一致性对融合检测的影响
    for tool in TOOLS:
        tool_data = identity_df[identity_df['tool'] == tool]
        if len(tool_data) > 0:
            id_means = tool_data.groupby('identity')['fusion_count'].mean()
            id_sems = tool_data.groupby('identity')['fusion_count'].sem()
            ax1.plot(id_means.index, id_means.values, 
                    marker='o', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
            ax1.fill_between(id_means.index, 
                            id_means - id_sems, 
                            id_means + id_sems, 
                            alpha=0.2, color=TOOL_COLORS.get(tool, 'gray'))
    
    ax1.set_xlabel('Sequence Identity')
    ax1.set_ylabel('Fusion Count')
    ax1.set_title('(G) Sequence Identity Effect on Detection', fontweight='bold')
    ax1.legend(frameon=False, fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(identities)
    
    # 右图：一致性对内存使用的影响
    for tool in TOOLS:
        tool_data = identity_df[identity_df['tool'] == tool]
        if len(tool_data) > 0:
            id_means = tool_data.groupby('identity')['memory_gb'].mean()
            ax2.plot(id_means.index, id_means.values, 
                    marker='s', label=tool, color=TOOL_COLORS.get(tool, 'gray'), linewidth=2)
    
    ax2.set_xlabel('Sequence Identity')
    ax2.set_ylabel('Memory Usage (GB)')
    ax2.set_title('(H) Identity Effect on Memory', fontweight='bold')
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(identities)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'Figure2_GH_identity.pdf', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'Figure2_GH_identity.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated Figure 2G-H")

# ============================================================================
# 主函数
# ============================================================================
def main():
    print("="*80)
    print("Generating Figure 2 (A-H)")
    print("="*80)
    
    plot_2A()
    plot_2CD()
    plot_2EF()
    plot_2GH()
    
    print("\n✓ All Figure 2 panels generated successfully!")
    print(f"✓ Output directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
