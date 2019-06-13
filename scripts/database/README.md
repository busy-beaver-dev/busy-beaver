# Database

Before we moved to a managed database service,
we used SQLite and then Postgres inside of a container.

This directory contains database tools that are not needed anymore

## Migrating from SQLite to Postgres

Using [pgloader](https://github.com/dimitri/pgloader) to migrate a SQLite database to Postgres.

## Steps

1. Install `pgloader` following [instructions on Github](https://github.com/dimitri/pgloader)
2. Use the [provided template](https://pgloader.readthedocs.io/en/latest/ref/sqlite.html), fill out your database migration requirements.
3. Run `pgloader sqlite_migration.load`

## Backup Postgres

Script that runs `pg_dump` and uploads resulting `.sql` file to S3.

### Reloading Database from Backup

[Postgres Docs](https://www.postgresql.org/docs/8.1/backup.html#BACKUP-DUMP-RESTORE)

```console
psql -U ${POSTGRES_USER} busy-beaver < [sql_dump]
```
