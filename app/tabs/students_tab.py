"""Onglet Gestion des Élèves"""

import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from dialogs import StudentDialog
from tabs.base import TabBase
from security import SecurityValidator


class StudentsTab(TabBase):
    """Onglet de gestion des élèves et des classes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_student_id = None
        self.current_class_id = None
    
    def create_widget(self):
        """Créer l'interface de l'onglet Élèves"""
        widget = QWidget()
        layout = QVBoxLayout()

        # ===== SECTION 1: GESTION DES CLASSES =====
        layout.addWidget(QLabel("Gestion des classes :"))
        classes_layout = QHBoxLayout()
        
        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("Nom de la nouvelle classe")
        classes_layout.addWidget(self.class_name_input)
        
        add_class_btn = QPushButton("Créer une classe")
        add_class_btn.clicked.connect(self.add_class)
        classes_layout.addWidget(add_class_btn)
        
        rename_class_btn = QPushButton("Renommer")
        rename_class_btn.clicked.connect(self.rename_class)
        classes_layout.addWidget(rename_class_btn)
        
        delete_class_btn = QPushButton("Supprimer")
        delete_class_btn.clicked.connect(self.delete_class)
        classes_layout.addWidget(delete_class_btn)
        
        layout.addLayout(classes_layout)

        # ComboBox pour sélectionner une classe
        classes_combo_layout = QHBoxLayout()
        classes_combo_layout.addWidget(QLabel("Sélectionner une classe :"))
        
        self.classes_combo = QComboBox()
        self.classes_combo.currentIndexChanged.connect(self.on_class_selected)
        classes_combo_layout.addWidget(self.classes_combo)
        
        layout.addLayout(classes_combo_layout)

        # ===== SECTION 2: GESTION DES ÉLÈVES DE LA CLASSE =====
        layout.addWidget(QLabel("Élèves de la classe :"))
        self.students_list = QListWidget()
        self.students_list.itemClicked.connect(self.on_student_selected)
        layout.addWidget(self.students_list)

        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter un Élève")
        add_btn.clicked.connect(self.add_student)
        edit_btn = QPushButton("Éditer")
        edit_btn.clicked.connect(self.edit_student)
        delete_btn = QPushButton("Supprimer de la classe")
        delete_btn.clicked.connect(self.delete_student)
        import_btn = QPushButton("Importer depuis CSV")
        import_btn.clicked.connect(self.import_csv)
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(import_btn)
        layout.addLayout(buttons_layout)

        widget.setLayout(layout)
        self.refresh_classes()
        return widget

    def refresh_classes(self):
        """Rafraîchir la ComboBox des classes"""
        self.classes_combo.blockSignals(True)
        self.classes_combo.clear()
        
        classes = self.db.get_all_classes()
        for class_id, class_name in classes:
            self.classes_combo.addItem(class_name, class_id)
        
        self.classes_combo.blockSignals(False)
        
        # Sélectionner la première classe ou n'afficher aucun élève
        if self.classes_combo.count() > 0:
            self.classes_combo.setCurrentIndex(0)
            self.on_class_selected()
        else:
            self.students_list.clear()
            self.current_class_id = None

    def on_class_selected(self):
        """Appelé quand une classe est sélectionnée dans le ComboBox"""
        if self.classes_combo.currentIndex() >= 0:
            self.current_class_id = self.classes_combo.currentData()
            self.refresh_students_list()
        else:
            self.current_class_id = None
            self.students_list.clear()

    def refresh_students_list(self):
        """Rafraîchir la liste des élèves de la classe sélectionnée"""
        self.students_list.clear()
        
        if self.current_class_id is None:
            return
        
        students = self.db.get_students_in_class(self.current_class_id)
        for student_id, firstname, lastname in students:
            item = QListWidgetItem(f"{lastname} {firstname}")
            item.setData(Qt.ItemDataRole.UserRole, student_id)
            self.students_list.addItem(item)

    def on_student_selected(self, item):
        """Quand un élève est sélectionné"""
        self.current_student_id = item.data(Qt.ItemDataRole.UserRole)

    def add_class(self):
        """Ajouter une nouvelle classe"""
        class_name = self.class_name_input.text().strip()
        
        if not class_name:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez entrer un nom de classe !")
            return
        
        # Valider le nom de la classe
        is_valid, error_msg = SecurityValidator.validate_class_name(class_name)
        if not is_valid:
            QMessageBox.warning(self.parent, "Erreur", error_msg)
            return
        
        class_id = self.db.add_class(class_name)
        if class_id is None:
            QMessageBox.warning(self.parent, "Erreur", f"La classe '{class_name}' existe déjà !")
            return
        
        self.class_name_input.clear()
        self.refresh_classes()
        QMessageBox.information(self.parent, "Succès", f"Classe '{class_name}' créée !")

    def rename_class(self):
        """Renommer la classe sélectionnée"""
        if self.current_class_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner une classe !")
            return
        
        new_name = self.class_name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez entrer un nouveau nom !")
            return
        
        # Valider le nouveau nom de classe
        is_valid, error_msg = SecurityValidator.validate_class_name(new_name)
        if not is_valid:
            QMessageBox.warning(self.parent, "Erreur", error_msg)
            return
        
        if self.db.rename_class(self.current_class_id, new_name):
            self.class_name_input.clear()
            self.refresh_classes()
            QMessageBox.information(self.parent, "Succès", "Classe renommée !")
        else:
            QMessageBox.warning(self.parent, "Erreur", f"Le nom '{new_name}' existe déjà !")

    def delete_class(self):
        """Supprimer la classe sélectionnée"""
        if self.current_class_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner une classe !")
            return
        
        class_name = self.classes_combo.currentText()
        reply = QMessageBox.question(self.parent, "Confirmation", 
                                     f"Êtes-vous sûr de vouloir supprimer la classe '{class_name}' ?\n"
                                     "(Les élèves seront conservés mais détachés de la classe)")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_class(self.current_class_id)
            self.class_name_input.clear()
            self.refresh_classes()
            QMessageBox.information(self.parent, "Succès", "Classe supprimée !")

    def add_student(self):
        """Ajouter un élève à la classe sélectionnée"""
        if self.current_class_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez d'abord créer ou sélectionner une classe !")
            return
        
        dialog = StudentDialog(self.parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['firstname'].strip() or not data['lastname'].strip():
                QMessageBox.warning(self.parent, "Erreur", "Le prénom et le nom ne peuvent pas être vides !")
                return
            
            # Ajouter l'élève et l'assigner à la classe
            student_id = self.db.add_student(data['firstname'], data['lastname'])
            self.db.assign_student_to_class(student_id, self.current_class_id)
            self.refresh_students_list()
            QMessageBox.information(self.parent, "Succès", "Élève ajouté à la classe !")

    def edit_student(self):
        """Éditer les informations d'un élève"""
        if self.current_student_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un élève !")
            return
        
        students = self.db.get_students_in_class(self.current_class_id)
        student = next((s for s in students if s[0] == self.current_student_id), None)
        
        if student:
            dialog = StudentDialog(self.parent, student)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if not data['firstname'].strip() or not data['lastname'].strip():
                    QMessageBox.warning(self.parent, "Erreur", "Le prénom et le nom ne peuvent pas être vides !")
                    return
                
                # Supprimer et recréer avec les nouveaux noms
                self.db.delete_student(self.current_student_id)
                student_id = self.db.add_student(data['firstname'], data['lastname'])
                self.db.assign_student_to_class(student_id, self.current_class_id)
                self.refresh_students_list()
                QMessageBox.information(self.parent, "Succès", "Élève modifié !")

    def delete_student(self):
        """Retirer un élève de la classe"""
        if self.current_student_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un élève !")
            return
        
        reply = QMessageBox.question(self.parent, "Confirmation", "Retirer cet élève de la classe ?")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.remove_student_from_class(self.current_student_id)
            self.refresh_students_list()
            QMessageBox.information(self.parent, "Succès", "Élève retiré de la classe !")

    def import_csv(self):
        """Importer une liste d'élèves depuis un fichier CSV et les assigner à la classe sélectionnée"""
        if self.current_class_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez d'abord créer ou sélectionner une classe !")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, 
            "Importer des élèves", 
            "", 
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if not file_path:
            return
        
        try:
            imported = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Détecter automatiquement le délimiteur du CSV
                sample = f.read(1024)
                f.seek(0)
                try:
                    delimiter = csv.Sniffer().sniff(sample).delimiter
                except:
                    delimiter = ','  # Par défaut si détection échoue
                
                reader = csv.reader(f, delimiter=delimiter)
                # Lire la première ligne (header) - on l'ignore
                header = next(reader, None)
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < 1 or not row[0].strip():
                        errors.append(f"Ligne {row_num} : vide")
                        continue
                    
                    # Prendre UNIQUEMENT la première colonne
                    full_name = row[0].strip()
                    
                    # D'abord vérifier s'il y a un espace (format: NOM Prenom)
                    if ' ' in full_name:
                        parts = full_name.split(' ', 1)
                        lastname = parts[0].strip()
                        firstname = parts[1].strip()
                    else:
                        # Format sans espace : NONprenom (chercher transition majuscule → minuscule)
                        split_index = -1
                        for i, char in enumerate(full_name):
                            if char.islower():
                                split_index = i
                                break
                        
                        if split_index == -1:
                            errors.append(f"Ligne {row_num} : format invalide (NOMPrenom attendu)")
                            continue
                        
                        lastname = full_name[:split_index].strip()
                        firstname = full_name[split_index:].strip()
                    
                    if not lastname or not firstname:
                        errors.append(f"Ligne {row_num} : nom ou prénom vide")
                        continue
                    
                    try:
                        student_id = self.db.add_student(firstname, lastname)
                        # Assigner l'élève à la classe sélectionnée
                        self.db.assign_student_to_class(student_id, self.current_class_id)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {str(e)}")
            
            self.refresh_students_list()
            
            msg = f"✓ {imported} élève(s) importé(s) dans la classe"
            if errors:
                msg += f"\n\n⚠ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... et {len(errors) - 5} autres erreurs"
            
            QMessageBox.information(self.parent, "Import CSV", msg)
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de l'import :\n{str(e)}")
