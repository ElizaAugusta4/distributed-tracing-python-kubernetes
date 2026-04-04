from flask import Flask, jsonify

from common.otel import setup_otel

app = Flask(__name__)
products = []

logger = setup_otel(app, "catalog-service")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
