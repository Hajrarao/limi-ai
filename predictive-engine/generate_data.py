import pandas as pd
import numpy as np
import random

np.random.seed(42)
n = 2000

data = {
    "voltage": np.random.normal(220, 15, n),
    "internal_temp": np.random.normal(45, 10, n),
    "usage_hours": np.random.uniform(0, 24, n),
    "external_temp": np.random.normal(30, 8, n),   # weather data
    "humidity": np.random.uniform(20, 90, n),
    "load_percentage": np.random.uniform(10, 100, n),
}

df = pd.DataFrame(data)

# Feature Engineering
df["temp_diff"] = df["internal_temp"] - df["external_temp"]
df["voltage_deviation"] = abs(df["voltage"] - 220)
df["heat_load_index"] = df["internal_temp"] * df["load_percentage"] / 100

# Label: failure if internal_temp > 65 OR voltage deviation > 30 AND usage > 20hrs
df["failure"] = (
    (df["internal_temp"] > 65) |
    ((df["voltage_deviation"] > 30) & (df["usage_hours"] > 20))
).astype(int)

df.to_csv("sensor_data.csv", index=False)
print(f"Dataset created: {len(df)} rows, {df['failure'].mean()*100:.1f}% failure rate")