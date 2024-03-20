import fastf1
from fastf1 import events

saudi_gp = fastf1.get_session(2024, 2, 'R')
saudi_gp.load()

saudi_laps = saudi_gp.laps
saudi_laps.to_parquet('docs/data/saudi_laps.parquet')
