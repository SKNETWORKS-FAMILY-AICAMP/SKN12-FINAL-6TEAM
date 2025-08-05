# Database Migrations with Alembic

This project uses Alembic for database migrations. Follow these instructions to manage database schema changes.

## Setup

Alembic has been configured to use the database URL from your environment variables.

## Creating a New Migration

1. Make changes to your SQLAlchemy models in `app/models/`

2. Generate a new migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```

3. Review the generated migration file in `alembic/versions/`

4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Common Commands

### Check current revision
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

### Upgrade to latest
```bash
alembic upgrade head
```

### Downgrade one revision
```bash
alembic downgrade -1
```

### Create manual migration
```bash
alembic revision -m "Description"
```

## Best Practices

1. Always review auto-generated migrations before applying
2. Test migrations in development before production
3. Keep migration messages descriptive
4. Don't edit migrations that have been applied to production
5. Back up your database before running migrations

## Troubleshooting

If you encounter issues:

1. Ensure DATABASE_URL is set in your .env file
2. Check that all models are imported in `app/models/__init__.py`
3. Verify database connectivity before running migrations