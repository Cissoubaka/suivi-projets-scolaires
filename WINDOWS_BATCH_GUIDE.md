# 🪟 Guide : Créer l'Exécutable Windows

## 📋 Fichiers fournis

Vous avez maintenant **2 scripts batch** pour créer l'exécutable :

### 1. **`full_setup_and_build.bat`** ⭐ (Recommandé)
- **Idéal pour** : Premier build, ou après avoir changé de répertoire
- **Ce qu'il fait** :
  - Active l'environnement virtuel Python
  - Installe PyInstaller si nécessaire
  - Nettoie les anciens builds
  - Crée l'exécutable

### 2. **`build_windows.bat`** (Simple)
- **Idéal pour** : Rebuilds rapides si PyInstaller est déjà installé
- **Ce qu'il fait** :
  - Nettoie les anciens builds
  - Crée l'exécutable directement

---

## 🚀 Utilisation

### Méthode 1 : Double-clic (Facile)
1. **Windows Explorer** → Aller à `/home/cissou/suivi_projet`
2. **Double-clic** sur :
   - `full_setup_and_build.bat` ← Première fois
   - `build_windows.bat` ← Builds suivants

### Méthode 2 : Ligne de commande

```cmd
REM Depuis le répertoire du projet
full_setup_and_build.bat
```

---

## ⏱️ Durée

- **Premier build** : 3-5 minutes
- **Builds suivants** : 2-3 minutes

---

## ✅ Résultat attendu

Après succès, vous verrez :

```
✅ SUCCÈS ! 

📁 Exécutable créé à:
   dist\SuiviProjets\SuiviProjets.exe

🚀 PRÊT À UTILISER :
   1. Naviguez vers le dossier 'dist\SuiviProjets'
   2. Double-cliquez sur 'SuiviProjets.exe'
```

---

## 💾 Distribution

Pour partager l'application avec d'autres :

1. **Copier le dossier** `dist\SuiviProjets\` entier
2. **Copier sur un autre PC Windows**
3. **Lancer** `SuiviProjets.exe`

**Requêtes système** :
- Windows 7+
- Aucune installation Python requise
- ~300 MB d'espace disque

---

## 🐛 Dépannage

### Erreur : "PyInstaller not found"
→ Le script essaie de l'installer automatiquement
→ Si ça échoue, installez manuellement :
```cmd
pip install PyInstaller
```

### Erreur : "Module not found"
→ Assurez-vous que toutes les dépendances sont installées :
```cmd
pip install -r requirements.txt
```

### Erreur : "'pyinstaller' is not recognized"
→ Utilisez le script `full_setup_and_build.bat` qui active l'environnement

### L'exécutable est trop volumineux
→ C'est normal (~250 MB avec PyQt6)
→ Vous pouvez le compresser :
```cmd
tar -czf SuiviProjets.tar.gz dist\SuiviProjets\
```

---

## 📝 Notes importantes

- ✅ L'exécutable est **portable** (copier/coller sur autre PC)
- ✅ La base de données SQLite se crée **automatiquement** au premier lancement
- ✅ Les exports (ODS, Excel) vont dans le même répertoire que l'exe
- ✅ Chaque update du code : relancer le script pour rebuild

---

## 🔄 Workflow typical

```
1. Modifier le code Python
   ↓
2. Tester sur votre machine (python main.py)
   ↓
3. Lancer build_windows.bat
   ↓
4. Tester dist\SuiviProjets\SuiviProjets.exe
   ↓
5. Si OK → Copier dist\SuiviProjets\ pour distribution
```

---

## ❓ Besoin d'aide ?

Si un script échoue :
1. **Lire l'erreur** affichée dans la console
2. **Exécuter depuis CMD** pour voir les messages :
   ```cmd
   cd C:\path\to\suivi_projet
   full_setup_and_build.bat
   ```
3. **Vérifier les prérequis** :
   - Python est installé et dans le PATH
   - pip fonctionne
   - Espace disque disponible
