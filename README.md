# Mobile Game A/B Test: First Progression Gate Placement

Tests whether moving the first progression gate in a mobile puzzle game from level 30 to level 40 changes player retention.

## Data
`data/cookie_cats.csv`: one row per player (90,189 players).
- `version`: `gate_30` (control) or `gate_40` (treatment)
- `sum_gamerounds`: game rounds played in the first 14 days
- `retention_1` / `retention_7`: whether the player returned 1 or 7 days after install

## Run
```
pip install pandas scipy numpy
python analysis.py
```
Results are written to `results/results.md` and `results/results.json`.

## Method
- Two-proportion z-test and 95% confidence intervals for 1-day and 7-day retention
- Sample ratio mismatch check (chi-square) to confirm the 50/50 split worked
- Duplicate-user and null-value checks

## Key findings
- 7-day retention fell from 19.02% (gate 30) to 18.20% (gate 40): -0.82 pts, 95% CI -1.33 to -0.31, p = 0.0016
- About 8,200 fewer retained players per 1M installs
- 1-day retention difference was not statistically significant (p = 0.07)
- The sample ratio mismatch (44,700 vs. 45,489, p = 0.009) is a data-quality flag: check the assignment logic before relying on the result

## Source
Dataset: the public Cookie Cats mobile game dataset (also used in many published A/B test tutorials).
