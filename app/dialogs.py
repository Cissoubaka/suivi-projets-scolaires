"""Dialogues pour la gestion des projets, élèves et catégories de notation"""

import os
import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QSpinBox, QMessageBox, QFileDialog, QComboBox
)


class ProjectDialog(QDialog):
    """Dialogue pour créer ou éditer un projet"""
    
    def __init__(self, parent=None, project=None, db=None):
        super().__init__(parent)
        self.project = project
        self.db = db
        self.project_id = project[0] if project else None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Projet" if self.project is None else f"Éditer - {self.project[1]}")
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout()

        # Nom du projet
        layout.addWidget(QLabel("Nom du projet :"))
        self.name_input = QLineEdit()
        if self.project:
            self.name_input.setText(self.project[1])
        layout.addWidget(self.name_input)

        # Description
        layout.addWidget(QLabel("Description :"))
        self.desc_input = QTextEdit()
        if self.project:
            self.desc_input.setText(self.project[2] or "")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # Nombre de répétitions
        layout.addWidget(QLabel("Nombre de répétitions :"))
        self.repetitions_spin = QSpinBox()
        self.repetitions_spin.setMinimum(1)
        self.repetitions_spin.setMaximum(20)
        if self.project:
            self.repetitions_spin.setValue(self.project[3])
        layout.addWidget(self.repetitions_spin)

        # Nombre de groupes
        layout.addWidget(QLabel("Nombre de groupes (les élèves seront distribués équitablement) :"))
        self.num_groups_spin = QSpinBox()
        self.num_groups_spin.setMinimum(1)
        self.num_groups_spin.setMaximum(100)
        if self.project:
            self.num_groups_spin.setValue(self.project[4])
        else:
            self.num_groups_spin.setValue(1)
        layout.addWidget(self.num_groups_spin)

        # CONFIGURATION DES RÉPERTOIRES
        layout.addWidget(QLabel("--- Configuration des répertoires ---"))
        
        # Répertoire source
        layout.addWidget(QLabel("Répertoire source :"))
        source_layout = QHBoxLayout()
        self.source_dir_input = QLineEdit()
        self.source_dir_input.setReadOnly(True)
        if self.project and len(self.project) > 5:
            self.source_dir_input.setText(self.project[5] or "")
        source_layout.addWidget(self.source_dir_input)
        browse_source_btn = QPushButton("Parcourir...")
        browse_source_btn.clicked.connect(self.browse_source_directory)
        source_layout.addWidget(browse_source_btn)
        layout.addLayout(source_layout)

        # Répertoire destination
        layout.addWidget(QLabel("Répertoire destination :"))
        dest_layout = QHBoxLayout()
        self.dest_dir_input = QLineEdit()
        self.dest_dir_input.setReadOnly(True)
        if self.project and len(self.project) > 6:
            self.dest_dir_input.setText(self.project[6] or "")
        dest_layout.addWidget(self.dest_dir_input)
        browse_dest_btn = QPushButton("Parcourir...")
        browse_dest_btn.clicked.connect(self.browse_dest_directory)
        dest_layout.addWidget(browse_dest_btn)
        layout.addLayout(dest_layout)

        # Préfixe
        layout.addWidget(QLabel("Préfixe des répertoires cibles (ex: Travail_, Groupe_, etc.) :"))
        prefix_layout = QHBoxLayout()
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("T")
        if self.project and len(self.project) > 7 and self.project[7]:
            self.prefix_input.setText(self.project[7])
        else:
            self.prefix_input.setText("T")
        self.prefix_input.setMaximumWidth(200)
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addStretch()
        layout.addLayout(prefix_layout)

        # Bouton de copie des répertoires (seulement en édition)
        if self.project:
            layout.addWidget(QLabel(""))
            copy_btn = QPushButton("Copier les répertoires des groupes")
            copy_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
            copy_btn.clicked.connect(self.copy_directories)
            layout.addWidget(copy_btn)

        # Boutons OK/Annuler
        layout.addWidget(QLabel(""))
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def browse_source_directory(self):
        """Sélectionner le répertoire source"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire source")
        if directory:
            self.source_dir_input.setText(directory)

    def browse_dest_directory(self):
        """Sélectionner le répertoire destination"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire destination")
        if directory:
            self.dest_dir_input.setText(directory)

    def copy_directories(self):
        """Ouvrir le dialogue de copie des répertoires"""
        if not self.project_id or not self.db:
            QMessageBox.warning(self, "Erreur", "Le projet doit d'abord être sauvegardé !")
            return
        
        # Utiliser les données du formulaire courant, pas celles en base de données
        source_dir = self.source_dir_input.text().strip()
        dest_dir = self.dest_dir_input.text().strip()
        prefix = self.prefix_input.text().strip() or 'T'
        repetitions = self.repetitions_spin.value()
        num_groups = self.num_groups_spin.value()
        
        dialog = CopyDirectoriesDialog(
            self, 
            self.project_id, 
            source_dir, 
            dest_dir, 
            prefix, 
            repetitions, 
            num_groups, 
            self.db
        )
        dialog.exec()

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'description': self.desc_input.toPlainText(),
            'repetitions': self.repetitions_spin.value(),
            'num_groups': self.num_groups_spin.value(),
            'source_directory': self.source_dir_input.text().strip(),
            'dest_directory': self.dest_dir_input.text().strip(),
            'prefix': self.prefix_input.text().strip() or 'T'
        }


