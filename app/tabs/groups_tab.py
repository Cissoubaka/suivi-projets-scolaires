"""Onglet Répartition des Groupes"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from tabs.base import TabBase


class GroupsTab(TabBase):
    """Onglet de répartition des groupes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_group_id = None
    
    def create_widget(self):
        """Créer l'interface de l'onglet Groupes"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Sélection du projet
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Projet :"))
        self.groups_project_combo = QComboBox()
        self.groups_project_combo.currentIndexChanged.connect(self.on_groups_project_changed)
        top_layout.addWidget(self.groups_project_combo)

        top_layout.addWidget(QLabel("Répétition :"))
        self.groups_repetition_combo = QComboBox()
        self.groups_repetition_combo.currentIndexChanged.connect(self.on_repetition_changed)
        top_layout.addWidget(self.groups_repetition_combo)
        
        top_layout.addWidget(QLabel("Classe :"))
        self.groups_class_combo = QComboBox()
        self.groups_class_combo.currentIndexChanged.connect(self.on_groups_class_changed)
        top_layout.addWidget(self.groups_class_combo)

        layout.addLayout(top_layout)

        # Bouton créer groupes
        create_groups_btn = QPushButton("Créer les Groupes")
        create_groups_btn.clicked.connect(self.create_groups)
        layout.addWidget(create_groups_btn)

        # Affichage des groupes et classe
        groups_layout = QHBoxLayout()

        # Groupes
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Groupes :"))
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.on_group_selected)
        left_layout.addWidget(self.groups_list)
        groups_layout.addLayout(left_layout)

        # Élèves dans le groupe
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(QLabel("Élèves du groupe :"))
        self.group_students_list = QListWidget()
        middle_layout.addWidget(self.group_students_list)
        remove_student_btn = QPushButton("Retirer de ce groupe")
        remove_student_btn.clicked.connect(self.remove_from_group)
        middle_layout.addWidget(remove_student_btn)
        groups_layout.addLayout(middle_layout)

        # Élèves non assignés
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Élèves non assignés :"))
        self.unassigned_students_list = QListWidget()
        self.unassigned_students_list.itemDoubleClicked.connect(self.add_to_group)
        right_layout.addWidget(self.unassigned_students_list)
        add_student_btn = QPushButton("Ajouter au groupe")
        add_student_btn.clicked.connect(self.add_to_group)
        right_layout.addWidget(add_student_btn)
        groups_layout.addLayout(right_layout)

        layout.addLayout(groups_layout)
        widget.setLayout(layout)

        self.refresh_groups_projects_combo()
        return widget

    def refresh_groups_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet groupes"""
        self.groups_project_combo.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            self.groups_project_combo.addItem(project[1], project[0])

    def on_groups_project_changed(self):
        """Mettre à jour les répétitions et classes quand le projet change"""
        self.groups_repetition_combo.blockSignals(True)
        self.groups_class_combo.blockSignals(True)
        
        if self.groups_project_combo.count() == 0:
            self.groups_repetition_combo.blockSignals(False)
            self.groups_class_combo.blockSignals(False)
            return
        
        project_id = self.groups_project_combo.currentData()
        project = self.db.get_project(project_id)
        if project:
            self.groups_repetition_combo.clear()
            for rep in range(1, project[3] + 1):
                self.groups_repetition_combo.addItem(f"Répétition {rep}", rep)
            
            # Charger les classes
            self.groups_class_combo.clear()
            classes = self.db.get_all_classes()
            for class_id, class_name in classes:
                self.groups_class_combo.addItem(class_name, class_id)
        
        self.groups_repetition_combo.blockSignals(False)
        self.groups_class_combo.blockSignals(False)
        
        # Déclencher le rafraîchissement de la liste des groupes
        self.refresh_groups_list()
        self.refresh_unassigned_students()

    def on_repetition_changed(self):
        """Rafraîchir quand la répétition change"""
        self.refresh_groups_list()
        self.refresh_unassigned_students()
    
    def on_groups_class_changed(self):
        """Rafraîchir quand la classe change"""
        self.refresh_unassigned_students()

    def create_groups(self):
        """Créer les groupes pour le projet et la répétition sélectionnés"""
        if self.groups_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet disponible !")
            return

        project_id = self.groups_project_combo.currentData()
        project = self.db.get_project(project_id)
        students = self.db.get_all_students()

        if not students:
            QMessageBox.warning(self.parent, "Erreur", "Ajoutez d'abord des élèves !")
            return

        num_groups = project[4]  # Nombre de groupes souhaité
        if num_groups <= 0:
            QMessageBox.warning(self.parent, "Erreur", "Le nombre de groupes doit être > 0 !")
            return

        repetition = self.groups_repetition_combo.currentData()
        self.db.create_groups(project_id, num_groups, repetition)
        
        # Initialiser les noms de répertoires (T01, T02, etc.)
        groups = self.db.get_groups_for_project(project_id, repetition)
        for group in groups:
            group_id = group[0]
            group_num = group[2]
            dir_name = f"T{group_num:02d}"  # T01, T02, T03, etc.
            self.db.set_group_directory(group_id, dir_name, "")
        
        self.refresh_groups_list()
        
        # Calculer la distribution des élèves
        total_students = len(students)
        base_size = total_students // num_groups
        remainder = total_students % num_groups
        
        sizes_msg = f"{remainder} groupe(s) de {base_size + 1} + {num_groups - remainder} groupe(s) de {base_size}"
        QMessageBox.information(self.parent, "Succès", f"{num_groups} groupes créés !\n\nDistribution : {sizes_msg}")

    def refresh_groups_list(self):
        """Rafraîchir la liste des groupes"""
        self.groups_list.clear()
        if self.groups_project_combo.count() == 0:
            return
        project_id = self.groups_project_combo.currentData()
        repetition = self.groups_repetition_combo.currentData()
        groups = self.db.get_groups_for_project(project_id, repetition)
        for group in groups:
            group_id = group[0]
            # Récupérer le nom du répertoire (T01, T02, etc.)
            dir_name, _ = self.db.get_group_directory(group_id)
            # Afficher le nom du répertoire ou le numéro du groupe par défaut
            display_name = dir_name if dir_name else f"Groupe {group[2]}"
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, group_id)
            self.groups_list.addItem(item)

    def on_group_selected(self, item):
        """Quand un groupe est sélectionné"""
        self.current_group_id = item.data(Qt.ItemDataRole.UserRole)
        self.refresh_group_students_list()
        self.refresh_unassigned_students()

    def refresh_group_students_list(self):
        """Rafraîchir la liste des élèves du groupe sélectionné"""
        self.group_students_list.clear()
        if self.current_group_id is None:
            return
        students = self.db.get_students_in_group(self.current_group_id)
        for student in students:
            item = QListWidgetItem(f"{student[2]} {student[1]}")
            item.setData(Qt.ItemDataRole.UserRole, student[0])
            self.group_students_list.addItem(item)

    def refresh_unassigned_students(self):
        """Rafraîchir la liste des élèves non assignés"""
        self.unassigned_students_list.clear()
        if self.groups_project_combo.count() == 0:
            return
        project_id = self.groups_project_combo.currentData()
        repetition = self.groups_repetition_combo.currentData()
        class_id = self.groups_class_combo.currentData()
        
        # Récupérer tous les élèves non assignés
        students = self.db.get_unassigned_students(project_id, repetition)
        
        # Filtrer par classe si sélectionnée
        if class_id is not None:
            class_students = self.db.get_students_in_class(class_id)
            class_student_ids = {s[0] for s in class_students}
            students = [s for s in students if s[0] in class_student_ids]
        
        for student in students:
            item = QListWidgetItem(f"{student[2]} {student[1]}")
            item.setData(Qt.ItemDataRole.UserRole, student[0])
            self.unassigned_students_list.addItem(item)

    def add_to_group(self, item=None):
        """Ajouter un élève au groupe sélectionné"""
        if self.current_group_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un groupe !")
            return
        
        # Si item est passé (du double-clic), l'utiliser directement
        # Sinon, récupérer l'élève sélectionné (du bouton)
        if item is None:
            selected = self.unassigned_students_list.selectedItems()
            if not selected:
                QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un élève !")
                return
            item = selected[0]
        
        student_id = item.data(Qt.ItemDataRole.UserRole)
        if self.db.add_student_to_group(self.current_group_id, student_id):
            self.refresh_group_students_list()
            self.refresh_unassigned_students()
        else:
            QMessageBox.warning(self.parent, "Erreur", "Cet élève est déjà dans ce groupe !")

    def remove_from_group(self):
        """Retirer un élève du groupe sélectionné"""
        if self.current_group_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un groupe !")
            return
        selected = self.group_students_list.selectedItems()
        if not selected:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un élève !")
            return
        student_id = selected[0].data(Qt.ItemDataRole.UserRole)
        self.db.remove_student_from_group(self.current_group_id, student_id)
        self.refresh_group_students_list()
        self.refresh_unassigned_students()
