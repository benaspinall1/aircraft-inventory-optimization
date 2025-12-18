from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import data.table_metadata as tmd


@dataclass
class CorruptionReport:
    step: str
    applied: bool
    details: Dict[str, Any]

@dataclass
class CorruptionStep:
    name: str
    p_apply: float
    p_row: float
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

        corruptible_columns = tmd.corruptible_tables[self.table_name]
        for col in corruptible_columns:
            print(col)
        out = df.copy()
        idx = rng.random(len(out)) < self.p_row
        affected = int(idx.sum())
        if affected:
            out.loc[idx, "qty"] = -out.loc[idx, "qty"].abs()

        return out, CorruptionReport(self.name, True, {"affected_rows": affected, "p_row": self.p_row})

@dataclass
class OutlierSpikeStep(CorruptionStep):
    # TODO: Get the min/max of values in the column and produce outliers
    spike_min: int = 0
    spike_max: int = 0

    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("OutlierSpikeStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        out = df.copy()
        idx = rng.random(len(out)) < self.p_row
        affected = int(idx.sum())
        if affected:
            spikes = rng.integers(self.spike_min, self.spike_max + 1, size=affected)
            out.loc[idx, "qty"] = spikes

        return out, CorruptionReport(self.name, True, {"affected_rows": affected, "p_row": self.p_row})


@dataclass
class ValueNullStep(CorruptionStep):
    # [TODO] Implement
    p_row: float = 0.001
    spike_min: int = 50
    spike_max: int = 500

    def run(self, df: pd.DataFrame, rng: np.random.Generator):
        print("ValueNullStep")
        if not self.should_apply(rng):
            return df, CorruptionReport(self.name, False, {})

        out = df.copy()
        idx = rng.random(len(out)) < self.p_row
        affected = int(idx.sum())
        if affected:
            spikes = rng.integers(self.spike_min, self.spike_max + 1, size=affected)
            out.loc[idx, "qty"] = spikes

        return out, CorruptionReport(self.name, True, {"affected_rows": affected, "p_row": self.p_row})
