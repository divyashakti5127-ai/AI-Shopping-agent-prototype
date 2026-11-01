import os
import requests
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("PAYPAL_CLIENT_ID")
secret = os.getenv("PAYPAL_CLIENT_SECRET")
BASE = "https://api-m.sandbox.paypal.com"

token_res = requests.post(
    f"{BASE}/v1/oauth2/token",
    auth=(client_id, secret),
    data={"grant_type": "client_credentials"},
)
token_res.raise_for_status()
token = token_res.json()["access_token"]

order_res = requests.post(
    f"{BASE}/v2/checkout/orders",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "10.00"}}],
    },
)
order = order_res.json()
print("Status:", order_res.status_code)
print("Order ID:", order.get("id"))
for link in order.get("links", []):
    if link["rel"] in ("approve", "payer-action"):
        print("Approve link:", link["href"])