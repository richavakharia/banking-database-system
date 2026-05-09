CREATE TABLE IF NOT EXISTS customers (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(10) NOT NULL DEFAULT 'customer'
                  CHECK (role IN ('customer', 'staff')),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    customer_id   INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(10) NOT NULL DEFAULT 'customer'
                  CHECK (role IN ('customer', 'staff'))
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id   SERIAL PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('checking', 'savings')),
    balance      NUMERIC(12, 2) NOT NULL DEFAULT 0.00
                 CHECK (balance >= 0),
    opened_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    status       VARCHAR(10) NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'closed'))
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   SERIAL PRIMARY KEY,
    account_id       INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    type             VARCHAR(20) NOT NULL CHECK (type IN ('deposit', 'withdrawal', 'transfer')),
    amount           NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description      TEXT
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id       SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    principal     NUMERIC(12, 2) NOT NULL CHECK (principal > 0),
    interest_rate NUMERIC(5, 4) NOT NULL CHECK (interest_rate >= 0),
    start_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    status        VARCHAR(10) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'approved', 'rejected', 'paid'))
);

CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id        SERIAL PRIMARY KEY,
    loan_id           INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    amount_paid       NUMERIC(12, 2) NOT NULL CHECK (amount_paid > 0),
    payment_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    remaining_balance NUMERIC(12, 2) NOT NULL CHECK (remaining_balance >= 0)
);
