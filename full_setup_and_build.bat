@echo off
REM Script pour préparer l'environnement et construire l'executable Windows
REM Utilisation: double-cliquez sur ce fichier ou lancez: full_setup_and_build.bat

setlocal enabledelayedexpansion

echo ==========================================
echo Configuration et Construction Windows
echo ==========================================
echo.

REM Chercher le fichier venv
if exist ".venv\Scripts\activate.bat" (
    echo ✓ Environnement virtuel trouvé
    echo 🔧 Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
    echo ✓ Environnement activé
    echo.
) else (
    echo ⚠️  Environnement virtuel non trouvé
    echo Assurez-vous d'être dans le répertoire racine du projet
    echo.
    pause
    exit /b 1
)

REM Vérifier que PyInstaller est installé
echo Vérification des dépendances...
pip show PyInstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 PyInstaller n'est pas installé, installation en cours...
    pip install PyInstaller --quiet
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation de PyInstaller
        echo Vérifiez votre connexion Internet
        pause
        exit /b 1
    )
    echo ✓ PyInstaller installé
) else (
    echo ✓ PyInstaller est installé
)

echo ✓ Toutes les dépendances sont présentes
echo.

REM Nettoyer les builds précédents
echo 🧹 Nettoyage des builds précédents...
if exist build (
    rmdir /s /q build >nul 2>&1
)
if exist dist (
    rmdir /s /q dist >nul 2>&1
)
if exist SuiviProjets.spec (
    del /q SuiviProjets.spec >nul 2>&1
)
echo ✓ Nettoyage effectué
echo.

REM Générer l'exécutable
echo 🔨 Construction de l'exécutable...
echo Cela peut prendre 2-5 minutes...
echo.
pyinstaller build.spec

REM Vérifier le succès
if exist "dist\SuiviProjets\SuiviProjets.exe" (
    echo.
    echo ==========================================
    echo ✅ SUCCÈS ! 
    echo ==========================================
    echo.
    echo 📁 Exécutable créé à:
    echo    dist\SuiviProjets\SuiviProjets.exe
    echo.
    echo 📊 Taille de l'installation: ~250-300 MB
    echo.
    echo 🚀 PRÊT À UTILISER :
    echo    1. Naviguez vers le dossier 'dist\SuiviProjets'
    echo    2. Double-cliquez sur 'SuiviProjets.exe'
    echo.
    echo 💾 DISTRIBUTION :
    echo    Copier le dossier complet 'dist\SuiviProjets' sur d'autres PC Windows
    echo    Aucune installation Python requise sur les machines cibles
    echo.
    pause
) else (
    echo.
    echo ==========================================
    echo ❌ ERREUR : La construction a échoué
    echo ==========================================
    echo.
    echo Les messages d'erreur sont affichés ci-dessus
    echo Vérifiez que tous les fichiers sont présents et intacts
    echo.
    pause
    exit /b 1
)
