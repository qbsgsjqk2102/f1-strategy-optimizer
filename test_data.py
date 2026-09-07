import os
import fastf1

cache_dir = os.path.join(os.getcwd(), "data")
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

print("1. Подключение к сессии...")
session = fastf1.get_session(2023, "Bahrain", "R")

print("2. Загрузка данных (только круги)...")
# telemetry=False и weather=False ускоряют загрузку в 10 раз (качается ~2 МБ вместо 150 МБ)
session.load(telemetry=False, weather=False, messages=False)

print(f"3. Успешно! Всего загружено кругов: {len(session.laps)}")
print(session.laps[["Driver", "LapNumber", "LapTime", "Compound"]].head())