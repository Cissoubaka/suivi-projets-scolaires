# Application de Suivi de Projets Scolaires

Enseignant en STI2D en spécialité IT, j'avais besoin d'une application qui permette de gérer et évaluer des projets


## Fonctionnalités

- Créer et gérer des projets scolaires
- Définir le nombre de répétitions d'un projet
- Configurer la taille des groupes (binômes, trinômes, etc.)
- Gérer une liste d'élèves
- Répartition **manuelle** des élèves dans les groupes
- Création des tâches et de leur notation
- Créer les groupes automatiquement
- Configuration des répertoires
- Export en LibreOffice Calc (.ods) directement dans le répertoire de travail des élèves
- Persistance des données (SQLite)
- Suivi de présence et évaluation par séance (journal de bord, GANTT, travail)
- Évaluation de toutes les tâches


## Utilisation

### Workflow type

1. **Gestion des Projets** ⚙️
   - Ajouter les projets scolaires
   - Définir le nombre de répétitions (ex: 3 groupes qui font le même projet)
   - Configurer le nombre de groupes (2 = binôme, 3 = trinôme)
   - Définir le chemin d'origine des fichiers du projet
   - Définir la racine du chemin des répertoires des projets élèves
   - Copier tous les fichiers du projet dans les répertoires des projets élèves
```
/
├── IT/
    ├── Projet01          # répertoire du premier groupe
    ├── Projet02          # répertoire du deuxième groupe
    ├── Projet03          # répertoire du troisième groupe
    └── Projet04          # répertoire du quatrième groupe
```

2. **Gestion des Élèves** 👥
   - Créer des classes
   - Ajouter des élèves à chaque classe
   - Importation de fichier CSV de Pronote pour ajouter tous les élèves d'une classe

3. **Répartition des Groupes** 📝
   - Sélectionner un projet
   - Cliquer sur "Créer les Groupes" (création automatique du nombre défini dans le projet)
   - **Drag & Drop Manuel** : Ajouter/retirer des élèves dans les groupes
   - Double-clic pour ajouter l'élève dans le groupe
   - Les élèves non assignés apparaissent dans la colonne de droite
   
4. **Barème** 👥
   - Créer des catégories/tâches avec 3 niveaux de profondeur
   - Affectation d'une note par catégories
   - S'il y a des catégories enfants, la note de la catégorie parente est le total de celles enfants
   
5. **Répartition des tâches** 👥
   - Choix de qui fait quoi dans le groupe en cochant ou décochant la case
 
6. **Suivi des présences et activités** 👥
   - Ajout de séance de travail avec 3 éléments évalués: le journal de bord, le diagramme de GANTT et le travail
   - Sélection du barème par éléments évalués
   - case de présence ou absence
   - note de suivi

7. **Évaluation** 👥
   - Pour chaque tâche (définie dans l'onglet barème) affectée à l'élève (défini à l'onglet répartition des tâches), on lui met une note


8. **Export** 📊
   - Exporter le suivi de présence et l'évaluation du groupe sous la forme d'un fichier LibreOffice Calc
   - Les fichiers Calc sont créés dans le dossier de chaque groupe
   - Choix d'un préfixe pour le nom ("Evaluation", "Séance")

## License

Libre d'utilisation pour usage scolaire

## Support

Pour toute question ou bug, consultez la documentation ou créez une issue.
