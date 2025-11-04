import numpy as np
import pandas as pd
import sqlite3
from filterpy.kalman import KalmanFilter

def sequential_lobing_tracking():
    conn = sqlite3.connect("traffic_radar.db")
    df = pd.read_sql_query("SELECT * FROM Detections_CFAR", conn)

    results = []
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([[0.0],[0.0]])
    kf.F = np.array([[1.,1.],[0.,1.]])
    kf.H = np.array([[1.,0.]])
    kf.P *= 10.0
    kf.R = 0.05
    kf.Q = np.array([[0.001,0.],[0.,0.001]])

    beam_offset = 0.5  # deg beam step
    gain = 2.0         # calibration constant

    for time, frame in df.groupby("time"):
        # emulate two beam positions: left/right
        left_power  = np.mean(10 ** (frame["SNR_dB"].values / 10)) * (1 - beam_offset/10)
        right_power = np.mean(10 ** (frame["SNR_dB"].values / 10)) * (1 + beam_offset/10)
        ratio = (right_power - left_power) / (right_power + left_power)
        theta_est = gain * ratio
        kf.predict()
        kf.update(theta_est)
        est_angle = float(kf.x[0])

        for _, r in frame.iterrows():
            err = abs(r["azimuth"] - est_angle)
            results.append((r["time"], r["target_id"], r["range"],
                            r["azimuth"], est_angle, err, r["SNR_dB"]))

    df_out = pd.DataFrame(results, columns=[
        "time","target_id","range","true_azimuth","est_azimuth",
        "tracking_error","SNR_dB"
    ])
    df_out.to_sql("TrackingResults_Sequential", conn,
                  if_exists="replace", index=False)
    conn.close()
    print(f"Inserted {len(df_out)} sequential-lobing tracking results.")
    print(df_out.head())

if __name__ == "__main__":
    sequential_lobing_tracking()
