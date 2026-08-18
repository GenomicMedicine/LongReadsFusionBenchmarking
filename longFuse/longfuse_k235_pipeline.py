#!/usr/bin/env python3
"""
LongFuse universal pipeline.

Two execution modes:
1) denovo: run upstream callers first, then integrate with LongFuse k2/k3/k5.
2) kickstart: directly ingest existing caller result files and integrate.

Paper benchmark default for real-data evaluation: consensus threshold K=4 (>=4/8 callers).
See longFuse/README.md "Recommended default (paper benchmark)".
"""

from __future__ import annotations

import argparse
import yaml
import json
import math
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import pandas as pd


DEFAULT_REAL_CONSENSUS_K = 4  # paper default: >=4/8 callers on real-data P/R evaluation

DEFAULT_K_CONFIGS: Dict[int, Dict[str, object]] = {
    2: {
        "scheme_name": "LongFuse_k2",
        "combo": ["JAFFAL", "LongGF"],
        "min_methods": 2,
        "max_methods": 2,
        "consensus_fraction": 1.0,
        "high_support_threshold": 0.65,
        "rescue_support_threshold": 0.80,
    },
    3: {
        "scheme_name": "LongFuse_k3",
        "combo": ["FLAIR-fusion", "JAFFAL", "LongGF"],
        "min_methods": 2,
        "max_methods": 3,
        "consensus_fraction": 2.0 / 3.0,
        "high_support_threshold": 0.55,
        "rescue_support_threshold": 0.75,
    },
    5: {
        "scheme_name": "LongFuse_k5",
        "combo": ["CTAT-LR-Fusion", "FLAIR-fusion", "JAFFAL", "LongGF", "genion"],
        "min_methods": 2,
        "max_methods": 5,
        "consensus_fraction": 2.0 / 3.0,
        "high_support_threshold": 0.50,
        "rescue_support_threshold": 0.70,
    },
}

METHOD_PATTERNS = {
    "CTAT-LR-Fusion": ["ctat"],
    "JAFFAL": ["jaffal"],
    "LongGF": ["longgf"],
    "FLAIR-fusion": ["flair"],
    "FusionSeeker": ["fusionseeker"],
    "pbfusion": ["pbfusion"],
    "IFDlong": ["ifdlong"],
    "genion": ["genion"],
}

GENE1_CANDIDATES = ["gene1", "gene_1", "geneA", "GeneA", "LeftGene", "gene_left"]
GENE2_CANDIDATES = ["gene2", "gene_2", "geneB", "GeneB", "RightGene", "gene_right"]
FUSION_CANDIDATES = ["fusion", "fusion_name", "fusion_gene", "fusion_pair"]
SUPPORT_CANDIDATES = ["support_reads", "junction_reads", "support", "count", "read_count"]
BP1_CANDIDATES = ["breakpoint1", "bp1", "left_breakpoint", "pos1", "start1"]
BP2_CANDIDATES = ["breakpoint2", "bp2", "right_breakpoint", "pos2", "start2"]


def safe_int(value: object) -> Optional[int]:
    try:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(float(str(value).strip()))
    except Exception:
        match = re.search(r"(\d+)", str(value))
        return int(match.group(1)) if match else None


def normalize_fusion_string(value: str) -> Optional[str]:
    text = str(value).strip()
    if not text:
        return None
    parts = re.split(r"--|::|:|&|/", text)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) < 2:
        return None
    a, b = sorted([parts[0], parts[1]])
    return f"{a}--{b}"


def fusion_key(gene1: str, gene2: str) -> str:
    a, b = sorted([str(gene1).strip(), str(gene2).strip()])
    return f"{a}--{b}"


