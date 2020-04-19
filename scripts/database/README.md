# Database

Before we moved to a managed database service,
we used SQLite and then Postgres inside of a container.

This directory contains database tools that are not needed anymore

## Copying Production Database to Local

[Postgres Docs](https://www.postgresql.org/docs/8.1/backup.html#BACKUP-DUMP-RESTORE)

1. Start up a postgres container in Kubernets

```console
kubectl run --generator=run-pod/v1 busybeaver-pg-dump --rm -i --tty --image postgres:11.7 --env DATABASE_URI=$(kubectl get secret busybeaver-production -o jsonpath="{.data.db-uri}" | base64 --decode) -- bash
```

2. Exec into container and run psql, save results locally

```console
kubectl exec -t busybeaver-pg-dump pg_dump $(kubectl get secret busybeaver-production -o jsonpath="{.data.db-uri}" | base64 --decode) > data_dump.sql
```

3. Load data in local database

```console
cat data_dump.sql | docker exec -i `docker-compose ps -q db` psql -U bbdev_user -d busy-beaver
```

## Migrating from SQLite to Postgres

When Busy Beaver first started out, it was a SQLite database. As the bot grow in scope, we migrated to Postgres. This was done using [pgloader](https://github.com/dimitri/pgloader), a tool that migrates SQLite databases to Postgres.

### Steps

1. Install `pgloader` following [instructions on Github](https://github.com/dimitri/pgloader)
2. Use the [provided template](https://pgloader.readthedocs.io/en/latest/ref/sqlite.html), fill out your database migration requirements.
3. Run `pgloader sqlite_migration.load`

```text
# sqlite_migration.load

load database
    from sqlite:///home/alysivji/busy-beaver/busy_beaver.db
    into postgresql://sivdev_user:sivdev_password@0.0.0.0:9432/busy-beaver

with include drop, create tables, create indexes, reset sequences

set work_mem to '16MB', maintenance_work_mem to '512 MB';
```
