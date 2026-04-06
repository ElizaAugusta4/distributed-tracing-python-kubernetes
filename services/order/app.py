from flask import Flask, request, jsonify
import requests

import os
import time

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from common.otel import setup_otel, get_trace_context_ids

app = Flask(__name__)
orders = []

logger = setup_otel(app, "order-service")

CATALOG_URL = "http://catalog:5000/products"
CART_URL = "http://cart:5001/cart"

DB = None
DB_INITED = False


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
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dependencies(trace_id, span_id, from_service, to_service, method, url, status_code, latency_ms)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (trace_id, span_id, "order-service", to_service, method, url, status_code, latency_ms),
            )
    except Exception as e:
        logger.warning(f"status_code=200 Falha ao registrar dependência no banco: {e}")


def _request_with_tracking(to_service: str, method: str, url: str, **kwargs):
    start = time.monotonic()
    status_code = None
    try:
        resp = requests.request(method, url, **kwargs)
        status_code = resp.status_code
        return resp
    finally:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        _record_dependency(to_service, method, url, status_code, elapsed_ms)


@app.route('/orders', methods=['GET'])
def list_orders():
    logger.info("status_code=200 Listando pedidos")
    db = _get_db()
    if db is None:
        return jsonify(orders)

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
        if cart_resp.ok:
            cart_items = cart_resp.json()

    catalog_resp = _request_with_tracking("catalog-service", "GET", CATALOG_URL)
    if catalog_resp.ok:
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
