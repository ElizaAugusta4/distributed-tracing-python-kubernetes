# Microprojeto: Aproximar o Virtual Store de Produção

Objetivo: evoluir este lab (microserviços Python + K8s + observabilidade + GitOps) para um cenário mais próximo de produção **sem perder o caráter didático**.

- Ambiente: Kind (local), mas com práticas que escalam para EKS/AKS/GKE
- Estratégia: **atividades pequenas**, cada uma com critério de aceite e impacto observável

---

## Regras do jogo

- Mudanças incrementais (PRs pequenos)
- Nada de “Big Bang refactor”
- Cada tarefa deve:
  - ter motivação (por que isso é produção)
  - ter critério de aceite (como validar)
  - ter impacto mensurável (métrica/log/trace/manifest)

---

## Baseline (onde estamos)

- 3 serviços Flask (catalog/cart/order) com OpenTelemetry (Tempo) + logs (Loki) + dashboards (Grafana)
- GitOps com ArgoCD; CI de Helm; CD build/push e bump de tag nos charts
- Postgres integrado no `order-service` e aparecendo no trace (spans `db.*`)
- Métricas Prometheus expostas em `/metrics` e ServiceMonitors criados
- Alertas SLO burn-rate adicionados

---

## Backlog (tarefas pequenas)

### P0 — Runtime e comportamento “prod-like”

1) Rodar Flask em produção (Gunicorn)
- Por quê: `app.run()` é servidor de dev; Gunicorn é padrão em produção.
- Como: trocar `CMD` nos Dockerfiles para `gunicorn` (com workers/threads/timeouts) e expor `wsgi:app`.
- Aceite:
  - Pods sobem e atendem normalmente
  - `kubectl logs` mostra workers do gunicorn
  - Latência não degrada visivelmente em carga leve

2) Shutdown gracioso (SIGTERM) e readiness real
- Por quê: produção precisa drenar conexões e parar sem perder requests.
- Como: garantir que o container encerra corretamente e que `readinessProbe` falha antes de matar.
- Aceite:
  - Durante rollout, requests não falham em massa
  - `readinessProbe` controla entrada de tráfego

3) Health checks com dependências (no `order-service`)
- Por quê: liveness/readiness devem refletir dependências críticas (ex.: DB).
- Como: `GET /healthz` opcionalmente valida Postgres quando `database.enabled=true`.
- Aceite:
  - Se Postgres cair, `order` fica NotReady (readiness)
  - Liveness continua simples (evitar restart storm)


### P1 — Segurança e hardening

4) Container hardening básico
- Por quê: reduzir superfície e garantir previsibilidade.
- Como:
  - pin de imagem base (major/minor)
  - `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`
  - confirmar `runAsNonRoot`, `readOnlyRootFilesystem`
- Aceite:
  - `helm template` não quebra
  - containers continuam iniciando sem permissões extras

5) Resource tuning mínimo (requests/limits + HPA sanity)
- Por quê: produção exige capacidade controlada e previsível.
- Como: revisar requests/limits e HPA para não “oscilar” em Kind.
- Aceite:
  - HPA escala sob carga (mesmo que sintética)
  - Sem OOM/restarts desnecessários


### P1 — Observabilidade “operacional”

6) Métricas com baixa cardinalidade (path estável)
- Por quê: `path` dinâmico explode séries no Prometheus.
- Como: usar `request.url_rule.rule` quando existir; fallback seguro.
- Aceite:
  - `http_server_requests_total` não cria séries infinitas
  - Dashboards/PromQL continuam funcionando

7) Alertas operacionais básicos (além de SLO)
- Por quê: SLO é saúde do usuário; precisamos de sinais operacionais.
- Exemplos:
  - CrashLoopBackOff / restarts
  - HPA maxed
  - Pods Pending/NotReady
- Aceite:
  - PrometheusRule aplicado
  - Alertas aparecem no Prometheus/Alertmanager (quando condição simulada)


### P2 — Configuração e entrega

8) Config 12-factor (env vars) + validação no startup
- Por quê: produção falha cedo se config estiver errada.
- Como: validar variáveis obrigatórias (ex.: DB) e logar config “safe”.
- Aceite:
  - app não sobe com config inválida
  - logs indicam claramente o motivo

9) Release hygiene (versionamento e changelog simples)
- Por quê: produção precisa rastreabilidade.
- Como: padronizar mensagens de commit e registrar mudanças relevantes.
- Aceite:
  - README e docs apontam como evoluir versões


---

## Backlog estendido (mais atividades “prod-like”)

### P2 — Confiabilidade (timeouts, retries, limites)

