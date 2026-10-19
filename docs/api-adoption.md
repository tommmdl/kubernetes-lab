# Adotando a API Alpine

O runtime padrão fixa a API Alpine básica testada. O overlay GitOps do Kubernetes também adota a derivada OpenTelemetry publicada. Bancos e volumes existentes não mudam. O [procedimento completo nos dois idiomas](https://github.com/tommmdl/security-lab/blob/main/docs/api-adoption.md) inclui backups privados, rollback real com escritas feitas após a troca, comandos de recuperação, tracing e achados preservados. O acesso principal continua em localhost:8000 (Docker) / localhost:8005 (Kubernetes).
