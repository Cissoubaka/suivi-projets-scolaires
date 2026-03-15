#!/bin/bash

# Script de lancement de l'application

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "❌ Erreur : Environnement virtuel non trouvé"
    echo "Exécutez d'abord : python3 -m venv .venv"
    exit 1
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'application
cd app
python3 main.py
