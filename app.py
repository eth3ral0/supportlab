from contextlib import contextmanager
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

@contextmanager
def get_db():
    """Context manager pour la gestion automatique des connexions DB"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

@app.route("/")
def index():
    return redirect(url_for("tickets_list"))

@app.route("/tickets")
def tickets_list():
    # Récupérer les paramètres de filtre
    filtre_statut = request.args.get('statut', '')
    filtre_priorite = request.args.get('priorite', '')
    filtre_categorie = request.args.get('categorie', '')
    recherche = request.args.get('search', '')
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Construction de la requête avec filtres
            query = "SELECT id, titre, categorie, priorite, statut, note, date_creation FROM tickets WHERE 1=1"
            params = []
            
            if filtre_statut:
                query += " AND statut = ?"
                params.append(filtre_statut)
            
            if filtre_priorite:
                query += " AND priorite = ?"
                params.append(filtre_priorite)
            
            if filtre_categorie:
                query += " AND categorie = ?"
                params.append(filtre_categorie)
            
            if recherche:
                query += " AND (titre LIKE ? OR description LIKE ?)"
                params.append(f"%{recherche}%")
                params.append(f"%{recherche}%")
            
            query += " ORDER BY id DESC"
            
            cursor.execute(query, params)
            tickets = cursor.fetchall()
            
        return render_template("tickets_list.html", tickets=tickets, 
                             filtre_statut=filtre_statut,
                             filtre_priorite=filtre_priorite,
                             filtre_categorie=filtre_categorie,
                             recherche=recherche)
    except sqlite3.Error as e:
        flash(f"Erreur lors du chargement des tickets: {str(e)}", "danger")
        return render_template("tickets_list.html", tickets=[])


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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, titre, description, categorie, priorite, statut, note, date_creation FROM tickets WHERE id = ?",
            (ticket_id,),
        )
        ticket = cursor.fetchone()
        conn.close()
        
        if ticket is None:
            flash("Ticket introuvable", "warning")
            return redirect(url_for("tickets_list"))
        
        return render_template("ticket_details.html", ticket=ticket)
    except sqlite3.Error as e:
        flash(f"Erreur lors de la récupération du ticket: {str(e)}", "danger")
        return redirect(url_for("tickets_list"))


# Statuts des tickets
@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_ticket_status(ticket_id):
    statut = request.form.get("statut", "").strip()

    # Validation du statut (whitelist)
    statuts_valides = ["Ouvert", "En cours", "Résolu", "Fermé"]
    if statut not in statuts_valides:
        flash("Statut invalide", "danger")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET statut = ? WHERE id = ?",
            (statut, ticket_id),
        )
        conn.commit()
        conn.close()
        flash("Statut mis à jour avec succès", "success")
    except sqlite3.Error as e:
        flash(f"Erreur lors de la mise à jour: {str(e)}", "danger")
    
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))
    

# Ajout d'une note au ticket
@app.route("/tickets/<int:ticket_id>/note", methods=["POST"])
def add_ticket_note(ticket_id):
    note = request.form.get("note", "").strip()
    
    # Pas de validation stricte, la note peut être vide
    # On accepte même une note vide pour effacer une note existante
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET note = ? WHERE id = ?",
            (note, ticket_id),
        )
        conn.commit()
        conn.close()
        
        if note:
            flash("Note mise à jour avec succès", "success")
        else:
            flash("Note supprimée", "info")
            
    except sqlite3.Error as e:
        flash(f"Erreur lors de la mise à jour de la note: {str(e)}", "danger")
    
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


# Suppression d'un ticket
@app.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        ticket = cursor.fetchone()
        
        if not ticket:
            conn.close()
            flash("Ticket introuvable", "danger")
            return redirect(url_for("tickets_list"))
        
        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        conn.commit()
        conn.close()
        flash("Ticket supprimé avec succès", "success")
    except sqlite3.Error as e:
        flash(f"Erreur lors de la suppression: {str(e)}", "danger")

    return redirect(url_for("tickets_list"))

@app.route("/reports")
def reports():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Statistiques générales
            cursor.execute("SELECT COUNT(*) as total FROM tickets")
            total_tickets = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE statut = 'Ouvert'")
            tickets_ouverts = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE statut = 'En cours'")
            tickets_en_cours = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE statut = 'Résolu'")
            tickets_resolus = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE statut = 'Fermé'")
            tickets_fermes = cursor.fetchone()['total']
            
            # Répartition par priorité
            cursor.execute("""
                SELECT priorite, COUNT(*) as count 
                FROM tickets 
                GROUP BY priorite
            """)
            repartition_priorite = cursor.fetchall()
            
            # Répartition par catégorie
            cursor.execute("""
                SELECT categorie, COUNT(*) as count 
                FROM tickets 
                GROUP BY categorie
            """)
            repartition_categorie = cursor.fetchall()
            
            # Tickets récents (7 derniers jours)
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM tickets 
                WHERE date_creation >= datetime('now', '-7 days')
            """)
            tickets_recents = cursor.fetchone()['total']
            
            stats = {
                'total': total_tickets,
                'ouverts': tickets_ouverts,
                'en_cours': tickets_en_cours,
                'resolus': tickets_resolus,
                'fermes': tickets_fermes,
                'recents': tickets_recents,
                'repartition_priorite': repartition_priorite,
                'repartition_categorie': repartition_categorie
            }
            
        return render_template("reports.html", stats=stats)
    except sqlite3.Error as e:
        flash(f"Erreur lors du chargement des rapports: {str(e)}", "danger")
        return render_template("reports.html", stats=None)

@app.route("/settings")
def settings():
    # Configuration de l'application
    config = {
        'statuts': ["Ouvert", "En cours", "Résolu", "Fermé"],
        'priorites': ["Basse", "Normale", "Haute"],
        'categories': ["Support utilisateur", "Problème technique", "Demande de service"]
    }
    return render_template("settings.html", config=config)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    # Active le debug seulement si on est en mode développement
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
