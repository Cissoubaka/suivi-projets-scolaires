"""Onglet Export - Interface simplifiée"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, 
    QLineEdit, QListWidget, QMessageBox, QGroupBox
)
from tabs.base import TabBase
from security import SecurityValidator


class ExportTab(TabBase):
    """Onglet d'export des données en ODS (LibreOffice Calc)"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_project_id = None
        self.selected_class_id = None
    
    def create_widget(self):
        """Créer l'interface de l'onglet Export"""
        widget = QWidget()
        main_layout = QVBoxLayout()

        # Section: Sélection du projet
        project_group = QGroupBox("Choisir le Projet")
        project_layout = QHBoxLayout()
        
        project_layout.addWidget(QLabel("Projet :"))
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet("QComboBox { color: black; }")
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        project_layout.addWidget(self.project_combo, 1)
        
        project_group.setLayout(project_layout)
        main_layout.addWidget(project_group)

        # Section: Sélection de la classe
        class_group = QGroupBox("Choisir la Classe")
        class_layout = QHBoxLayout()
        
        class_layout.addWidget(QLabel("Classe :"))
        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet("QComboBox { color: black; }")
        self.class_combo.currentIndexChanged.connect(self.on_class_changed)
        class_layout.addWidget(self.class_combo, 1)
        
        class_group.setLayout(class_layout)
        main_layout.addWidget(class_group)

        # Section: Préfixe du nom de fichier
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("Préfixe du fichier :"))
        self.filename_prefix = QLineEdit()
        self.filename_prefix.setPlaceholderText("ex: Evaluation, Notes, etc.")
        self.filename_prefix.setText("Evaluation")
        self.filename_prefix.textChanged.connect(self.update_filename_preview)
        prefix_layout.addWidget(self.filename_prefix, 1)
        config_layout.addLayout(prefix_layout)
        
        # Prévision du nom de fichier
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Aperçu :"))
        self.filename_preview = QLabel("")
        self.filename_preview.setStyleSheet("color: gray; font-style: italic;")
        preview_layout.addWidget(self.filename_preview, 1)
        config_layout.addLayout(preview_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Section: Bouton d'export
        export_group = QGroupBox("Exporter")
        export_layout = QVBoxLayout()
        
        export_all_groups_btn = QPushButton("Exporter Tous les Groupes de la Classe")
        export_all_groups_btn.setMinimumHeight(50)
        export_all_groups_btn.clicked.connect(self.export_all_groups)
        export_layout.addWidget(export_all_groups_btn)
        
        export_group.setLayout(export_layout)
        main_layout.addWidget(export_group)

        # Section: Journal d'export
        log_group = QGroupBox("Journal d'Export")
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Fichiers créés :"))
        self.export_log = QListWidget()
        log_layout.addWidget(self.export_log)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        main_layout.addStretch()
        widget.setLayout(main_layout)
        
        # Charger les projets au démarrage
        self.refresh_projects()
        self.update_filename_preview()
        
        return widget

    def refresh_projects(self):
        """Charger tous les projets dans le combo"""
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        
        projects = self.db.get_all_projects()
        for project in projects:
            self.project_combo.addItem(project[1], project[0])  # nom, id
        
        self.project_combo.blockSignals(False)
        
        # Sélectionner le premier projet par défaut
        if self.project_combo.count() > 0:
            self.project_combo.setCurrentIndex(0)
            self.on_project_changed()

    def on_project_changed(self):
        """Quand le projet change, mettre à jour les classes"""
        self.selected_project_id = self.project_combo.currentData()
        self.refresh_classes()
        self.update_filename_preview()

    def refresh_classes(self):
        """Charger les classes associées au projet sélectionné"""
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        
        if self.selected_project_id is None:
            self.class_combo.blockSignals(False)
            self.selected_class_id = None
            return
        
        # Récupérer les classes qui ont des élèves dans les groupes du projet
        groups = self.db.get_groups_for_project(self.selected_project_id)
        classes_dict = {}  # {class_id: class_name}
        
        for group in groups:
            students = self.db.get_students_in_group(group[0])
            for student in students:
                if student[3]:  # class_id
                    if student[3] not in classes_dict:
                        class_obj = self.db.get_class_by_id(student[3])
                        if class_obj:
                            classes_dict[student[3]] = class_obj[1]
        
        # Ajouter les classes trouvées
        for class_id in sorted(classes_dict.keys()):
            self.class_combo.addItem(classes_dict[class_id], class_id)
        
        self.class_combo.blockSignals(False)
        
        # Mettre à jour selected_class_id après avoir débloqué les signaux
        if self.class_combo.count() > 0:
            self.selected_class_id = self.class_combo.currentData()
            self.update_filename_preview()
        else:
            self.selected_class_id = None

    def on_class_changed(self):
        """Quand la classe change"""
        self.selected_class_id = self.class_combo.currentData()
        self.update_filename_preview()

    def update_filename_preview(self):
        """Mettre à jour la prévision du nom de fichier"""
        prefix = self.filename_prefix.text() or "Evaluation"
        
        # Récupérer le nom du projet
        project_name = self.project_combo.currentText() or "Projet"
        
        # Récupérer le nom de la classe
        class_name = self.class_combo.currentText() or "Classe"
        
        # Construire la prévision
        preview = f"{prefix}_{project_name}_{class_name}_Groupe*.ods"
        self.filename_preview.setText(preview)

    def export_all_groups(self):
        """Exporter tous les groupes de la classe sélectionnée"""
        if self.selected_project_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un projet !")
            return
        
        if self.selected_class_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez une classe !")
            return
        
        prefix = self.filename_prefix.text() or "Evaluation"
        
        # Valider le préfixe du nom de fichier
        is_valid, error_msg = SecurityValidator.validate_filename_prefix(prefix)
        if not is_valid:
            QMessageBox.warning(self.parent, "Erreur", f"Préfixe invalide : {error_msg}")
            return
        
        try:
            groups = self.db.get_groups_for_project(self.selected_project_id)
            
            # Filtrer par classe
            filtered_groups = []
            for group in groups:
                students = self.db.get_students_in_group(group[0])
                if any(s[3] == self.selected_class_id for s in students):
                    filtered_groups.append(group)
            
            if not filtered_groups:
                QMessageBox.warning(self.parent, "Erreur", "Aucun groupe trouvé pour cette classe !")
                return
            
            exported_files = []
            for group in filtered_groups:
                # Récupérer le chemin de destination pour ce groupe
                dest_path = self._get_group_export_path(group)
                
                file_path = self.exporter.export_group_to_ods(group[0], prefix, dest_path)
                exported_files.append(file_path)
                self.export_log.addItem(file_path)
            
            # Afficher le message avec le chemin du répertoire
            if exported_files:
                first_dir = os.path.dirname(exported_files[0])
                QMessageBox.information(self.parent, "Succès", 
                                       f"{len(exported_files)} fichier(s) créé(s)\n\n"
                                       f"Emplacement: {first_dir}")
        
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'export : {str(e)}")
            import traceback
            traceback.print_exc()

    def _get_group_export_path(self, group):
        """Récupérer le chemin d'export pour un groupe
        
        Stratégie:
        1. Si le chemin du groupe est défini ET existe, l'utiliser
        2. Sinon, construire avec directory_destination du projet + directory_name
        3. Sinon, retourner "." (répertoire courant)
        """
        group_id = group[0]
        
        # Étape 1: Vérifier si le chemin est défini et existe pour ce groupe
        directory_info = self.db.get_group_directory(group_id)
        if directory_info and directory_info[1]:  # directory_path
            stored_path = directory_info[1]
            # Vérifier que le chemin existe
            if os.path.exists(stored_path):
                return stored_path
        
        # Étape 2: Construire le chemin avec directory_destination du projet + directory_name
        if self.selected_project_id is None:
            return "."
        
        project = self.db.get_project(self.selected_project_id)
        if not project or len(project) <= 6:
            return "."
        
        directory_destination = project[6]  # dest_directory est à l'index 6
        
        if directory_destination and os.path.exists(directory_destination) and directory_info and directory_info[0]:
            # directory_info[0] est directory_name (ex: "T01" ou "test_group")
            constructed_path = os.path.join(directory_destination, directory_info[0])
            return constructed_path
        
        # Étape 3: Par défaut, répertoire courant
        return "."

    def get_destination_path(self):
        """Récupérer le répertoire destination pour ce groupe"""
        if self.selected_project_id is None:
            return "."
        
        # Parcourir les groupes de la classe pour trouver le premier avec un répertoire défini
        groups = self.db.get_groups_for_project(self.selected_project_id)
        
        for group in groups:
            students = self.db.get_students_in_group(group[0])
            if any(s[3] == self.selected_class_id for s in students):
                # Récupérer le répertoire du groupe
                directory_info = self.db.get_group_directory(group[0])
                if directory_info and directory_info[1]:  # directory_path
                    return directory_info[1]
        
        # Par défaut, retourner le répertoire courant
        return "."
