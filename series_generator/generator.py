import numpy as np
import pandas as pd

YEAR_DAYS = 365


class SeriesGenerator:

    def __init__(self, years):
        self.years = years
        self.days = YEAR_DAYS * years

    def generate_demand_series(self, prob_of_demand, mean_quantity, seed=None):
        # Create a boolean list indicating demand on that day with probability of prob_of_demand
        rng = np.random.default_rng(seed)
        demand_on_that_day = rng.random(self.days) < prob_of_demand

        # Create a demand series by counting false days as 0 and true days as either 1 or the true quantity
        # Since I used a poisson distribution to sample demand there is a chance that a 0 was generated for a true day
        # ,so I am effective raising all of these instances to a demand quantity of 1.
        quantities = rng.poisson(mean_quantity, size=self.days)
        demand_series = np.where(demand_on_that_day, np.maximum(1, quantities), 0)
        return demand_series




