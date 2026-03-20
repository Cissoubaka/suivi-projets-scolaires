# Instructions pour l'Application de Suivi de Projets Scolaires

## Vue d'ensemble du projet

Application desktop Python (PyQt5) permettant de gérer des projets scolaires avec :
- Gestion des projets (créer, éditer, supprimer)
- Gestion des élèves
- Répartition manuelle des élèves dans les groupes
- Export des résultats en Excel/LibreOffice Calc
- Persistance des données via SQLite

## Architecture

```
app/
├── main.py                     # Point d'entrée - Lance l'application principale
├── main_window.py              # Interface PyQt5 avec les onglets de gestion
├── database.py                 # Couche de données SQLite
├── export.py                   # Export vers Excel (openpyxl)
├── viewer_main.py              # Point d'entrée - Lance la visionneuse
├── viewer_window.py            # Fenêtre de la visionneuse (3 onglets)
├── viewer_base_tab.py          # Classe de base pour onglets visionneuse
├── viewer_attendance_tab.py    # Onglet suivi présence (lecture seule)
├── viewer_evaluation_tab.py    # Onglet évaluation (lecture seule)
├── viewer_task_assignment_tab.py # Onglet répartition tâches (lecture seule)
└── tabs/
    ├── projects_tab.py         # Onglet gestion des projets
    ├── students_tab.py         # Onglet gestion des élèves
    └── ...autres onglets...
```

### Flux de données

1. **PyQt5 UI** → appelle les méthodes de **Database**
2. **Database** → requêtes SQL SQLite (projects.db)
3. **Export** → génère fichiers Excel avec **openpyxl**

## Fonctionnalités implémentées

### Application Principale (app/main.py)
- ✅ Onglet 1 : Gestion des projets (CRUD)
- ✅ Onglet 2 : Gestion des élèves (CRUD)
- ✅ Onglet 3 : Répartition manuelle dans les groupes
- ✅ Onglet 4+ : Suivi de présence, Évaluation, Tâches, etc.
- ✅ Export en Excel/LibreOffice Calc

### Visionneuse (app/viewer_main.py)
- ✅ Onglet Suivi de Présence (lecture seule)
- ✅ Onglet Évaluation (lecture seule)
- ✅ Onglet Répartition des Tâches (lecture seule)
- ✅ Même visuel que l'app principale
- ✅ Aucune modification possible
- ✅ Destinée aux élèves

## Instructions de démarrage

### Application Principale
```bash
# 1. Environnement Python déjà configuré
# 2. Dépendances déjà installées (PyQt6, openpyxl)
# 3. Lancer l'application
cd app
python3 main.py
```

### Visionneuse (Élèves)
```bash
# Lancer la visionneuse en lecture seule
cd app
python3 viewer_main.py

# Ou utiliser le script de lancement
./run_viewer.sh
```

**Note**: La visionneuse utilise la même base de données que l'app principale.

## Conventions de code

- Noms de fonctions en snake_case
- Classes en PascalCase
- Imports organisés : stdlib, puis PyQt5, puis modules locaux
- Docstrings en français

## Base de données

SQLite avec 5 tables :
- `projects` : projets scolaires
- `students` : élèves
- `groups` : groupes par projet/répétition
- `group_students` : relation many-to-many

La BD est créée automatiquement au premier lancement.

## Points d'extension/amélioration future

### Application Principale
- Import CSV/Excel d'élèves
- Algorithme de répartition automatique
- Interface web (Flask)
- Statistiques et rapports

### Visionneuse
- Authentification des élèves
- Affichage personnalisé (données personnelles seulement)
- Export en PDF
- Comparaison anonyme avec les pairs
- Diagrammes de progression

## Notes importantes

- Les données sont sauvegardées en temps réel dans SQLite
- L'export crée des fichiers xlsx dans le dossier courant
- La répartition manuelle permet une flexibilité maximale
- Pas d'authentification (app locale)
