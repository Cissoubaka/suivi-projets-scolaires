# Application de Suivi de Projets Scolaires

Enseignant en STI2D en spécialité IT, j'avais besoin d'une application qui permette de gérer et évaluer des projets


## Fonctionnalités

- ✅ Créer et gérer des projets scolaires
- ✅ Définir le nombre de répétitions d'un projet
- ✅ Configurer la taille des groupes (binômes, trinômes, etc.)
- ✅ Gérer une liste d'élèves
- ✅ Répartition **manuelle** des élèves dans les groupes
- Création des taches et de leur notation
- ✅ Créer les groupes automatiquement
- configuration des répertoires
- ✅ Export en LibreOffice Calc (.ods) directement dans le repertoire de travail des eleves
- ✅ Persistance des données (SQLite)
- Suivi de présence et évaluation par séance (journal de bord, GANTT, travail)
- Evaluation de toutes les taches


## Installation

### Prérequis
- Python 3.7+
- pip

### Étapes

1. **Cloner ou télécharger le projet :**
```bash
cd suivi_projet
```

2. **Créer un environnement virtuel (recommandé) :**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

## Utilisation

### Démarrer l'application

```bash
cd app
python3 main.py
```

### Workflow type

1. **Gestion des Projets** ⚙️
   - Ajouter les projets scolaires
   - Définir le nombre de répétitions (ex: 3 groupes qui font le même projet)
   - Configurer la taille des groupes (2 = binôme, 3 = trinôme)

2. **Gestion des Élèves** 👥
   - Ajouter tous les élèves
   - Optionnel : ajouter leurs emails

3. **Répartition des Groupes** 📝
   - Sélectionner un projet
   - Cliquer sur "Créer les Groupes" (création automatique)
   - **Drag & Drop Manuel** : Ajouter/retirer des élèves dans les groupes
   - Les élèves non assignés apparaissent dans la colonne de droite

4. **Export** 📊
   - Exporter le projet courant ou tous les projets
   - Les fichiers Excel sont créés dans le dossier courant

## Structure du Projet

```
suivi_projet/
├── app/
│   ├── main.py              # Point d'entrée
│   ├── main_window.py       # Interface PyQt5
│   ├── database.py          # Gestion de la BD SQLite
│   ├── export.py            # Export Excel
│   └── projects.db          # Base de données (créée au 1er lancement)
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

## Technologies Utilisées

- **PyQt5** : Interface graphique desktop
- **SQLite** : Base de données locale
- **openpyxl** : Export en Excel/LibreOffice Calc

## Fichiers de sortie

Les fichiers Excel exportés sont créés dans le dossier courant avec le format :
- Projet unique : `NomDuProjet_rep1_20260313_153045.xlsx`
- Tous les projets : `ALL_PROJECTS_20260313_153045.xlsx`

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt5'"
→ Assurez-vous d'avoir installé les dépendances : `pip install -r requirements.txt`

### L'application ne démarre pas
→ Vérifiez votre version de Python : `python3 --version` (3.7+ requis)

### Les données ne persistent pas
→ Vérifiez les permissions d'écriture dans le dossier `/app`

## Développement futur

- [ ] Import d'élèves depuis CSV/Excel
- [ ] Répartition automatique intelligente
- [ ] Interface web
- [ ] Historique des modifications
- [ ] Statistiques et rapports

## License

Libre d'utilisation pour usage scolaire

## Support

Pour toute question ou bug, consultez la documentation ou créez une issue.
