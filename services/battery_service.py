# services/battery_service.py
from database import SessionLocal
from database.models import BatteryExchangeTask, Battery, BatteryVersion
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import logging

class BatteryService:
    def __init__(self, db_session=None):
        self.db = db_session or SessionLocal()

    def add_battery_exchange_task(self, bid, vid, version, station_id, event, event_time, comments=None):
        try:
            # 检查并更新电池版本
            self.update_battery_version(bid, version)

            # 初始化comments内容
            comments = comments or "顺利"  # 默认设为“顺利”，除非有异常情况

            if event == "Off-Load":
                # 查找未结束的 On-Load 任务
                on_load_task = self.db.query(BatteryExchangeTask).filter(
                    BatteryExchangeTask.bid == bid,
                    BatteryExchangeTask.vid == vid,
                    BatteryExchangeTask.event == "On-Load",
                    BatteryExchangeTask.end_time == None
                ).first()

                if on_load_task:
                    # 将 Off-Load 的 event_time 设置为对应的 end_time
                    on_load_task.end_time = event_time
                    on_load_task.comments = "顺利"
                    comments = "顺利"  # Off-Load 事件顺利完成
                    self.db.commit()
                    print(f"Updated end_time for On-Load task {on_load_task.task_id} with Off-Load event at {event_time}")
                else:
                    # 无对应的 On-Load 任务，标记为失败
                    comments = "失败: 无对应 On-Load 任务"

            # 检查电池电量是否低于设定的范围
            if not self.check_battery_capacity(bid):
                comments = (comments or "") + " | 警报: 电量过低"

            # 检查频繁更换情况
            if self.is_battery_frequently_swapped(bid):
                comments = (comments or "") + " | 警报: 短时间内频繁更换"

            # 创建新的任务记录
            task = BatteryExchangeTask(
                bid=bid,
                vid=vid,
                station_id=station_id,
                event=event,
                event_time=event_time,
                start_time=event_time if event == "On-Load" else None,
                end_time=event_time if event == "Off-Load" and on_load_task else None,
                comments=comments
            )
            self.db.add(task)
            self.db.commit()
            print(f"Added {event} task for bid {bid} at {event_time} with comments: {comments}")
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

    def check_battery_capacity(self, bid, min_capacity=20):
        """检查电池容量，返回 False 如果低于允许的最低容量"""
        battery = self.db.query(Battery).filter(Battery.bid == bid).first()
        if battery and battery.capacity_kwh < min_capacity:
            print(f"Warning: Battery {bid} capacity is below minimum threshold.")
            return False
        return True

    def is_battery_frequently_swapped(self, bid, threshold=3, time_frame_minutes=30):
        """检查短时间内电池频繁更换"""
        recent_tasks = self.db.query(BatteryExchangeTask).filter(
            BatteryExchangeTask.bid == bid,
            BatteryExchangeTask.event_time >= datetime.utcnow() - timedelta(minutes=time_frame_minutes)
        ).count()

        if recent_tasks > threshold:
            print(f"Warning: Battery {bid} has been swapped {recent_tasks} times in the last {time_frame_minutes} minutes.")
            return True
        return False
