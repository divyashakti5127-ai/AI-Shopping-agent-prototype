# AI Shopping Agent (PayPal AI Hackathon)

An AI shopping assistant that turns a plain-language request and a budget into a cart, checks the total in code, and pays through PayPal only after the user approves. Everything runs in the **PayPal Sandbox**, so no real money moves.

> Demo store: the catalogue is a made-up list of about 250 products, not a live shop.

## What it does

1. The user types what they need, for example "evening snacks for me", "skincare for dry skin" or "a gift for my sister who likes books and plants", and sets a maximum budget.
2. Our code shortlists matching products, and Gemini picks a small cart with a short reason for each item.
3. The server **re-checks the total in plain Python**. The AI never decides whether the cart is within budget.
4. The cart panel shows the items, the total and the budget check. If the cart is over budget, payment is disabled.
5. The user approves by paying with the PayPal button. The server creates the PayPal order from the verified total and captures the payment after approval.

## How it uses PayPal

- **PayPal Orders API v2** to create and capture orders (server side, `app.py`)
- **PayPal JavaScript SDK** for the checkout buttons and approval popup
- **PayPal Sandbox** for test accounts and test payments

## How it uses AI

- **Google Gemini** reads the request and picks products from a shortlist, with a reason for each pick.
- If nothing in the catalogue fits, it returns no items instead of inventing a match.
- Safety design: the AI only suggests. Prices and totals come from our own catalogue on the server, and the user must approve in PayPal before anything is paid.

## Tech stack

Python, Flask, HTML/CSS/JavaScript, PayPal Orders API v2 and JS SDK, Google Gemini API.

## Run it yourself

You need Python 3.10 or newer.

1. Clone the repository and open the folder.
2. Install the packages:
   ```
   pip install -r requirements.txt
   ```
3. Create your settings file by copying the example:
   ```
   copy .env.example .env
   ```
   (On Mac/Linux: `cp .env.example .env`)
4. Fill in `.env`:
   - `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`: at [developer.paypal.com](https://developer.paypal.com), create a **Sandbox** app under **Apps & Credentials**.
   - `GEMINI_API_KEY`: a free key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
5. Start the app:
   ```
   python app.py
   ```
6. Open http://127.0.0.1:5000

### Important sandbox setup

- Create the sandbox **Business (seller)** account with the country set to **United States**. A seller account in another country (for example India) can fail with "This seller doesn't accept payments in your currency" because the app charges in USD.
- To pay, log in to the PayPal popup with a sandbox **Personal (buyer)** account, not the seller account.
- Open the app at `127.0.0.1:5000` and allow popups.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Flask server, AI cart endpoint, PayPal create and capture order |
| `agent.py` | Gemini cart picker with retries |
| `store.py` / `catalog.py` | Demo catalogue, shortlist and the budget check |
| `index.html` | Store page, cart panel and PayPal button |
| `validate_catalog.py` | Checks the catalogue data |
| `test_paypal.py`, `check_order.py` | Small scripts for testing the PayPal connection |

## Limitations

- The catalogue is a demo list, not a real store.
- Payments are sandbox only.
- The AI can be slow or briefly unavailable when Gemini is busy, so the app retries and shows a friendly message.

## Demo video

(add your YouTube link here)

## License

MIT, see [LICENSE](LICENSE).