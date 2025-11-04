import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px

DB = "traffic_radar.db"

def load_data(table):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def predict_collisions(df):
    alerts = []
    for _, r in df.iterrows():
        v_rel = abs(r["velocity"])  # relative speed
        if v_rel < 0.1:
            continue
        ttc = r["range"] / v_rel  # Time To Collision
        level = (
            "HIGH" if ttc < 2 else
            "MEDIUM" if ttc < 4 else
            "LOW"
        )
        alerts.append((r["time"], r["target_id"], r["range"], v_rel, ttc, level))
    return pd.DataFrame(alerts, columns=["time","target_id","range","rel_vel","TTC","alert_level"])

def main():
    st.title("Radar-Based Traffic Monitoring and Collision Warning")
    st.sidebar.header("Controls")
    method = st.sidebar.selectbox(
        "Select Tracking Method",
        ["Monopulse","Sequential","Conical"]
    )

    df_track = load_data(f"TrackingResults_{method}")
    df_det = load_data("Detections_CFAR")

    st.subheader("Tracking Overview")
    st.write(f"Loaded {len(df_track)} tracking samples for {method} radar.")
    fig = px.scatter(df_track, x="time", y="tracking_error",
                     color="SNR_dB", title="Tracking Error over Time")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Collision Prediction")
    df_alerts = predict_collisions(df_det)
    st.dataframe(df_alerts.head())

    fig2 = px.scatter(df_alerts, x="time", y="TTC",
                      color="alert_level",
                      title="Predicted Time-To-Collision (TTC)")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Alert Summary")
    st.bar_chart(df_alerts["alert_level"].value_counts())

if __name__ == "__main__":
    main()
