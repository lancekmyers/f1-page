---
title: Saudi Arabia Grand Prix
sql:
  laps: ./data/saudi_laps.parquet
---

Saudi Arabia Grand Prix
=======================

```sql id=lap_times
select 
    LapTime * 1e-9 as lap_time, 
    LapNumber as lap_num, 
    Compound as compound, 
    Driver as driver, 
    *
from laps
where 
    PitOutTime is Null    -- non pit stop laps
    AND TrackStatus = '1' -- green flag conditions
    AND Driver = ${team}
```

```js
const team = view(
    Inputs.select(drivers.toArray().map(r => r['driver']), {label: "Driver:", value: 'VER'})
    );
```

```js
Plot.plot({
      title: "Lap Times",
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Lap Time (s)"},
      color: {legend: true, domain : ['HARD','MEDIUM', 'SOFT']},
      marks: [
        Plot.dot(lap_times, {x: "lap_num", y: "lap_time", stroke: "compound", tip: true}), 
      ]
    })
```


```sql id=drivers
select 
    distinct Driver as driver
from laps
```
```sql id=PitTime
WITH PitTime as (
    select 
        LapNumber,
        Driver,
        lag(TyreLife) OVER () as TyreAge,
        lag(Compound) OVER () as OldCompound,
        Compound as NewCompound,
        (PitOutTime - lag(PitInTime) OVER ()) / 1e9 as PitTime
    from laps
) 
select * 
from PitTime
where PitTime is not null
ORDER BY LapNumber
```

```js
Plot.plot({
      title: "Pit Stops",
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Lap Time (s)"},
      marks: [
        Plot.dotX(PitTime, 
            Plot.dodgeY({x: "LapNumber", title: "Driver", tip: true})
        ), 
      ]
    })
```

```js
Plot.plot({
      title: "Speeds",
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Speed (kph)"},
      marks: [
        Plot.dot(lap_times, {x: "lap_num", y: "SpeedI1", stroke: "red", tip: true}), 
        Plot.dot(lap_times, {x: "lap_num", y: "SpeedI2", stroke: "green", tip: true}), 
        Plot.dot(lap_times, {x: "lap_num", y: "SpeedFL", stroke: "blue", tip: true}), 
        Plot.dot(lap_times, {x: "lap_num", y: "SpeedST", stroke: "orange", tip: true})
      ]
    })
```
