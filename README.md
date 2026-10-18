# Kubernetes: a aplicação de notas em um cluster local

[English](README.en.md) · Português

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
