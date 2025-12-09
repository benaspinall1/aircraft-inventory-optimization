import numpy as np
import pandas as pd
import series_generator.generator as gen


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
        records.append({"day": day, "part_code": part_code, "qty": int(qty)})

df = pd.DataFrame(records)

print(df)





