import time
import os
import json
from dotenv import load_dotenv
from google import genai
from store import PRODUCTS, check_budget, shortlist

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
BY_ID = {p["id"]: p for p in PRODUCTS}


def pick_cart(request, budget):
    candidates = shortlist(request, budget, limit=40)
    if not candidates:
        return []

    prompt = f"""You are a shopping assistant.
Choose 2 to 4 products from this list that best match the request.
The total price MUST be under the budget.
If nothing in the list fits the request or budget, return an empty list: {{"items": []}}.
Only use product ids from the provided list.

Products: {json.dumps(candidates)}

Request: {request}
Budget (USD): {budget}

Reply with JSON only, in this format:
{{"items": [{{"id": 1, "reason": "short reason"}}]}}"""
    for attempt in range(5):
        try:
            res = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            items = json.loads(res.text).get("items", [])
            return [
                i for i in items
                if isinstance(i, dict) and i.get("id") in BY_ID
            ]
        except Exception:
            if attempt == 4:
                raise
            time.sleep(3 * (attempt + 1))  # wait 3s, 6s, 9s, 12s, then give up


if __name__ == "__main__":
    request = input("What do you need? ")
    budget = float(input("Budget in USD: "))

    items = pick_cart(request, budget)
    ids = [i["id"] for i in items]
    total, ok = check_budget(ids, budget)  # our own maths, not the AI's

    print()
    for i in items:
        p = BY_ID[i["id"]]
        print(f"- {p['name']} (${p['price']:.2f}): {i['reason']}")
    print(f"\nTotal: ${total:.2f}")
    print("Within budget" if ok else "OVER BUDGET - do not pay")
