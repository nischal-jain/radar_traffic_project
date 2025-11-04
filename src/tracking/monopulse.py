import numpy as np
import pandas as pd
import sqlite3
from filterpy.kalman import KalmanFilter

def monopulse_tracking():
    conn = sqlite3.connect("traffic_radar.db")
    # Read detections and raw channel data
    df_det = pd.read_sql_query("SELECT * FROM Detections_CFAR", conn)
    df_raw = pd.read_sql_query("SELECT time,target_id,V_sum,V_diff FROM RadarDetections", conn)

    merged = pd.merge(df_det, df_raw, on=["time","target_id"], how="left")
    results = []

    # Initialize a small 1-D Kalman filter for angle smoothing
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([[0.0],[0.0]])     # [angle, rate]
    kf.F = np.array([[1.,1.],[0.,1.]])
    kf.H = np.array([[1.,0.]])
    kf.P *= 10.0
    kf.R = 0.05
    kf.Q = np.array([[0.001,0.],[0.,0.001]])

    K_gain = 10.0   # calibration constant

    for _, r in merged.iterrows():
        if r["V_sum"] is None or r["V_diff"] is None:
            continue
        ratio = r["V_diff"] / (r["V_sum"] + 1e-9)
        theta_est = K_gain * ratio
        # Kalman update
        kf.predict()
        kf.update(theta_est)
        est_angle = float(kf.x[0])
        error = abs(r["azimuth"] - est_angle)
        results.append((r["time"], r["target_id"], r["range"],
                        r["azimuth"], est_angle, error, r["SNR_dB"]))

    df_out = pd.DataFrame(results, columns=[
        "time","target_id","range","true_azimuth","est_azimuth",
        "tracking_error","SNR_dB"
    ])
    df_out.to_sql("TrackingResults_Monopulse", conn,
                  if_exists="replace", index=False)
    conn.close()
    print(f"Inserted {len(df_out)} monopulse tracking results.")
    print(df_out.head())

if __name__ == "__main__":
    monopulse_tracking()
