# Adotando o PostgreSQL Alpine

O banco padrão agora usa o digest Alpine testado. O [procedimento completo nos dois idiomas](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-adoption.md) reúne a migração, os backups privados, o rollback testado e os achados preservados. Instalações Debian existentes precisam migrar logicamente antes de iniciar o novo padrão.

O Kubernetes usa o StatefulSet `postgres-alpine`, PVC `data-postgres-alpine-0`, UID/GID 70 e o mesmo Service `postgres`. O StatefulSet legado `postgres` fica em zero réplicas e conserva seu PVC. A fonte do Argo CD também precisa acompanhar a mudança.
