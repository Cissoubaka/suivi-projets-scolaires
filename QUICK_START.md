# 🎓 Application de Suivi de Projets Scolaires

**Une solution desktop simple et efficace pour gérer et répartir des projets scolaires entre élèves.**

---

## ✨ Fonctionnalités

| Onglet | Fonctionnalités |
|--------|-----------------|
| **📋 Gestion des Projets** | Créer, éditer, supprimer des projets scolaires |
| **👥 Gestion des Élèves** | Ajouter, éditer, supprimer des élèves |
| **👨‍👩‍👧 Répartition des Groupes** | Créer les groupes automatiquement, répartition manuelle des élèves |
| **📊 Export** | Exporter en Excel/LibreOffice Calc |

---

## 🚀 Démarrage Rapide

### Installation (5 minutes)

```bash
# 1. Cloner/télécharger le projet
cd suivi_projet

# 2. Installer automatiquement (Linux/Mac)
chmod +x install.sh
./install.sh

# Ou manuellement
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancer l'Application

```bash
./run.sh

# Ou manuellement
source .venv/bin/activate
cd app
python3 main.py
```

---

## 📖 Mode d'Emploi

### 1️⃣ **Ajouter les Projets** (Onglet 1)
- Cliquez **"+ Ajouter Projet"**
- Remplissez :
  - **Nom** : Ex. "Projet Python"
  - **Description** : Ex. "Créer un chatbot"
  - **Répétitions** : Combien de fois le projet est proposé (ex: 3)
  - **Taille des groupes** : 2 (binôme) ou 3 (trinôme)

### 2️⃣ **Ajouter les Élèves** (Onglet 2)
- Cliquez **"+ Ajouter Élève"**
- Entrez le nom et optionnel l'email
- ⚠️ Les élèves doivent être ajoutés AVANT la répartition

### 3️⃣ **Répartir dans les Groupes** (Onglet 3)
1. Sélectionnez le projet et la répétition
2. Cliquez **"Créer les Groupes"** → Les groupes sont créés automatiquement
3. **Répartition manuelle** :
   - Cliquez sur un groupe
   - Sélectionnez un élève dans la colonne droite
   - Cliquez **"Ajouter"**
   - Pour retirer : Colonne milieu + **"Retirer"**

### 4️⃣ **Exporter en Excel** (Onglet 4)
- **"Exporter ce Projet"** → Fichier pour le projet courant
- **"Exporter Tous les Projets"** → Un grand fichier avec tout

---

## 💾 Données

- **Sauvegarde automatique** : Toutes les données sont sauvegardées en temps réel
- **Fichier BD** : `app/projects.db` (SQLite)
- **Backup** : Copiez `projects.db` pour sauvegarder vos données

---

## 📁 Structure du Projet

```
suivi_projet/
├── app/
│   ├── main.py              # Point d'entrée
│   ├── main_window.py       # Interface Tkinter
│   ├── database.py          # Base de données SQLite
│   ├── export.py            # Export Excel (openpyxl)
│   └── projects.db          # Données (créé au 1er lancement)
├── requirements.txt         # Dépendances (openpyxl)
├── install.sh              # Script d'installation
├── run.sh                  # Script de lancement
├── test_app.py             # Test qui valide l'installation
├── README.md               # Documentation complète
└── GETTING_STARTED.md      # Guide de démarrage
```

---

## ⚙️ Prérequis

- **Python 3.7+** (préinstallé sur la plupart des systèmes)
- **Tkinter** (inclus avec Python par défaut)
- **openpyxl** (installé via pip, pour Excel)

**Pas besoin de PyQt5, Qt, ou dépendances graphiques compliquées !**

---

## 🔧 Troubles ?

### "ModuleNotFoundError: openpyx"
```bash
pip install --upgrade openpyxl
```

### "Command 'python3' not found"
```bash
# Installer Python (Ubuntu/Debian)
sudo apt-get install python3 python3-pip
```

### L'app ne démarre pas
```bash
# Vérifier la version Python
python3 --version  # Doit être 3.7+

# Vérifier la BD
ls app/projects.db  # Doit exister
```

---

## 📊 Exemple d'Utilisation

**Scénario : 15 élèves, 2 projets, 3 répétitions chacun**

```
Projet A (3 répétitions, binômes → 8 groupes chacun)
└── Rép. 1 : Groupes 1-8 (2 élèves chacun)
└── Rép. 2 : Groupes 1-8 (2 élèves chacun)
└── Rép. 3 : Groupes 1-7 + 1 groupe de 3 élèves

Projet B (3 rép., trinômes → 5 groupes)
└── Rép. 1 : Groupes 1-5 (3 élèves)
└── ...
```

💡 **Vous contrôlez la répartition à 100% !** Créez les groupes automatiquement, puis ajustez-les manuellement si besoin.

---

## 📈 Futur (Idées)

- [ ] Import d'élèves depuis CSV
- [ ] Répartition intelligente automatique
- [ ] Historique des modifications
- [ ] Statistiques (nb de projets par élève, etc.)
- [ ] Interface web pour accès distant

---

## 💡 Conseils

✅ **Best Practices** :
- Sauvegardez régulièrement votre `projects.db`
- Tester avec quelques élèves d'abord
- Exporter après chaque répartition pour archiver

❌ **À éviter** :
- Supprimer `projects.db` sans backup
- Modifier la BD directement sans UI
- Fermer l'app sans exporter vos groupes

---

## 👨‍💻 Technique

- **Frontend** : Tkinter (GUI native Python, zéro dépendances)
- **Backend** : Python 3.7+
- **BD** : SQLite 3
- **Export** : openpyxl (Excel/LibreOffice)

**Avantages** :
- ✅ Zéro dépendances GTK/Qt
- ✅ Ultra léger et rapide
- ✅ Fonctionne sur Raspberry Pi, Linux, Mac, Windows
- ✅ Pas de compilation
- ✅ Code simple et maintenable

---

## 📄 License

Libre d'utilisation pour usage scolaire et éducatif.

---

**Questions ?** Consultez [GETTING_STARTED.md](GETTING_STARTED.md) ou [README.md](README.md)

**Bon projet ! 🎉**
