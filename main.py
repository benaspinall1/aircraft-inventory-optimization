import numpy as np
import pandas as pd
import series_generator.generator as gen
import data.db as db
from datetime import datetime, timedelta, date
import data_processing.corruptor as dc

today = date.today()
# dc.OutlierSpikeStep(name="outlier_spike", p_apply=0.8, p_row=None, p_col=None, p_cell=0.1)
chain = dc.CorruptionChain(
    steps=[
        dc.OutlierSpikeStep(name="outlier_spike", p_apply=0.8, p_row=None, p_col=None, p_cell=0.1)

    ],
    seed=42,
)
# dc.OutlierSpikeStep(name="outlier_spikes", p_apply=1, p_row=0.1),
# dc.DropRowsStep(name="drop_rows", p_apply=1, p_row=0.08),
database = db.Database(chain)  # This creates the database from the unrealistic files.

years = 3
random_num_gen_seed = 42
generator = gen.SeriesGenerator(years)

parts = [
    ("ENG-FUEL-PUMP-001", 0.15, 4.0),  # frequent, small batches
    ("ENG-FUEL-PUMP-002", 0.03, 2.0),  # occasional, small batches
    ("ENG-FUEL-PUMP-003", 0.001, 1.0)  # extremely rare
]
records = []
for part_code, probability, mean_size in parts:
    demand = generator.generate_demand_series(probability, mean_size, random_num_gen_seed)
    for day, qty in enumerate(demand):
        date = today - timedelta(days=day + 1) # doing + 1 here because day starts at 0 due to enumerate() functionality
        records.append({"date": date, "part_code": part_code, "qty": int(qty)})

df = pd.DataFrame(records)
# print(df)

