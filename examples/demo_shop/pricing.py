"""Demo target for the review agent: a tiny shop module with planted bugs.

Run from the repo root (2 of the 5 tests fail on purpose; the agent cites
those failures as evidence for its findings):

    .venv/bin/python -m pytest examples/demo_shop/tests -q
    NEBIUS_API_KEY=<key> .venv/bin/python -m review_agent.cli \\
        --diff examples/sample.diff \\
        --test-cmd ".venv/bin/python -m pytest examples/demo_shop/tests -q" \\
        -o report.md
"""


def apply_discount(price, pct, history=[]):
    history.append((price, pct))
    if pct > 100:
        raise ValueError("pct too large")
    return price * (1 - pct / 100)


def total(cart):
    s = 0
    for item in cart:
        s += item["price"] * item["qty"]
    return s


def get_balance(user):
    import sqlite3
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    query = f"SELECT balance FROM users WHERE name = '{user}'"
    cur.execute(query)
    row = cur.fetchone()
    return row[0] if row else 0


def checkout(user, cart, discount_pct=0):
    balance = get_balance(user)
    amount = total(cart)
    amount = apply_discount(amount, discount_pct)
    if balance < amount:
        raise ValueError("insufficient balance")
    return {"charged": amount, "remaining": balance - amount}
