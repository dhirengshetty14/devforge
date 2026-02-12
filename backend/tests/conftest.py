import os

# Baseline env for tests that import app settings at module import time.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/devforge")
os.environ.setdefault("SYNC_DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/devforge")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_devforge_1234567890")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
