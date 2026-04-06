import signal

import os

from flask import Flask, jsonify, request

from common.http_client import http_request
from common.otel import setup_otel
from common.metrics import setup_metrics

app = Flask(__name__)
products = []

_shutting_down = False


def _handle_shutdown_signal(signum, frame):
    global _shutting_down
    _shutting_down = True


signal.signal(signal.SIGTERM, _handle_shutdown_signal)
signal.signal(signal.SIGINT, _handle_shutdown_signal)

logger = setup_otel(app, "catalog-service")
setup_metrics(app, "catalog-service")


def _dependency_check_urls() -> list[str]:
    raw = os.getenv("DEPENDENCY_CHECK_URLS", "").strip()
    if not raw:
        return []
    return [u.strip() for u in raw.split(",") if u.strip()]


def _check_dependencies() -> tuple[bool, list[dict]]:
    results: list[dict] = []
    ok = True
    for url in _dependency_check_urls():
        try:
            resp = http_request("GET", url)
            good = 200 <= resp.status_code < 400
            results.append({"url": url, "status_code": resp.status_code, "ok": good})
            if not good:
                ok = False
                logger.warning(f"dependency_check ok=false url={url} status_code={resp.status_code}")
        except Exception as e:
            ok = False
            results.append({"url": url, "error": str(e), "ok": False})
            logger.warning(f"dependency_check ok=false url={url} error={e}")
    return ok, results


@app.route('/products', methods=['GET'])
def list_products():
    logger.info("status_code=200 Listando produtos")
    return jsonify(products)


@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    products.append(data)
    logger.info(f"status_code=201 Produto adicionado: {data}")
    return jsonify(data), 201


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok"}), 200


@app.route('/readyz', methods=['GET'])
def readyz():
    if _shutting_down:
        return jsonify({"status": "shutting_down"}), 503

    deps = _dependency_check_urls()
    if deps:
        ok, details = _check_dependencies()
        if not ok:
            return jsonify({"status": "not_ready", "dependencies": details}), 503

    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
