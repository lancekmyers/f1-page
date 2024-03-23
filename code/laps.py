import fastf1
from fastf1 import events
import polars as pl

saudi_quali = fastf1.get_session(2024, 2, 'Qualifying')
saudi_quali.load()


saudi_gp = fastf1.get_session(2024, 2, 'R')
saudi_gp.load()

saudi_laps = saudi_gp.laps
saudi_laps.to_parquet('docs/data/saudi_laps.parquet')

saudi_gp.results

quali_pos = pl.concat(
    pl.DataFrame(v).with_columns(pl.lit(k).alias("driver"))
    for (k, v) in saudi_quali.pos_data.items()
)
quali_cars = pl.concat(
    pl.DataFrame(v).with_columns(pl.lit(k).alias("driver"))
    for (k, v) in saudi_quali.car_data.items()
) 
    
saudi_quali_results = pl.DataFrame(
        saudi_quali.results
    ).select(
        pl.col("Abbreviation").alias("Driver"), 
        "Position", "Q1", "Q2", "Q3"
    )
saudi_quali_results.write_parquet('docs/data/saudi_quali_results.parquet')