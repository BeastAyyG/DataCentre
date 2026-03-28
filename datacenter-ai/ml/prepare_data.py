import pandas as pd
import json
from pathlib import Path

raw_dir = Path("data/raw")
smd_dir = raw_dir / "OmniAnomaly" / "ServerMachineDataset"
hot_csv = raw_dir / "hot_corridor.csv"
cool_csv = raw_dir / "cooling_control.csv"

cols = [
    "inlet_temp_c",
    "outlet_temp_c",
    "power_kw",
    "airflow_cfm",
    "humidity_pct",
    "cpu_util_pct",
]

# We just load machine-1-1 for a quick start, which has ~28k train and ~28k test points
train_path = smd_dir / "train" / "machine-1-1.txt"
test_path = smd_dir / "test" / "machine-1-1.txt"
label_path = smd_dir / "test_label" / "machine-1-1.txt"

df_hot = None

if train_path.exists() and test_path.exists() and label_path.exists():
    print("Loading OmniAnomaly SMD dataset...")

    # Load Train
    df_train = pd.read_csv(train_path, header=None)
    df_train = df_train.iloc[:, :6]  # Take first 6 dims
    df_train.columns = cols
    df_train["anomaly"] = 0
    df_train["is_train"] = 1

    # Load Test
    df_test = pd.read_csv(test_path, header=None)
    df_test = df_test.iloc[:, :6]
    df_test.columns = cols
    df_labels = pd.read_csv(label_path, header=None)
    df_test["anomaly"] = df_labels[0].values
    df_test["is_train"] = 0

    # Combine
    df_hot = pd.concat([df_train, df_test], ignore_index=True)

    # Generate fake timestamps (5 minute intervals)
    start_time = pd.to_datetime("2026-01-01 00:00:00")
    df_hot["timestamp"] = [
        start_time + pd.Timedelta(minutes=5 * i) for i in range(len(df_hot))
    ]

    df_hot.to_csv(hot_csv, index=False)
    print(f"Saved {hot_csv} with SMD data: {len(df_hot)} rows.")
else:
    print(f"WARNING: SMD data not found in {smd_dir}")

# create dummy cooling control if not exists
if not cool_csv.exists() and df_hot is not None:
    df_cool = pd.DataFrame(
        {
            "timestamp": df_hot["timestamp"][:1000],
            "cooling_setpoint_c": 22.0,
            "inlet_temp_c": df_hot["inlet_temp_c"][:1000],
        }
    )
    df_cool.to_csv(cool_csv, index=False)
elif not cool_csv.exists():
    # Generate minimal dummy data if SMD is not available
    start_time = pd.to_datetime("2026-01-01 00:00:00")
    df_cool = pd.DataFrame(
        {
            "timestamp": [
                start_time + pd.Timedelta(minutes=5 * i) for i in range(1000)
            ],
            "cooling_setpoint_c": [22.0] * 1000,
            "inlet_temp_c": [20.0 + (i % 10) * 0.5 for i in range(1000)],
        }
    )
    df_cool.to_csv(cool_csv, index=False)

print("Data preprocessed!")
