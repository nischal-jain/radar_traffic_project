import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time

def cognitive_radar_cycle(iterations=10):
    conn = sqlite3.connect("traffic_radar.db")

    # Ensure configuration table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS RadarConfig (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            iteration INTEGER,
            pulse_width REAL,
            detection_threshold REAL,
            avg_snr REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Initial radar parameters
    pulse_width = 1e-6
    freq = 10e9  # 10 GHz
    c = 3e8
    noise_level = 0.5
    detection_threshold = 2.0

    for i in range(iterations):
        print(f"\nCycle {i+1}/{iterations}")
        t = np.linspace(0, pulse_width, 1000)
        tx_signal = np.sin(2 * np.pi * freq * t)

        # Simulate target reflection with random distance and noise
        target_distance = np.random.uniform(100, 1000)
        delay = 2 * target_distance / c
        noise = np.random.normal(0, noise_level, len(t))
        rx_signal = np.roll(tx_signal, int(delay * len(t) / pulse_width)) + noise

        snr = np.mean(tx_signal**2) / np.mean(noise**2)
        print(f"Target Range: {target_distance:.1f} m | SNR: {snr:.2f}")

        # Cognitive decision-making (adapt pulse width and detection threshold)
        if snr < detection_threshold:
            pulse_width *= 1.5
            detection_threshold *= 0.9
            print(f"Low SNR → Increasing pulse width to {pulse_width:.2e}s")
        elif snr > detection_threshold * 4:
            pulse_width *= 0.8
            detection_threshold *= 1.1
            print(f"High SNR → Reducing pulse width to {pulse_width:.2e}s")

        # Log configuration to database
        conn.execute("""
            INSERT INTO RadarConfig (iteration, pulse_width, detection_threshold, avg_snr)
            VALUES (?, ?, ?, ?)
        """, (i+1, pulse_width, detection_threshold, snr))
        conn.commit()

        time.sleep(0.3)

    conn.close()
    print("\nCognitive radar feedback complete — parameters saved to RadarConfig table.")

    # Visualize adaptation
    df = pd.read_sql_query("SELECT * FROM RadarConfig", sqlite3.connect("traffic_radar.db"))
    plt.figure(figsize=(8,4))
    plt.plot(df["iteration"], df["pulse_width"]*1e6, label="Pulse Width (µs)")
    plt.plot(df["iteration"], df["detection_threshold"], label="Detection Threshold")
    plt.xlabel("Cycle")
    plt.ylabel("Value")
    plt.title("Cognitive Radar Parameter Adaptation")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    cognitive_radar_cycle(iterations=10)
