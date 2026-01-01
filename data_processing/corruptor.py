from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import data.table_metadata as tmd
import math


@dataclass
class CorruptionReport:
    step: str
    applied: bool
    details: Dict[str, Any]

@dataclass
class CorruptionStep:
    name: str
    p_apply: float
    p_row: Optional[float]
    p_col: Optional[float]
    p_cell: Optional[float]
    table_name: str = ""

    def run(self, df: pd.DataFrame, rng: np.random.Generator) -> Tuple[pd.DataFrame, CorruptionReport]: ...

    def should_apply(self, rng: np.random.Generator) -> bool:
        return rng.random() < self.p_apply

    def set_table_name(self, table):
        self.table_name = table

class CorruptionChain:
    def __init__(self, steps: List[CorruptionStep], table_name: str = "", seed: Optional[int] = None):
        self.table_name = table_name
        self.steps = steps
        self.rng = np.random.default_rng(seed)

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[CorruptionReport]]:
        reports: List[CorruptionReport] = []
        out = df.copy()
        for step in self.steps:
            step.set_table_name(self.table_name)
            out, rep = step.run(out, self.rng)
            reports.append(rep)
        return out, reports

    def set_table_name(self, table):
        self.table_name = table

@dataclass
class DropRowsStep(CorruptionStep):
    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("DropRowsStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        mask_keep = rng.random(len(df)) >= self.p_row
        dropped = int((~mask_keep).sum())
        out = df.loc[mask_keep].reset_index(drop=True)

        return out, CorruptionReport(self.name, True, {"dropped_rows": dropped, "p_row": self.p_row})

@dataclass
class NegativeQtyStep(CorruptionStep):
    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("NegativeQtyStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        out = df.copy()
        cell_mask = rng.random((len(out), len(out.columns))) < self.p_cell
        affected_cells = {}
        negatable_columns = tmd.negatable_columns[self.table_name]

        for c, col in enumerate(negatable_columns):
            column_type = tmd.negatable_columns[self.table_name][col]
            out.loc[cell_mask[:, c], col] = -out.loc[cell_mask[:, c], col].abs()
            affected_cells[f"{col} {column_type}"] = out.loc[cell_mask[:, c], col]
        return out, CorruptionReport(self.name, True, {"affected_cells": affected_cells, "p_cell": self.p_cell})


def multiplicative_spike(rng, df, column_mask, column_name):
    col = df[column_name]
    q1 = col.quantile(0.25)
    q3 = col.quantile(0.75)
    iqr = q3 - q1
    print("-" * 100)
    print(f"Column Name: {column_name}")
    print(f"DF:  {df}")
    print(f"Column Mask: {column_mask}")
    print(f"Q1:  {q1}")
    print(f"Q3:  {q3}")
    print(f"IQR: {iqr}")
    # Extreme Tukey fences for global outliers
    lower = q1 - 3.0 * iqr
    upper = q3 + 3.0 * iqr
    # Negative "low" outliers are not allowed
    lower = max(0, lower if np.isfinite(lower) else 0)
    # Handle infinite upper or degenerate IQR
    if not np.isfinite(upper) or iqr <= 1e-12:
        col_values = col.to_numpy()
        col_max = np.nanmax(col_values) if col_values.size else 0
        # If everything is zero or NaN, pick a safe positive upper
        upper = col_max * 3 if np.isfinite(col_max) and col_max > 0 else 1.0
        # Pick a small non-negative lower
        positive_vals = col_values[col_values > 0]
        lower = max(0.0, float(np.nanmin(positive_vals)) * 0.25) if positive_vals.size else 0.0
    print(f"Upper (extreme): {upper}")
    print(f"Lower (extreme, non-negative): {lower}")
    # Start with original column values
    updated_values = col.to_numpy(copy=True)
    # Generate replacements only for masked positions
    num_replacements = int(column_mask.sum())
    if num_replacements > 0:
        # Decide which masked rows get the low vs high anchor
        assign_low = rng.random(num_replacements) < 0.5
        replacements = np.empty(num_replacements, dtype=float)
        # Use the same base low/high anchor, then apply small multiplicative noise
        low_count = int(assign_low.sum())
        high_count = num_replacements - low_count
        if low_count > 0:
            low_noise = rng.uniform(0.95, 1.05, size=low_count)
            replacements[assign_low] = float(lower) * low_noise
        if high_count > 0:
            high_noise = rng.uniform(0.95, 1.05, size=high_count)
            replacements[~assign_low] = float(upper) * high_noise
        # Ensure non-negative
        np.maximum(replacements, 0, out=replacements)
        # Match dtype of the column to avoid unintended casting issues
        if np.issubdtype(updated_values.dtype, np.integer):
            replacements = np.rint(replacements)
        try:
            replacements = replacements.astype(updated_values.dtype, copy=False)
        except Exception:
            pass
        # Apply replacements where mask is True
        updated_values[column_mask] = replacements
    # Apply replacements where mask is True
    print(f"Updated Values: {updated_values}")
    return updated_values


@dataclass
class OutlierSpikeStep(CorruptionStep):
    # TODO: Get the min/max of values in the column and produce outliers
    spike_min: int = 0
    spike_max: int = 0

    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("OutlierSpikeStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        corrupted_df = df.copy()
        cell_mask = rng.random((len(corrupted_df), len(corrupted_df.columns))) < self.p_cell
        affected_cells = {}
        global_outlier_columns = tmd.global_outlier_columns[self.table_name]

        for c, col in enumerate[str](global_outlier_columns):
            corrupted_df[col] = multiplicative_spike(rng, corrupted_df, cell_mask[:, c], col)
        return corrupted_df, CorruptionReport(self.name, True, {"affected_cells": affected_cells, "p_cell": self.p_cell})

    def additive_spike(self):
        pass

    def extreme_percentiles(self):
        pass



@dataclass
class ValueNullStep(CorruptionStep):
    # [TODO] Implement

    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("ValueNullStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        affected = 0
        out = df.copy()

        return out, CorruptionReport(self.name, True, {"affected_rows": affected, "p_row": self.p_row})
