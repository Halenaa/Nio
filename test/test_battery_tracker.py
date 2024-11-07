import random
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from services.battery_service import BatteryService
from database import SessionLocal
from database.models import BatteryExchangeTask


def generate_random_data():
    bid = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    vid = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    version = random.randint(1, 5)
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=random.randint(1, 12))
    return bid, vid, version, start_time, end_time


def test_generate_data():
    db_session = SessionLocal()
    service = BatteryService(db_session)
    on_load_records = {}  # 追踪 On-Load

    for i in range(200):
        bid, vid, version, start_time, end_time = generate_random_data()
        station_id = random.randint(1, 10)
        comments = f"Generated event for bid {bid}"

        # 每隔一条生成 On-Load 和 Off-Load 配对
        if i % 2 == 0:
            print(f"Adding On-Load for bid {bid} and vid {vid} at {start_time}")
            service.add_battery_exchange_task(bid, vid, version, station_id, "On-Load", start_time, comments)
            on_load_records[bid] = start_time
        else:

            if bid in on_load_records:
                print(f"Adding Off-Load for bid {bid} and vid {vid} at {end_time}")
                service.add_battery_exchange_task(bid, vid, version, station_id, "Off-Load", end_time, comments)
                del on_load_records[bid]
            else:
                print(f"Adding single On-Load for bid {bid} and vid {vid} at {start_time}")
                service.add_battery_exchange_task(bid, vid, version, station_id, "On-Load", start_time, comments)
                on_load_records[bid] = start_time

    tasks = db_session.query(BatteryExchangeTask).all()
    for task in tasks:
        print(
            f"{task.event}: bid={task.bid}, vid={task.vid}, battery_version={task.battery_version}, event_time={task.event_time}, comments={task.comments}")

    db_session.close()


if __name__ == "__main__":
    test_generate_data()
