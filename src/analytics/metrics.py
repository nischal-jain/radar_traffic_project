import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def compare_tracking_methods():
    conn = sqlite3.connect("traffic_radar.db")
    tables = {
        "Monopulse": "TrackingResults_Monopulse",
        "Sequential": "TrackingResults_Sequential",
        "Conical": "TrackingResults_Conical",
    }
    stats = []

    for name, table in tables.items():
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if len(df) == 0:
            continue
        mean_err = df["tracking_error"].mean()
        rms_err = (df["tracking_error"]**2).mean()**0.5
        avg_snr = df["SNR_dB"].mean()
        stats.append((name, mean_err, rms_err, avg_snr))

    conn.close()

    results = pd.DataFrame(stats, columns=["Method","MeanError","RMSError","AvgSNR"])
    print("\nPerformance Summary:\n", results)

    # plot error comparison
    plt.figure()
    plt.bar(results["Method"], results["MeanError"])
    plt.title("Mean Tracking Error Comparison")
    plt.ylabel("Error (deg)")
    plt.xlabel("Tracking Method")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    compare_tracking_methods()
