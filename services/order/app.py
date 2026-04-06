from flask import Flask, request, jsonify

import os
import signal
import time

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

from common.otel import setup_otel, get_trace_context_ids
from common.http_client import DEFAULT_TIMEOUT, http_request
from common.metrics import setup_metrics

app = Flask(__name__)
orders = []

_shutting_down = False


def _handle_shutdown_signal(signum, frame):
    global _shutting_down
    _shutting_down = True


signal.signal(signal.SIGTERM, _handle_shutdown_signal)
signal.signal(signal.SIGINT, _handle_shutdown_signal)

logger = setup_otel(app, "order-service")
setup_metrics(app, "order-service")

tracer = trace.get_tracer("order-service")

CATALOG_URL = "http://catalog:5000/products"
CART_URL = "http://cart:5001/cart"

DB = None
DB_INITED = False

_last_db_ready_check_ts = 0.0
_last_db_ready_check_ok = True


def _db_is_configured() -> bool:
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")
    return bool(host and port and user and password and name)


def _check_db_ready() -> bool:
    """Return True if Postgres is reachable.

    Notes:
    - This is for Kubernetes readiness only.
    - Kept lightweight (no tracing spans, no schema init).
    - Uses a short timeout and a small TTL cache to avoid connection storms.
    """

    global _last_db_ready_check_ok, _last_db_ready_check_ts

    if not _db_is_configured():
        return True

    now = time.time()
    if (now - _last_db_ready_check_ts) < 5:
        return _last_db_ready_check_ok

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")

    ok = False
    try:
        with psycopg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            dbname=name,
            connect_timeout=1,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        ok = True
    except Exception:
        ok = False

    _last_db_ready_check_ok = ok
    _last_db_ready_check_ts = now
    return ok


def _get_db():
    global DB, DB_INITED

    if DB is not None:
        return DB

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")

    if not all([host, port, user, password, name]):
        return None

    dsn = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    try:
        with tracer.start_as_current_span(
            "db.connect",
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.name": name,
                "net.peer.name": host,
                "net.peer.port": int(port),
                "peer.service": "postgres",
            },
        ):
            DB = psycopg.connect(dsn, autocommit=True, row_factory=dict_row)
    except Exception as e:
        logger.warning(f"status_code=200 Banco indisponível, seguindo sem persistência: {e}")
        DB = None
        return None

    if not DB_INITED:
        try:
            with DB.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                      id BIGSERIAL PRIMARY KEY,
                      user_id TEXT,
                      items JSONB NOT NULL,
                      status TEXT NOT NULL,
                      trace_id TEXT,
                      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dependencies (
                      id BIGSERIAL PRIMARY KEY,
                      trace_id TEXT,
                      span_id TEXT,
                      from_service TEXT NOT NULL,
                      to_service TEXT NOT NULL,
                      method TEXT NOT NULL,
                      url TEXT NOT NULL,
                      status_code INT,
                      latency_ms INT,
                      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
            DB_INITED = True
        except Exception as e:
            logger.warning(f"status_code=200 Falha ao inicializar tabelas no banco: {e}")

    return DB


def _record_dependency(to_service: str, method: str, url: str, status_code: int | None, latency_ms: int | None):
    db = _get_db()
    if db is None:
        return

    trace_id, span_id = get_trace_context_ids()
    try:
        with tracer.start_as_current_span(
            "db.dependencies.insert",
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.operation": "INSERT",
                "db.sql.table": "dependencies",
                "peer.service": "postgres",
            },
        ) as span:
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dependencies(trace_id, span_id, from_service, to_service, method, url, status_code, latency_ms)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (trace_id, span_id, "order-service", to_service, method, url, status_code, latency_ms),
                )
            span.set_status(Status(StatusCode.OK))
    except Exception as e:
        try:
            span.record_exception(e)  # type: ignore[name-defined]
            span.set_status(Status(StatusCode.ERROR))  # type: ignore[name-defined]
        except Exception:
            pass
        logger.warning(f"status_code=200 Falha ao registrar dependência no banco: {e}")


def _request_with_tracking(to_service: str, method: str, url: str, **kwargs):
    start = time.monotonic()
    status_code = None
    try:
        timeout = kwargs.pop("timeout", None)
        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        resp = http_request(method, url, timeout=timeout, **kwargs)
        status_code = resp.status_code
        return resp
    except Exception as e:
        trace_id, _ = get_trace_context_ids()
        logger.warning(
            f"status_code=503 dependency_error to_service={to_service} method={method} url={url} "
            f"timeout={timeout} trace_id={trace_id} error={e}"
        )
        return None
    finally:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        _record_dependency(to_service, method, url, status_code, elapsed_ms)


@app.route('/orders', methods=['GET'])
def list_orders():
    logger.info("status_code=200 Listando pedidos")
    db = _get_db()
    if db is None:
        return jsonify(orders)

    with tracer.start_as_current_span(
        "db.orders.select",
        kind=SpanKind.CLIENT,
        attributes={
            "db.system": "postgresql",
            "db.operation": "SELECT",
            "db.sql.table": "orders",
            "peer.service": "postgres",
        },
    ):
        with db.cursor() as cur:
            cur.execute("SELECT id, user_id, items, status, trace_id, created_at FROM orders ORDER BY id DESC LIMIT 50")
            rows = cur.fetchall()
    return jsonify(rows)


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    user_id = data.get('user_id')
    cart_items = []

    if user_id:
        cart_resp = _request_with_tracking("cart-service", "GET", f"{CART_URL}/{user_id}")
        if cart_resp is not None and cart_resp.ok:
            cart_items = cart_resp.json()

    catalog_resp = _request_with_tracking("catalog-service", "GET", CATALOG_URL)
    if catalog_resp is not None and catalog_resp.ok:
        products = catalog_resp.json()
        for item in cart_items:
            if item not in products:
                logger.warning(f"Produto não encontrado: {item}")

    order = {
        "user_id": user_id,
        "items": cart_items,
        "status": "criado"
    }

    trace_id, _ = get_trace_context_ids()
    db = _get_db()
    if db is None:
        orders.append(order)
    else:
        try:
            with tracer.start_as_current_span(
                "db.orders.insert",
                kind=SpanKind.CLIENT,
                attributes={
                    "db.system": "postgresql",
                    "db.operation": "INSERT",
                    "db.sql.table": "orders",
                    "peer.service": "postgres",
                },
            ):
                with db.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO orders(user_id, items, status, trace_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """,
                        (user_id, Jsonb(cart_items), order["status"], trace_id if trace_id != "-" else None),
                    )
                    row = cur.fetchone()
            order["id"] = row["id"]
            order["trace_id"] = trace_id
        except Exception as e:
            logger.warning(f"status_code=200 Falha ao persistir pedido no banco: {e}")
            orders.append(order)
    logger.info(f"status_code=201 Pedido criado: {order}")
    return jsonify(order), 201


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"status_code=500 Erro capturado: {e}")
    return jsonify({"error": str(e)}), 500


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok"}), 200


@app.route('/readyz', methods=['GET'])
def readyz():
    if _shutting_down:
        return jsonify({"status": "shutting_down"}), 503
    if not _check_db_ready():
        return jsonify({"status": "db_unavailable"}), 503
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
