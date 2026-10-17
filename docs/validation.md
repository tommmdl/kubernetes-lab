# O que aconteceu no cluster

[English](validation.en.md) · [Voltar ao projeto](../README.md)

Os **24 testes passaram localmente e no [GitHub Actions](https://github.com/tommmdl/kubernetes-lab/actions/runs/39080854670)**. A execução local terminou em 17/10/2026 20:53:52, no fuso America/Sao_Paulo. O CI usou o commit `8c2510eb24fdcd0dbdfa1af5faa8e2c8f8c28a0c`.

## Os exercícios na prática

| Cenário | O que foi observado |
| --- | --- |
| Inicialização | Dois nós Ready, duas réplicas da API e Job de esquema concluído |
| Persistência | PVC do PostgreSQL Bound |
| HTTP | Health/readiness 200, página servida e nota criada com 201 |
| Pod da API excluído | Deployment criou outro; a nota continuou disponível |
| Escala | Três réplicas prontas; reaplicar o manifesto restaurou duas |
| Pod do banco excluído | StatefulSet criou outro, mantendo o mesmo PVC e a nota |
| Imagem inexistente | Erro de pull observado; réplicas antigas continuaram disponíveis |
| Rollback | Imagem fixada por digest restaurada e nota legível |
| Limpeza do teste | Apenas a nota criada pelo teste foi excluída |

A atualização inválida foi intencional. O teste verificou o erro de imagem e fez uma requisição à API antiga antes de desfazer a mudança. Isso demonstra o comportamento neste cenário, sem afirmar disponibilidade contínua em todos os tipos de falha.

## O que já existia na máquina

Antes de criar o cluster, foram consultadas as pastas de labs e os containers existentes. Havia projetos anteriores de Kubernetes e Argo CD. Foram comparados hashes de 23 arquivos de documentação, manifests e scripts desses projetos antes/depois; os arquivos verificados permaneceram iguais.

O novo ambiente usa outro nome de cluster e outro namespace. Não foram copiadas credenciais dos projetos anteriores. Caminhos pessoais, discos de VMs e o levantamento da máquina ficaram somente no relatório local, fora do repositório.

## Evidências

- [Resultados e checks locais](../evidence/local-results.json)
- [Resultados e checks no CI](../evidence/ci-results.json)
- [Etapas e metadados do workflow](../evidence/ci-run.json)
- [Versões do cluster](../evidence/runtime.json)
- [Conferência dos projetos anteriores](../evidence/preservation.json)
- [Teste completo](../tests/verify.py)

Kind 0.33.0, Kubernetes 1.37.0, kubectl 1.37.1 e Docker Engine 29.1.3 foram usados localmente. A API veio do GHCR por digest, sem precisar de token de pull. O arquivo de senha e o kubeconfig foram excluídos do Git e dos artefatos do workflow.

## Onde a aplicação ficou

O cluster local continua rodando, com a aplicação em http://localhost:8005. No CI, o cluster do runner foi removido depois de guardar os relatórios. O estado final no JSON descreve o momento anterior ao cleanup do CI.

## Limites que importam

O teste de persistência substituiu um Pod, sem simular perda do worker, disco ou cluster. O PostgreSQL tem uma réplica, e o armazenamento é local ao nó. Não houve teste de backup/restauração, tráfego de produção, perda de nó, TLS, autenticação de usuários, Ingress, autoscaling ou NetworkPolicy. A página foi verificada via HTTP, sem automação visual.

A etapa de esquema só cria a tabela inicial; não implementa migrações versionadas. O relatório de preservação cobre os arquivos de projeto selecionados, não uma auditoria forense de todas as partições. A execução técnica foi feita com ajuda do assistente e autorização do proprietário.
