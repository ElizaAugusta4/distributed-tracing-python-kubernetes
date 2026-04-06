# Sprints com Issues (GitHub)

Objetivo: organizar as próximas tarefas do lab em ciclos curtos (sprints), com rastreabilidade e critérios de aceite.

## Modelo recomendado (simples)

- Use **Issues** para cada tarefa pequena.
- Use **GitHub Projects (v2)** para organizar em colunas e usar **Iterations** como sprint.

## Setup (5–10 min)

1) Crie um Project
- GitHub → Projects → New project
- Nome sugerido: `Virtual Store — Prod-like`

2) Ative Iterations (Sprint)
- Add field → `Iteration`
- Configure: duração 1 semana ou 2 semanas
- Sprint naming: `Sprint 01`, `Sprint 02`…

3) Campos mínimos
- `Status`: Backlog / Ready / In progress / Done
- `Priority`: P0/P1/P2
- `Area`: runtime | observability | security | delivery | k8s

4) Labels sugeridas
- `prod-like`, `observability`, `security`, `k8s`, `delivery`, `runtime`
- `P0`, `P1`, `P2`

## Padrão de Issue (como escrever)
- Por quê
- O que mudar
- Critério de aceite
- Como validar
- Impacto observável (métrica/log/trace/manifest)

## Dica de sprint planning
- Pegue 3–6 issues por sprint (tarefas pequenas)
- Cada issue deve caber em 0.5–2h (no máximo)

## Definition of Done (DoD)
- Critério de aceite validado
- Evidência anexada (print/log/trace/metric)
- Mudança pequena e revertível
