from flask import Flask, request, jsonify

from common.otel import setup_otel

app = Flask(__name__)
carts = {}

logger = setup_otel(app, "cart-service")


@app.route('/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    logger.info(f"status_code=200 Carrinho do usuário {user_id}")
    return jsonify(carts.get(user_id, []))


@app.route('/cart/<user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.json
    carts.setdefault(user_id, []).append(data)
    logger.info(f"status_code=201 Produto adicionado ao carrinho {user_id}: {data}")
    return jsonify(data), 201


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
