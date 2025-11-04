import numpy as np
import pandas as pd
import sqlite3

# constants
C = 3e8               # speed of light (m/s)
FREQ = 10e9           # 10 GHz radar
LAMBDA = C / FREQ
PT = 1.0              # transmitted power (W)
G = 30                # antenna gain (linear scale)
K = 1.38e-23
T0 = 290              # noise temperature (K)
B = 1e6               # bandwidth (Hz)

def radar_equation(range_m, rcs):
    """Simple radar range equation to compute received power (W)."""
    num = PT * (G**2) * (LAMBDA**2) * rcs
    den = (4 * np.pi)**3 * (range_m**4)
    return num / den

def generate_echoes():
    conn = sqlite3.connect("traffic_radar.db")
    df = pd.read_sql_query("SELECT * FROM TargetData", conn)

    results = []
    for _, row in df.iterrows():
        Pr = radar_equation(row["true_range"], row["rcs"])
        noise = K * T0 * B
        snr = 10 * np.log10(Pr / noise)
        # Create sum and difference channel voltages for monopulse simulation
        theta_err = np.deg2rad(row["true_azimuth"])
        V_sum = np.sqrt(Pr) * np.cos(theta_err) + np.random.normal(0, 0.01)
        V_diff = np.sqrt(Pr) * np.sin(theta_err) + np.random.normal(0, 0.01)
        results.append((
            row["time"], row["true_id"], row["true_range"],
            row["true_azimuth"], row["true_v"], snr, V_sum, V_diff
        ))

    echo_df = pd.DataFrame(results, columns=[
        "time", "target_id", "range", "azimuth",
        "velocity", "SNR_dB", "V_sum", "V_diff"
    ])

    echo_df.to_sql("RadarDetections", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Inserted {len(echo_df)} radar echo samples.")

if __name__ == "__main__":
    generate_echoes()
