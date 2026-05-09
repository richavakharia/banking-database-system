from decimal import Decimal
from db.connection import get_connection


def get_loans_by_customer(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT loan_id, customer_id, principal, interest_rate, start_date, status, loan_purpose
        FROM loans
        WHERE customer_id = %s
        ORDER BY start_date DESC
        """,
        (customer_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_loan_by_id(loan_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT loan_id, customer_id, principal, interest_rate, start_date, status, loan_purpose
        FROM loans
        WHERE loan_id = %s
        """,
        (loan_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row


def create_loan(customer_id, principal, loan_purpose):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO loans (customer_id, principal, loan_purpose, status)
            VALUES (%s, %s, %s, 'pending')
            """,
            (customer_id, Decimal(str(principal)), loan_purpose)
        )

        conn.commit()
        cur.close()
        return True

    except Exception:
        conn.rollback()
        return False

    finally:
        conn.close()


def get_payments_by_loan(loan_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT payment_id, loan_id, amount_paid, payment_date, remaining_balance
        FROM loan_payments
        WHERE loan_id = %s
        ORDER BY payment_date DESC
        """,
        (loan_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_remaining_balance(loan_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT remaining_balance
        FROM loan_payments
        WHERE loan_id = %s
        ORDER BY payment_date DESC, payment_id DESC
        LIMIT 1
        """,
        (loan_id,)
    )

    row = cur.fetchone()

    if row:
        cur.close()
        conn.close()
        return row[0]

    cur.execute(
        "SELECT principal FROM loans WHERE loan_id = %s",
        (loan_id,)
    )

    loan = cur.fetchone()

    cur.close()
    conn.close()

    if loan:
        return loan[0]

    return None


def make_loan_payment(loan_id, amount):
    amount = Decimal(str(amount))
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT status
            FROM loans
            WHERE loan_id = %s
            """,
            (loan_id,)
        )

        status_row = cur.fetchone()

        if not status_row or status_row[0] != "approved":
            cur.close()
            return False

        cur.execute(
            """
            SELECT remaining_balance
            FROM loan_payments
            WHERE loan_id = %s
            ORDER BY payment_date DESC, payment_id DESC
            LIMIT 1
            """,
            (loan_id,)
        )

        row = cur.fetchone()

        if row:
            current_balance = row[0]
        else:
            cur.execute(
                "SELECT principal FROM loans WHERE loan_id = %s",
                (loan_id,)
            )
            loan = cur.fetchone()

            if not loan:
                cur.close()
                return False

            current_balance = loan[0]

        if amount <= 0 or amount > current_balance:
            cur.close()
            return False

        new_balance = current_balance - amount

        cur.execute(
            """
            INSERT INTO loan_payments (loan_id, amount_paid, remaining_balance)
            VALUES (%s, %s, %s)
            """,
            (loan_id, amount, new_balance)
        )

        if new_balance == 0:
            cur.execute(
                "UPDATE loans SET status = 'paid' WHERE loan_id = %s",
                (loan_id,)
            )

        conn.commit()
        cur.close()
        return True

    except Exception:
        conn.rollback()
        return False

    finally:
        conn.close()