@echo off
REM Script pour générer l'executable Windows avec PyInstaller
REM Utilisation: double-cliquez sur ce fichier ou lancez: build_windows.bat

setlocal enabledelayedexpansion

REM Déterminer l'interpréteur Python à utiliser (venv prioritaire)
set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
    ) else (
        where python >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_EXE=python"
        )
    )
)

echo ==========================================
echo Création de l'exécutable Windows
echo ==========================================
echo.

if "%PYTHON_EXE%"=="" (
    echo [ERREUR] Python introuvable.
    echo Installez Python puis relancez le script.
    echo.
    pause
    exit /b 1
)

REM Vérifier que PyInstaller est installé
%PYTHON_EXE% -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller n'est pas installe. Installation en cours...
    %PYTHON_EXE% -m pip install --upgrade PyInstaller
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer PyInstaller.
        echo.
        pause
        exit /b 1
    )
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
if exist Visionneuse.spec (
    del /q Visionneuse.spec >nul 2>&1
)

REM === Construction de l'application principale ===
echo.
echo ========================================
echo 🔨 Construction de l'application principale...
echo ========================================
echo Cela peut prendre quelques minutes...
echo.
%PYTHON_EXE% -m PyInstaller build.spec

REM Vérifier la construction principale
if not exist "dist\SuiviProjets\SuiviProjets.exe" (
    echo.
    echo ❌ ERREUR : La construction de l'application principale a échoué
    echo Vérifiez les messages d'erreur ci-dessus
    echo.
    pause
    exit /b 1
)

echo ✅ Application principale construite avec succès

REM === Construction de la visionneuse ===
echo.
echo ========================================
echo 🔨 Construction de la visionneuse...
echo ========================================
echo Cela peut prendre quelques minutes...
echo.
%PYTHON_EXE% -m PyInstaller build_viewer.spec

REM Vérifier la construction de la visionneuse
if exist "dist\Visionneuse\Visionneuse.exe" (
    echo ✅ Visionneuse construite avec succès
) else (
    echo ❌ ERREUR : La construction de la visionneuse a échoué
    echo Vérifiez les messages d'erreur ci-dessus
    echo.
    pause
    exit /b 1
)

REM === Résumé final ===
echo.
echo ==========================================
echo ✅ SUCCÈS ! Tous les exécutables sont créés
echo ==========================================
echo.
echo 📁 Application principale (SuiviProjets)
echo    dist\SuiviProjets\SuiviProjets.exe
echo.
echo 📁 Visionneuse (pour les élèves)
echo    dist\Visionneuse\Visionneuse.exe
echo.
echo 📝 Pour utiliser les applications :
echo    1. Aller dans le dossier 'dist\SuiviProjets' ou 'dist\Visionneuse'
echo    2. Double-cliquer sur l'exécutable (.exe)
echo.
echo 💾 Pour distribuer sur d'autres ordinateurs :
echo    - Copier le dossier complet 'dist\SuiviProjets' OU 'dist\Visionneuse'
echo    - Exécuter l'application sur la machine cible
echo    (Aucune installation supplémentaire n'est nécessaire)
echo.
pause
