#!/bin/bash

# Script d'installation de l'application

echo "🚀 Installation de l'Application de Suivi de Projets Scolaires"
echo "============================================================="

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur : Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 détecté"
python3 --version

# Créer l'environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate

# Mettre à jour pip
echo ""
echo "🔄 Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo ""
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "✅ Installation terminée !"
echo ""
echo "🎉 Prêt à démarrer l'application !"
echo ""
echo "Pour lancer l'app, exécutez :"
echo "  ./run.sh"
echo ""
echo "Ou manuellement :"
echo "  source .venv/bin/activate"
echo "  cd app"
echo "  python3 main.py"