def pick_column(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    lookup = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    return None


def detect_method_from_path(path: Path) -> Optional[str]:
    text = path.as_posix().lower()
    for method, keys in METHOD_PATTERNS.items():
        if any(k in text for k in keys):
            return method
    return None


def load_curated_fusion_keys(known_file: Optional[Path]) -> Set[str]:
    if known_file is None or not known_file.exists():
        return set()
    curated = pd.read_csv(known_file)
    if "fusion" not in curated.columns:
        return set()
    keys: Set[str] = set()
    for value in curated["fusion"].dropna().tolist():
        norm = normalize_fusion_string(str(value))
        if norm:
            keys.add(norm.upper())
    return keys


def load_truth_keys(gt_file: Optional[Path]) -> Set[str]:
    if gt_file is None or not gt_file.exists():
        return set()
    gt_df = pd.read_csv(gt_file, sep="\t")
    required = {"ensembl_id1", "ensembl_id2"}
    if not required.issubset(set(gt_df.columns)):
        return set()
    return set(
        gt_df.apply(
            lambda row: fusion_key(str(row["ensembl_id1"]).split(".")[0], str(row["ensembl_id2"]).split(".")[0]),
            axis=1,
        ).tolist()
    )


def build_ensembl_symbol_map(mapping_file: Optional[Path]) -> Dict[str, str]:
    if mapping_file is None or not mapping_file.exists():
        return {}
    df = pd.read_csv(mapping_file, sep="\t")
    if not {"ensembl_id", "gene_symbol"}.issubset(set(df.columns)):
        return {}
    out: Dict[str, str] = {}
    for _, row in df.iterrows():
        ens = str(row["ensembl_id"]).split(".")[0].strip()
        symbol = str(row["gene_symbol"]).strip()
        if ens and symbol:
            out[ens] = symbol
    return out


def to_symbol(gene: str, ens_to_symbol: Dict[str, str]) -> str:
    g = str(gene).split(".")[0].strip()
    if g.startswith("ENSG"):
        return ens_to_symbol.get(g, g)
    return g


def binary_metrics(predicted: Set[str], truth: Set[str]) -> Dict[str, float]:
    tp = len(predicted.intersection(truth))
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return {"tp": float(tp), "fp": float(fp), "fn": float(fn), "precision": p, "recall": r, "f1": f1}


def parse_method_result_file(
    file_path: Path,
    dataset_id: Optional[str],
    cohort: str,
    forced_method: Optional[str] = None,
) -> pd.DataFrame:
    sep = "\t" if file_path.suffix.lower() in {".tsv", ".txt"} else ","
    df = pd.read_csv(file_path, sep=sep)
    if df.empty:
        return pd.DataFrame()

    method = forced_method or detect_method_from_path(file_path)
    method_col = pick_column(df, ["method", "caller"])
    if method_col is not None:
        method = str(df.iloc[0][method_col]).strip() or method
    if method is None:
        raise ValueError(f"Cannot detect method for file: {file_path}")

    dataset = dataset_id or file_path.parent.name
    dataset_col = pick_column(df, ["dataset_id", "sample", "sample_id"])
    if dataset_col is not None:
        dataset = str(df.iloc[0][dataset_col]).strip() or dataset

    g1_col = pick_column(df, GENE1_CANDIDATES)
    g2_col = pick_column(df, GENE2_CANDIDATES)
    fusion_col = pick_column(df, FUSION_CANDIDATES)
    support_col = pick_column(df, SUPPORT_CANDIDATES)
    bp1_col = pick_column(df, BP1_CANDIDATES)
    bp2_col = pick_column(df, BP2_CANDIDATES)

    rows: List[Dict[str, object]] = []
    for _, row in df.iterrows():
        if g1_col and g2_col:
            g1 = str(row[g1_col]).strip()
            g2 = str(row[g2_col]).strip()
        elif fusion_col:
            norm = normalize_fusion_string(str(row[fusion_col]))
            if norm is None:
                continue
            g1, g2 = norm.split("--", 1)
        else:
            continue

        if not g1 or not g2 or g1.lower() == "nan" or g2.lower() == "nan":
            continue
        rows.append(
            {
                "dataset_id": dataset,
                "cohort": cohort,
                "method": method,
                "gene1": g1,
                "gene2": g2,
                "support_reads": float(row[support_col]) if support_col and pd.notna(row[support_col]) else 1.0,
                "breakpoint_left": safe_int(row[bp1_col]) if bp1_col else None,
                "breakpoint_right": safe_int(row[bp2_col]) if bp2_col else None,
                "source_file": str(file_path),
            }
        )

    return pd.DataFrame(rows)


def discover_method_result_files(root: Path) -> List[Path]:
    files = []
    for pattern in ("**/*.csv", "**/*.tsv", "**/*.txt"):
        files.extend(root.glob(pattern))
    return sorted(set([f for f in files if f.is_file()]))


def ensure_calls_schema(df: pd.DataFrame) -> pd.DataFrame:
    required = {"dataset_id", "method", "gene1", "gene2"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input calls table missing required columns: {sorted(missing)}")
    out = df.copy()
    if "support_reads" not in out.columns:
        out["support_reads"] = 1.0
    out["support_reads"] = pd.to_numeric(out["support_reads"], errors="coerce").fillna(1.0)
    if "breakpoint_left" not in out.columns:
        out["breakpoint_left"] = None
    if "breakpoint_right" not in out.columns:
        out["breakpoint_right"] = None
    out["fusion_key"] = out.apply(lambda r: fusion_key(str(r["gene1"]), str(r["gene2"])), axis=1)
    out["relative_support"] = out.groupby(["dataset_id", "method"])["support_reads"].rank(pct=True)
    return out


def aggregate_candidates(
    calls_df: pd.DataFrame,
    curated_keys: Set[str],
    ens_to_symbol: Dict[str, str],
    scheme_name: str,
    min_methods: int,
    max_methods: Optional[int],
    consensus_fraction: float,
    high_support_threshold: float,
    rescue_support_threshold: float,
    breakpoint_window_bp: int = 50,
) -> pd.DataFrame:
    if calls_df.empty:
        return pd.DataFrame()

    work_df = calls_df.copy()

    def event_merge_key(row: pd.Series) -> str:
        b1 = safe_int(row.get("breakpoint_left"))
        b2 = safe_int(row.get("breakpoint_right"))
        if b1 is None or b2 is None:
            return f"{row['fusion_key']}#bpNA"
        bin1 = int(round(float(b1) / float(max(1, breakpoint_window_bp))))
        bin2 = int(round(float(b2) / float(max(1, breakpoint_window_bp))))
        return f"{row['fusion_key']}#bp{bin1}:{bin2}"

    work_df["event_merge_key"] = work_df.apply(event_merge_key, axis=1)
    dataset_method_counts = calls_df.groupby("dataset_id")["method"].nunique().to_dict()

    precision_methods = {"CTAT-LR-Fusion", "JAFFAL", "FLAIR-fusion", "genion", "LongGF"}
    noisy_methods = {"pbfusion", "FusionSeeker", "IFDlong"}
    anchor_methods = {"CTAT-LR-Fusion", "JAFFAL", "IFDlong"}
    splice_methods = {"CTAT-LR-Fusion", "JAFFAL", "FLAIR-fusion"}

    rows: List[Dict[str, object]] = []
    for (dataset_id, merge_key), grp in work_df.groupby(["dataset_id", "event_merge_key"]):
        methods = sorted(set(grp["method"].astype(str).tolist()))
        method_set = set(methods)
        n_methods = len(method_set)
        available_methods = int(dataset_method_counts.get(dataset_id, n_methods))
        consensus_n = max(1, math.ceil(consensus_fraction * available_methods))
        eligible = n_methods >= min_methods and (max_methods is None or n_methods <= max_methods)

        g1 = str(grp.iloc[0]["gene1"])
        g2 = str(grp.iloc[0]["gene2"])
        sym_key = fusion_key(to_symbol(g1, ens_to_symbol), to_symbol(g2, ens_to_symbol)).upper()

        relative_median = float(grp["relative_support"].median())
        relative_max = float(grp["relative_support"].max())
        max_support = float(grp["support_reads"].max())
        curated_support = sym_key in curated_keys if curated_keys else False
        anchor_support = bool(method_set.intersection(anchor_methods)) and max_support >= 2
        transcript_plausible = bool(method_set.intersection(splice_methods)) and relative_max >= 0.4
        non_repetitive_proxy = bool(method_set.intersection(precision_methods))
        non_readthrough_proxy = not method_set.issubset(noisy_methods)
        caller_agreement = n_methods >= consensus_n
        orthogonal_evidence_count = sum(
            [
                1 if curated_support else 0,
                1 if anchor_support else 0,
                1 if transcript_plausible else 0,
                1 if non_repetitive_proxy else 0,
                1 if non_readthrough_proxy else 0,
            ]
        )
        negative_evidence_count = sum(
            [
                1 if (n_methods == 1 and max_support < 2 and relative_max < 0.2) else 0,
                1 if (n_methods == 1 and relative_max < 0.1) else 0,
                1 if ((not non_repetitive_proxy) and relative_max < 0.2 and max_support < 2) else 0,
                1 if ((not non_readthrough_proxy) and relative_max < 0.2) else 0,
            ]
        )
        hard_filter = negative_evidence_count >= 2
        high_conf = eligible and caller_agreement and (relative_median >= high_support_threshold) and (not hard_filter)
        rescue = (
            eligible
            and (not high_conf)
            and (not hard_filter)
            and (orthogonal_evidence_count >= 2)
            and (curated_support or n_methods >= min_methods or (max_support >= 5 and relative_max >= rescue_support_threshold))
        )
        if high_conf:
            tier = "high_confidence"
        elif rescue:
            tier = "rescue"
        elif hard_filter:
            tier = "filtered"
        else:
            tier = "low_confidence"
        rows.append(
            {
                "scheme": scheme_name,
                "dataset_id": dataset_id,
                "fusion_key": str(grp.iloc[0]["fusion_key"]),
                "event_merge_key": merge_key,
                "gene1": g1,
                "gene2": g2,
                "fusion_symbol_key": sym_key,
                "methods": "|".join(methods),
                "n_methods": n_methods,
                "available_methods": available_methods,
                "consensus_required": consensus_n,
                "max_support": max_support,
                "relative_support_median": relative_median,
                "relative_support_max": relative_max,
                "curated_support": curated_support,
                "hard_filter": hard_filter,
                "eligible_for_scheme": eligible,
                "tier": tier,
                "cohort": str(grp.iloc[0].get("cohort", "unknown")),
            }
        )

    return pd.DataFrame(rows)


def evaluate_simulated(agg_df: pd.DataFrame, truth_keys: Set[str]) -> Dict[str, float]:
    if agg_df.empty or not truth_keys:
        return {
            "sim_high_precision": 0.0,
            "sim_high_recall": 0.0,
            "sim_high_f1": 0.0,
            "sim_combined_precision": 0.0,
            "sim_combined_recall": 0.0,
            "sim_combined_f1": 0.0,
            "sim_datasets": float(agg_df["dataset_id"].nunique()) if not agg_df.empty else 0.0,
        }
    pooled = {"high": {"tp": 0.0, "fp": 0.0, "fn": 0.0}, "combined": {"tp": 0.0, "fp": 0.0, "fn": 0.0}}
    for _, grp in agg_df.groupby("dataset_id"):
        high = set(grp[grp["tier"] == "high_confidence"]["fusion_key"].tolist())
        combined = set(grp[grp["tier"].isin(["high_confidence", "rescue"])]["fusion_key"].tolist())
        for key, metric in [("high", binary_metrics(high, truth_keys)), ("combined", binary_metrics(combined, truth_keys))]:
            pooled[key]["tp"] += metric["tp"]
            pooled[key]["fp"] += metric["fp"]
            pooled[key]["fn"] += metric["fn"]

    def to_prf(counts: Dict[str, float]) -> Tuple[float, float, float]:
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        return p, r, f

    hp, hr, hf = to_prf(pooled["high"])
    cp, cr, cf = to_prf(pooled["combined"])
    return {
        "sim_high_precision": hp,
        "sim_high_recall": hr,
        "sim_high_f1": hf,
        "sim_combined_precision": cp,
        "sim_combined_recall": cr,
        "sim_combined_f1": cf,
        "sim_datasets": float(agg_df["dataset_id"].nunique()),
    }


def evaluate_real(agg_df: pd.DataFrame) -> Dict[str, float]:
    if agg_df.empty:
        return {
            "real_mean_combined_curated_hit_rate": 0.0,
            "real_global_precision_like": 0.0,
            "real_total_hits": 0.0,
            "real_total_calls": 0.0,
            "real_datasets": 0.0,
        }
    rates, total_hits, total_calls = [], 0.0, 0.0
    for _, grp in agg_df.groupby("dataset_id"):
        combined = grp[grp["tier"].isin(["high_confidence", "rescue"])]
        if combined.empty:
            rates.append(0.0)
            continue
        hit_rate = float(combined["curated_support"].mean())
        rates.append(hit_rate)
        total_hits += float(combined["curated_support"].sum())
        total_calls += float(len(combined))
    return {
        "real_mean_combined_curated_hit_rate": (sum(rates) / len(rates)) if rates else 0.0,
        "real_global_precision_like": (total_hits / total_calls) if total_calls else 0.0,
        "real_total_hits": total_hits,
        "real_total_calls": total_calls,
        "real_datasets": float(agg_df["dataset_id"].nunique()),
    }


def run_single_k(
    k: int,
    cfg: Dict[str, object],
    calls_df: pd.DataFrame,
    output_dir: Path,
    curated_keys: Set[str],
    ens_to_symbol: Dict[str, str],
    truth_keys: Set[str],
    breakpoint_window_bp: int,
) -> Dict[str, object]:
    methods = set(str(x) for x in cfg["combo"])
    sub = calls_df[calls_df["method"].isin(methods)].copy()
    sim_sub = sub[sub["cohort"] == "simulated"].copy()
    real_sub = sub[sub["cohort"] == "real"].copy()
    if sim_sub.empty:
        sim_sub = sub.copy()
    if real_sub.empty:
        real_sub = sub.copy()

    k_out = output_dir / f"k{k}"
    k_out.mkdir(parents=True, exist_ok=True)
    sim_agg = aggregate_candidates(
        sim_sub,
        curated_keys,
        ens_to_symbol,
        str(cfg["scheme_name"]),
        int(cfg["min_methods"]),
        int(cfg["max_methods"]),
        float(cfg["consensus_fraction"]),
        float(cfg["high_support_threshold"]),
        float(cfg["rescue_support_threshold"]),
        breakpoint_window_bp,
    )
    real_agg = aggregate_candidates(
        real_sub,
        curated_keys,
        ens_to_symbol,
        str(cfg["scheme_name"]),
        int(cfg["min_methods"]),
        int(cfg["max_methods"]),
        float(cfg["consensus_fraction"]),
        float(cfg["high_support_threshold"]),
        float(cfg["rescue_support_threshold"]),
        breakpoint_window_bp,
    )
    sim_agg.to_csv(k_out / "simulated_candidates.csv", index=False)
    real_agg.to_csv(k_out / "real_candidates.csv", index=False)
    sim_m = evaluate_simulated(sim_agg, truth_keys)
    real_m = evaluate_real(real_agg)
    score = 0.7 * float(sim_m["sim_combined_f1"]) + 0.3 * float(real_m["real_mean_combined_curated_hit_rate"])
    summary = {
        "k": k,
        "scheme_name": str(cfg["scheme_name"]),
        "combo": list(cfg["combo"]),
        "min_methods": int(cfg["min_methods"]),
        "max_methods": int(cfg["max_methods"]),
        "consensus_fraction": float(cfg["consensus_fraction"]),
        "high_support_threshold": float(cfg["high_support_threshold"]),
        "rescue_support_threshold": float(cfg["rescue_support_threshold"]),
        "selection_score_0.7simF1_0.3realHit": score,
        **sim_m,
        **real_m,
        "input_rows": int(len(sub)),
        "sim_output_rows": int(len(sim_agg)),
        "real_output_rows": int(len(real_agg)),
    }
    (k_out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def write_integrated(outputs: List[Dict[str, object]], output_dir: Path) -> None:
    if not outputs:
        raise RuntimeError("No k2/k3/k5 outputs were produced.")
    df = pd.DataFrame(outputs).sort_values("k")
    df.to_csv(output_dir / "k235_integrated_summary.csv", index=False)
    best = df.sort_values("selection_score_0.7simF1_0.3realHit", ascending=False).iloc[0]
    (output_dir / "k235_integrated_summary.json").write_text(
        json.dumps({"best_k": int(best["k"]), "results": df.to_dict(orient="records")}, indent=2), encoding="utf-8"
    )
    lines = ["# LongFuse k2/k3/k5 Integrated Report", "", "## Best k", f"- best_k: {int(best['k'])}", "", "## All k Results"]
    for _, row in df.iterrows():
        combo = "|".join(row["combo"]) if isinstance(row["combo"], list) else str(row["combo"])
        lines.append(
            f"- k={int(row['k'])}: combo={combo}, sim_f1={float(row['sim_combined_f1']):.4f}, "
            f"real_hit={float(row['real_mean_combined_curated_hit_rate']):.4f}, "
            f"score={float(row['selection_score_0.7simF1_0.3realHit']):.4f}"
        )
    (output_dir / "k235_integrated_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_k_pipeline(
    calls_df: pd.DataFrame,
    output_dir: Path,
    curated_file: Optional[Path],
    truth_file: Optional[Path],
    ensembl_map: Optional[Path],
    execution: str,
    workers: int,
    breakpoint_window_bp: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    calls_df = ensure_calls_schema(calls_df)
    curated = load_curated_fusion_keys(curated_file)
    truth = load_truth_keys(truth_file)
    ens_map = build_ensembl_symbol_map(ensembl_map)

    outputs: List[Dict[str, object]] = []
    if execution == "serial":
        for k, cfg in DEFAULT_K_CONFIGS.items():
            outputs.append(run_single_k(k, cfg, calls_df, output_dir, curated, ens_map, truth, breakpoint_window_bp))
    else:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(
                    run_single_k, k, cfg, calls_df, output_dir, curated, ens_map, truth, breakpoint_window_bp
                ): k
                for k, cfg in DEFAULT_K_CONFIGS.items()
            }
            for future in as_completed(futures):
                outputs.append(future.result())
    write_integrated(outputs, output_dir)


def parse_key_values(items: Optional[List[str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"Invalid KEY=VALUE format: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parse_method_file_assignments(items: Optional[List[str]]) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"Invalid METHOD=PATH format: {item}")
        method, path = item.split("=", 1)
        out[method.strip()] = Path(path.strip()).resolve()
    return out


def load_kickstart_calls(args: argparse.Namespace, output_dir: Path) -> pd.DataFrame:
    root = Path(args.method_results_root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"method-results-root does not exist: {root}")

    discovered = discover_method_result_files(root)
    forced = parse_method_file_assignments(args.method_file)
    files_to_read = list(discovered)
    for path in forced.values():
        if path not in files_to_read:
            files_to_read.append(path)

    rows = []
    detected_records = []
    for file_path in sorted(set(files_to_read)):
        forced_method = None
        for m, p in forced.items():
            if p == file_path:
                forced_method = m
        try:
            parsed = parse_method_result_file(file_path, args.dataset_id, args.cohort, forced_method=forced_method)
            if not parsed.empty:
                rows.append(parsed)
                detected_records.append(
                    {"file": str(file_path), "detected_method": str(parsed["method"].iloc[0]), "rows": int(len(parsed))}
                )
        except Exception:
            continue

    if not rows:
        raise RuntimeError("No valid method result files detected. Check file format and paths.")
    calls = pd.concat(rows, ignore_index=True)
    calls.to_csv(output_dir / "kickstart_normalized_calls.csv", index=False)
    pd.DataFrame(detected_records).to_csv(output_dir / "kickstart_detected_method_files.csv", index=False)
    return calls


def run_denovo(args: argparse.Namespace) -> None:
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    runner = Path(args.runner_script).resolve()
    if not runner.exists():
        raise FileNotFoundError(f"runner-script not found: {runner}")

    extra_env = os.environ.copy()
    extra_env.update(parse_key_values(args.caller_arg))
    if args.reference_root:
        extra_env["LONGFUSE_REFERENCE_ROOT"] = str(Path(args.reference_root).resolve())
    if args.callers:
        extra_env["LONGFUSE_CALLERS"] = ",".join(args.callers)

    caller_workspace = out_dir / "caller_workspace"
    caller_workspace.mkdir(parents=True, exist_ok=True)
    cmd = [str(runner), str(caller_workspace), args.reads, args.seq_type]
    cmd.extend(args.runner_extra_arg or [])
    subprocess.run(cmd, check=True, env=extra_env)

    kick = argparse.Namespace(
        method_results_root=str(caller_workspace),
        method_file=None,
        dataset_id=args.dataset_id,
        cohort="real",
        output_dir=str(out_dir),
        curated_fusions=args.curated_fusions,
        ground_truth=args.ground_truth,
        ensembl_map=args.ensembl_map,
        execution=args.execution,
        workers=args.workers,
        breakpoint_window_bp=args.breakpoint_window_bp,
    )
    calls = load_kickstart_calls(kick, out_dir)
    run_k_pipeline(
        calls,
        out_dir,
        Path(args.curated_fusions).resolve() if args.curated_fusions else None,
        Path(args.ground_truth).resolve() if args.ground_truth else None,
        Path(args.ensembl_map).resolve() if args.ensembl_map else None,
        args.execution,
        args.workers,
        args.breakpoint_window_bp,
    )


def run_kickstart(args: argparse.Namespace) -> None:
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    calls = load_kickstart_calls(args, out_dir)
    run_k_pipeline(
        calls,
        out_dir,
        Path(args.curated_fusions).resolve() if args.curated_fusions else None,
        Path(args.ground_truth).resolve() if args.ground_truth else None,
        Path(args.ensembl_map).resolve() if args.ensembl_map else None,
        args.execution,
        args.workers,
        args.breakpoint_window_bp,
    )


def add_common_integration_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-dir", required=True, help="Output directory for LongFuse integration results")
    parser.add_argument("--curated-fusions", default=None, help="Optional curated fusion CSV with a 'fusion' column")
    parser.add_argument("--ground-truth", default=None, help="Optional simulated truth TSV (ensembl_id1/ensembl_id2)")
    parser.add_argument("--ensembl-map", default=None, help="Optional Ensembl-to-symbol mapping TSV")
    parser.add_argument("--execution", default="serial", choices=["serial", "parallel"], help="Run k2/k3/k5 serially or in parallel")
    parser.add_argument("--workers", type=int, default=3, help="Worker count when --execution parallel")
    parser.add_argument("--breakpoint-window-bp", type=int, default=50, help="Breakpoint merge window size in base pairs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LongFuse universal pipeline (denovo + kickstart)")
    sub = parser.add_subparsers(dest="mode", required=True)

    denovo = sub.add_parser("denovo", help="Run callers from raw reads, then run LongFuse integration")
    denovo.add_argument("--config", help="Path to YAML/JSON configuration file")
    denovo.add_argument("--reads", required=False, help="Input reads file path passed to caller runner")
 required=True, help="Input reads file path passed to caller runner")
    
    denovo.add_argument("--seq-type", required=True, help="Sequencing type passed to caller runner, e.g. ONT_cDNA")
    denovo.add_argument("--runner-script", default="GFD_main.sh", help="Caller orchestration script path")
    denovo.add_argument("--runner-extra-arg", action="append", default=[], help="Extra argument appended to runner command (repeatable)")
    denovo.add_argument("--caller-arg", action="append", default=[], help="Pass-through env var to callers in KEY=VALUE format (repeatable)")
    denovo.add_argument("--callers", nargs="*", default=None, help="Optional caller subset; exported as LONGFUSE_CALLERS")
    denovo.add_argument("--reference-root", default=None, help="Optional reference root; exported as LONGFUSE_REFERENCE_ROOT")
    denovo.add_argument("--dataset-id", default=None, help="Optional dataset id override for parsed outputs")
    add_common_integration_args(denovo)

    kick = sub.add_parser("kickstart", help="Ingest existing caller result files and run LongFuse integration")
    kick.add_argument("--config", help="Path to YAML configuration file")
    kick.add_argument("--method-results-root", required=False, help="Root directory containing method result files")
 help="Root directory containing method result files")
    kick.add_argument(
        "--method-file",
        action="append",
        default=[],
        help="Optional explicit method result in METHOD=PATH format; use multiple times for multiple methods",
    )
    kick.add_argument("--dataset-id", default=None, help="Optional dataset id override")
    kick.add_argument("--cohort", default="real", choices=["real", "simulated", "mixed"], help="Cohort label when input files do not contain cohort column")
    add_common_integration_args(kick)
    return parser



def update_args_from_config(args: argparse.Namespace) -> None:
    if getattr(args, 'config', None):
        with open(args.config, 'r') as f:
            if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        for k, v in config.items():
            k_attr = k.replace('-', '_')
            if getattr(args, k_attr, None) is None or getattr(args, k_attr) == build_parser().get_default(k_attr) or getattr(args, k_attr) == []: 
                # Very simple override
                setattr(args, k_attr, v)

def main() -> None:

    args = build_parser().parse_args()
    update_args_from_config(args)
    if args.mode == "denovo":
        run_denovo(args)
    else:
        run_kickstart(args)
    print(f"LongFuse pipeline finished. Outputs: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
