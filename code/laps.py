import fastf1
from fastf1 import events
import polars as pl
from requests import Session

rounds = [1, 2, 3, 4]
season = 2024


lap_telem_schema = {'Date': pl.Datetime(time_unit='ns', time_zone=None), 'SessionTime': pl.Duration(time_unit='ns'), 'DriverAhead': pl.String, 'DistanceToDriverAhead': pl.Float64, 'Time': pl.Duration(time_unit='ns'), 'RPM': pl.Int64, 'Speed': pl.Int64, 'nGear': pl.Int64, 'Throttle': pl.Int64, 'Brake': pl.Boolean, 'DRS': pl.Int64, 'Source': pl.String, 'Distance': pl.Float64, 'RelativeDistance': pl.Float64, 'Status': pl.String, 'X': pl.Float64, 'Y': pl.Float64, 'Z': pl.Float64}

def handle_qualifying(quali : Session, loc : str): 
    quali_results = pl.DataFrame(
            quali.results
        ).select(
            pl.col("Abbreviation").alias("Driver"), 
            "Position", "Q1", "Q2", "Q3"
        )
    
    quali_fastest_laps = {
        driver: quali.laps.pick_drivers([driver]).pick_fastest() 
        for driver in quali.drivers
    }

    quali_telem = pl.concat(
        pl.DataFrame(
            lap.get_telemetry(), schema=lap_telem_schema
        ).with_columns(pl.lit(driver).alias("Driver"))
        for (driver, lap) in quali_fastest_laps.items() 
        if not lap.isna().all() 
    )

    quali_results.write_parquet(f'docs/data/{loc}_quali_results.parquet')
    quali_telem.write_parquet(f'docs/data/{loc}_quali_telem.parquet')


def handle_race(gp : Session, loc : str): 
    gp_laps = gp.laps
    gp_laps.to_parquet(f'docs/data/{loc}_laps.parquet')

def handle_circuit(circuit_info, loc : str ): 
    corners = circuit_info.corners
    corners['RelativeDistance'] = (corners['Distance'] / corners['Distance'].sum()).cumsum()
    corners = pl.DataFrame(corners)
    corners.write_parquet(f'docs/data/{loc}_corners.parquet')



def handle_round(n):
    gp = fastf1.get_session(season, n, "R")
    gp.load()
    quali = fastf1.get_session(season, n, "Qualifying")
    quali.load()
    circuit_info = quali.get_circuit_info()
    
    location = quali.event.Location

    handle_circuit(circuit_info, location)
    handle_qualifying(quali, location)
    handle_race(gp, location)

for round in rounds: 
    handle_round(round)