class CopyDirectoriesDialog(QDialog):
    """Dialogue pour copier les répertoires des groupes"""
    
    def __init__(self, parent=None, project_id=None, source_dir="", dest_dir="", prefix="T", repetitions=1, num_groups=1, db=None):
        super().__init__(parent)
        self.project_id = project_id
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.prefix = prefix
        self.num_groups = num_groups
        self.db = db
        self.init_ui(repetitions)

    def init_ui(self, repetitions):
        self.setWindowTitle("Copier les répertoires des groupes")
        self.setGeometry(100, 100, 400, 220)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Sélectionnez la répétition :"))
        
        self.repetition_combo = QComboBox()
        for rep in range(1, repetitions + 1):
            self.repetition_combo.addItem(f"Répétition {rep}", rep)
        layout.addWidget(self.repetition_combo)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Répertoire source :"))
        source_label = QLabel(self.source_dir)
        source_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        layout.addWidget(source_label)

        layout.addWidget(QLabel("Répertoire destination :"))
        dest_label = QLabel(self.dest_dir)
        dest_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        layout.addWidget(dest_label)

        layout.addWidget(QLabel("Préfixe :"))
        prefix_label = QLabel(self.prefix)
        prefix_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        layout.addWidget(prefix_label)

        layout.addWidget(QLabel(""))
        
        buttons_layout = QHBoxLayout()
        copy_btn = QPushButton("Copier")
        copy_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        copy_btn.clicked.connect(self.copy_directories)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

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
        if not self.project_id or not self.db:
            QMessageBox.warning(self, "Erreur", "Données manquantes !")
            return

        source_dir = self.source_dir
        dest_dir = self.dest_dir
        prefix = self.prefix
        num_groups = self.num_groups
        
        if not source_dir:
            QMessageBox.warning(self, "Erreur", "Le répertoire source n'a pas été configuré !\n\nVeuillez revenir à l'édition du projet pour le configurer.")
            return
        
        if not os.path.isdir(source_dir):
            QMessageBox.warning(self, "Erreur", f"Le répertoire source n'existe pas :\n\n{source_dir}\n\nVérifiez le chemin et réessayez.")
            return
        
        if not dest_dir:
            QMessageBox.warning(self, "Erreur", "Le répertoire destination n'a pas été configuré !")
            return
        
        if not os.path.isdir(dest_dir):
            QMessageBox.warning(self, "Erreur", f"Le répertoire destination n'existe pas :\n\n{dest_dir}\n\nVérifiez le chemin et réessayez.")
            return
        
        repetition = self.repetition_combo.currentData()
        groups = self.db.get_groups_for_project(self.project_id, repetition)
        
        # Si les groupes n'existent pas, les créer automatiquement
        if not groups:
            try:
                self.db.create_groups(self.project_id, num_groups, repetition)
                groups = self.db.get_groups_for_project(self.project_id, repetition)
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de créer les groupes :\n{str(e)}")
                return
        
        # Créer les répertoires des groupes et sauvegarder leurs chemins
        try:
            created_dirs = 0
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
                    created_dirs += 1
                except Exception as e:
                    errors.append(f"Groupe {group_number}: {str(e)}")
            
            if errors:
                msg = "⚠ Erreurs lors de la création des répertoires :\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... et {len(errors) - 5} autres erreurs"
                QMessageBox.warning(self, "Avertissement", msg)
                return
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création des répertoires :\n{str(e)}")
            return
        
        # Copier les fichiers
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
            
            QMessageBox.information(self, "Copie terminée", msg)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la copie :\n{str(e)}")


class StudentDialog(QDialog):
    """Dialogue pour créer ou éditer un élève"""
    
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Élève" if self.student is None else f"Éditer - {self.student[2]} {self.student[1]}")
        self.setGeometry(100, 100, 350, 150)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Prénom :"))
        self.firstname_input = QLineEdit()
        if self.student:
            self.firstname_input.setText(self.student[1])
        layout.addWidget(self.firstname_input)

        layout.addWidget(QLabel("Nom de famille :"))
        self.lastname_input = QLineEdit()
        if self.student:
            self.lastname_input.setText(self.student[2])
        layout.addWidget(self.lastname_input)

        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_data(self):
        return {
            'firstname': self.firstname_input.text(),
            'lastname': self.lastname_input.text()
        }


class RatingCategoryDialog(QDialog):
    """Dialogue pour créer ou éditer une catégorie de notation"""
    
    def __init__(self, parent=None, title="Catégorie", required_points=False, initial_name="", initial_points=None):
        super().__init__(parent)
        self.required_points = required_points
        self.initial_name = initial_name
        self.initial_points = initial_points
        self.init_ui(title)

    def init_ui(self, title):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 350, 180)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nom :"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.initial_name)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Points (optionnel)" if not self.required_points else "Points (obligatoire) :"))
        self.points_input = QLineEdit()
        if self.initial_points is not None:
            self.points_input.setText(str(self.initial_points))
        self.points_input.setPlaceholderText("Laisser vide pour calculer automatiquement")
        layout.addWidget(self.points_input)

        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_data(self):
        name = self.name_input.text().strip()
        points_text = self.points_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire !")
            return None, None
        
        points = None
        if points_text:
            try:
                points = int(points_text)
                if points < 0:
                    QMessageBox.warning(self, "Erreur", "Les points doivent être positifs !")
                    return None, None
            except ValueError:
                QMessageBox.warning(self, "Erreur", "Les points doivent être un nombre !")
                return None, None
        elif self.required_points:
            QMessageBox.warning(self, "Erreur", "Les points sont obligatoires !")
            return None, None
        
        return name, points
