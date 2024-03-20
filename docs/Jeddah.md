---
title: Saudi Arabia Grand Prix
sql:
  laps: ./data/saudi_laps.parquet
---


```sql id=lap_times
select 
    LapTime as lap_time, 
    LapNumber as lap_num, 
    Compound as compound
from laps
where 
    PitOutTime is Null    -- non pit stop laps
    AND TrackStatus = '1' -- green flag conditions
```

```js
Plot.plot({
      title: "Lap Times",
      grid: true,
      x: {label: "Lap Number"},
      y: {label: "Lap Time (s)"},
      color: {legend: true},
      marks: [
        Plot.dot(lap_times, {x: "lap_num", y: "lap_time", stroke: "compound", tip: true})
      ]
    })
```