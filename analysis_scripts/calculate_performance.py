#!/usr/bin/env python3
"""
计算模拟数据真实性能指标（改进版）
使用完整的ground truth集合，不考虑sample字段
"""

import os
import csv
import glob
import re
from collections import defaultdict
import numpy as np

# ============================================================================
# 配置
# ============================================================================
BASE_DIR = "/data6/mark/Project/chimericRNA_detection/datasets_and_results"
GROUND_TRUTH_DIR = "/data6/mark/Project/chimericRNA_detection/datasets/simulated_data/PBSIM3_PacBio_n_ONT_simulated_fusion_reads.Feb2024"
OUTPUT_DIR = "/data6/mark/Project/chimericRNA_detection/datasets_and_results/script/sim_data"

# Ground truth文件
ONT_TRUTH_FILE = os.path.join(GROUND_TRUTH_DIR, "ONT_pbsim3/ont_fusion_brkpt_truth_set.tsv")
PACBIO_TRUTH_FILE = os.path.join(GROUND_TRUTH_DIR, "PacBio_pbsim3/pbsim3_wreps.truthset.rep1.TSV")

# 工具配置
TOOLS_CONFIG = {
    'CTAT-LR-Fusion': {
        'file_pattern': '**/ctat-LR-fusion.fusion_predictions.tsv',
        'delimiter': '\t',
        'has_header': True,
        'fusion_col': '#FusionName'
    },
    'JAFFAL': {
        'file_pattern': '**/jaffa_results.csv',
        'delimiter': ',',
        'has_header': True,
        'fusion_col': 'fusion genes'
    },
    'LongGF': {
        'file_pattern': '**/Genefusion_result.csv',
        'delimiter': None,  # 特殊处理
        'has_header': False,
        'fusion_col': None
    },
    'genion': {
        'file_pattern': '**/fusion_detection_results.tsv',
        'delimiter': '\t',
        'has_header': True,
        'fusion_col': None  # 需要从两列拼接
    },
    'pbfusion': {
        'file_pattern': '**/pbfusion.breakpoints.groups.bed',
        'delimiter': '\t',
        'has_header': False,
        'fusion_col': None  # 从INFO列提取
    },
    'FusionSeeker': {
        'file_pattern': '**/FusionSeeker_res.txt',
        'delimiter': '\t',
        'has_header': True,
        'fusion_col': 'FusionGene'
    },
    'IFDlong': {
        'file_pattern': '**/*_fusion_report.txt',
        'delimiter': '\t',
        'has_header': True,
        'fusion_col': 'Fusion'
    },
    'FLAIR_fusion': {
        'file_pattern': '**/*fusion*.bed',
        'delimiter': '\t',
        'has_header': False,
        'fusion_col': 3  # BED第4列
    }
}

# ============================================================================
# Ground Truth加载
# ============================================================================
def load_ground_truth(platform):
    """加载ground truth，返回所有融合的set（不考虑sample）"""
    truth_file = ONT_TRUTH_FILE if platform == 'ONT' else PACBIO_TRUTH_FILE
    
    ground_truth = set()
    with open(truth_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            fusion_name = row['FusionName']
            # 标准化：GENE1--GENE2，按字母顺序
            genes = fusion_name.split('--')
            if len(genes) == 2:
                normalized = '--'.join(sorted(genes))
                ground_truth.add(normalized)
    
    print(f"Loaded {len(ground_truth)} unique fusions for {platform}")
    return ground_truth


def normalize_fusion(fusion_str):
    """标准化融合名称"""
    fusion_str = fusion_str.strip()
    
    # 处理不同分隔符
    for sep in ['--', ':', '_', '|']:
        if sep in fusion_str:
            parts = fusion_str.split(sep)
            break
    else:
        # 尝试单横线
        if '-' in fusion_str and fusion_str.count('-') >= 1:
            parts = fusion_str.split('-')
        else:
            return None
    
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        # 按字母顺序排序（不考虑方向）
        return '--'.join(sorted(parts[:2]))
    
    return None


# ============================================================================
# 工具输出解析
# ============================================================================
def parse_longGF_output(filepath):
    """特殊处理LongGF输出"""
    fusions = set()
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('GF') or line.startswith('SumGF'):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        # 格式: GF GENE1:GENE2 ...
                        fusion_str = parts[1]
                        normalized = normalize_fusion(fusion_str)
                        if normalized:
                            fusions.add(normalized)
    except:
        pass
    return fusions


def parse_pbfusion_output(filepath):
    """特殊处理pbfusion BED输出"""
    fusions = set()
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                cols = line.strip().split('\t')
                if len(cols) > 10:
                    # 从INFO列提取GN字段
                    info = cols[10]
                    for field in info.split(';'):
                        if field.startswith('GN='):
                            genes_str = field[3:]
                            genes = genes_str.split(',')
                            if len(genes) >= 2:
                                normalized = normalize_fusion(f"{genes[0]}--{genes[1]}")
                                if normalized:
                                    fusions.add(normalized)
                            break
    except:
        pass
    return fusions


def parse_genion_output(filepath):
    """特殊处理genion输出（从两列拼接）"""
    fusions = set()
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                gene1 = row.get('Gene1', row.get('gene1', ''))
                gene2 = row.get('Gene2', row.get('gene2', ''))
                if gene1 and gene2:
                    normalized = normalize_fusion(f"{gene1}--{gene2}")
                    if normalized:
                        fusions.add(normalized)
    except:
        pass
    return fusions


def parse_tool_output(dataset_dir, tool_name, ground_truth):
    """解析工具输出并计算TP/FP/FN"""
    config = TOOLS_CONFIG[tool_name]
    tool_dir = os.path.join(dataset_dir, tool_name)
    
    if not os.path.exists(tool_dir):
        return None
    
    # 查找输出文件
    pattern = os.path.join(tool_dir, config['file_pattern'])
    files = glob.glob(pattern, recursive=True)
    
    if not files:
        return None
    
    output_file = files[0]
    
    # 解析输出
    predictions = set()
    
    # 特殊处理
    if tool_name == 'LongGF':
        predictions = parse_longGF_output(output_file)
    elif tool_name == 'pbfusion':
        predictions = parse_pbfusion_output(output_file)
    elif tool_name == 'genion':
        predictions = parse_genion_output(output_file)
    else:
        # 标准CSV/TSV处理
        try:
            with open(output_file, 'r') as f:
                if config['has_header']:
                    reader = csv.DictReader(f, delimiter=config['delimiter'])
                    for row in reader:
                        fusion = row.get(config['fusion_col'], '')
                        normalized = normalize_fusion(fusion)
                        if normalized:
                            predictions.add(normalized)
                else:
                    # 无表头，按索引
                    for line in f:
                        if line.startswith('#'):
                            continue
                        cols = line.strip().split(config['delimiter'])
                        if len(cols) > config['fusion_col']:
                            fusion = cols[config['fusion_col']]
                            normalized = normalize_fusion(fusion)
                            if normalized:
                                predictions.add(normalized)
        except:
            return None
    
    # 计算指标
    tp = len(ground_truth & predictions)
    fp = len(predictions - ground_truth)
    fn = len(ground_truth - predictions)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'TP': tp,
        'FP': fp,
        'FN': fn,
        'Precision': round(precision, 4),
        'Recall': round(recall, 4),
        'F1': round(f1, 4),
        'Total_Predictions': len(predictions)
    }


