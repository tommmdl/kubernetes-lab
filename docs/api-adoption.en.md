# Adopting the Alpine API

Default runtime pins the tested basic Alpine image. The Kubernetes GitOps overlay also adopts the published OpenTelemetry derivative. Existing databases/volumes are unchanged. [Full bilingual procedure](https://github.com/tommmdl/security-lab/blob/main/docs/api-adoption.en.md) includes private backups, actual image rollback with post-cutover writes, recovery commands, tracing checks and retained findings. Main access remains localhost:8000 (Docker) / localhost:8005 (Kubernetes).
