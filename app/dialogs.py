"""Dialogues pour la gestion des projets, élèves et catégories de notation"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QSpinBox, QMessageBox, QFileDialog, QComboBox, QTableWidget,
    QTableWidgetItem, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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


class DialogueJournalDeBord(QDialog):
    """Dialogue pour afficher le journal de bord et les tâches d'un élève par date"""
    
    def __init__(self, parent=None, student_name="", group_id=None, student_id=None, 
                 db=None, attendance_tab=None):
        super().__init__(parent)
        self.student_name = student_name
        self.group_id = group_id
        self.student_id = student_id
        self.db = db
        self.attendance_tab = attendance_tab
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialiser l'interface du dialogue"""
        self.setWindowTitle(f"Journal de bord - {self.student_name}")
        self.setGeometry(100, 100, 1200, 700)
        
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel(f"Journal de bord et tâches de {self.student_name}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Créer deux sections avec défilement
        content_layout = QHBoxLayout()
        
        # --- SECTION GAUCHE : JOURNAL DE BORD ---
        left_section = QVBoxLayout()
        left_section.addWidget(QLabel("Journal de bord par date :"))
        
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(2)
        self.journal_table.setHorizontalHeaderLabels(["Date", "Contenu"])
        self.journal_table.setColumnWidth(0, 150)
        self.journal_table.setColumnWidth(1, 350)
        self.journal_table.resizeRowsToContents()
        left_section.addWidget(self.journal_table)
        
        left_widget = QWidget()
        left_widget.setLayout(left_section)
        content_layout.addWidget(left_widget, 1)
        
        # --- SECTION DROITE : TÂCHES ---
        right_section = QVBoxLayout()
        right_section.addWidget(QLabel("Tâches et pourcentages :"))
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(2)
        self.tasks_table.setHorizontalHeaderLabels(["Tâche", "Pourcentage"])
        self.tasks_table.setColumnWidth(0, 250)
        self.tasks_table.setColumnWidth(1, 100)
        right_section.addWidget(self.tasks_table)
        
        right_widget = QWidget()
        right_widget.setLayout(right_section)
        content_layout.addWidget(right_widget, 1)
        
        layout.addLayout(content_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Charger les données du journal de bord et des tâches"""
        if not self.db or not self.group_id or not self.student_id:
            return
        
        try:
            # Récupérer le projet principal
            groups = self.db.get_group_by_id(self.group_id)
            if not groups:
                return
            
            project_id = groups[1]
            project = self.db.get_project(project_id)
            
            if not project:
                return
            
            # Charger le journal de bord
            self._load_journal_de_bord(project)
            
            # Charger les tâches GANTT
            self._load_tasks_gantt(project)
            
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement des données: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_journal_de_bord(self, project):
        """Charger les dates du journal de bord avec leur contenu"""
        try:
            dest_dir = project[6]  # dest_directory
            if not dest_dir or not os.path.isdir(dest_dir):
                return
            
            group_info = self.db.get_group_by_id(self.group_id)
            if not group_info:
                return
            
            group_number = group_info[2]
            dir_name, _ = self.db.get_group_directory(self.group_id)
            if not dir_name:
                dir_name = f"T{group_number:02d}"
            
            students_in_group = self.db.get_students_in_group(self.group_id)
            student_info = next((s for s in students_in_group if s[0] == self.student_id), None)
            
            if not student_info:
                return
            
            student_firstname = student_info[1]
            student_lastname = student_info[2]
            
            # Construire les variantes de noms possibles
            base_name_variants = [
                student_firstname,
                student_lastname,
                f"{student_firstname} {student_lastname}",
                f"{student_lastname} {student_firstname}",
            ]
            
            group_dir_path = os.path.join(dest_dir, dir_name)
            
            # Chercher le fichier journal de bord
            odt_file_path = self._find_journal_file(group_dir_path, base_name_variants)
            
            if not odt_file_path:
                self.journal_table.setRowCount(1)
                item = QTableWidgetItem("Aucun journal de bord trouvé")
                self.journal_table.setItem(0, 0, item)
                return
            
            # Extraire les données du journal
            table_data = self._extract_odt_table(odt_file_path)
            
            if not table_data:
                self.journal_table.setRowCount(1)
                item = QTableWidgetItem("Table ODT non trouvée ou vide")
                self.journal_table.setItem(0, 0, item)
                return
            
            self.journal_table.setRowCount(len(table_data))
            
            for row, (date_str, content) in enumerate(table_data):
                date_item = QTableWidgetItem(date_str)
                date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.journal_table.setItem(row, 0, date_item)
                
                # Créer un widget avec QLabel pour pouvoir utiliser setWordWrap
                content_widget = QWidget()
                content_layout = QVBoxLayout()
                content_layout.setContentsMargins(2, 2, 2, 2)
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                content_layout.addWidget(content_label)
                content_widget.setLayout(content_layout)
                
                self.journal_table.setCellWidget(row, 1, content_widget)
            
            self.journal_table.resizeRowsToContents()
            
        except Exception as e:
            print(f"[ERROR] Erreur _load_journal_de_bord: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_tasks_gantt(self, project):
        """Charger les tâches GANTT avec leurs pourcentages"""
        try:
            dest_dir = project[6]  # dest_directory
            if not dest_dir or not os.path.isdir(dest_dir):
                return
            
            group_info = self.db.get_group_by_id(self.group_id)
            if not group_info:
                return
            
            group_number = group_info[2]
            dir_name, _ = self.db.get_group_directory(self.group_id)
            if not dir_name:
                dir_name = f"T{group_number:02d}"
            
            group_dir_path = os.path.join(dest_dir, dir_name)
            
            # Récupérer le chemin du fichier GANTT
            gantt_file_path = self.attendance_tab.get_gantt_file_path(group_dir_path, project[0])
            
            if not os.path.isfile(gantt_file_path):
                self.tasks_table.setRowCount(1)
                item = QTableWidgetItem("Fichier GANTT non trouvé")
                self.tasks_table.setItem(0, 0, item)
                return
            
            # Parser le fichier GANTT
            from mindview_parser import MindViewParser
            parser = MindViewParser(gantt_file_path)
            
            if not parser.parse():
                self.tasks_table.setRowCount(1)
                item = QTableWidgetItem("Impossible de parser le fichier GANTT")
                self.tasks_table.setItem(0, 0, item)
                return
            
            # Récupérer les pourcentages des tâches
            task_percentages = parser.get_task_percentages()
            
            if not task_percentages:
                self.tasks_table.setRowCount(1)
                item = QTableWidgetItem("Aucune tâche trouvée")
                self.tasks_table.setItem(0, 0, item)
                return
            
            self.tasks_table.setRowCount(len(task_percentages))
            
            for row, task in enumerate(task_percentages):
                task_name = task.get('name', 'Unknown')
                task_percent = task.get('percent', 0)
                
                name_item = QTableWidgetItem(task_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tasks_table.setItem(row, 0, name_item)
                
                percent_item = QTableWidgetItem(f"{task_percent}%")
                percent_item.setFlags(percent_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                percent_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tasks_table.setItem(row, 1, percent_item)
            
            self.tasks_table.resizeRowsToContents()
            
        except Exception as e:
            print(f"[ERROR] Erreur _load_tasks_gantt: {e}")
            import traceback
            traceback.print_exc()
    
    def _find_journal_file(self, directory_path, base_name_variants):
        """Chercher le fichier journal de bord dans le répertoire, spécifique à l'élève"""
        try:
            if not os.path.isdir(directory_path):
                return None
            
            files = os.listdir(directory_path)
            
            # Chercher un fichier contenant le nom de l'élève
            for variant in base_name_variants:
                for filename in files:
                    filename_upper = filename.upper()
                    if (filename_upper.startswith("JOURNAL DE BORD") and 
                        variant.upper() in filename_upper and 
                        filename.lower().endswith(".odt")):
                        full_path = os.path.join(directory_path, filename)
                        if os.path.isfile(full_path):
                            return full_path
            
            # Fallback : chercher un fichier commençant par "JOURNAL DE BORD" s'il n'y en a qu'un
            # (pour compatibilité avec les anciens fichiers)
            matching_files = [f for f in files 
                            if f.upper().startswith("JOURNAL DE BORD") and f.lower().endswith(".odt")]
            if len(matching_files) == 1:
                full_path = os.path.join(directory_path, matching_files[0])
                if os.path.isfile(full_path):
                    return full_path
            
            return None
        except Exception as e:
            print(f"[ERROR] Erreur _find_journal_file: {e}")
            return None
    
    def _extract_odt_table(self, odt_file_path):
        """Extraire un tableau d'un fichier ODT"""
        try:
            with zipfile.ZipFile(odt_file_path, 'r') as odtzip:
                xml_content = odtzip.read('content.xml')
                root = ET.fromstring(xml_content)
                
                namespaces = {
                    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                }
                
                tables = root.findall('.//table:table', namespaces)
                
                if not tables:
                    return []
                
                table = tables[0]
                rows = table.findall('.//table:table-row', namespaces)
                
                extracted_data = []
                
                for row_idx, row in enumerate(rows):
                    if row_idx == 0:  # Sauter l'en-tête
                        continue
                    
                    cells = row.findall('.//table:table-cell', namespaces)
                    
                    if len(cells) < 2:
                        continue
                    
                    date_cell = cells[0]
                    date_texts = date_cell.findall('.//text:p', namespaces)
                    date_str = ''.join([''.join(t.itertext()) for t in date_texts]).strip()
                    
                    work_cell = cells[1]
                    work_texts = work_cell.findall('.//text:p', namespaces)
                    work_str = ''.join([''.join(t.itertext()) for t in work_texts]).strip()
                    
                    if date_str:
                        extracted_data.append((date_str, work_str))
                
                return extracted_data
        
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'extraction du tableau ODT : {e}")
            import traceback
            traceback.print_exc()
            return []


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
