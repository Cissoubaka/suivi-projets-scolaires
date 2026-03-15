#!/bin/bash
# Script pour générer l'executable Windows avec PyInstaller

echo "=========================================="
echo "Création de l'exécutable Windows"
echo "=========================================="
echo ""

# Vérifier que PyInstaller est installé
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller n'est pas installé"
    echo "Installation: pip install PyInstaller"
    exit 1
fi

# Nettoyer les builds précédents
echo "🧹 Nettoyage des builds précédents..."
rm -rf build dist SuiviProjets.spec

# Générer l'exécutable
echo "🔨 Construction de l'exécutable..."
pyinstaller build.spec

# Vérifier le succès
if [ -d "dist/SuiviProjets" ]; then
    echo ""
    echo "✅ SUCCÈS ! Exécutable créé avec succès"
    echo ""
    echo "📁 Localisation: dist/SuiviProjets/SuiviProjets.exe"
    echo ""
    echo "📝 Pour utiliser l'exécutable :"
    echo "   1. Copier le dossier 'dist/SuiviProjets' sur votre machine Windows"
    echo "   2. Lancer 'SuiviProjets.exe'"
    echo ""
else
    echo ""
    echo "❌ ERREUR : La construction a échoué"
    echo "Vérifiez les messages d'erreur ci-dessus"
    exit 1
fi
