import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class TyreDegradationModel:
    def __init__(self, laps_df: pd.DataFrame):
        self.laps_df = laps_df
        self.models = {}
        self._fit_models()

    def _fit_models(self):
        """Обучает отдельную полиномиальную кривую для каждого типа шин."""
        compounds = ["SOFT", "MEDIUM", "HARD"]

        for compound in compounds:
            subset = self.laps_df[self.laps_df["Compound"] == compound]
            if len(subset) < 15:
                continue

            # Независимая переменная: возраст шины (в кругах)
            X = subset[["TyreLife"]].values
            y = subset["LapTimeSeconds"].values

            poly = PolynomialFeatures(degree=2, include_bias=True)
            X_poly = poly.fit_transform(X)

            reg = LinearRegression()
            reg.fit(X_poly, y)

            self.models[compound] = {
                "poly": poly,
                "reg": reg,
                "base_pace": reg.intercept_
            }

    def predict_lap_time(self, compound: str, tyre_age: int) -> float:
        """Предсказывает время круга для конкретного возраста шины."""
        if compound not in self.models:
            # Дефолтный запасной расчет, если данных по компаунду не хватило
            return 95.0 + tyre_age * 0.1

        poly = self.models[compound]["poly"]
        reg = self.models[compound]["reg"]

        X = np.array([[tyre_age]])
        X_poly = poly.transform(X)
        return float(reg.predict(X_poly)[0])


def evaluate_pit_window(current_lap: int, total_laps: int, current_compound: str,
                        current_tyre_age: int, model: TyreDegradationModel,
                        safety_car: bool = False) -> dict:
    """
    Сравнивает две стратегии в реальном времени:
    Вариант А: Ограничиться продолжением текущего отрезка (Stay Out).
    Вариант Б: Заехать на пит-стоп на этом круге (Box This Lap) за новым Hard.
    """
    remaining_laps = total_laps - current_lap
    if remaining_laps <= 0:
        return {"action": "STAY_OUT", "time_delta": 0.0}

    # Потеря времени на пит-стопе в секундах
    # При обычном режиме трассы ~22 сек, под Safety Car / VSC ~12 сек
    pit_loss = 12.0 if safety_car else 22.0

    # 1. Считаем суммарное оставшееся время при STAY OUT (допустим еще 10 кругов на этих шинах)
    horizon = min(remaining_laps, 12)
    stay_out_time = sum(
        model.predict_lap_time(current_compound, current_tyre_age + i)
        for i in range(horizon)
    )

    # 2. Считаем суммарное время при BOX THIS LAP (переход на свежий Hard)
    box_time = pit_loss + sum(
        model.predict_lap_time("HARD", 1 + i)
        for i in range(horizon)
    )

    time_delta = stay_out_time - box_time  # Если > 0, то пит-стоп быстрее!

    if time_delta > 1.5:
        recommendation = "BOX THIS LAP"
        reason = f"Свежий Hard нивелирует пит-стоп и сбережет {abs(time_delta):.1f} сек за {horizon} кругов."
    else:
        recommendation = "STAY OUT"
        reason = f"Шины еще в рабочем окне. Заезд сейчас приведет к чистой потере {abs(time_delta):.1f} сек."

    return {
        "action": recommendation,
        "time_delta": round(time_delta, 2),
        "reason": reason
    }