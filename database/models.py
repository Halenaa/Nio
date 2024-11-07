from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Battery(Base):
    __tablename__ = 'battery'
    id = Column(Integer, primary_key=True, index=True)
    bid = Column(String, unique=True, nullable=False)
    battery_version = Column(Integer, nullable=False)
    capacity_kwh = Column(Integer, nullable=False, default=75)
    current_vehicle_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    last_update = Column(DateTime, default=datetime.utcnow)

class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Column(Integer, primary_key=True, index=True)
    vid = Column(String, unique=True, nullable=False)
    model = Column(String)
    owner_id = Column(Integer)

class BatteryExchangeTask(Base):
    __tablename__ = 'battery_exchange_task'
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    bid = Column(String, ForeignKey('battery.bid'))
    vid = Column(String, ForeignKey('vehicle.vid'))
    station_id = Column(Integer)
    event = Column(String)  # On-Load / Off-Load
    event_time = Column(DateTime, default=datetime.utcnow)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)

class BatteryVersion(Base):
    __tablename__ = 'battery_version'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bid = Column(String, ForeignKey('battery.bid'))
    version = Column(Integer, nullable=False)
    update_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)

# 创建表
Base.metadata.create_all(engine)
