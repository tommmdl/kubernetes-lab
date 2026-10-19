# Adopting PostgreSQL Alpine

The default database now uses the tested Alpine digest. Follow the [complete bilingual procedure](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-adoption.en.md) for the migration, private backups, tested rollback and retained findings. Existing Debian installations must migrate logically before starting the new default.

Kubernetes uses StatefulSet `postgres-alpine`, PVC `data-postgres-alpine-0`, UID/GID 70 and the unchanged Service name `postgres`. Legacy StatefulSet `postgres` stays at zero replicas and retains its PVC. Update the Argo CD source as well.
