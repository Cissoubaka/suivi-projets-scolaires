"""Onglet Répertoire"""

import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QMessageBox
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

        # Info sur la configuration
        info_label = QLabel(
            "Configurez le répertoire source, le répertoire destination et le préfixe\n"
            "lors de la création ou l'édition d'un projet (onglet Projets)."
        )
        info_label.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        layout.addWidget(QLabel(""))

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

        # Affichage du répertoire source (lecture seule)
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Répertoire source :"))
        self.source_dir_input = QLineEdit()
        self.source_dir_input.setReadOnly(True)
        source_layout.addWidget(self.source_dir_input)
        layout.addLayout(source_layout)

        # Affichage du répertoire destination (lecture seule)
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Répertoire destination :"))
        self.dest_dir_input = QLineEdit()
        self.dest_dir_input.setReadOnly(True)
        dest_layout.addWidget(self.dest_dir_input)
        layout.addLayout(dest_layout)

        # Affichage du préfixe (lecture seule)
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("Préfixe des répertoires cibles :"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setReadOnly(True)
        self.prefix_input.setMaximumWidth(150)
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addStretch()
        layout.addLayout(prefix_layout)

        layout.addWidget(QLabel(""))

        # Bouton de copie
        copy_btn = QPushButton("Copier les répertoires")
        copy_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        copy_btn.clicked.connect(self.copy_directories)
        layout.addWidget(copy_btn)

        layout.addStretch()
        widget.setLayout(layout)
        self.refresh_dir_projects_combo()
        
        return widget

    def refresh_dir_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet répertoire"""
        self.dir_project_combo.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            self.dir_project_combo.addItem(project[1], project[0])

    def on_dir_project_changed(self):
        """Mettre à jour les répétitions et les chemins quand le projet change"""
        self.dir_repetition_combo.clear()
        if self.dir_project_combo.count() == 0:
            self.source_dir_input.clear()
            self.dest_dir_input.clear()
            self.prefix_input.clear()
            return
        
        project_id = self.dir_project_combo.currentData()
        project = self.db.get_project(project_id)
        if project:
            # Mettre à jour les répétitions
            for rep in range(1, project[3] + 1):
                self.dir_repetition_combo.addItem(f"Répétition {rep}", rep)
            
            # Charger et afficher les chemins du projet
            source_dir = project[5] if len(project) > 5 else ""
            dest_dir = project[6] if len(project) > 6 else ""
            prefix = project[7] if len(project) > 7 else "T"
            
            self.source_dir_input.setText(source_dir or "")
            self.dest_dir_input.setText(dest_dir or "")
            self.prefix_input.setText(prefix or "T")

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
