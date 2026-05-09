# CS157A Banking App

A bank account management system built with Flask and PostgreSQL.

---

## Prerequisites

- Python 3.8+
- Git
- PostgreSQL

---

## 1. Clone the Repository

```bash
git clone https://github.com/rahulallamraju/cs157a-banking.git
cd cs157a-banking
```

---

## 2. Install PostgreSQL

### macOS

1. Download and install **Postgres.app** from the official site: https://postgresapp.com
2. Open the app.
3. Start the server from the app interface by clicking **Start**.
4. Add the command-line tools to your PATH if prompted — Postgres.app documents its binaries and PATH setup at https://postgresapp.com/documentation/cli-tools.html


## 3. Set Up the Database

### macOS / Linux

Open a terminal and run:

```bash
psql postgres
```

Then inside psql, create the database and a user:

```sql
CREATE DATABASE bank_db;
CREATE USER your_username WITH PASSWORD '';
GRANT ALL PRIVILEGES ON DATABASE bank_db TO your_username;
\q
```

Replace `your_username` with your local system username (run `whoami` in your terminal to find it).

### Windows

Open **SQL Shell (psql)** from the Start Menu. Log in as `postgres` (use the password you set during installation), then run:

```sql
CREATE DATABASE bank_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bank_db TO your_username;
\q
```

---

## 4. Configure the Database Connection

Open [db/connection.py](db/connection.py) and update the fields to match your local PostgreSQL setup:

```python
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="bank_db",
        user="your_username",   # replace with your OS username or psql user
        password=""             # replace with your password if you set one
    )
```

---

## 5. Set Up the Python Environment

Open a terminal in VS Code (`Terminal > New Terminal`) from the project root.

Create the virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate


---

## 6. Install Dependencies

```bash
pip install flask psycopg2-binary
```

Save them to `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## 7. Run the Flask App

```bash
python app.py
or
python3 app.py
```

The app will start at **http://127.0.0.1:5000**

To verify the database connection is working, visit:

```
http://127.0.0.1:5000/test-db
```

You should see: `Database connected successfully!`

---

## Troubleshooting

**`psql: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed`**
PostgreSQL is not running. Start it with `brew services start postgresql@14` (macOS) or `sudo systemctl start postgresql` (Linux).

**`FATAL: role "your_username" does not exist`**
Make sure you created the PostgreSQL user in Step 3 with a username that matches what is in `db/connection.py`.

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment is not activated. Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows) before running the app.
