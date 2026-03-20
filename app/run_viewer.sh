#!/bin/bash
# Script de lancement de la visionneuse

cd "$(dirname "$0")"
python3 viewer_main.py "$@"
