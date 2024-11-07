
from database import SessionLocal
from database.models import BatteryExchangeTask, Battery, BatteryVersion
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

class BatteryService:
    def __init__(self, db_session=None):
        self.db = db_session or SessionLocal()

    def add_battery_exchange_task(self, bid, vid, version, station_id, event, event_time, comments=None):
        try:
            self.update_battery_version(bid, version)

            if event == "Off-Load":
                on_load_task = self.db.query(BatteryExchangeTask).filter(
                    BatteryExchangeTask.bid == bid,
                    BatteryExchangeTask.vid == vid,
                    BatteryExchangeTask.event == "On-Load",
                    BatteryExchangeTask.end_time == None
                ).first()

                if on_load_task:
                    on_load_task.end_time = event_time
                    on_load_task.comments = "顺利"
                    self.db.commit()
                    print(f"Updated end_time for On-Load task {on_load_task.task_id} with Off-Load event at {event_time}")
                else:
                    comments = "异常: 无对应 On-Load 任务"

            task = BatteryExchangeTask(
                bid=bid,
                vid=vid,
                station_id=station_id,
                event=event,
                event_time=event_time,
                start_time=event_time if event == "On-Load" else None,
                end_time=event_time if event == "Off-Load" and on_load_task else None,  # 只有找到对应 On-Load 时才添加 end_time
                comments=comments
            )
            self.db.add(task)
            self.db.commit()
            print(f"Added {event} task for bid {bid} at {event_time}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error(f"Database error while adding task for {bid}: {e}")
            raise RuntimeError("Failed to add battery exchange task due to database error")

    def update_battery_version(self, bid, new_version):
        battery = self.db.query(Battery).filter(Battery.bid == bid).first()
        if battery and battery.battery_version < new_version:
            battery.battery_version = new_version
            self.db.commit()
            print(f"Updated battery version for {bid} to {new_version}")
