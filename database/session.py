from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # 可替换为实际数据库路径
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
