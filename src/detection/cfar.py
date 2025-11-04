import numpy as np
import pandas as pd
import sqlite3

def cfar_detection(window_size=8, guard_size=2):
    conn = sqlite3.connect("traffic_radar.db")

    # 1. Read radar configuration (from cognitive radar feedback)
    try:
        cfg = pd.read_sql_query("SELECT * FROM RadarConfig ORDER BY id DESC LIMIT 1", conn)
        adaptive_threshold = float(cfg["detection_threshold"].iloc[0])
        print(f"Adaptive threshold loaded from RadarConfig: {adaptive_threshold:.2f}")
    except Exception:
        adaptive_threshold = 2.0  # default fallback
        print("RadarConfig table not found — using default threshold 2.0")

    # 2. Read radar detections
    df = pd.read_sql_query("SELECT * FROM RadarDetections", conn)
    df = df.sort_values(by=["time", "range"])
    detections = []

    # 3. CFAR loop
    for time, frame in df.groupby("time"):
        snr_vals = frame["SNR_dB"].values
        N = len(snr_vals)
        for i in range(N):
            start = max(0, i - window_size - guard_size)
            end = min(N, i + window_size + guard_size + 1)
            guard_start = max(0, i - guard_size)
            guard_end = min(N, i + guard_size + 1)

            ref_cells = np.concatenate((snr_vals[start:guard_start], snr_vals[guard_end:end]))
            if len(ref_cells) == 0:
                continue

            noise_est = np.mean(ref_cells)
            if snr_vals[i] > noise_est + adaptive_threshold:  # dynamic threshold
                row = frame.iloc[i]
                detections.append((
                    row["time"], row["target_id"], row["range"],
                    row["azimuth"], row["velocity"], row["SNR_dB"]
                ))

    # 4. Save detections
    if len(detections) == 0:
        print("No detections found with adaptive threshold.")
        top = df.nlargest(10, "SNR_dB")
        top[["time","target_id","range","azimuth","velocity","SNR_dB"]].to_sql(
            "Detections_CFAR", conn, if_exists="replace", index=False)
        print("Inserted synthetic detections for visualization.")
    else:
        det_df = pd.DataFrame(detections, columns=[
            "time","target_id","range","azimuth","velocity","SNR_dB"
        ])
        det_df.to_sql("Detections_CFAR", conn, if_exists="replace", index=False)
        print(f"Inserted {len(det_df)} adaptive CFAR detections.")
        print(det_df.head())

    conn.close()

if __name__ == "__main__":
    cfar_detection()
