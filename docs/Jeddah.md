---
title: Saudi Arabia Grand Prix
sql:
  laps: ./data/saudi_laps.parquet
  quali_results: ./data/saudi_quali_results.parquet
---

<div class="hero">
<h1> Jeddah </h1>
<h2> Saudi Arabia Grand Prix </h2>
</div>

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
    AND Driver = ${selected_driver}
```

```js
const selected_driver = view(
    Inputs.select(drivers.toArray().map(r => r['driver']), {label: "Driver:", value: 'VER'})
    );
```

```sql id=laps
select * from laps
```

<div class="card"> 
    ${resize((width) => Plot.plot({
        title: "Positions",
        width, 
        x: {axis: "bottom", label: "Lap"},
        y: {label: "Position", reverse: "true"},
        marks: [
            Plot.line(laps, 
              {x:"LapNumber", y:"Position", z:"Driver", title: "Driver", 
              strokeWidth: ((d) => d.Driver == selected_driver ? 4 : 2), tip: true}
            ),
            Plot.text(laps, Plot.selectLast({
              x: "LapNumber",
              y: "Position",
              z: "Driver",
              text: "Driver",
              textAnchor: "start",
              dx: 3
            }))
        ]
    }))}
</div>

<div class = "card">
${resize((width) => Plot.plot({
      title: "Lap Times",
      width,
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Lap Time (s)"},
      color: {legend: true, domain : ['HARD','MEDIUM', 'SOFT']},
      marks: [
        Plot.dot(
            lap_times, 
            {x: "lap_num", y: "lap_time", stroke: "compound", tip: true}), 
      ]
    }))}
</div>

<div class = "card">
${Plot.plot({
      title: "Speeds",
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Speed (kph)"},
      marks: [
        Plot.line(lap_times, {x: "lap_num", y: "SpeedI1", stroke: "red", tip: true}), 
        Plot.line(lap_times, {x: "lap_num", y: "SpeedI2", stroke: "green", tip: true}), 
        Plot.line(lap_times, {x: "lap_num", y: "SpeedFL", stroke: "blue", tip: true}), 
        Plot.line(lap_times, {x: "lap_num", y: "SpeedST", stroke: "orange", tip: true})
      ]
    })}
</div>

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

```sql id=stints
select 
    Driver, Stint, 
    first(LapNumber) as FirstLap, last(LapNumber) as LastLap,
    any_value(compound) as Compound 
from laps
group by Driver, stint
```

<div class="card">
    ${resize((width) => Plot.plot({
        title: "Stints",
        width, 
        grid: true,
        color: {legend: true, domain : ['HARD','MEDIUM', 'SOFT']},
        x: {label: "Lap Number"},
        y: {label: ""},
        marks: [
            Plot.ruleY(stints, {
                y: "Driver",  
                x1: "FirstLap",
                x2: "LastLap",
                title: "Driver", 
                stroke: "Compound",
                strokeWidth: (d) => (d.Driver == selected_driver) ? 8 : 4})
        ]
    }))}
</div>


<div class="card"> 
    ${Inputs.table(PitTime)}
</div>

## Qualifying

```js
const lap_fmt = new Intl.NumberFormat('en-US', 
    {minimumFractionalDigits: 3, maximumFractionalDigits: 3, signDisplay: "always"}
  )
```

<div class="card"> 
    ${Plot.plot({
        title: "Quali",
        width, 
        x: {axis: "top", label: "Session"},
        y: {label: "Driver", domain: quali_results.toArray().map(r => r.Driver)},
        color: {type: "linear", scheme: "RdPu"},
        marks: [
            Plot.cell(
              quali_results, 
              {x : 1, y : "Driver",  fill : "Q1" }
            ),
            Plot.cell(
              quali_results, 
              {x : 2, y : "Driver", fill : "Q2"}
            ),
            Plot.cell(
              quali_results, 
              {x : 3, y : "Driver", fill : "Q3"}
            ),
        ]
    })}
</div>

```sql id=quali_results

select Driver, Position, 
  Q1 / (min(Q1) over ()) as Q1,
  Q2 / (min(Q2) over ()) as Q2,
  Q3 / (min(Q3) over ()) as Q3, 
from quali_results
order by position
```

