# Runbook – Observabilidade Microserviços Python

## Objetivo
Guia prático para operação e resposta rápida a incidentes no ambiente de observabilidade do projeto.

## 1. Acesso ao Grafana
- URL: http://localhost:3000
- Usuário padrão: admin
- Senha: verifique no secret do grafana

## 2. Dashboards principais
- **Incidente – Erros, Logs e Traces**: monitora taxa de erro 5xx por serviço.
- **Trace-Log Correlation**: correlaciona logs e traces por trace_id.

## 3. Passos em caso de incidente
1. Acesse o dashboard "Incidente – Erros, Logs e Traces".
2. Identifique o serviço com aumento de erros 5xx.
3. Clique no serviço para filtrar logs e traces relacionados.
4. Analise logs detalhados e traces para identificar a causa.
5. Se necessário, reinicie o pod afetado:
   ```sh
   kubectl rollout restart deployment/<servico> -n virtual-store
   ```
6. Registre o incidente e a ação tomada.

## 4. Contatos
- DevOps: <email/devops>
- SRE: <email/sre>

---
