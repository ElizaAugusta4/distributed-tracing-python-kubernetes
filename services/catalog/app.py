from flask import Flask, request, jsonify
import logging

from common.otel import setup_otel

app = Flask(__name__)
products = []

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger("catalog-service")

setup_otel(app, "catalog-service")


@app.route('/products', methods=['GET'])
def list_products():
    logger.info("Listando produtos")
    return jsonify(products)


@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    products.append(data)
    logger.info(f"Produto adicionado: {data}")
    return jsonify(data), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
