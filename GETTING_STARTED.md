# 🚀 Guide de Démarrage Rapide

## Installation (première fois)

### Option 1 : Automatique (Recommandé) 

```bash
chmod +x install.sh
./install.sh
```

### Option 2 : Manuel

```bash
# 1. Créer l'environnement virtuel
python3 -m venv .venv

# 2. Activer l'environnement
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

## Lancer l'application

### Option 1 : Script de lancement

```bash
chmod +x run.sh
./run.sh
```

### Option 2 : Manuel

```bash
source .venv/bin/activate  # N'oubliez pas si vous avez fermé le terminal
cd app
python3 main.py
```

---

## 📝 Utilisation de l'Application

### 1️⃣ Onglet "Gestion des Projets"

- **Ajouter un Projet** : Nom, Description, Nombre de répétitions, Taille des groupes
- **Éditer** : Modifier les paramètres d'un projet
- **Supprimer** : Supprimer un projet et tous ses groupes

**Exemple :**
- Nom : "Projet Python"
- Description : "Développer un chatbot"
- Répétitions : 3 (3 fois le même projet)
- Taille des groupes : 2 (binômes)

---

### 2️⃣ Onglet "Gestion des Élèves"

- **Ajouter** : Ajouter les élèves de la classe
- **Éditer** : Modifier le nom ou l'email
- **Supprimer** : Retirer un élève

⚠️ Les élèves doivent être ajoutés **avant** la répartition !

---

### 3️⃣ Onglet "Répartition des Groupes"

**Étapes :**

1. **Sélectionner un Projet** dans le dropdown
2. **Choisir la Répétition** (Rép. 1, Rép. 2, etc.)
3. **Créer les Groupes** → Bouton "Créer les Groupes" (création automatique)
4. **Répartition Manuelle** :
   - Cliquer sur un groupe dans la liste du milieu
   - Sélectionner un élève dans la colonne "Élèves non assignés" (droite)
   - Cliquer "Ajouter au groupe"
   - Pour retirer : Sélectionner dans la colonne du milieu + "Retirer de ce groupe"

**Layout :**
```
[Groupes] →  [Élèves du groupe] ← [Élèves non assignés]
```

---

### 4️⃣ Onglet "Export"

- **Exporter ce Projet** : Exporte le projet sélectionné en Excel
- **Exporter Tous les Projets** : Cré un fichier avec toutes les répétitions

📄 **Fichiers créés** :
- `NomDuProjet_rep1_20260313_150000.xlsx` (Un projet)
- `ALL_PROJECTS_20260313_150000.xlsx` (Tous les projets)

Les fichiers sont créés dans le **dossier courant** (généralement `suivi_projet/`)

---

## 🎯 Workflow Complet (Exemple)

### Scénario : 12 élèves, 3 projets

1. **Ajouter 3 projets** ⚙️
   - Projet A (3 rép., binômes)
   - Projet B (2 rép., trinômes)
   - Projet C (1 rép., binômes)

2. **Ajouter 12 élèves** 👥
   - Alice, Bob, Charlie, Diana, Eva, Frank, Grace, Henry, Iris, Jack, Kate, Liam

3. **Répartir les groupes** 📝
   - Projet A, Répétition 1 → Créer 6 groupes (12 élèves ÷ 2)
   - Projet A, Répétition 2 → Créer 6 groupes
   - Projet A, Répétition 3 → Créer 6 groupes
   - Projet B, Répétition 1 → Créer 4 groupes (12 élèves ÷ 3)
   - ... etc

4. **Exporter** 📊
   - Exporter tous les projets
   - Ouvrir le fichier Excel

---

## ❓ FAQ

### Q: Où sont sauvegardées mes données ?
**R:** Dans le fichier `app/projects.db` (SQLite)

### Q: Je peux ajouter plus de 3 élèves par groupe ?
**R:** Oui, configurez la "Taille des groupes" à 4, 5, etc.

### Q: Comment récupérer les données sauvegardées ?
**R:** Sauvegardez le fichier `app/projects.db` sur une clé USB ou un cloud

### Q: Puis-je supprimer et recréer les groupes ?
**R:** Oui, créer de nouveaux groupes supprime automatiquement les anciens

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5==5.15.9
```

### "L'application ne démarre pas"
```bash
python3 --version  # Vérifiez que vous avez Python 3.7+
pip list  # Vérifiez que PyQt5 et openpyxl sont installés
```

### "Je ne peux pas lancer run.sh"
```bash
chmod +x run.sh  # Rendre le script exécutable
./run.sh
```

---

## 📞 Support

Pour toute question, consultez le fichier `README.md` ou créez une issue.

**Bon projet ! 🎉**
