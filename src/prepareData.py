import pandas as pd

# Load dataset
df = pd.read_csv('clean_operation_log.csv', header=0, names=["Timestamp", "State", "X", "Y", "Z", "Proximity", "Gripper"])

# boolean to binary
df['Proximity'] = df['Proximity'].map({False: 0, True: 1})
df['Gripper'] = df['Gripper'].map({False: 0, True: 1})

# converting Timestamp to datetime and extract features
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
df['Timestamp'] = df['Timestamp'].astype('int64') // 10**9  # Convert to milliseconds


# Now df['Timestamp'] contains datetime objects for further processing
print(df.head())


# anomaly labelling based on known injection timestamp - printed by client
df['Anomaly'] = 0

x_anomaly_start = pd.to_datetime('2024-04-28 11:45:46.751803').timestamp()
x_anomaly_end = pd.to_datetime('2024-04-28 12:10:46.875127').timestamp()

y_anomaly_start = pd.to_datetime('2024-04-28 11:10:08.784189').timestamp()
y_anomaly_end = pd.to_datetime('2024-04-28 11:35:08.939258').timestamp()

z_anomaly_start = pd.to_datetime('2024-04-28 12:21:37.199814').timestamp()
z_anomaly_end = pd.to_datetime('2024-04-28 12:46:37.316787').timestamp()

print(x_anomaly_start)
print(x_anomaly_end)

df.loc[df['Timestamp'].between(x_anomaly_start, x_anomaly_end), 'Anomaly'] = 1
df.loc[df['Timestamp'].between(y_anomaly_start, y_anomaly_end ), 'Anomaly'] = 1
df.loc[df['Timestamp'].between(z_anomaly_start, z_anomaly_end ), 'Anomaly'] = 1


# cleaned and prepared data to CSV
df.to_csv('prepared_operation_log.csv', index=False)
