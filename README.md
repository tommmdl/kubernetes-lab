# Kubernetes: a aplicação de notas em um cluster local

[English](README.en.md) · Português
## Banco atual: Alpine, com rollback testado

Os labs agora usam a imagem PostgreSQL Alpine testada, fixada por digest. A adoção usou backup lógico e volumes novos; os volumes Debian originais continuam guardados. O rollback real da API preservou uma nota criada depois da troca. Veja o [procedimento de migração, backup e recuperação](docs/postgres-adoption.md). Os relatórios de segurança anteriores continuam disponíveis.


A aplicação já funciona no Docker. Agora a ideia é observar o que muda quando ela passa a rodar em um cluster: quem recria um Pod, como o tráfego chega às réplicas e o que precisa continuar existindo quando o banco reinicia.

Este projeto usa a imagem do [docker-lab](https://github.com/tommmdl/docker-lab) publicada no GHCR. A API tem duas réplicas; o PostgreSQL usa um StatefulSet e um volume persistente. O cluster kind fica separado dos outros ambientes da máquina.

[![Testes](https://github.com/tommmdl/kubernetes-lab/actions/workflows/test.yml/badge.svg)](https://github.com/tommmdl/kubernetes-lab/actions/workflows/test.yml)

## Para começar

Use Linux/WSL com Docker acessível, Python 3, Bash e curl. O instalador automático de kind/kubectl atende Linux x86_64. Você precisa de internet para os primeiros downloads, espaço para as imagens e a porta 8005 livre.

```bash
git clone https://github.com/tommmdl/kubernetes-lab.git
cd kubernetes-lab
bash scripts/prepare.sh
bash scripts/lab.sh up
bash scripts/lab.sh status
```

Abra **http://localhost:8005**. A interface alterna entre português e inglês. O acesso é local; a API deste exercício não tem autenticação de usuários.

O nome do cluster é `devops-notes`, e o namespace da aplicação é `notes-lab`. O wrapper `scripts/k.sh` sempre usa o kubeconfig e o contexto deste projeto, sem depender do contexto global do seu terminal.

## O que observar

1. Crie uma nota e exclua um Pod da API. Veja o Deployment repor a réplica.
2. Aumente a API para três réplicas e confira o Service.
3. Recrie o Pod do banco e veja o que o PVC preserva.
4. Experimente uma imagem inexistente, acompanhe a falha de rollout e faça rollback.

```bash
bash scripts/k.sh get pods -o wide
bash scripts/k.sh scale deployment/notes-api --replicas=3
bash scripts/k.sh rollout status deployment/notes-api
bash scripts/k.sh apply -f manifests/api.yaml
```

O último comando devolve a configuração declarada no arquivo, incluindo duas réplicas. O [guia de uso](docs/guide.md) explica as peças e mostra como investigar cada cenário.

## Conferir o projeto

```bash
python3 tests/verify.py
```

O teste usa somente este cluster/namespace, cria sua própria nota e a remove ao final. Ele substitui Pods, escala a API, confere a persistência e provoca uma atualização inválida seguida de rollback. A troca do Pod do banco causa uma breve indisponibilidade enquanto ele volta.

Os [resultados registrados](docs/validation.md) explicam o que foi verificado de verdade, com recaps do ambiente e os limites dos exercícios. O cluster local fica rodando depois dos testes para você explorar.

Os 24 testes passaram localmente e no GitHub Actions, incluindo recuperação dos Pods, persistência, escala e rollback.

## Quando terminar

```bash
bash scripts/lab.sh down
```

**Esse comando apaga o cluster e os dados do banco, incluindo os PVCs.** O volume protege os dados contra a troca de um Pod; ele não é um backup fora do cluster. O script só remove o cluster com o nome e o marcador local deste projeto.

Kind, kubectl, senha e kubeconfig ficam em `.local/`, fora do Git. Guarde a senha enquanto mantiver o banco: gerar outra não muda automaticamente a credencial já inicializada no PostgreSQL.

[Ver os outros projetos do portfólio](https://github.com/tommmdl/devops-portfolio)

## Próximo passo: GitOps

O [argocd-lab](https://github.com/tommmdl/argocd-lab) usa esta mesma aplicação e cluster para praticar drift e self-heal. Depois da adoção pelo Argo CD, faça mudanças de configuração por aquele repositório; os exercícios de escala daqui podem ser revertidos automaticamente.

Para acompanhar a saúde da aplicação, o [monitoring-lab](https://github.com/tommmdl/monitoring-lab) adiciona Prometheus, Grafana e sondas HTTP no mesmo cluster, com um exercício de alerta que mantém a API disponível.

Para praticar como a configuração chega aos containers, o [kubernetes-config-lab](https://github.com/tommmdl/kubernetes-config-lab) traz 26 exercícios de ambiente, ConfigMaps, Secrets, TLS e Downward API em um namespace separado, com soluções em português e inglês.

## Etapas anteriores de segurança (evidências históricas)

Na etapa anterior, os digests das imagens incluíram a primeira rodada de correções na API e no PostgreSQL. Naquela etapa, o banco continuou na versão 17 e no Bookworm; mudaram o auxiliar gosu e suas dependências Go. A API atualiza Flask/liblzma e remove da execução as ferramentas de instalação do pip. Veja os [relatórios completos de antes e depois](https://github.com/tommmdl/security-lab/blob/main/docs/remediation.md). Os achados restantes continuam bloqueando o gate de segurança separado.

Validação das correções: 23 testes do Compose, restauração controlada de três notas da imagem original do PostgreSQL para a recompilada e 19 testes locais de tracing. A aplicação do Argo CD está Synced/Healthy e mantém o mesmo PVC. As evidências completas e as pendências estão no link acima.

A [análise dos críticos do PostgreSQL](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.md) remove o SQLite sem uso e limita a conta da aplicação. Volumes existentes exigem execução explícita do `lab-db-harden` depois da troca de imagem; os hooks não se repetem. Neste lab Kubernetes, use `bash scripts/harden-db.sh` no checkout do kubernetes-lab depois de salvar backups dos dados/objetos globais/HBA. A manutenção passa a usar `psql -U notes_admin -d notes` pelo socket Unix do container do banco. Dois achados críticos continuam visíveis e bloqueando.

Depois da análise dos críticos do PostgreSQL, a API usa uma conta SQL comum e a imagem do banco fica sem SQLite. A aplicação está saudável; passaram 24 testes de Kubernetes e 19 de tracing no CI. A [análise completa](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.md) mantém os dois críticos restantes e seus limites visíveis.
