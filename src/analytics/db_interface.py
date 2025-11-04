import sqlite3
import pandas as pd

def preview_table(table, n=5):
    conn = sqlite3.connect("traffic_radar.db")
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {n}", conn)
    conn.close()
    return df

if __name__ == "__main__":
    print(preview_table("Detections_CFAR"))
