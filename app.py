import streamlit as st
import plotly.graph_objects as go
from src.data_loader import load_race_data
from src.strategy_engine import TyreDegradationModel, evaluate_pit_window

st.set_page_config(page_title="F1 Dynamic Strategy Optimizer", layout="wide")

st.title("🏎️ F1 Dynamic Race Strategy Optimizer")
st.markdown("An interactive decision-support tool simulating telemetry-driven race strategies and tyre degradation dynamics.")

@st.cache_data
def get_cached_data():
    return load_race_data(2023, "Bahrain")

with st.spinner("Loading and filtering race telemetry..."):
    laps_df = get_cached_data()

model = TyreDegradationModel(laps_df)

# Sidebar: Race State Controls
st.sidebar.header("Current Race State")
current_lap = st.sidebar.slider("Current Lap", min_value=1, max_value=57, value=17)
compound = st.sidebar.selectbox("Current Compound", ["SOFT", "MEDIUM"])
tyre_age = st.sidebar.number_input("Tyre Age (Laps)", min_value=1, max_value=40, value=17)
safety_car = st.sidebar.toggle("🚨 Safety Car / VSC Deployed", value=False)

# Decision Engine Evaluation
decision = evaluate_pit_window(
    current_lap=current_lap,
    total_laps=57,
    current_compound=compound,
    current_tyre_age=tyre_age,
    model=model,
    safety_car=safety_car
)

# Output Recommendation Cards
col1, col2 = st.columns(2)
with col1:
    if decision["action"] == "BOX THIS LAP":
        st.error(f"### Recommendation: {decision['action']}")
    else:
        st.success(f"### Recommendation: {decision['action']}")
    st.write(decision["reason"])

with col2:
    st.metric(
        label="Net Time Delta (Box vs Stay)",
        value=f"{decision['time_delta']:+.2f} s",
        delta="Favors Pit Stop" if decision["time_delta"] > 0 else "Favors Staying Out"
    )

# Plotting Degradation Curves
st.subheader("Tyre Pace Degradation Models")
fig = go.Figure()
tyre_ages = list(range(1, 31))

colors = {"SOFT": "red", "MEDIUM": "gold", "HARD": "white"}
for comp in ["SOFT", "MEDIUM", "HARD"]:
    if comp in model.models:
        preds = [model.predict_lap_time(comp, age) for age in tyre_ages]
        fig.add_trace(go.Scatter(
            x=tyre_ages,
            y=preds,
            mode="lines+markers",
            name=comp,
            line=dict(color=colors.get(comp, "cyan"))
        ))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Tyre Age (Laps)",
    yaxis_title="Expected Lap Time (seconds)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)