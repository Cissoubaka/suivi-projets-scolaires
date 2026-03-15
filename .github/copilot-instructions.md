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
├── main.py              # Point d'entrée - Lance la fenêtre principale
├── main_window.py       # Interface PyQt5 avec 4 onglets
├── database.py          # Couche de données SQLite
└── export.py            # Export vers Excel (openpyxl)
```

### Flux de données

1. **PyQt5 UI** → appelle les méthodes de **Database**
2. **Database** → requêtes SQL SQLite (projects.db)
3. **Export** → génère fichiers Excel avec **openpyxl**

## Fonctionnalités implémentées

- ✅ Onglet 1 : Gestion des projets (CRUD)
- ✅ Onglet 2 : Gestion des élèves (CRUD)
- ✅ Onglet 3 : Répartition manuelle dans les groupes
- ✅ Onglet 4 : Export en Excel

## Instruction de démarrage

```bash
# 1. Environnement Python déjà configuré
# 2. Dépendances déjà installées (PyQt5, openpyxl)
# 3. Lancer l'application
cd app
python3 main.py
```

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

- Import CSV/Excel d'élèves
- Algorithme de répartition automatique
- Interface web (Flask)
- Statistiques et rapports

## Notes importantes

- Les données sont sauvegardées en temps réel dans SQLite
- L'export crée des fichiers xlsx dans le dossier courant
- La répartition manuelle permet une flexibilité maximale
- Pas d'authentification (app locale)
