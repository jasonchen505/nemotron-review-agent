"""Tests for the demo shop module.

Two of these FAIL on purpose: each failure is executable evidence for one of
the review findings (mutable default arg, SQL injection). The agent's verify
pass cites this output when deciding KEEP vs DROP.
"""
import sqlite3

import pytest

from pricing import apply_discount, get_balance, total


@pytest.fixture()
def shop_db(tmp_path, monkeypatch):
    # get_balance() hardcodes a relative "shop.db"; point it at a temp dir.
    monkeypatch.chdir(tmp_path)
    conn = sqlite3.connect("shop.db")
    conn.execute("CREATE TABLE users (name TEXT, balance REAL)")
    conn.execute("INSERT INTO users VALUES ('alice', 50.0)")
    conn.commit()
    conn.close()


def test_apply_discount_basic():
    assert apply_discount(100, 10) == 90.0


def test_total():
    cart = [{"price": 10, "qty": 2}, {"price": 5, "qty": 1}]
    assert total(cart) == 25


def test_history_default_does_not_leak_between_calls():
    # The default list object is shared across calls; inspect it directly.
    apply_discount.__defaults__ = ([],)  # reset shared state
    apply_discount(100, 10)
    apply_discount(200, 20)
    assert apply_discount.__defaults__[0] == [], "mutable default arg leaked history"


def test_get_balance_unknown_user_returns_zero(shop_db):
    assert get_balance("mallory") == 0


def test_get_balance_sql_injection(shop_db):
    # With an f-string query, this returns alice's balance instead of 0.
    assert get_balance("mallory' OR '1'='1") == 0
