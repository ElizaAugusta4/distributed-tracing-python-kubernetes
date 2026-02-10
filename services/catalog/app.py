from flask import Flask, request, jsonify
import logging

from common.otel import setup_otel

app = Flask(__name__)
products = []

setup_otel(app, "catalog-service")
logger = logging.getLogger("catalog-service")


@app.route('/products', methods=['GET'])
def list_products():
    from flask import request
    logger.info(f"service=catalog-service status_code=200 trace_id={request.headers.get('traceparent', '')} Listando produtos")
    return jsonify(products)


@app.route('/products', methods=['POST'])
def add_product():
    from flask import request
    data = request.json
    products.append(data)
    logger.info(f"service=catalog-service status_code=201 trace_id={request.headers.get('traceparent', '')} Produto adicionado: {data}")
    return jsonify(data), 201


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
