from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "crm.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT,
            status TEXT DEFAULT 'New'
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    customer_count = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    lead_count = conn.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        customer_count=customer_count,
        lead_count=lead_count
    )


@app.route("/customers", methods=["GET", "POST"])
def manage_customers():
    conn = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()

        if name and "@" in email:
            conn.execute(
                """INSERT INTO customers
                   (name, email, phone, company)
                   VALUES (?, ?, ?, ?)""",
                (name, email, phone, company)
            )
            conn.commit()

        conn.close()
        return redirect(url_for("manage_customers"))

    customers = conn.execute(
        "SELECT * FROM customers ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return render_template("customers.html", customers=customers)


@app.route("/customers/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM customers WHERE id = ?",
        (customer_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("manage_customers"))


@app.route("/leads", methods=["GET", "POST"])
def manage_leads():
    conn = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        source = request.form.get("source", "").strip()
        status = request.form.get("status", "New")

        if name:
            conn.execute(
                """INSERT INTO leads (name, source, status)
                   VALUES (?, ?, ?)""",
                (name, source, status)
            )
            conn.commit()

        conn.close()
        return redirect(url_for("manage_leads"))

    leads = conn.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return render_template("leads.html", leads=leads)


@app.route("/leads/delete/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM leads WHERE id = ?",
        (lead_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("manage_leads"))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
