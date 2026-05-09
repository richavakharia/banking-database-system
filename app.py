import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_connection
from dao.transaction_dao import get_transactions_by_account, deposit, withdraw, transfer
from dao.account_dao import (
    get_accounts_by_customer,
    get_account_by_id,
    create_account,
    close_account,
)
from dao.loan_dao import (
    get_loans_by_customer,
    get_loan_by_id,
    create_loan,
    get_payments_by_loan,
    get_remaining_balance,
    make_loan_payment,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

@app.route("/")
def home():
    if "user_id" in session:
        if session.get("role") == "staff":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
        "SELECT id, name, password_hash, role FROM customers WHERE email = %s",
        (email,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["role"] = user[3]

            if user[3] == "staff":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM customers WHERE email = %s", (email,))
        if cur.fetchone():
            flash("An account with that email already exists.", "warning")
            return redirect(url_for("login") + "?tab=register")
        cur.execute(
            """
            INSERT INTO customers (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, generate_password_hash(password), role),
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()
    flash("Account created! Please sign in.", "success")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    accounts = get_accounts_by_customer(session["user_id"])
    return render_template("dashboard.html", accounts=accounts)


@app.route("/accounts/new", methods=["GET", "POST"])
def new_account():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        account_type = request.form["account_type"]
        create_account(session["user_id"], account_type)
        flash("Account created successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_account.html")


@app.route("/accounts/<int:account_id>")
def account_detail(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    account = get_account_by_id(account_id)
    if not account or account[1] != session["user_id"]:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))
    transactions = get_transactions_by_account(account_id)
    return render_template("account_detail.html", account=account, transactions=transactions)

@app.route("/accounts/<int:account_id>/deposit", methods=["POST"])
def deposit_route(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    account = get_account_by_id(account_id)
    if not account or account[1] != session["user_id"]:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))

    amount = request.form["amount"]

    if deposit(account_id, amount):
        flash("Deposit successful.", "success")
    else:
        flash("Deposit failed.", "danger")

    return redirect(url_for("account_detail", account_id=account_id))


@app.route("/accounts/<int:account_id>/withdraw", methods=["POST"])
def withdraw_route(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    account = get_account_by_id(account_id)
    if not account or account[1] != session["user_id"]:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))

    amount = request.form["amount"]

    if withdraw(account_id, amount):
        flash("Withdrawal successful.", "success")
    else:
        flash("Withdrawal failed. Check your balance.", "danger")

    return redirect(url_for("account_detail", account_id=account_id))


@app.route("/accounts/<int:account_id>/transfer", methods=["POST"])
def transfer_route(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    account = get_account_by_id(account_id)
    if not account or account[1] != session["user_id"]:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))

    to_account_id = int(request.form["to_account_id"])
    amount = request.form["amount"]

    if transfer(account_id, to_account_id, amount):
        flash("Transfer successful.", "success")
    else:
        flash("Transfer failed. Check the account number and balance.", "danger")

    return redirect(url_for("account_detail", account_id=account_id))


@app.route("/accounts/<int:account_id>/close", methods=["POST"])
def close_account_route(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    account = get_account_by_id(account_id)
    if not account or account[1] != session["user_id"]:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))
    close_account(account_id)
    flash("Account closed.", "warning")
    return redirect(url_for("dashboard"))

@app.route("/test-db")
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return "Database connected successfully!"
    except Exception as e:
        return f"Database connection failed: {e}"



@app.route("/loans")
def loans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    loans = get_loans_by_customer(session["user_id"])
    return render_template("loans.html", loans=loans)


@app.route("/loans/new", methods=["GET", "POST"])
def new_loan():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        principal = request.form["principal"]
        loan_purpose = request.form["loan_purpose"]

        if create_loan(session["user_id"], principal, loan_purpose):
            flash("Loan application submitted.", "success")
        else:
            flash("Loan application failed.", "danger")

        return redirect(url_for("loans"))

    return render_template("new_loan.html")


@app.route("/loans/<int:loan_id>")
def loan_detail(loan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    loan = get_loan_by_id(loan_id)

    if not loan or loan[1] != session["user_id"]:
        flash("Loan not found.", "danger")
        return redirect(url_for("loans"))

    payments = get_payments_by_loan(loan_id)
    remaining_balance = get_remaining_balance(loan_id)

    return render_template(
        "loan_detail.html",
        loan=loan,
        payments=payments,
        remaining_balance=remaining_balance
    )


@app.route("/loans/<int:loan_id>/pay", methods=["POST"])
def pay_loan(loan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    loan = get_loan_by_id(loan_id)

    if not loan or loan[1] != session["user_id"]:
        flash("Loan not found.", "danger")
        return redirect(url_for("loans"))

    amount = request.form["amount"]

    if make_loan_payment(loan_id, amount):
        flash("Loan payment successful.", "success")
    else:
        flash("Loan payment failed. Check the amount.", "danger")

    return redirect(url_for("loan_detail", loan_id=loan_id))

@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT loan_id, customer_id, principal, interest_rate, start_date, status, loan_purpose
            FROM loans
            ORDER BY start_date DESC
        """)
        loans = cur.fetchall()
        cur.close()
    finally:
        conn.close()

    return render_template("admin_dashboard.html", loans=loans)


@app.route("/admin/loans/<int:loan_id>/approve", methods=["POST"])
def approve_loan(loan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    interest_rate = request.form["interest_rate"]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE loans
            SET status = 'approved', interest_rate = %s
            WHERE loan_id = %s
            """,
            (interest_rate, loan_id)
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    flash("Loan approved with interest rate.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/loans/<int:loan_id>/reject", methods=["POST"])
def reject_loan(loan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE loans SET status = 'rejected' WHERE loan_id = %s", (loan_id,))
        conn.commit()
        cur.close()
    finally:
        conn.close()

    flash("Loan rejected.", "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/customers")
def admin_customers():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                c.id,
                c.name,
                c.email,
                c.role,
                c.created_at,
                COUNT(DISTINCT a.account_id) AS account_count,
                COALESCE(SUM(a.balance), 0) AS total_balance,
                COUNT(DISTINCT l.loan_id) AS loan_count
            FROM customers c
            LEFT JOIN accounts a ON c.id = a.customer_id
            LEFT JOIN loans l ON c.id = l.customer_id
            WHERE c.name ILIKE %s OR c.email ILIKE %s
            GROUP BY c.id, c.name, c.email, c.role, c.created_at
            ORDER BY c.created_at DESC
            """,
            (f"%{search}%", f"%{search}%")
        )
        customers = cur.fetchall()
        cur.close()
    finally:
        conn.close()

    return render_template("admin_customers.html", customers=customers, search=search)


@app.route("/admin/customers/<int:customer_id>")
def admin_customer_detail(customer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, email, role, created_at
            FROM customers
            WHERE id = %s
            """,
            (customer_id,)
        )
        customer = cur.fetchone()

        if not customer:
            flash("Customer not found.", "danger")
            return redirect(url_for("admin_customers"))

        cur.execute(
            """
            SELECT account_id, account_type, balance, opened_date, status
            FROM accounts
            WHERE customer_id = %s
            ORDER BY opened_date DESC
            """,
            (customer_id,)
        )
        accounts = cur.fetchall()

        cur.execute(
            """
            SELECT loan_id, principal, interest_rate, start_date, status, loan_purpose
            FROM loans
            WHERE customer_id = %s
            ORDER BY start_date DESC
            """,
            (customer_id,)
        )
        loans = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    return render_template(
        "admin_customer_detail.html",
        customer=customer,
        accounts=accounts,
        loans=loans
    )


@app.route("/admin/accounts/<int:account_id>/freeze", methods=["POST"])
def freeze_account(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE accounts SET status = 'frozen' WHERE account_id = %s",
            (account_id,)
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    flash("Account frozen.", "warning")
    return redirect(request.referrer or url_for("admin_customers"))


@app.route("/admin/accounts/<int:account_id>/close", methods=["POST"])
def admin_close_account(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE accounts SET status = 'closed' WHERE account_id = %s",
            (account_id,)
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    flash("Account closed.", "warning")
    return redirect(request.referrer or url_for("admin_customers"))


@app.route("/admin/accounts/<int:account_id>/activate", methods=["POST"])
def activate_account(account_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "staff":
        flash("Staff access required.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE accounts SET status = 'active' WHERE account_id = %s",
            (account_id,)
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    flash("Account reactivated.", "success")
    return redirect(request.referrer or url_for("admin_customers"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
