from db.connection import get_connection


def get_account_by_id(account_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM accounts WHERE account_id = %s",
        (account_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_accounts_by_customer(customer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM accounts WHERE customer_id = %s ORDER BY opened_date DESC",
        (customer_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_all_accounts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT a.account_id, c.name, a.account_type, a.balance, a.opened_date, a.status
        FROM accounts a
        JOIN customers c ON a.customer_id = c.id
        ORDER BY a.account_id
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def create_account(customer_id, account_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO accounts (customer_id, account_type)
        VALUES (%s, %s)
        RETURNING account_id
        """,
        (customer_id, account_type)
    )
    account_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return account_id


def update_balance(account_id, new_balance):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET balance = %s WHERE account_id = %s",
        (new_balance, account_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def close_account(account_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET status = 'closed' WHERE account_id = %s",
        (account_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
