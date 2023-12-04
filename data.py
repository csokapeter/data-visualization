import os
import pandas as pd

directory = 'data'
original_df = pd.read_csv(os.path.join(directory, 'athletics_world_championship_finals.csv'))
population_df = pd.read_csv(os.path.join(directory, 'population.csv'))
ioc_iso_df = pd.read_csv(os.path.join(directory, 'IOCtoISO.csv'))
