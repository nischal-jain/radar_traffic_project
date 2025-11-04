import numpy as np
import pandas as pd
import sqlite3
from filterpy.kalman import KalmanFilter

def conical_scan_tracking():
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

    # scanning parameters
    scan_rate = 10.0       # degrees/second
    amplitude = 0.5        # cone radius (degrees)
    gain = 5.0             # scaling factor for error

    times = sorted(df["time"].unique())
    for t in times:
        frame = df[df["time"] == t]
        phase = (t * scan_rate) % 360
        # synthetic amplitude modulation signal
        mod_signal = amplitude * np.cos(np.deg2rad(phase))
        theta_est = gain * mod_signal / 10.0

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
    df_out.to_sql("TrackingResults_Conical", conn,
                  if_exists="replace", index=False)
    conn.close()
    print(f"Inserted {len(df_out)} conical-scan tracking results.")
    print(df_out.head())

if __name__ == "__main__":
    conical_scan_tracking()
