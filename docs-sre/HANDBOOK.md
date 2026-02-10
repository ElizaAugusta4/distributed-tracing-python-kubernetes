# Handbook – Visão Geral e Boas Práticas

## Objetivo
Referência para entendimento do projeto, arquitetura, responsabilidades e boas práticas de operação e evolução.

## 1. Arquitetura
- Microserviços Python: catalog, cart, order
- Observabilidade: OpenTelemetry, Tempo, Loki, Grafana
- Orquestração: Kubernetes + Helm

## 2. Fluxo de Observabilidade
- Cada serviço exporta traces e logs com trace_id
- Tempo armazena traces, Loki armazena logs
- Grafana centraliza visualização e dashboards

## 3. Boas Práticas
- Sempre instrumente novos serviços com OpenTelemetry
- Padronize logs para incluir trace_id
- Use dashboards simples e objetivos para confiabilidade
- Documente critérios de saúde antes de criar alertas
- Mantenha o PROJETO_MAPEAMENTO.md atualizado

## 4. Evolução
- Antes de criar novos dashboards, valide os existentes
- Implemente alertas apenas após garantir confiabilidade básica
- Use o PLAYBOOK para tarefas operacionais e troubleshooting
- Use o RUNBOOK para resposta rápida a incidentes

---
