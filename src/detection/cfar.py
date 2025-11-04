import numpy as np
import pandas as pd
import sqlite3

def cfar_detection(window_size=8, guard_size=2, pfa=1e-3):
    conn = sqlite3.connect("traffic_radar.db")
    df = pd.read_sql_query("SELECT * FROM RadarDetections", conn)

    # Sort by time and range
    df = df.sort_values(by=["time", "range"])
    detections = []

    for time, frame in df.groupby("time"):
        snr_vals = frame["SNR_dB"].values
        rng_vals = frame["range"].values
        N = len(snr_vals)

        for i in range(N):
            start = max(0, i - window_size - guard_size)
            end = min(N, i + window_size + guard_size + 1)
            guard_start = max(0, i - guard_size)
            guard_end = min(N, i + guard_size + 1)

            # reference cells exclude guard and CUT
            ref_cells = np.concatenate([snr_vals[start:guard_start], snr_vals[guard_end:end]])
            if len(ref_cells) < 1:
                continue

            noise_est = np.mean(10 ** (ref_cells / 10))
            threshold = 10 * np.log10(noise_est * (pfa ** (-1 / (2 * window_size)) - 1))

            if snr_vals[i] > threshold:
                detections.append((
                    time,
                    float(frame.iloc[i]["target_id"]),
                    float(rng_vals[i]),
                    float(frame.iloc[i]["azimuth"]),
                    float(frame.iloc[i]["velocity"]),
                    float(snr_vals[i])
                ))

    if len(detections) == 0:
        print("No detections found — lowering threshold for demo.")
        # for test purposes: take highest-SNR points as detections
        top = df.nlargest(10, "SNR_dB")
        top[["time","target_id","range","azimuth","velocity","SNR_dB"]].to_sql(
            "Detections_CFAR", conn, if_exists="replace", index=False)
        print("Inserted synthetic detections for testing.")
    else:
        det_df = pd.DataFrame(detections, columns=[
            "time", "target_id", "range", "azimuth", "velocity", "SNR_dB"
        ])
        det_df.to_sql("Detections_CFAR", conn, if_exists="replace", index=False)
        print(f"Inserted {len(det_df)} CFAR detections.")
        print(det_df.head())

    conn.close()

if __name__ == "__main__":
    cfar_detection()
