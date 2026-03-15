"""Onglet Répertoire"""

import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QMessageBox, QFileDialog
)
from tabs.base import TabBase


class DirectoryTab(TabBase):
    """Onglet de gestion des répertoires"""
    
    def __init__(self, parent):
        super().__init__(parent)
    
    def create_widget(self):
        """Créer l'interface de l'onglet Répertoire"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Sélection du projet et répétition
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Projet :"))
        self.dir_project_combo = QComboBox()
        self.dir_project_combo.currentIndexChanged.connect(self.on_dir_project_changed)
        project_layout.addWidget(self.dir_project_combo)
        
        project_layout.addWidget(QLabel("Répétition :"))
        self.dir_repetition_combo = QComboBox()
        project_layout.addWidget(self.dir_repetition_combo)
        layout.addLayout(project_layout)

        # Choix du répertoire source
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Répertoire source :"))
        self.source_dir_input = QLineEdit()
        self.source_dir_input.setReadOnly(True)
        source_layout.addWidget(self.source_dir_input)
        browse_source_btn = QPushButton("Parcourir...")
        browse_source_btn.clicked.connect(self.browse_source_directory)
        source_layout.addWidget(browse_source_btn)
        layout.addLayout(source_layout)

        # Choix du répertoire destination
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Répertoire destination :"))
        self.dest_dir_input = QLineEdit()
        self.dest_dir_input.setReadOnly(True)
        dest_layout.addWidget(self.dest_dir_input)
        browse_dest_btn = QPushButton("Parcourir...")
        browse_dest_btn.clicked.connect(self.browse_dest_directory)
        dest_layout.addWidget(browse_dest_btn)
        layout.addLayout(dest_layout)

        # Configuration du préfixe
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("Préfixe des répertoires cibles (ex: T) :"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("T")
        self.prefix_input.setText("T")
        self.prefix_input.setMaximumWidth(100)
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addStretch()
        layout.addLayout(prefix_layout)

        # Bouton de copie
        copy_btn = QPushButton("Copier les répertoires")
        copy_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        copy_btn.clicked.connect(self.copy_directories)
        layout.addWidget(copy_btn)

        layout.addStretch()
        widget.setLayout(layout)
        self.refresh_dir_projects_combo()
        
        # Charger les chemins sauvegardés
        self.load_directory_paths()
        
        return widget

    def refresh_dir_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet répertoire"""
        self.dir_project_combo.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            self.dir_project_combo.addItem(project[1], project[0])

    def on_dir_project_changed(self):
        """Mettre à jour les répétitions quand le projet change"""
        self.dir_repetition_combo.clear()
        if self.dir_project_combo.count() == 0:
            return
        
        project_id = self.dir_project_combo.currentData()
        project = self.db.get_project(project_id)
        if project:
            for rep in range(1, project[3] + 1):
                self.dir_repetition_combo.addItem(f"Répétition {rep}", rep)

    def copy_directory_contents(self, source, destination):
        """Copier le contenu d'un répertoire source vers un répertoire destination existant"""
        for item in os.listdir(source):
            src_path = os.path.join(source, item)
            dst_path = os.path.join(destination, item)
            
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    def copy_directories(self):
        """Copier le contenu du répertoire source dans les répertoires des groupes"""
        source_dir = self.source_dir_input.text().strip()
        dest_dir = self.dest_dir_input.text().strip()
        prefix = self.prefix_input.text().strip() or "T"
        
        if not source_dir or not os.path.isdir(source_dir):
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un répertoire source valide !")
            return
        
        if not dest_dir or not os.path.isdir(dest_dir):
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un répertoire destination valide !")
            return
        
        if self.dir_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet sélectionné !")
            return
        
        project_id = self.dir_project_combo.currentData()
        repetition = self.dir_repetition_combo.currentData()
        groups = self.db.get_groups_for_project(project_id, repetition)
        
        if not groups:
            QMessageBox.warning(self.parent, "Erreur", "Aucun groupe trouvé pour cette répétition !")
            return
        
        try:
            copied = 0
            errors = []
            
            for group in groups:
                group_id, _, group_number, _ = group
                target_dir_name = f"{prefix}{group_number:02d}"
                target_dir_path = os.path.join(dest_dir, target_dir_name)
                
                try:
                    if not os.path.isdir(target_dir_path):
                        errors.append(f"Groupe {group_number}: le répertoire {target_dir_name} n'existe pas")
                        continue
                    
                    self.copy_directory_contents(source_dir, target_dir_path)
                    copied += 1
                except Exception as e:
                    errors.append(f"Groupe {group_number}: {str(e)}")
            
            msg = f"✓ {copied} répertoire(s) copié(s)"
            if errors:
                msg += f"\n\n⚠ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... et {len(errors) - 5} autres erreurs"
            
            QMessageBox.information(self.parent, "Copie terminée", msg)
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la copie :\n{str(e)}")

    def browse_source_directory(self):
        """Sélectionner le répertoire source"""
        directory = QFileDialog.getExistingDirectory(self.parent, "Sélectionner le répertoire source")
        if directory:
            self.source_dir_input.setText(directory)
            self.save_directory_paths()

    def browse_dest_directory(self):
        """Sélectionner le répertoire destination et créer les répertoires de groupes"""
        directory = QFileDialog.getExistingDirectory(self.parent, "Sélectionner le répertoire destination")
        if directory:
            self.dest_dir_input.setText(directory)
            self.save_directory_paths()
            # Créer et configurer les répertoires des groupes
            self.setup_group_directories()

    def save_directory_paths(self):
        """Sauvegarder les chemins source et destination en base de données"""
        source_path = self.source_dir_input.text().strip()
        dest_path = self.dest_dir_input.text().strip()
        
        self.db.set_setting("directory_source", source_path)
        self.db.set_setting("directory_destination", dest_path)

    def setup_group_directories(self):
        """Créer les répertoires des groupes et sauvegarder leurs chemins"""
        dest_dir = self.dest_dir_input.text().strip()
        prefix = self.prefix_input.text().strip() or "T"
        
        if not dest_dir or not os.path.isdir(dest_dir):
            QMessageBox.warning(self.parent, "Erreur", "Répertoire destination invalide !")
            return
        
        if self.dir_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet sélectionné !")
            return
        
        project_id = self.dir_project_combo.currentData()
        repetition = self.dir_repetition_combo.currentData()
        groups = self.db.get_groups_for_project(project_id, repetition)
        
        if not groups:
            QMessageBox.warning(self.parent, "Erreur", "Aucun groupe trouvé pour cette répétition !")
            return
        
        try:
            created = 0
            errors = []
            
            for group in groups:
                group_id, _, group_number, _ = group
                target_dir_name = f"{prefix}{group_number:02d}"
                target_dir_path = os.path.join(dest_dir, target_dir_name)
                
                try:
                    # Créer le répertoire s'il n'existe pas
                    if not os.path.exists(target_dir_path):
                        os.makedirs(target_dir_path, exist_ok=True)
                    
                    # Sauvegarder le chemin dans la base de données
                    self.db.set_group_directory(group_id, target_dir_name, target_dir_path)
                    created += 1
                except Exception as e:
                    errors.append(f"Groupe {group_number}: {str(e)}")
            
            msg = f"✓ {created} répertoire(s) configuré(s)"
            if errors:
                msg += f"\n\n⚠ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... et {len(errors) - 5} autres erreurs"
            
            QMessageBox.information(self.parent, "Configuration terminée", msg)
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la configuration :\n{str(e)}")

    def load_directory_paths(self):
        """Charger les chemins source et destination depuis la base de données"""
        source_path = self.db.get_setting("directory_source", "")
        dest_path = self.db.get_setting("directory_destination", "")
        
        if source_path:
            self.source_dir_input.setText(source_path)
        if dest_path:
            self.dest_dir_input.setText(dest_path)
