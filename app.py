import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-insecure')
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'supportlab.db')

if app.config['SECRET_KEY'] == 'dev-key-insecure':
    print("WARNING: Using default insecure secret key. Set a proper SECRET_KEY in the .env file for production.")

# Accès à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
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
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        categorie = request.form.get("categorie", "").strip()
        priorite = request.form.get("priorite", "").strip()
        note = request.form.get("note", "").strip()
        
        # Validation des champs
        if not titre:
            flash("Le titre est obligatoire.", "danger")
            return render_template("ticket_new.html")
        if not description:
            flash("La description est obligatoire.", "danger")
            return render_template("ticket_new.html")
        priorite_valides = ["Basse", "Moyenne", "Haute"]
        
        # Validation de la priorité (whitelist)
        if priorite not in priorite_valides:
            flash("La priorité doit être l'une des suivantes : Basse, Moyenne, Haute.", "danger")
            return render_template("ticket_new.html")
        
        # Validation de la catégorie (whitelist)
        categories_valides = ["Logiciel", "Matériel", "Réseau", "Autre"]
        if categorie not in categories_valides:
            flash("Catégorie invalide", "danger")
            return render_template("ticket_new.html")

        # Insertion sécurisée avec gestion d'erreur
        try:
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
            flash("Ticket créé avec succès !", "success")
            return redirect(url_for("tickets_list"))
        except Exception as e:
            flash(f"Une erreur est survenue lors de la création du ticket : {str(e)}", "danger")
            return render_template("ticket_new.html")

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
    app.run(debug=False)
