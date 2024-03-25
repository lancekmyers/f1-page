import fastf1
from fastf1 import events
import polars as pl

rounds = [1, 2]


saudi_quali = fastf1.get_session(2024, 2, 'Qualifying')
saudi_quali.load()

saudi_quali.car_data['1'].columns

saudi_quali.car_data['1']['nGear']

saudi_gp = fastf1.get_session(2024, 2, 'R')
saudi_gp.load()

saudi_laps = saudi_gp.laps
saudi_laps.to_parquet('docs/data/saudi_laps.parquet')

saudi_gp.results

quali_pos = pl.concat(
    pl.DataFrame(v).with_columns(pl.lit(k).alias("driver"))
    for (k, v) in saudi_quali.pos_data.items()
)
    
saudi_quali_results = pl.DataFrame(
        saudi_quali.results
    ).select(
        pl.col("Abbreviation").alias("Driver"), 
        "Position", "Q1", "Q2", "Q3"
    )

saudi_quali_results.write_parquet('docs/data/saudi_quali_results.parquet')

quali_pos.write_parquet('docs/data/saudi_quali_position.parquet')
saudi_gp.track_status


quali_fastest_laps = {
    driver: saudi_quali.laps.pick_drivers([driver]).pick_fastest() 
    for driver in saudi_quali.drivers
    }
lap_telem_schema = {'Date': pl.Datetime(time_unit='ns', time_zone=None), 'SessionTime': pl.Duration(time_unit='ns'), 'DriverAhead': pl.String, 'DistanceToDriverAhead': pl.Float64, 'Time': pl.Duration(time_unit='ns'), 'RPM': pl.Int64, 'Speed': pl.Int64, 'nGear': pl.Int64, 'Throttle': pl.Int64, 'Brake': pl.Boolean, 'DRS': pl.Int64, 'Source': pl.String, 'Distance': pl.Float64, 'RelativeDistance': pl.Float64, 'Status': pl.String, 'X': pl.Float64, 'Y': pl.Float64, 'Z': pl.Float64}

quali_telem = pl.concat(
    pl.DataFrame(
        lap.get_telemetry(), schema=lap_telem_schema
    ).with_columns(pl.lit(driver).alias("Driver"))
    for (driver, lap) in quali_fastest_laps.items() 
    if not lap.isna().all() 
)

quali_telem.write_parquet('docs/data/saudi_quali_telemetry.parquet')