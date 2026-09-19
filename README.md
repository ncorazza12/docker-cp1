# CP1 — Docker & Kubernetes: Exercícios da Apostila (Módulo 3)

Repositório com a resolução prática dos exercícios 3.1 a 3.4 sobre Pods, Services, DNS e containers múltiplos no Kubernetes, executados em ambiente local com Minikube (Windows 11 + Docker Desktop).

## Ambiente utilizado

- **SO**: Windows 11
- **Orquestrador**: Minikube (driver Docker)
- **Ferramentas**: kubectl, Docker Desktop, Python/Flask (imagem `store-api:1.0` customizada)
- **Recursos do cluster**: 2 vCPU / 3GB RAM (Minikube), limitado por Pod a no máximo 500m CPU / 256Mi RAM para não sobrecarregar a máquina host
- **Namespace principal**: `store-dev` (mais `store-prod` no exercício 3.2, item f)

## Estrutura do repositório

```
.
├── README.md
├── pod-store-api.yaml
├── pod-store-api-2.yaml
├── pod-store-api-3.yaml
├── svc-clusterip.yaml
├── svc-nodeport.yaml
├── svc-headless.yaml
├── quebrado.yaml
├── corrigido.yaml
├── pod-store-api-full.yaml
├── ex3-1.md
├── ex3-2.md
├── ex3-3.md
├── ex3-4.md
└── images/
    ├── ex3-1/
    ├── ex3-2/
    ├── ex3-3/
    └── ex3-4/
```

---

## Exercício 3.1 — Manifesto de Pod completo da store-api

**Objetivo**: escrever manualmente um manifesto de Pod com probes, recursos e contexto de segurança, sem usar `--dry-run` como gerador.

**Arquivo**: [`pod-store-api.yaml`](./pod-store-api.yaml)

### Evidências

| # | Descrição | Imagem |
|---|---|---|
| 1 | Saída do `minikube start` mostrando `Done!` | ![Print 1](./images/ex3-1/Print%201%20sa%C3%ADda%20do%20minikube%20start%20mostrando%20Done!.jpeg) |
| 2 | Saída de `kubectl create namespace` + `kubectl get ns` | ![Print 2](./images/ex3-1/Print%202%20sa%C3%ADda%20do%20kubectl%20create%20namespace%20%2B%20kubectl%20get%20ns.jpeg) |
| 3 | Build da imagem `store-api:1.0` concluído e confirmado com `minikube image ls` | ![Print 3](./images/ex3-1/Print%203%20sa%C3%ADda%20do%20build%20terminando%20com%20sucesso%2C%20e%20depois%20minikube%20image%20ls%20%20findstr%20store-api%20confirmando%20que%20a%20imagem%20est%C3%A1%20l%C3%A1..jpeg) |
| 4 | `kubectl explain` (Downward API) consultado antes de escrever o manifesto | ![Print 4](./images/ex3-1/Print%204%20sa%C3%ADda%20de%20pelo%20menos%20um%20desses%20explain%20(ex%20o%20da%20Downward%20API).jpeg) |
| 5 | Validação com `kubectl apply --dry-run=server` sem erros | ![Print 5](./images/ex3-1/Print%205%20sa%C3%ADda%20confirmando%20created%20(dry%20run)%20sem%20erros.jpeg) |
| 6 | Aplicação real do manifesto (`kubectl apply`) | ![Print 6](./images/ex3-1/Print%206%20Aplicar%20de%20verdade.jpeg) |
| 7 | Pod `1/1 Running` | ![Print 7](./images/ex3-1/Print%207%20mostrando%2011%20e%20Running.jpeg) |
| 8 | QoS Class identificada (`Burstable`) | ![Print 8](./images/ex3-1/Print%208%20Descobrir%20e%20justificar%20a%20QoS.jpeg) |
| 9 | `describe` mostrando as três probes (Startup/Readiness/Liveness) | ![Print 9](./images/ex3-1/Print%209%20role%20at%C3%A9%20a%20se%C3%A7%C3%A3o%20do%20container%20e%20capture%20LivenessReadinessStartup.jpeg) |
| 10 | `POD_NAME` e `NODE_NAME` corretos dentro do container | ![Print 10](./images/ex3-1/Print%2010%20Provar%20POD_NAME%20e%20NODE_NAME.jpeg) |

### Respostas dos itens analíticos

- **QoS Class**: `Burstable`, pois `requests` (100m/128Mi) é diferente de `limits` (500m/256Mi) em pelo menos um container. A classe `Guaranteed` exigiria `requests == limits` em todos os recursos de todos os containers.
- **(g) Tempo máximo até o container ser morto após a liveness começar a falhar**: `initialDelaySeconds + failureThreshold × periodSeconds`. Como a `startupProbe` precisa ser satisfeita primeiro (até 30 × 2 = 60s), a liveness só passa a agir depois disso; com os defaults não sobrescritos na liveness (`failureThreshold: 3`, `periodSeconds: 10`), o cálculo é 0 + 3×10 = 30s após o startup concluir.

