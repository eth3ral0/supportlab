import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Accès à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect("supportlab.db")
    conn.row_factory = sqlite3.Row  # pour accéder aux colonnes par nom
    return conn

@app.route("/")
def index():
    return redirect(url_for("tickets_list"))

@app.route("/tickets")
def tickets_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre, priorite, statut FROM tickets ORDER BY id DESC;")
    tickets = cursor.fetchall()
    conn.close()
    return render_template("tickets_list.html", tickets=tickets)

@app.route("/tickets/new", methods=["GET", "POST"])
def ticket_new():
    if request.method == "POST":
        titre = request.form.get("titre")
        description = request.form.get("description")
        categorie = request.form.get("categorie")
        priorite = request.form.get("priorite")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (titre, description, categorie, priorite, statut) VALUES (?, ?, ?, ?, ?)",
            (titre, description, categorie, priorite, "Ouvert"),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("tickets_list"))
    return render_template("ticket_new.html")

@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, titre, description, priorite, statut FROM tickets WHERE id = ?",
        (ticket_id,),
    )
    ticket = cursor.fetchone()
    conn.close()

    if ticket is None:
        return "Ticket introuvable", 404
    return render_template("ticket_details.html", ticket=ticket)


# Fermer un ticket
@app.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def ticket_close(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tickets SET statut = ? WHERE id = ?",
        ("Fermé", ticket_id),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

if __name__ == "__main__":
    app.run(debug=True)
