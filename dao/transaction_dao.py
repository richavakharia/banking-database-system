from decimal import Decimal
from db.connection import get_connection


def get_transactions_by_account(account_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT transaction_id, account_id, type, amount, transaction_date, description
        FROM transactions
        WHERE account_id = %s
        ORDER BY transaction_date DESC
        """,
        (account_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def deposit(account_id, amount):
    amount = Decimal(str(amount))
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s AND status = 'active'",
            (amount, account_id)
        )
        cur.execute(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (%s, 'deposit', %s, 'Deposit')
            """,
            (account_id, amount)
        )
        conn.commit()
        cur.close()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def withdraw(account_id, amount):
    amount = Decimal(str(amount))
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT balance FROM accounts WHERE account_id = %s AND status = 'active'",
            (account_id,)
        )
        row = cur.fetchone()

        if not row or row[0] < amount:
            cur.close()
            return False

        cur.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, account_id)
        )
        cur.execute(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (%s, 'withdrawal', %s, 'Withdrawal')
            """,
            (account_id, amount)
        )
        conn.commit()
        cur.close()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def transfer(from_account_id, to_account_id, amount):
    amount = Decimal(str(amount))
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT balance FROM accounts WHERE account_id = %s AND status = 'active'",
            (from_account_id,)
        )
        from_account = cur.fetchone()

        cur.execute(
            "SELECT account_id FROM accounts WHERE account_id = %s AND status = 'active'",
            (to_account_id,)
        )
        to_account = cur.fetchone()

        if not from_account or not to_account or from_account[0] < amount or from_account_id == to_account_id:
            cur.close()
            return False

        cur.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, from_account_id)
        )
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, to_account_id)
        )

        cur.execute(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (%s, 'transfer', %s, %s)
            """,
            (from_account_id, amount, f"Transfer to account #{to_account_id}")
        )

        cur.execute(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (%s, 'transfer', %s, %s)
            """,
            (to_account_id, amount, f"Transfer from account #{from_account_id}")
        )

        conn.commit()
        cur.close()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()