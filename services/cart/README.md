# Serviço: Cart

Serviço responsável pelo carrinho de compras do usuário.

Funcionalidades sugeridas:
- Adicionar produto ao carrinho
- Remover produto do carrinho
- Visualizar carrinho

## Configuração (env vars)

### HTTP client (outbound)

Estas variáveis controlam o client compartilhado em `services/common/http_client.py` (timeouts e retries para chamadas HTTP outbound).

- `HTTP_CONNECT_TIMEOUT` (default: `0.5`) — timeout de conexão (segundos)
- `HTTP_READ_TIMEOUT` (default: `2.0`) — timeout de leitura/resposta (segundos)
- `HTTP_RETRY_TOTAL` (default: `2`) — número de retries (apenas métodos idempotentes)
- `HTTP_RETRY_BACKOFF` (default: `0.2`) — backoff entre tentativas

### Readiness com dependências (opcional)

Se você definir `DEPENDENCY_CHECK_URLS`, o endpoint `/readyz` valida dependências antes de retornar ready.

- `DEPENDENCY_CHECK_URLS` — lista separada por vírgula com URLs a checar via `GET` (ex.: `http://catalog:5000/healthz,http://order:5002/healthz`)
