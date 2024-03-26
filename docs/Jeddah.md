---
title: Saudi Arabia Grand Prix
sql:
  laps: ./data/saudi_laps.parquet
  quali_results: ./data/saudi_quali_results.parquet
  quali_telemetry_source: ./data/saudi_quali_telemetry.parquet
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
```

```js
const selected_driver = view(
    Inputs.select(drivers.toArray().map(r => r['driver']), {label: "Driver:", value: 'VER'})
    );
```

```sql id=laps
select * from laps
```

```sql id=drivers
select 
    distinct Driver as driver
from laps
```

<div class="grid grid-cols-2">
<div class="card"> 
    ${resize((width) => Plot.plot({
        title: "Positions",
        width, 
        x: {axis: "bottom", label: "Lap"},
        y: {label: "Position", reverse: "true"},
        color: {legend: true, domain : ['HARD','MEDIUM', 'SOFT']},
        marks: [
            Plot.line(laps, 
              {x:"LapNumber", y:"Position", z:"Driver", title: "Driver",
              opacity : ((d) => d.Driver == selected_driver ? 1 : 0.5), 
              strokeWidth: ((d) => d.Driver == selected_driver ? 10 : 8), tip: true,
              stroke: "Compound"
              }
            ),
            Plot.dot(
              PitTime, {
                x: "LapNumber", y:"Position",
                stroke: "NewCompound", 
                fill: "OldCompound"
              }
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
<div>
${resize((width) => Plot.plot({
      title: "Lap Times",
      width,
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Lap Time (s)", domain: [1, 1.1]},
      color: {legend: true, domain : ['HARD','MEDIUM', 'SOFT']},
      marks: [
        Plot.dot(
            lap_times, 
            Plot.normalizeY("min", {
              x: "lap_num", y: "lap_time", z: "driver",
              stroke: "compound", 
              opacity: (d) => d.driver == selected_driver ? 1 : 0.1 ,
              tip: true
              })
        ), 
      ]
    }))}
</div>


</div>

<div class="card" style="grid-column: span 3; height: fit-content;"> 
  ${resize((width) => 
    Plot.plot({
      width, 
      title: "Lap Times",
      x : {domain: [1,1.15]},
      marks: [
        Plot.boxX(
          lap_times, 
          Plot.normalizeX("min", {
            x: d => d["Sector3Time"] * 1e-9, 
            fy : (_) => "Sector3",
            opacity: 0.5 
          })),
        Plot.dot(
          lap_times, 
          Plot.dodgeY("middle", 
            Plot.normalizeX("min", {
              x: d => d["Sector3Time"] * 1e-9, 
              fy : (_) => "Sector3",
              r: 1.5,
              opacity: (d) => d.Driver == selected_driver ? 1 : 0,
              tip: true,
          }))),
        Plot.boxX(
          lap_times, 
          Plot.normalizeX("min", {
            x: d => d["Sector2Time"] * 1e-9, 
            fy : (_) => "Sector2",
            opacity: 0.5 
          })),
      Plot.dot(
          lap_times, 
          Plot.dodgeY("middle", 
            Plot.normalizeX("min", {
              x: d => d["Sector2Time"] * 1e-9, 
              fy : (_) => "Sector2",
              r: 1.5,
              opacity: (d) => d.Driver == selected_driver ? 1 : 0,
              tip: true,
          }))), 
      Plot.boxX(
          lap_times, 
          Plot.normalizeX("min", {
            filter: "Sector1Time",
            x: d => d["Sector1Time"] * 1e-9, 
            fy : (_) => "Sector1",
            opacity: 0.5
          })),
      Plot.dot(
          lap_times, 
          Plot.dodgeY("middle", 
            Plot.normalizeX("min", {
              x: d => d["Sector1Time"] * 1e-9, 
              filter: "Sector1Time",
              fy : (_) => "Sector1",
              r: 1.5,
              opacity: (d) => d.Driver == selected_driver ? 1 : 0,
              tip: true,
          })))
      ]
    }))}
</div>

</div>


```sql id=PitTime
WITH PitTime as (
    select 
        LapNumber,
        Driver,
        lag(TyreLife) OVER () as TyreAge,
        lag(Compound) OVER () as OldCompound,
        Compound as NewCompound,
        Position,
        (PitOutTime - lag(PitInTime) OVER ()) / 1e9 as PitTime
    from laps
) 
select * 
from PitTime
where PitTime is not null
ORDER BY LapNumber
```



<div class="card"> 
    ${Inputs.table(PitTime)}
</div>

## Qualifying

```js
const lap_fmt = new Intl.NumberFormat('en-US', 
    {minimumFractionalDigits: 2, maximumFractionalDigits: 3, 
    signDisplay: "always"}
  )
