import numpy as np
import pandas as pd
import sqlite3

def generate_targets(n_targets=2, t_end=10, dt=0.1):
    times = np.arange(0, t_end, dt)
    rows = []
    for tid in range(n_targets):
        range0 = np.random.uniform(50, 200)   # initial distance (m)
        v = np.random.uniform(-10, -5)        # m/s toward radar
        az = np.random.uniform(-5, 5)         # degrees
        for t in times:
            range_t = range0 + v * t
            az_t = az + np.random.normal(0, 0.1)
            elev_t = 0
            rcs = np.random.uniform(5, 15)
            noise = np.random.uniform(-90, -70)
            rows.append((t, tid, range_t, az_t, elev_t, v, rcs, noise))
    df = pd.DataFrame(rows, columns=[
        "time","true_id","true_range","true_azimuth",
        "true_elevation","true_v","rcs","noise_power"
    ])
    conn = sqlite3.connect("traffic_radar.db")
    df.to_sql("TargetData", conn, if_exists="append", index=False)
    conn.close()
    print("Inserted", len(df), "rows into TargetData.")

if __name__ == "__main__":
    generate_targets()
