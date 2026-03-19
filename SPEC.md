# Cluster Routing Visualiser — Spec

## Overview
A Streamlit app that interactively visualises percentage routing across 4 clusters based on a scoring formula.

## Formulas

```
cluster_score[i] = wC * C[i] - wU * (U[i] / (ULimit - U[i]))
final_cluster_score  = softmax(cluster_score)          # sums to 1 over active clusters
percentage_routing[i] = (1 - L) * (1/N_active) + L * final_cluster_score[i]
```

- `N_active` = number of enabled clusters (dynamic, 0–4)
- Disabled clusters receive `routing[i] = 0`
- `percentage_routing` sums to 1 across active clusters (0 if all disabled)
- Softmax uses `exp(x - max(x)) / sum(...)` for numerical stability

## Parameters

| Parameter    | Type   | Default | Range        | Description                        |
|--------------|--------|---------|--------------|------------------------------------|
| `wC`         | float  | 10.0     | any          | Weight for cost per EMR unit       |
| `wU`         | float  | 1.0     | any          | Weight for utilisation score       |
| `L`          | float  | 0.5     | 0.0 – 1.0    | Mixing parameter (0 = uniform, 1 = score-based) |
| `ULimit`     | int    | 1000    | ≥ 2          | Utilisation cap, shared across clusters |
| `enabled[i]` | bool   | True    | True/False   | Whether cluster i participates in routing |
| `C[i]`       | float  | 0.7     | 0.0 – 2.0    | Cost per EMR unit for cluster i    |
| `U[i]`       | int    | 0       | 0 – ULimit-1 | Utilisation for cluster i; capped at ULimit-1 so denominator never hits zero |

## UI Layout

### Sidebar
- `wC` — `st.number_input` (float, step 0.1)
- `wU` — `st.number_input` (float, step 0.1)
- `L`  — `st.number_input` (float, step 0.05, min 0.0, max 1.0)
- `ULimit` — `st.number_input` (int, step 1, min 2)
- **Enable/Disable Clusters** section — `enabled[0]`–`enabled[3]` as `st.checkbox` (default True)
- **Cost per EMR Unit** section — `C[0]`–`C[3]` as `st.slider` (float, 0.0 – 2.0, step 0.1, default 0.7)
- **Utilisation** section — `U[0]`–`U[3]` as `st.slider` (int, 0 – ULimit-1); max updates reactively with ULimit

### Main Panel
1. **Bar chart** (`st.bar_chart`) — routing percentage per cluster
2. **Summary table** (`st.dataframe`) — columns: `Enabled`, `C[i]`, `U[i]`, `cluster_score[i]`, `final_cluster_score[i]`, `routing[i]`, `routing (%)`
3. **Caption** — displays `routing.sum()` as a sanity check

## Files

| File              | Purpose                        |
|-------------------|--------------------------------|
| `app.py`          | Main Streamlit application     |
| `pyproject.toml`  | Dependencies (`streamlit`, `numpy`, `pandas`), Python ≥ 3.10 |
| `SPEC.md`         | This file                      |

## Running

```bash
uv sync
uv run streamlit run app.py
```

## Edge Cases & Expected Behaviour

| Scenario                        | Expected result                                              |
|---------------------------------|--------------------------------------------------------------|
| `L = 0`                         | Equal routing (1/N_active each), scores ignored              |
| `L = 1`                         | Purely score-based routing via softmax                       |
| `U[i]` → `ULimit - 1`          | `U / (ULimit - U)` grows large, that cluster dominates       |
| All `C[i]` and `U[i]` equal    | Equal routing regardless of `L`                              |
| `wC = 0`, `wU = 0`             | All raw scores = 0, softmax → uniform, routing = 1/N_active each |
| All clusters disabled           | routing[i] = 0 for all i; routing sum = 0.0                  |
| One cluster enabled             | That cluster receives 100% routing                           |
| `L = 0`, 2 active clusters     | 50% each                                                     |
| `L = 0`, 4 active clusters     | 25% each                                                     |
