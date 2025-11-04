import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_report():
    conn = sqlite3.connect("traffic_radar.db")
    summary = []
    for table in [
        "TrackingResults_Monopulse",
        "TrackingResults_Sequential",
        "TrackingResults_Conical"
    ]:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if len(df) == 0:
            continue
        mean_err = df["tracking_error"].mean()
        rms_err = (df["tracking_error"]**2).mean()**0.5
        summary.append((table, round(mean_err,2), round(rms_err,2), len(df)))
    conn.close()

    doc = SimpleDocTemplate("Radar_Project_Report.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Radar-Based Traffic Monitoring and Collision Warning</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Generated automatically from the radar simulation database.", styles["Normal"]))
    story.append(Spacer(1, 12))

    data = [["Tracking Mode","Mean Error (°)","RMS Error (°)","Samples"]] + summary
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.gray),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1,12))
    story.append(Paragraph("This report summarizes the comparative performance of Monopulse, Sequential, and Conical-scan tracking techniques implemented entirely in software.", styles["Normal"]))

    doc.build(story)
    print("Report generated: Radar_Project_Report.pdf")

if __name__ == "__main__":
    generate_report()