# ============================================================================
# 主处理流程
# ============================================================================
def process_all_datasets():
    """处理所有模拟数据集"""
    results = []
    
    simulated_dirs = [
        os.path.join(BASE_DIR, 'simulated_data'),
        os.path.join(BASE_DIR, 'simulated_data_cpu25')
    ]
    
    for sim_dir in simulated_dirs:
        if not os.path.exists(sim_dir):
            continue
        
        for dataset_name in sorted(os.listdir(sim_dir)):
            dataset_path = os.path.join(sim_dir, dataset_name)
            if not os.path.isdir(dataset_path):
                continue
            
            # 解析数据集参数
            params = parse_dataset_name(dataset_name)
            if not params:
                continue
            
            print(f"\nProcessing {dataset_name}...")
            
            # 加载ground truth
            platform = params['platform']
            ground_truth = load_ground_truth(platform)
            
            # 处理每个工具
            for tool_name in TOOLS_CONFIG.keys():
                metrics = parse_tool_output(dataset_path, tool_name, ground_truth)
                
                if metrics is None:
                    print(f"  {tool_name}: No output found")
                    continue
                
                print(f"  {tool_name}: P={metrics['Precision']:.3f}, R={metrics['Recall']:.3f}, F1={metrics['F1']:.3f}")
                
                result = {
                    'dataset': dataset_name,
                    'platform': params['seq_platform'],
                    'depth': params['depth'],
                    'identity': params['identity'],
                    'read_length': params['read_length'],
                    'tool': tool_name,
                    **metrics
                }
                results.append(result)
    
    return results


def parse_dataset_name(dataset_name):
    """解析数据集名称"""
    pattern = r'(nanopore|pacbio)(\d+)_(\d+x)_(\d+\.\d+)_(\d+)'
    match = re.match(pattern, dataset_name)
    
    if not match:
        return None
    
    platform_type, year, depth, identity, read_length = match.groups()
    seq_platform = 'ONT' if platform_type == 'nanopore' else 'PacBio'
    
    return {
        'platform': seq_platform,
        'seq_platform': f"{platform_type}{year}",
        'depth': depth,
        'identity': identity,
        'read_length': read_length
    }


def save_results(results):
    """保存结果"""
    output_file = os.path.join(OUTPUT_DIR, 'tables/performance_metrics.csv')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    fieldnames = ['dataset', 'platform', 'depth', 'identity', 'read_length', 'tool',
                  'TP', 'FP', 'FN', 'Precision', 'Recall', 'F1', 'Total_Predictions']
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Saved {len(results)} records to {output_file}")
    
    # 统计摘要
    print("\n" + "="*80)
    print("Performance Summary:")
    print("="*80)
    
    tool_stats = defaultdict(list)
    for r in results:
        tool_stats[r['tool']].append(r['F1'])
    
    print(f"{'Tool':<20} {'Mean F1':<10} {'Max F1':<10} {'Records':<10}")
    print("-"*50)
    for tool in sorted(tool_stats.keys()):
        f1_scores = tool_stats[tool]
        print(f"{tool:<20} {np.mean(f1_scores):<10.4f} {np.max(f1_scores):<10.4f} {len(f1_scores):<10}")


# ============================================================================
# 主函数
# ============================================================================
def main():
    print("="*80)
    print("Calculating True Performance Metrics (Improved)")
    print("="*80)
    
    results = process_all_datasets()
    save_results(results)


if __name__ == '__main__':
    main()
