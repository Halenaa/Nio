from database import SessionLocal
from services.battery_service import BatteryService
from services.data_generator import generate_test_data
import sys

def initialize_service():
    db_session = SessionLocal()
    return BatteryService(db_session)

if __name__ == "__main__":
    service = initialize_service()


    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("Generating test data...")

            generate_test_data(service)
            print("Test data generated successfully.")
        elif sys.argv[1] == "export":
            from services.export_data import export_battery_assignments_to_csv
            export_battery_assignments_to_csv("battery_history.csv")
            print("Data exported to battery_history.csv.")
        else:
            print("Unknown command.")
    else:
        print("Usage: python main.py [command]")