10) Timeouts e retries padronizados para chamadas HTTP entre serviços
- Por quê: em produção, dependência lenta/indisponível causa cascata; `requests` sem timeout é risco.
- Como:
  - definir timeouts padrão (connect/read)
  - aplicar retries com backoff apenas para erros transitórios (5xx, timeouts)
  - garantir que o trace/log registre falha com contexto (serviço destino, timeout)
- Aceite:
  - nenhuma chamada `requests.*` fica sem timeout
  - ao derrubar um serviço, o chamador falha rápido (sem “pendurar”)
  - logs mostram erro com `trace_id`

11) Limite de concorrência por pod (proteção contra overload)
- Por quê: produção precisa evitar saturação por pico; limite explícito ajuda a manter latência estável.
- Como: ajustar `gunicorn` (workers/threads) + HPA de forma consistente com CPU/mem.
- Aceite:
  - sob carga leve a moderada, p95 não degrada drasticamente
  - sem aumento de restarts por OOM


### P2 — Segurança (supply-chain e runtime)

12) Pin e atualização controlada de dependências Python
- Por quê: reproducibilidade e menor risco de “quebrar do nada” em deploy.
- Como:
  - pin de versões no `requirements.txt` (ou lockfile gerado)
  - rotina clara de atualização (ex.: mensal) com validação
- Aceite:
  - `pip install -r requirements.txt` é determinístico
  - docs explicam como atualizar dependências com segurança

13) SBOM no CI (Software Bill of Materials)
- Por quê: produção/segurança exige inventário de dependências.
- Como: gerar SBOM (por imagem e/ou por diretório) no GitHub Actions e publicar como artifact.
- Aceite:
  - pipeline publica SBOM por build
  - é possível baixar o artifact e auditar dependências

14) Scan de vulnerabilidades no CI
- Por quê: detectar CVEs cedo e ter trilha de evidência.
- Como: rodar scan (ex.: Trivy) em imagem/container e falhar em severidade alta/crítica (configurável).
- Aceite:
  - workflow executa scan automaticamente
  - resultado fica visível no run (e/ou artifact)


### P2 — Kubernetes “mais produção” (sem complicar)

15) Quotas e limites do namespace (`ResourceQuota` + `LimitRange`)
- Por quê: produção precisa de guardrails para evitar “um serviço derrubar o cluster”.
- Como: aplicar quota simples (cpu/mem/pods) e limite default por container.
- Aceite:
  - manifests aplicam sem quebrar deploy atual
  - ao tentar extrapolar quota, K8s bloqueia e o motivo aparece no evento

16) Estratégia de rollout explícita + `revisionHistoryLimit`
- Por quê: produção precisa rollback previsível e histórico controlado.
- Como: setar RollingUpdate (maxSurge/maxUnavailable) e `revisionHistoryLimit` no Deployment.
- Aceite:
  - rollout não derruba todos os pods simultaneamente
  - histórico não cresce indefinidamente


### P2 — Observabilidade “operacional” (operar e debugar rápido)

17) Runbooks mínimos para alertas
- Por quê: alerta sem ação vira ruído.
- Como: para cada alerta, documentar “o que significa”, “como confirmar”, “como mitigar”.
- Aceite:
  - docs-sre contém runbook por alerta
  - durante simulação, o passo-a-passo resolve/explica o incidente

18) Dashboard operacional de Kubernetes
- Por quê: reduzir MTTR com visão clara de pods, restarts, HPA e erros.
- Como: dashboard simples (Grafana) focado em: restarts, readiness, HPA, CPU/mem e erros 5xx.
- Aceite:
  - dashboard mostra sinais coerentes quando você simula problemas


### P3 — Entrega e governança (bem enxuto)

19) Política de versionamento para charts e serviços
- Por quê: rastreabilidade de release e rollback com clareza.
- Como: definir regra simples (ex.: chart version semver + appVersion = SHA/tag) e documentar.
- Aceite:
  - README explica claramente como versionar
  - `Chart.yaml` e automação seguem a regra

20) Changelog leve (human-friendly)
- Por quê: produção precisa comunicar mudanças relevantes.
- Como: manter `CHANGELOG.md` curto com categorias (Breaking/Feature/Fix/Infra).
- Aceite:
  - cada mudança “de produção” deixa uma nota no changelog

---

## Ordem sugerida (trilha rápida)

1. Gunicorn
2. Readiness/shutdown
3. Healthz com DB
4. Métricas com path estável
5. Alertas operacionais
6. Timeouts/retries
7. Pin dependências + SBOM/scan
8. Quotas/limites + runbooks
