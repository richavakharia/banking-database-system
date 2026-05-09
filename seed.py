from werkzeug.security import generate_password_hash
from db.connection import get_connection

def seed():
    conn = get_connection()
    cur = conn.cursor()

    # Customers
    customers = [
        ("Alice Johnson", "alice@example.com", generate_password_hash("password123")),
        ("Bob Smith",     "bob@example.com",   generate_password_hash("password123")),
        ("Carol White",   "carol@example.com", generate_password_hash("password123")),
    ]
    cur.executemany(
        "INSERT INTO customers (name, email, password_hash) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
        customers
    )

    # Fetch customer IDs
    cur.execute("SELECT id FROM customers WHERE email = 'alice@example.com'")
    alice_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM customers WHERE email = 'bob@example.com'")
    bob_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM customers WHERE email = 'carol@example.com'")
    carol_id = cur.fetchone()[0]

    # Accounts
    cur.execute("""
        INSERT INTO accounts (customer_id, account_type, balance, opened_date)
        VALUES
            (%s, 'checking', 2500.00, '2024-01-10'),
            (%s, 'savings',  10000.00, '2024-01-10'),
            (%s, 'checking', 800.50,  '2024-03-05'),
            (%s, 'savings',  4200.75, '2024-03-05'),
            (%s, 'checking', 150.00,  '2024-06-20')
        ON CONFLICT DO NOTHING
        RETURNING account_id
    """, (alice_id, alice_id, bob_id, bob_id, carol_id))

    conn.commit()

    # Fetch account IDs
    cur.execute("SELECT account_id FROM accounts WHERE customer_id = %s ORDER BY opened_date", (alice_id,))
    alice_accounts = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT account_id FROM accounts WHERE customer_id = %s ORDER BY opened_date", (bob_id,))
    bob_accounts = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT account_id FROM accounts WHERE customer_id = %s ORDER BY opened_date", (carol_id,))
    carol_accounts = [r[0] for r in cur.fetchall()]

    a_chk, a_sav = alice_accounts[0], alice_accounts[1]
    b_chk, b_sav = bob_accounts[0], bob_accounts[1]
    c_chk = carol_accounts[0]

    # Transactions
    cur.execute("""
        INSERT INTO transactions (account_id, type, amount, transaction_date, description) VALUES
            (%s, 'deposit',    3000.00, '2024-01-15', 'Initial deposit'),
            (%s, 'withdrawal',  500.00, '2024-02-01', 'Rent payment'),
            (%s, 'deposit',   10000.00, '2024-01-15', 'Initial deposit'),
            (%s, 'deposit',     200.00, '2024-03-10', 'Monthly savings'),
            (%s, 'deposit',    1000.00, '2024-03-06', 'Initial deposit'),
            (%s, 'withdrawal',  199.50, '2024-04-01', 'Grocery shopping'),
            (%s, 'deposit',    5000.00, '2024-03-06', 'Initial deposit'),
            (%s, 'withdrawal',  800.00, '2024-04-15', 'Car repair'),
            (%s, 'deposit',     500.00, '2024-06-21', 'Initial deposit'),
            (%s, 'transfer',    350.00, '2024-07-01', 'Transfer to savings')
    """, (
        a_chk, a_chk,
        a_sav, a_sav,
        b_chk, b_chk,
        b_sav, b_sav,
        c_chk, c_chk,
    ))

    # Loans
    cur.execute("""
        INSERT INTO loans (customer_id, principal, interest_rate, start_date, status) VALUES
            (%s, 15000.00, 0.0750, '2024-02-01', 'approved'),
            (%s,  5000.00, 0.0500, '2024-05-01', 'pending'),
            (%s,  8000.00, 0.1000, '2024-04-01', 'approved')
        RETURNING loan_id
    """, (alice_id, bob_id, carol_id))

    conn.commit()

    cur.execute("SELECT loan_id FROM loans WHERE customer_id = %s AND status = 'approved'", (alice_id,))
    alice_loan_id = cur.fetchone()[0]
    cur.execute("SELECT loan_id FROM loans WHERE customer_id = %s AND status = 'approved'", (carol_id,))
    carol_loan_id = cur.fetchone()[0]

    # Loan payments
    cur.execute("""
        INSERT INTO loan_payments (loan_id, amount_paid, payment_date, remaining_balance) VALUES
            (%s, 1500.00, '2024-03-01', 13500.00),
            (%s, 1500.00, '2024-04-01', 12000.00),
            (%s, 1500.00, '2024-05-01', 10500.00),
            (%s, 1000.00, '2024-05-15',  7000.00),
            (%s, 1000.00, '2024-06-15',  6000.00)
    """, (
        alice_loan_id, alice_loan_id, alice_loan_id,
        carol_loan_id, carol_loan_id,
    ))

    conn.commit()
    cur.close()
    conn.close()
    print("Database seeded successfully.")
    print("Test accounts:")
    print("  alice@example.com / password123")
    print("  bob@example.com   / password123")
    print("  carol@example.com / password123")

if __name__ == "__main__":
    seed()