```
<div class="grid grid-cols-2">
<div class="card"> 
    ${resize((width) => Plot.plot({
        title: "Quali",
        width, 
        x: {axis: "top", label: "Session"},
        y: {label: "Driver", domain: quali_results.toArray().map(r => r.Driver)},
        color: {type: "diverging", scheme: "RdBu"},
        marks: [
            Plot.cell(
              quali_results,
              {x : 1, y : "Driver",  fill : "Q1" }
            ),
            Plot.cell(
              quali_results,
              {x : 2, y : "Driver", fill : "Q2", "filter": "Q2"}
            ),
            Plot.cell(
              quali_results, 
              {x : 3, y : "Driver", fill : "Q3", "filter": "Q3"}
            ),
            Plot.text(
              quali_results,
              { x:1, y: "Driver", 
                "filter": "Q1",
                text : (d) => lap_fmt.format(100 * (d["Q1"])) + "\%"}
            ),
            Plot.text(
              quali_results,
              { x:2, y: "Driver",
                "filter": "Q2", 
                text : (d) => lap_fmt.format(100 * (d["Q2"])) + "\%"}
            ),
            Plot.text(
              quali_results,
              { x:3, y: "Driver", 
                "filter": "Q3",
                text : (d) => lap_fmt.format(100 * (d["Q3"])) + "\%"}
            ),
        ]
    }))}
  </div> 
  <div class="card">
  ${Plot.plot({
        x: {label:null, ticks: []},
        y: {label:null, ticks: []},
        color: {scheme: "Cividis", legend: true},
        marks: [
          Plot.line(
            quali_telemetry_selected, 
            {x : "Y", y:"X", stroke: "Speed", z: "Driver", strokeWidth: 5}
          )
        ], 
      aspectRatio: 1})
    }
  </div>
</div>


```sql id=quali_results

select Driver, Position, 
  -1.0 + Q1 / (nth_value(Q1, 15) over ()) as Q1,
  -1.0 + Q2 / (nth_value(Q2, 10) over ()) as Q2,
  -1.0 + Q3 / (MIN(Q3) over ()) as Q3,
from quali_results
order by position
```

```sql id=quali_telemetry
select *, min(SessionTime) OVER (PARTITION BY Driver) as LapStart from quali_telemetry_source
```

```sql id=quali_telemetry_selected
select * from quali_telemetry_source
where Driver = '1'
```

## Qualifying Telemetry


```js
const nGearScale = d3.scaleLinear().domain([1,8]).range([0,1]);
```
<div>
  <div class="card"> 
  ${resize((width) => Plot.plot({
    width,
    marks: [
      Plot.line(
        quali_telemetry, 
        Plot.normalizeY({
          x : "RelativeDistance", y:"nGear", fy: (_) => "nGear",
          opacity: (d) => d.Driver == '1' ? 1 : 0.1,
          z: "Driver", sort: "RelativeDistance"})
    ), 
    Plot.line(
        quali_telemetry, 
        Plot.normalizeY({
          x : "RelativeDistance", y:"Throttle", fy: (_) => "Throttle",
          opacity: (d) => d.Driver == '1' ? 1 : 0.1,
          z: "Driver", sort: "RelativeDistance"})
    ),
    Plot.line(
        quali_telemetry,
        Plot.normalizeY({
          x : "RelativeDistance", y: "Speed", fy: (_) => "Speed",
          opacity: (d) => d.Driver == '1' ? 1 : 0.1,
          z: "Driver", sort: "RelativeDistance" })
    ),]}))
  }
  </div>
  
</div>