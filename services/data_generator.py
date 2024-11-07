import random
from services.battery_service import BatteryService
from database import SessionLocal
from database.models import BatteryExchangeTask
from datetime import datetime, timedelta

# 随机生成电池和车辆数据,时间组合，电量设置，报警，频繁更换等
def generate_random_data():
    bid = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    vid = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    version = random.randint(1, 5)

    time_type = random.choices(['start_only', 'end_only', 'both', 'none'], [0.15, 0.15, 0.6, 0.1])[0]
    start_time = datetime.now() if time_type in ['start_only', 'both'] else None
    end_time = (start_time + timedelta(hours=random.randint(1, 12))
                if start_time and time_type == 'both' else
                (datetime.now() if time_type == 'end_only' else None))

    capacity_kwh = random.choice([75, 100, 15, 10, 5])
    return bid, vid, version, start_time, end_time, capacity_kwh


def generate_test_data(service, record_count=150):
    db_session = SessionLocal()

    db_session.query(BatteryExchangeTask).delete()
    db_session.commit()

    for i in range(record_count):
        bid, vid, version, start_time, end_time, capacity_kwh = generate_random_data()
        station_id = random.randint(1, 10)
        comments = ""

        if capacity_kwh < 20:
            comments = "警报: 电量过低"

        if random.random() < 0.2:
            freq_change_time = start_time or datetime.now()
            for j in range(4):
                freq_change_time += timedelta(minutes=5)
                comments = "警报: 短时间内频繁更换" if "警报" not in comments else comments
                service.add_battery_exchange_task(
                    bid, vid, version, station_id,
                    "On-Load" if j % 2 == 0 else "Off-Load",
                    freq_change_time,
                    comments=comments
                )
            continue

        if random.random() < 0.2:
            comments = "无效事件测试"
            service.add_battery_exchange_task(bid, vid, version, station_id, "Off-Load", end_time or datetime.now(),
                                              comments=comments)
            continue

        if start_time and not end_time:
            service.add_battery_exchange_task(bid, vid, version, station_id, "On-Load", start_time,
                                              comments=comments or "顺利")
        elif start_time and end_time:
            service.add_battery_exchange_task(bid, vid, version, station_id, "On-Load", start_time,
                                              comments=comments or "顺利")
            service.add_battery_exchange_task(bid, vid, version, station_id, "Off-Load", end_time, comments="顺利")
        else:
            comments = "失败: 无效事件"
            service.add_battery_exchange_task(bid, vid, version, station_id,
                                              "On-Load" if random.random() < 0.5 else "Off-Load", datetime.now(),
                                              comments=comments)

    db_session.commit()
    db_session.close()
    print("Test data generated with randomized events, low battery alerts, frequent swap alerts, and invalid events.")



if __name__ == "__main__":
    service = BatteryService()
    generate_test_data(service)
