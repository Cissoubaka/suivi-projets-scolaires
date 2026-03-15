@echo off
REM Script pour générer l'executable Windows avec PyInstaller
REM Utilisation: double-cliquez sur ce fichier ou lancez: build_windows.bat

setlocal enabledelayedexpansion

echo ==========================================
echo Création de l'exécutable Windows
echo ==========================================
echo.

REM Vérifier que PyInstaller est installé
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller n'est pas installé
    echo Installation: pip install PyInstaller
    echo.
    pause
    exit /b 1
)

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

REM Générer l'exécutable
echo 🔨 Construction de l'exécutable...
echo Cela peut prendre quelques minutes...
echo.
pyinstaller build.spec

REM Vérifier le succès
if exist "dist\SuiviProjets\SuiviProjets.exe" (
    echo.
    echo ✅ SUCCÈS ! Exécutable créé avec succès
    echo.
    echo 📁 Localisation: dist\SuiviProjets\SuiviProjets.exe
    echo.
    echo 📝 Pour utiliser l'exécutable :
    echo    1. Aller dans le dossier 'dist\SuiviProjets'
    echo    2. Double-cliquer sur 'SuiviProjets.exe'
    echo.
    echo 💾 Pour distribuer sur d'autres ordinateurs :
    echo    - Copier le dossier complet 'dist\SuiviProjets'
    echo    - Exécuter 'SuiviProjets.exe' sur la machine cible
    echo.
    pause
) else (
    echo.
    echo ❌ ERREUR : La construction a échoué
    echo Vérifiez les messages d'erreur ci-dessus
    echo.
    pause
    exit /b 1
)
