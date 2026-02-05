from flask import Flask, request, jsonify
import logging
import requests

from common.otel import setup_otel

app = Flask(__name__)
orders = []

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger("order-service")

setup_otel(app, "order-service")

CATALOG_URL = "http://catalog:5000/products"
CART_URL = "http://cart:5001/cart"


@app.route('/orders', methods=['GET'])
def list_orders():
    logger.info(f"service=order-service status_code=200 trace_id={request.headers.get('traceparent', '')} Listando pedidos")
    return jsonify(orders)


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    user_id = data.get('user_id')
    cart_items = []

    if user_id:
        cart_resp = requests.get(f"{CART_URL}/{user_id}")
        if cart_resp.ok:
            cart_items = cart_resp.json()

    catalog_resp = requests.get(CATALOG_URL)
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

    orders.append(order)
    logger.info(f"service=order-service status_code=201 trace_id={request.headers.get('traceparent', '')} Pedido criado: {order}")
    return jsonify(order), 201


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"service=order-service status_code=500 trace_id={request.headers.get('traceparent', '')} Erro capturado: {e}")
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
