# SentinelAI Database Migrations

For this MVP, table schemas are automatically created on application startup via:
```python
Base.metadata.create_all(bind=engine)
```

In a production environment, Alembic would track schema migrations:
```bash
alembic init backend/app/database/migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```
