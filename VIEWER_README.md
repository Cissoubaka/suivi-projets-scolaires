# Visionneuse - Guide d'utilisation

## Vue d'ensemble

La visionneuse est une application destinée aux **élèves** pour consulter leurs résultats en mode **lecture seule**. Elle ne permet pas de modifier les données, contrairement à l'application principale.

### Fonctionnalités

- **Onglet Suivi de Présence** : Affiche les présences et les notes de chaque séance (journal, GANTT, comportement)
- **Onglet Évaluation** : Affiche les évaluations par catégorie et le total des points
- **Onglet Répartition des Tâches** : Affiche l'assignation des tâches aux élèves (checkboxes en lecture seule)
- **Protection totale** : Aucune modification possible, aucun bouton d'édition
- **Même visuel** : Identical appearance à l'application principale pour une meilleure cohérence

## Lancement

### Depuis le répertoire `app/`
```bash
python3 viewer_main.py
```

### Ou utiliser le script de lancement
```bash
./run_viewer.sh
```

### Depuis le répertoire racine du projet
```bash
cd app && python3 viewer_main.py
```

## Architecture

### Fichiers créés

```
app/
├── viewer_main.py                   # Point d'entrée principal
├── viewer_window.py                 # Fenêtre principale (3 onglets)
├── viewer_base_tab.py               # Classe de base pour les onglets étudiants
├── viewer_attendance_tab.py         # Onglet suivi présence (read-only)
├── viewer_evaluation_tab.py         # Onglet évaluation (read-only)
├── viewer_task_assignment_tab.py    # Onglet répartition des tâches (read-only)
├── run_viewer.sh                    # Script de lancement
└── test_viewer_all_tabs.py          # Script de test complet
```

### Classe ParentElement

Tous les onglets de la visionneuse héritent de `ViewerTabBase` qui:
- Donne accès à `self.db` (base de données)
- Marque le mode comme `is_viewer_mode = True`

### Différences avec l'application principale

#### Onglet Suivi de Présence
- ✓ Affichage des combos Projet/Répétition
- ✗ Pas de champs d'édition (date, journal, GANTT, comportement)
- ✗ Pas de boutons (Ajouter, Vérifier Journal, Vérifier GANTT)
- ✗ Pas de bouton "Sauvegarder les présences"
- ✓ Tableau avec les données en lecture seule
- ✓ Les présences affichent: présent/absent + J:n/m G:n/m C:n/m
- ✓ Les absences sont colorées en rouge clair

#### Onglet Évaluation
- ✓ Affichage des combos Projet/Répétition/Classe
- ✗ Pas de spinboxes éditables (remplacées par des labels)
- ✗ Pas de bouton "Sauvegarder les évaluations"
- ✓ Tableau avec les barèmes en première ligne
- ✓ Affichage des colonnes: Répertoire, Élève, Catégories, Suivi, Total Max, Total
- ✓ N/D affiché pour les élèves non assignés à une tâche

#### Onglet Répartition des Tâches
- ✓ Affichage des combos Projet/Répétition/Classe
- ✓ Sélection du niveau de catégories à afficher (niveau 2, 2+3, ou niveau 3 seul)
- ✗ Checkboxes désactivées (impossible à cocher/décocher)
- ✗ Pas de bouton "Sauvegarder la répartition"
- ✓ Tableau avec les assignations en lecture seule
- ✓ Affichage des colonnes: Répertoire, Élève, Catégories (+indentation), Total
- ✓ Total calculé automatiquement en fonction des assignations

## Notes techniques

### Réutilisation de code
- Les onglets visionneuse réutilisent la logique de la base de données
- Les fonctions de calcul (pro-rata, totaux) sont identiques
- Les palettes de couleurs et formatages sont conservés

### Base de données
- La visionneuse utilise la **même base de données** `projects.db` que l'application principale
- Les données sont chargées en première lecture, pas modifiées
- Lecture seule garantie par désactivation des widgets et suppression des boutons

### Logging
- Les logs de la visionneuse sont stockés dans `app/logs/viewer_*.log`
- Format de fichier: `viewer_YYYYMMDD_HHMMSS.log`

## Exemple d'utilisation

1. Lancer l'application principale pour créer des projets et entrer les données
2. Assigner les tâches aux élèves dans l'onglet "Répartition des Tâches"
3. Saisir les données de présence et d'évaluation
4. Une fois les données saisies, les élèves peuvent lancer la visionneuse
5. Sélectionner le projet, la répétition (et la classe pour évaluation et tâches)
6. Consulter les résultats en lecture seule
7. Aucun risque de modification accidentelle

## Évolutions futures possibles

- Authentification des élèves
- Affichage personnalisé par élève (ses données seulement)
- Export des données en PDF
- Comparaison avec ses pairs (anonyme)
- Diagrammes de progression
- Connexion à un système de gestion d'établissement (Pronote, École Directe, etc.)
