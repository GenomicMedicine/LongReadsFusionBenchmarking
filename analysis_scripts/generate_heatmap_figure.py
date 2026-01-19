#!/usr/bin/env python3
"""
生成高品质的Heatmap科研图
显示不同平台、细胞系和方法的融合检测性能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import os

# 全局字体和样式设置
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Liberation Sans', 'DejaVu Sans']
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.5

OUTPUT_DIR = "/data6/mark/Project/chimericRNA_detection/datasets_and_results/real_data/r1"

# 方法顺序（按性能排序）
METHODS_ORDER = ['FusionSeeker', 'JAFFAL', 'CTAT-LR-Fusion', 'LongGF', 
                 'genion', 'pbfusion', 'IFDlong', 'FLAIR_fusion']


def prepare_heatmap_data(results_df, ground_truth_file):
    """准备heatmap数据"""
    
    # 加载真实值
    with open(ground_truth_file, 'r') as f:
        ground_truth = set(line.strip() for line in f if line.strip())
    
    # 创建两个数据结构：一个用于TP数量，一个用于命中率
    ont_tp_data = []
    ont_hitrate_data = []
    pacbio_tp_data = []
    pacbio_hitrate_data = []
    
    # 处理ONT平台数据
    ont_data = results_df[results_df['Platform'] == 'ONT']
    
    # 获取所有细胞系-库类型组合
    ont_cellline_lib = []
    for _, row in ont_data.iterrows():
        cellline_lib = f"{row['CellLine']}-{row['LibraryType']}" if row['LibraryType'] != 'unknown' else row['CellLine']
        if cellline_lib not in ont_cellline_lib:
            ont_cellline_lib.append(cellline_lib)
    
    # 为每个细胞系-库类型组合创建数据
    for cl_lib in ont_cellline_lib:
        if '-' in cl_lib:
            cl, lib = cl_lib.rsplit('-', 1)
        else:
            cl, lib = cl_lib, 'unknown'
        
        tp_row = []
        hr_row = []
        
        for method in METHODS_ORDER:
            # 查找该组合的数据
            mask = (ont_data['CellLine'] == cl) & \
                   (ont_data['LibraryType'] == lib) & \
                   (ont_data['Method'] == method)
            
            method_data = ont_data[mask]
            
            if len(method_data) > 0:
                tp = method_data['TP'].values[0]
                total_pred = method_data['TotalPredictions'].values[0]
                
                # 命中率 = TP / 真实值总数
                hitrate = tp / len(ground_truth) if len(ground_truth) > 0 else 0
                
                tp_row.append(tp)
                hr_row.append(hitrate * 100)  # 转换为百分比
            else:
                tp_row.append(0)
                hr_row.append(0)
        
        ont_tp_data.append(tp_row)
        ont_hitrate_data.append(hr_row)
    
    # 处理PacBio平台数据
    pacbio_data = results_df[results_df['Platform'] == 'PacBio']
    
    pacbio_celllines = pacbio_data['CellLine'].unique()
    
    for cellline in pacbio_celllines:
        tp_row = []
        hr_row = []
        
        for method in METHODS_ORDER:
            mask = (pacbio_data['CellLine'] == cellline) & \
                   (pacbio_data['Method'] == method)
            
            method_data = pacbio_data[mask]
            
            if len(method_data) > 0:
                tp = method_data['TP'].values[0]
                hitrate = tp / len(ground_truth) if len(ground_truth) > 0 else 0
                
                tp_row.append(tp)
                hr_row.append(hitrate * 100)
            else:
                tp_row.append(0)
                hr_row.append(0)
        
        pacbio_tp_data.append(tp_row)
        pacbio_hitrate_data.append(hr_row)
    
    # 转换为DataFrame
    ont_tp_df = pd.DataFrame(ont_tp_data, index=ont_cellline_lib, columns=METHODS_ORDER)
    ont_hr_df = pd.DataFrame(ont_hitrate_data, index=ont_cellline_lib, columns=METHODS_ORDER)
    
    pacbio_tp_df = pd.DataFrame(pacbio_tp_data, index=list(pacbio_celllines), columns=METHODS_ORDER)
    pacbio_hr_df = pd.DataFrame(pacbio_hitrate_data, index=list(pacbio_celllines), columns=METHODS_ORDER)
    
    return ont_tp_df, ont_hr_df, pacbio_tp_df, pacbio_hr_df


def plot_combined_heatmap(tp_df, hr_df, title, output_file):
    """
    绘制组合heatmap：颜色表示TP数量，数字表示命中率
    """
    
    fig, ax = plt.subplots(figsize=(16, max(10, len(tp_df) * 0.6)))
    
    # 创建颜色映射
    # 使用对数尺度以更好地展示差异
    tp_values = tp_df.values.flatten()
    max_tp = tp_values[tp_values > 0].max() if np.any(tp_values > 0) else 1
    
    # 使用YlOrRd配色方案（黄-橙-红）
    cmap = plt.cm.YlOrRd
    
    # 绘制每个单元格
    for i in range(len(tp_df)):
        for j in range(len(tp_df.columns)):
            tp = tp_df.iloc[i, j]
            hr = hr_df.iloc[i, j]
            
            # 计算颜色（使用对数尺度）
            if tp > 0:
                # 对数尺度归一化
                norm_value = np.log10(tp + 1) / np.log10(max_tp + 1)
                color = cmap(norm_value)
            else:
                color = 'white'
            
            # 绘制矩形
            rect = Rectangle((j, i), 1, 1, facecolor=color, 
                           edgecolor='black', linewidth=1.5)
            ax.add_patch(rect)
            
            # 添加文本：上半部分显示TP数量，下半部分显示命中率
            if tp > 0:
                # TP数量（加粗）
                ax.text(j + 0.5, i + 0.7, f'{int(tp)}',
                       ha='center', va='center', 
                       fontsize=10, fontweight='bold',
                       color='black' if norm_value < 0.7 else 'white')
                
                # 命中率（小字）
                ax.text(j + 0.5, i + 0.3, f'{hr:.2f}%',
                       ha='center', va='center', 
                       fontsize=8,
                       color='black' if norm_value < 0.7 else 'white')
    
    # 设置坐标轴
    ax.set_xlim(0, len(tp_df.columns))
    ax.set_ylim(0, len(tp_df))
    
    ax.set_xticks(np.arange(len(tp_df.columns)) + 0.5)
    ax.set_xticklabels(tp_df.columns, rotation=45, ha='right', fontsize=14, fontweight='bold')
    
    ax.set_yticks(np.arange(len(tp_df)) + 0.5)
    ax.set_yticklabels(tp_df.index, fontsize=12)
    
    ax.set_xlabel('Detection Method', fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel('Cell Line - Library Type', fontsize=16, fontweight='bold', labelpad=10)
    
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    
    # 反转y轴使第一行在顶部
    ax.invert_yaxis()
    
    # 添加colorbar图例
    sm = plt.cm.ScalarMappable(cmap=cmap, 
                               norm=plt.Normalize(vmin=0, vmax=np.log10(max_tp + 1)))
    sm.set_array([])
    
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('True Positives (log scale)', fontsize=14, fontweight='bold')
    
    # 设置colorbar的刻度为实际TP值
    tick_positions = np.linspace(0, np.log10(max_tp + 1), 5)
    tick_labels = [f'{int(10**x - 1)}' if x > 0 else '0' for x in tick_positions]
    cbar.set_ticks(tick_positions)
    cbar.set_ticklabels(tick_labels, fontsize=12)
    
    # 添加说明文字
    ax.text(0.02, -0.08, 
           'Bold number: True Positive count | Small text: Hit rate (%)',
           transform=ax.transAxes, fontsize=11, 
           style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.savefig(output_file.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 保存到: {output_file}")


def plot_simple_heatmap(tp_df, title, output_file):
    """
    绘制简洁版heatmap：只显示TP数量
    适用于PacBio等数据较少的情况
    """
    
    fig, ax = plt.subplots(figsize=(14, max(6, len(tp_df) * 0.8)))
    
    # 使用seaborn绘制
    sns.heatmap(tp_df, annot=True, fmt='g', cmap='YlOrRd',
               cbar_kws={'label': 'True Positives'},
               linewidths=2, linecolor='black',
               square=False, ax=ax,
               annot_kws={'fontsize': 14, 'fontweight': 'bold'})
    
    ax.set_xlabel('Detection Method', fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel('Cell Line', fontsize=16, fontweight='bold', labelpad=10)
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    
    # 调整刻度标签
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=14, fontweight='bold')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=14)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.savefig(output_file.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 保存到: {output_file}")


def main():
    print("="*80)
    print("生成高品质Heatmap科研图")
    print("="*80)
    
    # 加载数据
    results_file = os.path.join(OUTPUT_DIR, 'detailed_results_summary.csv')
    ground_truth_file = os.path.join(OUTPUT_DIR, 'ground_truth_union.txt')
    
    results_df = pd.read_csv(results_file)
    print(f"\n加载结果: {len(results_df)} 条记录")
    
    # 准备heatmap数据
    print("\n准备heatmap数据...")
    ont_tp_df, ont_hr_df, pacbio_tp_df, pacbio_hr_df = prepare_heatmap_data(
        results_df, ground_truth_file)
    
    print(f"  ONT平台: {len(ont_tp_df)} 个细胞系-库类型组合")
    print(f"  PacBio平台: {len(pacbio_tp_df)} 个细胞系")
    
    # 生成图表
    print("\n生成图表...")
    
    # Figure 1: ONT平台 - 组合heatmap（TP数量+命中率）
    plot_combined_heatmap(
        ont_tp_df, ont_hr_df,
        'Fusion Detection Performance - ONT Platform',
        os.path.join(OUTPUT_DIR, 'Figure_Heatmap_ONT_combined.pdf')
    )
    
    # Figure 2: PacBio平台 - 简洁heatmap（只显示TP）
    plot_simple_heatmap(
        pacbio_tp_df,
        'Fusion Detection Performance - PacBio Platform',
        os.path.join(OUTPUT_DIR, 'Figure_Heatmap_PacBio.pdf')
    )
    
    # 生成统计报告
    print("\n" + "="*80)
    print("统计摘要")
    print("="*80)
    
    print("\nONT平台:")
    print(f"  总细胞系-库类型组合: {len(ont_tp_df)}")
    print(f"  最高TP数: {ont_tp_df.max().max()}")
    print(f"  最高命中率: {ont_hr_df.max().max():.2f}%")
    print(f"\n  各方法平均TP:")
    for method in METHODS_ORDER:
        avg_tp = ont_tp_df[method].mean()
        print(f"    {method:<20}: {avg_tp:>6.1f}")
    
    print("\nPacBio平台:")
    print(f"  总细胞系: {len(pacbio_tp_df)}")
    print(f"  最高TP数: {pacbio_tp_df.max().max()}")
    print(f"  最高命中率: {pacbio_hr_df.max().max():.2f}%")
    print(f"\n  各方法平均TP:")
    for method in METHODS_ORDER:
        avg_tp = pacbio_tp_df[method].mean()
        print(f"    {method:<20}: {avg_tp:>6.1f}")
    
    print("\n" + "="*80)
    print("所有图表生成完成！")
    print("="*80)
    print("\n生成的文件:")
    print("  - Figure_Heatmap_ONT_combined.pdf/png")
    print("  - Figure_Heatmap_PacBio.pdf/png")


if __name__ == '__main__':
    main()
