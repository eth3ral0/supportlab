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
    cursor.execute("SELECT id, titre, categorie, priorite, statut, note, date_creation FROM tickets ORDER BY id DESC;")
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
        note = request.form.get("note")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tickets (titre, description, priorite, statut, categorie, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (titre, description, priorite, "Ouvert", categorie, note),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("tickets_list"))

    # Ici : affichage du formulaire en GET
    return render_template("ticket_new.html")


@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, titre, description, categorie, priorite, statut, note, date_creation FROM tickets WHERE id = ?",
        (ticket_id,),
    )
    ticket = cursor.fetchone()
    conn.close()

    if ticket is None:
        return "Ticket introuvable", 404
    return render_template("ticket_details.html", ticket=ticket)


# Statuts des tickets
@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_ticket_status(ticket_id):
    statut = request.form.get("statut")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tickets SET statut = ? WHERE id = ?",
        (statut, ticket_id),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

# Ajout d'une note au ticket
@app.route("/tickets/<int:ticket_id>/note", methods=["POST"])
def add_ticket_note(ticket_id):
    note = request.form.get("note")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tickets SET note = ? WHERE id = ?",
        (note, ticket_id),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

# Suppression d'un ticket
@app.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("tickets_list"))
@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")
if __name__ == "__main__":
    app.run(debug=True)
