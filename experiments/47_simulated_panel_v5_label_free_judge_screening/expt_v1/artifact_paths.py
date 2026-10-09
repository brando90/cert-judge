"""Locate relocated owned bytes without rewriting frozen historical path fields."""
from pathlib import Path
from e47_adapter import ROOT

ORIGINAL_ROOT=Path('/dfs/scratch0/brando9/cert-judge-e47-v5-sandbox/experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1')

def local_path(recorded):
    path=Path(recorded)
    if '..' in path.parts:raise ValueError('parent traversal in recorded artifact path')
    return ROOT/path.relative_to(ORIGINAL_ROOT) if path.is_relative_to(ORIGINAL_ROOT) else path

def historical_path(actual):
    path=Path(actual)
    if '..' in path.parts:raise ValueError('parent traversal in artifact origin path')
    return str(ORIGINAL_ROOT/path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
