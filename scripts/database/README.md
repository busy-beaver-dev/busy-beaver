# Migrating from SQLite to Postgres

Using [pgloader](https://github.com/dimitri/pgloader) to migrate a SQLite database to Postgres.

## Steps

1. Install `pgloader` following [instructions on Github](https://github.com/dimitri/pgloader)
2. Use the [provided template](https://pgloader.readthedocs.io/en/latest/ref/sqlite.html), fill out your database migration requirements.
3. Run `pgloader sqlite_migration.load`
