# Guide : Créer un Exécutable Windows

## 📋 Prérequis

- **Python 3.8+** (vous avez Python 3.13.5 ✓)
- **PyInstaller** (déjà installé ✓)
- Tous les packages dans `requirements.txt` (déjà installés ✓)

## 🚀 Étapes

### Option 1 : Via le script (Recommandé)

```bash
# Linux/Mac
chmod +x build_windows.sh
./build_windows.sh

# Ou manuellement
bash build_windows.sh
```

### Option 2 : Commande directe

```bash
# Depuis la racine du projet
pyinstaller build.spec
```

## 📂 Résultat

Après succès, vous trouverez :
- **`dist/SuiviProjets/`** : Dossier avec l'exécutable complet (UTILISÉ SUR WINDOWS)
- **`build/`** : Fichiers temporaires de construction
- **`SuiviProjets.spec`** : Fichier de configuration généré

## 🔧 Configuration (build.spec)

Le fichier `build.spec` contrôle la génération :
- **`console=False`** : Lance l'app sans console (pur GUI)
- **`console=True`** : Lance avec une fenêtre console (utile pour les debug)

Pour basculer, modifiez la ligne :
```python
console=False,  # Mettre True pour activer la console
```

## 💾 Distribution sur Windows

Pour distribuer votre application sur d'autres machines Windows :

1. **Copier le dossier** `dist/SuiviProjets/` entier
2. **Sur la machine cible** : Lancer `SuiviProjets.exe`

**Requêtes système Windows** :
- Windows 7+ (testé sur Windows 10/11)
- Aucune installation Python requise
- ~200-300 MB d'espace disque

## 🐛 Dépannage

### Erreur : "ModuleNotFoundError"
→ Vérifier que le module est dans `hiddenimports` dans build.spec

### Erreur : "DLL not found"
→ Vérifier que PyQt6 est bien installé :
```bash
pip install PyQt6 --upgrade
```

### L'exécutable est trop volumineux
→ C'est normal avec PyQt6 (~250 MB). Vous pouvez compresser le dossier `dist/`

## 📌 Notes

- L'exécutable inclut Python et toutes les dépendances
- La base de données SQLite sera créée au premier lancement
- Les fichiers d'export iront dans le même répertoire que l'exe

## ✅ Vérification

Après création, testez sur Windows :
1. Lancer `dist/SuiviProjets/SuiviProjets.exe`
2. Vérifier que l'interface PyQt6 s'affiche correctement
3. Tester une création de projet et un export
