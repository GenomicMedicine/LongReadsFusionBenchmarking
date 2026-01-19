#!/usr/bin/env python3
"""
生成Table S1：统计检验结果
包括：
1. 工具间融合检测数量的比较（ANOVA + post-hoc）
2. 平台效应（t-test）
3. 参数效应（相关性分析）
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f_oneway, ttest_ind, pearsonr
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path('/data6/mark/Project/chimericRNA_detection/datasets_and_results')
OUTPUT_DIR = BASE_DIR / 'script/sim_data/tables'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 读取数据
df = pd.read_csv(OUTPUT_DIR / 'simulated_benchmark.csv')

# 工具列表
TOOLS = ['CTAT-LR-Fusion', 'FLAIR_fusion', 'FusionSeeker', 'genion', 
         'IFDlong', 'JAFFAL', 'LongGF', 'pbfusion']

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
# Table S1A: Tool Comparison (ANOVA + Pairwise)
# ============================================================================
def generate_tool_comparison():
    """工具间比较统计"""
    results = []
    
    # 整体ANOVA
    groups = [df[df['tool'] == tool]['fusion_count'].values for tool in TOOLS if tool in df['tool'].values]
    f_stat, p_val = f_oneway(*groups)
    
    results.append({
        'Analysis': 'Overall ANOVA',
        'Comparison': 'All Tools',
        'Statistic': f'F={f_stat:.2f}',
        'P_value': f'{p_val:.2e}',
        'Significant': 'Yes' if p_val < 0.05 else 'No'
    })
    
    # 两两比较（t-test）
    for i, tool1 in enumerate(TOOLS):
        for tool2 in TOOLS[i+1:]:
            data1 = df[df['tool'] == tool1]['fusion_count']
            data2 = df[df['tool'] == tool2]['fusion_count']
            
            if len(data1) > 0 and len(data2) > 0:
                t_stat, p_val = ttest_ind(data1, data2)
                mean_diff = data1.mean() - data2.mean()
                
                results.append({
                    'Analysis': 'Pairwise t-test',
                    'Comparison': f'{tool1} vs {tool2}',
                    'Statistic': f't={t_stat:.2f}',
                    'P_value': f'{p_val:.4f}',
                    'Mean_Diff': f'{mean_diff:.1f}',
                    'Significant': 'Yes' if p_val < 0.05 else 'No'
                })
    
    return pd.DataFrame(results)

# ============================================================================
# Table S1B: Platform Effect
# ============================================================================
def generate_platform_effect():
    """平台效应分析"""
    results = []
    
    for tool in TOOLS:
        ont_data = df[(df['tool'] == tool) & (df['platform'] == 'ONT')]['fusion_count']
        pacbio_data = df[(df['tool'] == tool) & (df['platform'] == 'PacBio')]['fusion_count']
        
        if len(ont_data) > 0 and len(pacbio_data) > 0:
            t_stat, p_val = ttest_ind(ont_data, pacbio_data)
            
            results.append({
                'Tool': tool,
                'ONT_Mean': f'{ont_data.mean():.1f}',
                'ONT_SD': f'{ont_data.std():.1f}',
                'PacBio_Mean': f'{pacbio_data.mean():.1f}',
                'PacBio_SD': f'{pacbio_data.std():.1f}',
                'T_Statistic': f'{t_stat:.2f}',
                'P_value': f'{p_val:.4f}',
                'Significant': 'Yes' if p_val < 0.05 else 'No'
            })
    
    return pd.DataFrame(results)

# ============================================================================
# Table S1C: Parameter Correlations
# ============================================================================
def generate_parameter_correlations():
    """参数相关性分析"""
    results = []
    
    for tool in TOOLS:
        tool_data = df[df['tool'] == tool]
        
        if len(tool_data) > 0:
            # 深度相关性
            if len(tool_data['depth'].unique()) > 1:
                corr_depth, p_depth = pearsonr(tool_data['depth'], tool_data['fusion_count'])
            else:
                corr_depth, p_depth = 0, 1
            
            # 一致性相关性
            if len(tool_data['identity'].unique()) > 1:
                corr_id, p_id = pearsonr(tool_data['identity'], tool_data['fusion_count'])
            else:
                corr_id, p_id = 0, 1
            
            # 读长相关性
            if len(tool_data['read_length'].unique()) > 1:
                corr_len, p_len = pearsonr(tool_data['read_length'], tool_data['fusion_count'])
            else:
                corr_len, p_len = 0, 1
            
            results.append({
                'Tool': tool,
                'Depth_Corr': f'{corr_depth:.3f}',
                'Depth_P': f'{p_depth:.4f}',
                'Identity_Corr': f'{corr_id:.3f}',
                'Identity_P': f'{p_id:.4f}',
                'ReadLength_Corr': f'{corr_len:.3f}',
                'ReadLength_P': f'{p_len:.4f}'
            })
    
    return pd.DataFrame(results)

# ============================================================================
# Table S1D: Summary Statistics
# ============================================================================
def generate_summary_stats():
    """汇总统计"""
    results = []
    
    for tool in TOOLS:
        tool_data = df[df['tool'] == tool]
        
        if len(tool_data) > 0:
            results.append({
                'Tool': tool,
                'N_Datasets': len(tool_data),
                'Mean_Fusions': f'{tool_data["fusion_count"].mean():.1f}',
                'Median_Fusions': f'{tool_data["fusion_count"].median():.1f}',
                'SD_Fusions': f'{tool_data["fusion_count"].std():.1f}',
                'Min_Fusions': int(tool_data["fusion_count"].min()),
                'Max_Fusions': int(tool_data["fusion_count"].max()),
                'CV': f'{tool_data["fusion_count"].std() / tool_data["fusion_count"].mean():.2f}',
                'Mean_Runtime': f'{tool_data["runtime_minutes"].mean():.1f}',
                'Mean_Memory': f'{tool_data["memory_gb"].mean():.1f}'
            })
    
    return pd.DataFrame(results)

# ============================================================================
# 主函数
# ============================================================================
def main():
    print("="*80)
    print("Generating Table S1: Statistical Analysis")
    print("="*80)
    
    # Table S1A: Tool Comparison
    print("\n[1/4] Generating tool comparison statistics...")
    tool_comp = generate_tool_comparison()
    tool_comp.to_csv(OUTPUT_DIR / 'TableS1A_tool_comparison.csv', index=False)
    print(f"  ✓ Saved {len(tool_comp)} comparisons")
    
    # Table S1B: Platform Effect
    print("\n[2/4] Analyzing platform effects...")
    platform_eff = generate_platform_effect()
    platform_eff.to_csv(OUTPUT_DIR / 'TableS1B_platform_effect.csv', index=False)
    print(f"  ✓ Analyzed {len(platform_eff)} tools")
    
    # Table S1C: Parameter Correlations
    print("\n[3/4] Computing parameter correlations...")
    param_corr = generate_parameter_correlations()
    param_corr.to_csv(OUTPUT_DIR / 'TableS1C_parameter_correlations.csv', index=False)
    print(f"  ✓ Computed correlations for {len(param_corr)} tools")
    
    # Table S1D: Summary Statistics
    print("\n[4/4] Generating summary statistics...")
    summary_stats = generate_summary_stats()
    summary_stats.to_csv(OUTPUT_DIR / 'TableS1D_summary_statistics.csv', index=False)
    print(f"  ✓ Summarized {len(summary_stats)} tools")
    
    print("\n" + "="*80)
    print("Table S1 Components Generated Successfully!")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_DIR / 'TableS1A_tool_comparison.csv'}")
    print(f"  - {OUTPUT_DIR / 'TableS1B_platform_effect.csv'}")
    print(f"  - {OUTPUT_DIR / 'TableS1C_parameter_correlations.csv'}")
    print(f"  - {OUTPUT_DIR / 'TableS1D_summary_statistics.csv'}")
    
    # 显示关键结果
    print("\n" + "="*80)
    print("Key Findings:")
    print("="*80)
    print("\n1. Tool Performance Summary:")
    print(summary_stats[['Tool', 'Mean_Fusions', 'SD_Fusions', 'CV']].to_string(index=False))
    
    print("\n2. Platform Effect (significant differences):")
    sig_platform = platform_eff[platform_eff['Significant'] == 'Yes']
    if len(sig_platform) > 0:
        print(sig_platform[['Tool', 'ONT_Mean', 'PacBio_Mean', 'P_value']].to_string(index=False))
    else:
        print("  No significant platform effects detected")
    
    print("\n3. Parameter Correlations (|r| > 0.3):")
    for _, row in param_corr.iterrows():
        if abs(float(row['Depth_Corr'])) > 0.3:
            print(f"  {row['Tool']}: Depth correlation = {row['Depth_Corr']} (p={row['Depth_P']})")
        if abs(float(row['Identity_Corr'])) > 0.3:
            print(f"  {row['Tool']}: Identity correlation = {row['Identity_Corr']} (p={row['Identity_P']})")

if __name__ == '__main__':
    main()
