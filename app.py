import streamlit as st
import plotly.graph_objects as go
from src.data_loader import load_race_data
from src.strategy_engine import TyreDegradationModel, evaluate_pit_window

st.set_page_config(page_title="F1 Dynamic Strategy Optimizer", layout="wide")

st.title("🏎️ F1 Dynamic Race Strategy Optimizer")
st.markdown("Интерактивный инструмент принятия тактических решений на основе телеметрии и регрессионного анализа износа шин.")

@st.cache_data
def get_cached_data():
    return load_race_data(2023, "Bahrain")

with st.spinner("Загрузка и фильтрация телеметрии гонки..."):
    laps_df = get_cached_data()

model = TyreDegradationModel(laps_df)

# Боковая панель управления (Live Race State)
st.sidebar.header("Параметры текущей гонки")
current_lap = st.sidebar.slider("Текущий круг гонки", min_value=1, max_value=57, value=17)
compound = st.sidebar.selectbox("Текущий компаунд", ["SOFT", "MEDIUM"])
tyre_age = st.sidebar.number_input("Возраст шины (круги)", min_value=1, max_value=40, value=17)
safety_car = st.sidebar.toggle("🚨 Выезд Safety Car / VSC", value=False)

# Анализ решения
decision = evaluate_pit_window(
    current_lap=current_lap,
    total_laps=57,
    current_compound=compound,
    current_tyre_age=tyre_age,
    model=model,
    safety_car=safety_car
)

# Вывод карточек с решением
col1, col2 = st.columns(2)
with col1:
    if decision["action"] == "BOX THIS LAP":
        st.error(f"### Рекомендация: {decision['action']}")
    else:
        st.success(f"### Рекомендация: {decision['action']}")
    st.write(decision["reason"])

with col2:
    st.metric(
        label="Дельта времени (Box vs Stay)",
        value=f"{decision['time_delta']:+.2f} сек",
        delta="В пользу пит-стопа" if decision["time_delta"] > 0 else "В пользу трассы"
    )

# Построение графиков деградации
st.subheader("Модель деградации темпа по составам резины")
fig = go.Figure()
tyre_ages = list(range(1, 31))

colors = {"SOFT": "red", "MEDIUM": "gold", "HARD": "white"}
for comp in ["SOFT", "MEDIUM", "HARD"]:
    if comp in model.models:
        preds = [model.predict_lap_time(comp, age) for age in tyre_ages]
        fig.add_trace(go.Scatter(x=tyre_ages, y=preds, mode="lines+markers", name=comp, line=dict(color=colors[comp])))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Возраст шины (круги)",
    yaxis_title="Ожидаемое время круга (сек)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)