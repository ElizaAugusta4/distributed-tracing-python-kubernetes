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
- Métricas Prometheus expostas em `/metrics` e ServiceMonitors criados; alertas SLO burn-rate adicionados

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

## Ordem sugerida (trilha rápida)

1. Gunicorn
2. Readiness/shutdown
3. Healthz com DB
4. Métricas com path estável
5. Alertas operacionais

