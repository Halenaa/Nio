# services/export_data.py
import csv
from database import SessionLocal
from database.models import BatteryExchangeTask, Battery

def export_battery_assignments_to_csv(file_name):
    db_session = SessionLocal()

    assignments = db_session.query(BatteryExchangeTask).all()

    with open(file_name, mode="w", newline="") as csv_file:
        fieldnames = ["task_id", "bid", "vid", "battery_version", "station_id", "event", "event_time", "start_time", "end_time", "comments"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for assignment in assignments:
            battery = db_session.query(Battery).filter(Battery.bid == assignment.bid).first()
            writer.writerow({
                "task_id": assignment.task_id,
                "bid": assignment.bid,
                "vid": assignment.vid,
                "battery_version": battery.battery_version if battery else "N/A",
                "station_id": assignment.station_id,
                "event": assignment.event,
                "event_time": assignment.event_time,
                "start_time": assignment.start_time,
                "end_time": assignment.end_time,
                "comments": assignment.comments
            })

    db_session.close()
    print(f"Data exported to {file_name}")