Detalhamento completo dos 7 itens (comandos + saídas): ver [`ex3-1.md`](./ex3-1.md).

---

## Exercício 3.2 — Três Services e a prova de DNS

**Objetivo**: criar e diferenciar ClusterIP, NodePort e headless, comprovando o comportamento distinto de resolução DNS de cada um.

**Arquivos**: [`pod-store-api-2.yaml`](./pod-store-api-2.yaml), [`pod-store-api-3.yaml`](./pod-store-api-3.yaml), [`svc-clusterip.yaml`](./svc-clusterip.yaml), [`svc-nodeport.yaml`](./svc-nodeport.yaml), [`svc-headless.yaml`](./svc-headless.yaml)

### Evidências

| # | Descrição | Imagem |
|---|---|---|
| 1 | Os 3 Pods (`store-api`, `store-api-2`, `store-api-3`) `1/1 Running` | ![Print 1](./images/ex3-2/Print%201%20os%203%20pods%2011%20Running.jpeg) |
| 2 | Confirmação de criação dos 3 Services | ![Print 2](./images/ex3-2/Print%202%20as%203%20confirma%C3%A7%C3%B5es%20de%20created.jpeg) |
| 3 | `kubectl get svc,endpoints` — 3 Services com 3 endpoints cada | ![Print 3](./images/ex3-2/Print%203%20deve%20mostrar%20os%203%20Services%20e%2C%20em%20cada%20Endpoints%20correspondente%2C%20os%203%20IPs%20de%20pod%20na%20porta%208000.jpeg) |
| 4 | `kubectl get endpointslices` | ![Print 4](./images/ex3-2/Print%204%20EndpointSlices.jpeg) |
| 5 | `nslookup` dos três Services | ![Print 5](./images/ex3-2/Print%205%20as%20tr%C3%AAs%20sa%C3%ADdas%20de%20nslookup.jpeg) |
| 6 | Distribuição das 12 requisições entre os 3 Pods | ![Print 6](./images/ex3-2/Print%206%20distribui%C3%A7%C3%A3o%20(deve%20ficar%20espalhada%20entre%20store-api%2C%20store-api-2%2C%20store-api-3%2C%20j%C3%A1%20que%20o%20iptables%20faz%20round-robin%C3%A1nd%C3%B4mico%20sem%20afinidade).jpeg) |
| 7 | Acesso externo via NodePort (`minikube service --url`) | ![Print 7](./images/ex3-2/Print%207%20a%20URL%20gerada%20%2B%20resposta%20do%20curl.jpeg) |
| 8 | Falha do nome curto cross-namespace e sucesso do FQDN | ![Print 8](./images/ex3-2/Print%208%20primeiro%20comando%20falhando%20(timeoutDNS%20not%20found)%2C%20segundo%20funcionando.jpeg) |
| 9 | Com `sessionAffinity: ClientIP`, as 12 requisições vão para o mesmo Pod | ![Print 9](./images/ex3-2/Print%209%20agora%20as%2012%20respostas%20devem%20vir%20todas%20do%20mesmo%20hostnamepod%2C%20porque%20o%20sessionAffinity%20ClientIP%20faz%20o%20kube-proxy%20fixar%20as%20requisi%C3%A7%C3%B5es%20de%20um%20mesmo%20IP%20de%20origem%20sempre%20no%20mesmo%20endpoint%20(por%20padr%C3%A3o%2C%20por%20at%C3%A9.jpeg) |

### Principais conclusões

- **Endpoints vs EndpointSlice**: `Endpoints` é o objeto legado (um único objeto por Service); `EndpointSlice` particiona os endpoints, escala melhor e é o que `kube-proxy`/CoreDNS usam hoje.
- **DNS ClusterIP/NodePort vs headless**: o ClusterIP e o NodePort resolvem para 1 IP virtual estável (load-balanceado pelo `kube-proxy`); o headless (`clusterIP: None`) devolve diretamente os 3 IPs dos Pods, pois não há proxy intermediário.
- **Cross-namespace**: o `search` do `/etc/resolv.conf` do Pod só inclui o namespace dele mesmo; por isso o nome curto só resolve no mesmo namespace, sendo necessário o FQDN para cruzar namespaces.

Detalhamento completo (comandos + saídas + explicações): ver [`ex3-2.md`](./ex3-2.md).

---

## Exercício 3.3 — Consertar o manifesto quebrado

**Objetivo**: localizar e corrigir cinco defeitos distintos, classificando cada um por tipo de erro.

**Arquivos**: [`quebrado.yaml`](./quebrado.yaml) (versão original com os 5 defeitos), [`corrigido.yaml`](./corrigido.yaml) (versão final funcional)

### Evidências

| # | Descrição | Imagem |
|---|---|---|
| 1 | Defeito (i): erro de parser YAML (indentação) | ![Print 1](./images/ex3-3/Print%201%20essa%20mensagem%20de%20erro.jpeg) |
| 2 | Defeito (ii): campo desconhecido `livenessprobe` | ![Print 2](./images/ex3-3/Print%202%20Corre%C3%A7%C3%A3o%20livenessprobe%20%E2%86%92%20livenessProbe%20(camelCase%20correto)%2C%20e%20trocar%20port%208000%20por%20port%20http%20para%20casar%20com%20a%20boa%20pr%C3%A1tica%20do%203.1%20(n%C3%A3o%20%C3%A9%20obrigat%C3%B3rio%2C%20mas%20%C3%A9%20consistente)..jpeg) |
| 3 | Defeito (iii): `apiVersion: extensions/v1beta1` inválida para Service | ![Print 3](./images/ex3-3/Print%203%20Corre%C3%A7%C3%A3o%20apiVersion%20extensionsv1beta1%20%E2%86%92%20apiVersion%20v1%20(Service%20sempre%20foi%20v1%3B%20extensionsv1beta1%20nunca%20existiu%20para%20Service%20%E2%80%94%20esse%20grupo%20era%20usado%20por%20recursos%20antigos%20como%20IngressDeployment%20em%20vers%C3%B5es%20be.jpeg) |
| 4 | Dry-run passando após corrigir (i), (ii) e (iii) | ![Print 4](./images/ex3-3/Print%204%20Dry-run%20passando.jpeg) |
| 5 | Defeito (iv): `Endpoints` vazio por selector divergente (`env: prod` vs `env: dev`) | ![Print 5](./images/ex3-3/Print%205%20repare%20que%20o%20Service%20aparece%20criado%2C%20mas%20o%20ENDPOINTS%20dele%20fica%20none%20%E2%80%94%20mesmo%20o%20Pod%20estando%20Running.%20Isso%20%C3%A9%20o%20defeito%20(iv)%20o%20selector%20do%20Service%20pede%20env%20prod%2C%20mas%20o%20label%20do%20Pod%20%C3%A9%20env%20dev.%20Nenhuma%20mensagem%20de.jpeg) |
| 6 | Defeito (v): `curl` trava/timeout por `targetPort: 9000` incorreto | ![Print 6](./images/ex3-3/Print%206%20esse%20curl%20deve%20travardar%20timeout%20%E2%80%94%20porque%20nada%20est%C3%A1%20escutando%20na%20porta%209000%20dentro%20do%20container%20(a%20app%20escuta%20em%208000).%20Isso%20%C3%A9%20o%20defeito%20(v)%20nenhum%20erro%20no%20apply%2C%20o%20problema%20s%C3%B3%20aparece%20em%20tempo%20de%20execu%C3%A7.jpeg) |
| 7 | `corrigido.yaml` funcionando: Pod Running, Endpoints correto, curl com sucesso | ![Print 7](./images/ex3-3/Print%207%20Pod%20Running%2C%20Endpoints%20com%20o%20IP8000%2C%20e%20curl%20retornando%20ok%20com%20sucesso%20%E2%80%94%20esse%20%C3%A9%20o%20entreg%C3%A1vel%20final%20do%20crit%C3%A9rio%20de%20aceite..jpeg) |

### Tabela dos 5 defeitos

| # | Linha | Tipo | Sintoma | Comando revelador | Correção |
|---|---|---|---|---|---|
| i | `tier: backend` | Sintaxe YAML | Parser falha, "did not find expected key" | `kubectl apply --dry-run=server` | Alinhar indentação com os outros labels |
| ii | `livenessprobe:` | API inválida | ValidationError: unknown field | `kubectl apply --dry-run=server` | Corrigir para `livenessProbe` (camelCase) |
| iii | `apiVersion: extensions/v1beta1` | API inválida | "no matches for kind Service in version..." | `kubectl apply --dry-run=server` | Trocar para `apiVersion: v1` |
| iv | `env: prod` no selector | Incoerente com outro objeto | Endpoints vazio, sem erro no apply | `kubectl get endpoints` | Selector deve casar com labels do Pod |
| v | `targetPort: 9000` | Incoerente com a aplicação | curl trava/timeout | `curl` de dentro de um Pod cliente | `targetPort: http` (8000) |

### Pergunta de fechamento

Os defeitos (iv) e (v) não geram erro no `apply` porque são sintaticamente válidos e respeitam o schema da API — o problema é semântico (referências entre objetos) e só se manifesta em tempo de execução. Isso ensina que `kubectl apply`, mesmo em modo `--dry-run=server`, garante apenas conformidade estrutural e de schema, nunca a correção funcional das referências entre selectors, portas e nomes. Validar um deploy real exige sempre um segundo nível de checagem com `get endpoints`, `describe` e testes de conectividade.

Detalhamento completo (progressão de mensagens de erro, comandos): ver [`ex3-3.md`](./ex3-3.md).

---

## Exercício 3.4 — Pod multi-container com initContainer, sidecar e emptyDir

**Objetivo**: Pod `store-api-full` com um initContainer que prepara configuração, um container principal e um sidecar de logs, compartilhando um volume `emptyDir`.

**Arquivo**: [`pod-store-api-full.yaml`](./pod-store-api-full.yaml)

### Evidências

| # | Descrição | Imagem |
|---|---|---|
| 1 | Validação (`--dry-run=server`) | ![Print 1](./images/ex3-4/Print%201%20Passo%202%20%E2%80%94%20Validar%20e%20aplicar.jpeg) |
| 2 | Aplicação real do manifesto | ![Print 2](./images/ex3-4/Print%202.jpeg) |
| 3 | Acompanhamento do initContainer rodando e terminando (`Init:0/1` → `Running`) | ![Print 3](./images/ex3-4/Print%203%20Acompanhar%20o%20initContainer%20rodando%20e%20terminando.jpeg) |
| 4 | Logs do initContainer: config criada com sucesso | ![Print 4](./images/ex3-4/Print%204%20deve%20mostrar%20Config%20criada%20com%20sucesso%20e%20o%20conte%C3%BAdo%20do%20config.txt.jpeg) |
| 5 | Pod `2/2 Running` (store-api + log-sidecar) | ![Print 5](./images/ex3-4/Print%205%20coluna%20READY%20deve%20mostrar%2022%20(store-api%20%2B%20log-sidecar%3B%20o%20initContainer%20n%C3%A3o%20conta%20nesse%20n%C3%BAmero%20porque%20j%C3%A1%20terminou).jpeg) |
| 6 | `emptyDir` compartilhado: mesmo conteúdo visível nos dois containers | ![Print 6](./images/ex3-4/Print%206%20os%20dois%20devem%20mostrar%20o%20mesmo%20conte%C3%BAdo%2C%20mesmo%20tendo%20sido%20escrito%20por%20um%20terceiro%20container%20(o%20initContainer)%20que%20j%C3%A1%20nem%20existe%20mais%20%E2%80%94%20prova%20de%20que%20o%20emptyDir%20sobrevive%20%C3%A0%20execu%C3%A7%C3%A3o%20do%20initContainer%20e%20%C3%A9%20com.jpeg) |
| 7 | Logs do sidecar rodando continuamente (loop a cada 15s) | ![Print 7](./images/ex3-4/Print%207%20deve%20mostrar%20as%20linhas%20repetidas%20a%20cada%2015s%2C%20confirmando%20que%20o%20sidecar%20est%C3%A1%20de%20fato%20rodando%20em%20paralelo%20ao%20container%20principal..jpeg) |
| 8 | `describe` mostrando `Init Containers` separados e a ordem nos `Events` | ![Print 8](./images/ex3-4/Print%208%20procure%20a%20se%C3%A7%C3%A3o%20Init%20Containers%20(separada%20de%20Containers)%20e%20os%20Events%20no%20final%2C%20que%20mostram%20a%20sequ%C3%AAncia%20real%20pullstart%20do%20init-config%20%E2%86%92%20ele%20termina%20%E2%86%92%20depois%20start%20de%20store-api%20e%20log-sidecar%20juntos..jpeg) |

### Pergunta de fechamento

O kubelet garante que initContainers rodam sequencialmente e cada um precisa terminar com `exit 0` antes do próximo (init ou container principal) iniciar — útil para pré-condições como configuração ou espera por dependências. O `emptyDir`, por sua vez, tem ciclo de vida atrelado ao **Pod**, não ao container: sobrevive a restarts de containers individuais, mas é destruído permanentemente se o Pod inteiro for removido ou reagendado — não é armazenamento persistente.

Detalhamento completo: ver [`ex3-4.md`](./ex3-4.md).

---

## Como reproduzir

```powershell
minikube start --driver=docker --cpus=2 --memory=3000
kubectl create namespace store-dev

# 3.1
kubectl apply -f pod-store-api.yaml

# 3.2
kubectl apply -f pod-store-api-2.yaml
kubectl apply -f pod-store-api-3.yaml
kubectl apply -f svc-clusterip.yaml
kubectl apply -f svc-nodeport.yaml
kubectl apply -f svc-headless.yaml

# 3.3
kubectl apply -f corrigido.yaml

# 3.4
kubectl apply -f pod-store-api-full.yaml
```

## Autor

Atividade prática desenvolvida para a disciplina de Docker/Kubernetes — CP1.
