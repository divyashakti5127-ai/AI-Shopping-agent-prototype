import os
import requests
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("PAYPAL_CLIENT_ID")
secret = os.getenv("PAYPAL_CLIENT_SECRET")
BASE = "https://api-m.sandbox.paypal.com"

order_id = input("Paste the Order ID: ").strip()

token = requests.post(
    f"{BASE}/v1/oauth2/token",
    auth=(client_id, secret),
    data={"grant_type": "client_credentials"},
).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

order = requests.get(f"{BASE}/v2/checkout/orders/{order_id}", headers=headers).json()
status = order.get("status")
print("Order status:", status)

if status == "APPROVED":
    cap = requests.post(
        f"{BASE}/v2/checkout/orders/{order_id}/capture",
        headers={**headers, "Content-Type": "application/json"},
    )
    print("Capture status code:", cap.status_code)
    print("Payment status:", cap.json().get("status"))