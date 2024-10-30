import os

POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


TOKEN_TTL = int(os.getenv("TOKEN_TTL", 60))

SQL_DEBUG = os.getenv("SQL_DEBUG", "False").lower() in ("true", "1")
DEFAULT_ROLE = os.getenv("DEFAULT_ROLE", "user")

# settings for email
MAIL_USERNAME = "6021185@mail.ru"
MAIL_PASSWORD = "gczmmbasyXGXRCsZprZk"
MAIL_FROM = "6021185@mail.ru"
MAIL_PORT = 465
MAIL_SERVER = "smtp.mail.ru"
MAIL_SSL_TLS = True

# REDIS
REDIS_HOST="localhost"
REDIS_PORT="6378"

CELERY_BROKER_URL = 'redis://localhost:6378/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6378/0'
