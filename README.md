# Support Lab

![image](https://github.com/eth3ral0/supportlab/blob/main/banner.png)

Application web de **ticketing** développée avec Flask et Python, conçue pour centraliser les demandes support et suivre leur traitement de manière simple et pédagogique.

## Fonctionnalités

- Création de tickets de support (titre, description, éventuellement priorité / catégorie selon ton implémentation).
- Liste des tickets existants avec leur statut (par exemple : ouvert, en cours, résolu).
- Consultation du détail d’un ticket sur une page dédiée.
- Utilisation de templates HTML (`templates/`) avec une base commune (`base.html`) et des vues spécifiques :
  - `tickets_list.html` : liste des tickets.
  - `ticket_new.html` : création d’un nouveau ticket.
  - `ticket_details.html` : détail d’un ticket.
  - `404.html` : page d’erreur personnalisée.
- Stockage des données dans une base SQLite (`supportlab.db`).

## Prérequis

- Python 3.x  
- Bibliothèque Python :
  - `Flask`

Installation des dépendances :

```bash
pip install -r requirements.txt
```

Initialisation de la base de données :

```bash
python init_db.py
```
Cela crée (ou met à jour) le fichier supportlab.db avec la structure nécessaire pour les tickets.

Démarrage de l’application
Depuis la racine du projet SUPPORTLAB :

```bash
python app.py
```
Par défaut, l’application Flask est accessible à l’adresse :
```text
http://127.0.0.1:5000
```

Cas d’usage :

- Centraliser les demandes utilisateurs (incidents, demandes de service) dans une interface unique.

- Disposer d’un mini outil de ticketing pour un petit lab, un club, un projet étudiant ou une équipe interne.

- Illustrer des compétences en développement web back-end avec Flask (routes, templates, gestion de formulaires) et en gestion de données avec SQLite.

Améliorations futures :

- Ajouter un système d’authentification (comptes agents / utilisateurs) et des rôles.

- Gérer des priorités, catégories et filtres (par statut, date, type de ticket).

- Ajouter la possibilité de joindre des fichiers (captures d’écran, logs).

- Mettre en place des notifications e-mail à la création ou mise à jour d’un ticket.

- Ajouter un dashboard avec statistiques (nombre de tickets ouverts, résolus, temps moyen de traitement).
