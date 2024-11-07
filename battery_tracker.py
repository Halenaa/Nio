from database.models import Battery, Vehicle, BatteryAssignment, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatteryTracker:
    def __init__(self, db_session=None):
        self.db = db_session or SessionLocal()

    def validate_and_clean_input(self, bid, vid, version, start_time, end_time=None):

        if not bid or len(bid) != 6:
            return None, None, None, None, {"detail": "Invalid battery ID"}

        if not vid or len(vid) != 6:
            return None, None, None, None, {"detail": "Invalid vehicle ID"}

        if not isinstance(version, int):
            return None, None, None, None, {"detail": "Invalid version type"}

        if end_time and end_time <= start_time:
            return bid, vid, version, start_time, {"detail": "end_time must be after start_time"}

        return bid, vid, version, start_time, end_time

    def add_battery(self, bid, vid, version, start_time, end_time=None):

        bid, vid, version, start_time, error = self.validate_and_clean_input(bid, vid, version, start_time, end_time)
        if error:
            return error


        battery = self.db.query(Battery).filter(Battery.bid == bid).first()
        if not battery:
            battery = Battery(bid=bid, battery_version=version, capacity_kwh=75)  # 假定的容量
            self.db.add(battery)

        vehicle = self.db.query(Vehicle).filter(Vehicle.vid == vid).first()
        if not vehicle:
            vehicle = Vehicle(vid=vid, model="ModelX", owner_id=1)  # 假定的车型和车主ID
            self.db.add(vehicle)

        assignment = BatteryAssignment(battery=battery, vehicle=vehicle, start_time=start_time, end_time=end_time)
        self.db.add(assignment)
        self.db.commit()
        return {'message': 'Record added successfully'}

        assignments = (
            self.db.query(BatteryAssignment)
            .join(Battery)
            .join(Vehicle)
            .all()
        )


        with open(file_name, mode="w", newline="") as csv_file:
            fieldnames = ["battery_id", "battery_version", "vehicle_id", "start_time", "end_time"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()


            for assignment in assignments:
                writer.writerow({
                    "battery_id": assignment.battery.bid,
                    "battery_version": assignment.battery.version,
                    "vehicle_id": assignment.vehicle.vid,
                    "start_time": assignment.start_time,
                    "end_time": assignment.end_time
                })

        print(f"Data exported to {file_name}")


if __name__ == "__main__":
    tracker = BatteryTracker()
    tracker.export_battery_assignments_to_csv()
