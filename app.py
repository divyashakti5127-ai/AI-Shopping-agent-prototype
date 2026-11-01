import json
import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from store import PRODUCTS, check_budget
from agent import pick_cart

load_dotenv()
CLIENT_ID = (os.getenv("PAYPAL_CLIENT_ID") or "").strip()
SECRET = (os.getenv("PAYPAL_CLIENT_SECRET") or "").strip()
BASE = "https://api-m.sandbox.paypal.com"
BY_ID = {p["id"]: p for p in PRODUCTS}

app = Flask(__name__)


def log_paypal_response(label, response):
    """Print the full JSON PayPal returns (including error name and details)."""
    try:
        body = response.json()
    except Exception:
        body = {"raw_text": response.text}

    print(f"\n--- PayPal {label} (HTTP {response.status_code}) ---")
    print(json.dumps(body, indent=2))
    if isinstance(body, dict) and ("name" in body or "details" in body or "error" in body):
        print(f"PayPal Error Name: {body.get('name') or body.get('error')}")
        print(f"PayPal Message:    {body.get('message') or body.get('error_description')}")
        print(f"PayPal Details:    {json.dumps(body.get('details', []), indent=2)}")
    print("-" * 50, flush=True)
    return body


def paypal_headers():
    r = requests.post(
        f"{BASE}/v1/oauth2/token",
        auth=(CLIENT_ID, SECRET),
        data={"grant_type": "client_credentials"},
    )
    if not r.ok:
        log_paypal_response("OAUTH TOKEN ERROR", r)
        r.raise_for_status()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@app.route("/")
def home():
    html = open("index.html", encoding="utf-8").read()
    return html.replace("__CLIENT_ID__", CLIENT_ID)


@app.route("/api/products")
def api_products():
    return jsonify(PRODUCTS)


@app.route("/api/cart", methods=["POST"])
def api_cart():
    data = request.get_json()
    budget = float(data["budget"])
    items = pick_cart(data["request"], budget)
    items = [i for i in items if i["id"] in BY_ID]
    ids = [i["id"] for i in items]
    total, ok = check_budget(ids, budget)  # our own maths, not the AI's
    cart = [
        {"id": i["id"], "name": BY_ID[i["id"]]["name"],
         "price": BY_ID[i["id"]]["price"], "reason": i["reason"]}
        for i in items
    ]
    return jsonify({"cart": cart, "total": total, "ok": ok})


@app.route("/api/create-order", methods=["POST"])
def create_order():
    data = request.get_json()
    ids = [int(i) for i in data["ids"]]
    budget = float(data["budget"])
    total, ok = check_budget(ids, budget)
    if not ids or not ok:
        return jsonify({"error": "Cart is empty or over budget"}), 400
    r = requests.post(
        f"{BASE}/v2/checkout/orders",
        headers=paypal_headers(),
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {"amount": {"currency_code": "USD", "value": f"{total:.2f}"}}
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "return_url": "http://127.0.0.1:5000/",
                        "cancel_url": "http://127.0.0.1:5000/",
                        "user_action": "PAY_NOW",
                    }
                }
            },
        },
    )
    body = log_paypal_response("CREATE ORDER", r)
    return jsonify(body), r.status_code


@app.route("/api/capture-order/<order_id>", methods=["POST"])
def capture_order(order_id):
    r = requests.post(
        f"{BASE}/v2/checkout/orders/{order_id}/capture",
        headers=paypal_headers(),
    )
    body = log_paypal_response("CAPTURE ORDER", r)
    return jsonify(body), r.status_code


if __name__ == "__main__":
    app.run(port=5000, debug=True)
