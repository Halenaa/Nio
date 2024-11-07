
import os

# 配置数据库连接信息
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./battery_records.db")

# Redis连接信息
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 30))
