import signal

from flask import Flask, jsonify, request

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
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
