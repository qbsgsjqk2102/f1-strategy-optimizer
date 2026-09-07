# Real-Time Dynamic F1 Strategy Optimization System

An interactive decision-support system simulating telemetry-driven Formula 1 race strategies under uncertainty. The project couples empirical tyre degradation regression curves with a discrete event evaluation engine to recommend pit stops in real time.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Frontend-Streamlit-red)

---

## Project Overview
In modern Formula 1, race outcomes hinge on real-time trade-offs between **track position** and **tyre delta** (the grip advantage of fresher compounds). Unforeseen events such as Safety Cars (SC) disrupt pre-race plans by compressing the field and halving pit-lane time loss.

This tool models dynamic race scenarios to evaluate whether a car should pit immediately (**Box This Lap**) or remain on track (**Stay Out**), recalculating cumulative race times based on:
* Compound wear non-linearities.
* In-race events (Green Flag vs. SC/VSC neutralization).
* Rolling evaluation horizons up to the chequered flag.

---

## Mathematical Modeling & Architecture

### 1. Data Cleaning & Feature Pipeline
* Sourced via `FastF1` timing telemetry from the Bahrain Grand Prix.
* **Strict Anomaly Filtering:** In-laps, Out-laps, and laps affected by yellow flags/safety car periods (`TrackStatus != '1'`) are filtered out to extract pure race pace.
* Extreme outliers ($\Delta t > \text{median} + 7.0\text{s}$) caused by lock-ups or driver errors are pruned.

### 2. Tyre Degradation Regression
Tyre performance does not degrade strictly linearly; thermal degradation exhibits a progressive "cliff." We fit a 2nd-degree polynomial model for each compound:

$$\text{LapTime}(t) = \beta_0 + \beta_1 \cdot t + \beta_2 \cdot t^2$$

where $t$ denotes tyre age in laps, $\beta_0$ represents baseline single-lap pace, and $\beta_2$ captures the non-linear degradation cliff.

### 3. Real-Time Strategy Decision Logic
At each lap $L$, the engine compares the remaining cumulative horizon time $H$:

$$\Delta T = T_{\text{StayOut}} - T_{\text{Box}}$$

$$T_{\text{StayOut}} = \sum_{i=0}^{H-1} \widehat{\text{LapTime}}(\text{Compound}_{\text{current}}, \text{Age} + i)$$

$$T_{\text{Box}} = \Delta t_{\text{PitLoss}} + \sum_{i=0}^{H-1} \widehat{\text{LapTime}}(\text{Compound}_{\text{new}}, 1 + i)$$

* **Green Flag $\Delta t_{\text{PitLoss}}$:** $\approx 22.0\text{ s}$
* **Safety Car $\Delta t_{\text{PitLoss}}$:** $\approx 12.0\text{ s}$ (effectively creating a "cheap pit stop" window)
* A pit stop is recommended if $\Delta T > 1.5\text{ s}$.

---

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)qbsgsjqk2102/f1-strategy-optimizer.git
   cd f1-strategy-optimizer
