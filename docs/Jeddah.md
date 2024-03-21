---
title: Saudi Arabia Grand Prix
sql:
  laps: ./data/saudi_laps.parquet
---

<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

</style>

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