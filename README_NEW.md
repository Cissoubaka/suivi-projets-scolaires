# Application de Suivi de Projets Scolaires

Une application desktop pour gérer et répartir des projets scolaires entre des élèves avec export en Excel/LibreOffice Calc.

## ✨ Fonctionnalités

- ✅ Créer et gérer des projets scolaires
- ✅ Définir le nombre de répétitions d'un projet
- ✅ Définir le nombre de groupes (répartition équitable automatique)
- ✅ Gérer les élèves (prénom + nom) via interface ou **import CSV**
- ✅ Répartition **manuelle** des élèves dans les groupes
- ✅ Créer les groupes automatiquement
- ✅ Export en Excel/LibreOffice Calc (.xlsx)
- ✅ Persistance des données (SQLite)

## 📥 Import CSV

Vous pouvez importer rapidement une liste d'élèves depuis un fichier CSV.

**Format CSV obligatoire** :
```csv
nom
DUPONTAlice
MARTINBob
DURANDCharlie
```

La première colonne contient le **nom en majuscules + prénom en minuscules** (collés ensemble).

**Format détaillé** :
- **Majuscules** = nom de famille (ex: DUPONT)
- **Minuscules** = prénom (ex: Alice)

**Exemples valides** :
- `DUPONTAlice` → Nom: DUPONT, Prénom: Alice ✓
- `MARTINBob` → Nom: MARTIN, Prénom: Bob ✓
- `PETITJean-Paul` → Nom: PETIT, Prénom: Jean-Paul ✓

Les autres colonnes du CSV (s'il y en a) sont ignorées - seule la première colonne est lue.

**Étapes** :
1. Allez dans l'onglet "Gestion des Élèves"
2. Cliquez sur "Importer depuis CSV"
3. Sélectionnez votre fichier CSV
4. Les élèves sont importés automatiquement

Un exemple de fichier est fourni : `exemple_eleves.csv`

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
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
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
   - Configurer le nombre de groupes (ex: 5 groupes)

2. **Gestion des Élèves** 👥
   - Ajouter les élèves manuellement (Prénom + Nom)
   - Ou importer depuis un fichier CSV en cliquant "Importer depuis CSV"

3. **Répartition des Groupes** 📝
   - Sélectionner un projet
   - Cliquer sur "Créer les Groupes" (création automatique et équitable)
   - **Répartition Manuelle** : Ajouter/retirer des élèves dans les groupes
   - Les élèves non assignés apparaissent dans la colonne de droite

4. **Export** 📊
   - Exporter le projet courant ou tous les projets
   - Les fichiers Excel sont créés dans le dossier courant

## Structure du Projet

```
suivi_projet/
├── app/
│   ├── main.py              # Point d'entrée
│   ├── main_window.py       # Interface PyQt6
│   ├── database.py          # Gestion de la BD SQLite
│   ├── export.py            # Export Excel
│   └── projects.db          # Base de données (créée au 1er lancement)
├── requirements.txt         # Dépendances Python
├── exemple_eleves.csv       # Exemple pour l'import
├── README.md               # Ce fichier
├── QUICK_START.md          # Guide rapide
└── GETTING_STARTED.md      # Guide détaillé
```

## Technologies Utilisées

- **PyQt6** : Interface graphique desktop
- **SQLite** : Base de données locale
- **openpyxl** : Export en Excel/LibreOffice Calc

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"
→ Assurez-vous d'avoir installé les dépendances : `pip install -r requirements.txt`

### L'application ne démarre pas
→ Vérifiez votre version de Python : `python3 --version` (3.7+ requis)

### Les données ne persistent pas
→ Vérifiez les permissions d'écriture dans le dossier `/app`

### L'import CSV ne fonctionne pas
→ Vérifiez le format du fichier : 2 colonnes (prénom, nom) avec header

## Développement futur

- [ ] Répartition automatique intelligente
- [ ] Interface web
- [ ] Historique des modifications
- [ ] Statistiques et rapports

## License

Libre d'utilisation pour usage scolaire

## Support

Pour toute question, consultez les fichiers de documentation ou créez une issue.
