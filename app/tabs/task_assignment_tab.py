from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QScrollArea, QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from custom_widgets import VerticalHeaderView
from tabs.base import TabBase


class TaskAssignmentTab(TabBase):
    """Onglet de répartition des tâches aux groupes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_selection_id = None
        self.task_checkboxes = {}
        self.task_total_labels = {}
        self.task_categories = []
    
    def create_widget(self):
        """Créer l'onglet de répartition des tâches (tous les groupes)"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Section sélection projet/répétition
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Projet :"))
        self.task_project_combo = QComboBox()
        self.task_project_combo.currentIndexChanged.connect(self.on_task_project_changed)
        selection_layout.addWidget(self.task_project_combo)
        
        selection_layout.addWidget(QLabel("Répétition :"))
        self.task_repetition_combo = QComboBox()
        self.task_repetition_combo.currentIndexChanged.connect(self.on_task_repetition_changed)
        selection_layout.addWidget(self.task_repetition_combo)
        
        selection_layout.addWidget(QLabel("Classe :"))
        self.task_class_combo = QComboBox()
        self.task_class_combo.currentIndexChanged.connect(self.on_task_class_changed)
        selection_layout.addWidget(self.task_class_combo)
        
        layout.addLayout(selection_layout)

        # Section sélection niveaux de catégories
        category_level_layout = QHBoxLayout()
        category_level_layout.addWidget(QLabel("Afficher les catégories :"))
        
        self.task_level_group = QComboBox()
        self.task_level_group.addItem("Niveau 2 seulement (tâches)", [2])
        self.task_level_group.addItem("Niveaux 2 + 3 (tâches et sous-tâches)", [2, 3])
        self.task_level_group.addItem("Niveau 3 seulement (sous-tâches)", [3])
        self.task_level_group.currentIndexChanged.connect(self.on_task_category_level_changed)
        category_level_layout.addWidget(self.task_level_group)
        category_level_layout.addStretch()
        
        layout.addLayout(category_level_layout)

        # Zone de scroll pour afficher les tableaux par groupe
        self.task_scroll_area = QScrollArea()
        self.task_scroll_area.setWidgetResizable(True)
        self.task_scroll_container = QWidget()
        self.task_scroll_layout = QVBoxLayout()
        self.task_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.task_scroll_container.setLayout(self.task_scroll_layout)
        self.task_scroll_area.setWidget(self.task_scroll_container)
        layout.addWidget(self.task_scroll_area, 1)

        # Bouton de sauvegarde
        save_btn = QPushButton("Sauvegarder la répartition")
        save_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        save_btn.clicked.connect(self.save_task_assignments)
        layout.addWidget(save_btn)

        widget.setLayout(layout)
        self.refresh_data()
        return widget

    def refresh_data(self):
        """Rafraîchir l'onglet de répartition des tâches"""
        self.refresh_task_projects_combo()

    def refresh_task_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet répartiton des tâches"""
        self.task_project_combo.blockSignals(True)
        self.task_repetition_combo.blockSignals(True)
        
        self.task_project_combo.clear()
        self.task_repetition_combo.clear()
        
        projects = self.db.get_all_projects()
        for project in projects:
            self.task_project_combo.addItem(project[1], project[0])
        
        self.task_project_combo.blockSignals(False)
        self.task_repetition_combo.blockSignals(False)
        
        if self.task_project_combo.count() > 0:
            self.task_project_combo.setCurrentIndex(0)
            self.on_task_project_changed()

    def on_task_project_changed(self):
        """Mettre à jour les répétitions et les classes quand le projet change"""
        try:
            self.task_repetition_combo.blockSignals(True)
            self.task_class_combo.blockSignals(True)
            
            self.task_repetition_combo.clear()
            self.task_class_combo.clear()
            
            if self.task_project_combo.count() == 0:
                self.task_repetition_combo.blockSignals(False)
                self.task_class_combo.blockSignals(False)
                return
            
            project_id = self.task_project_combo.currentData()
            project = self.db.get_project(project_id)
            
            if project:
                for rep in range(1, project[3] + 1):
                    self.task_repetition_combo.addItem(f"Répétition {rep}", rep)
            
            classes = self.db.get_all_classes()
            for class_id, class_name in classes:
                self.task_class_combo.addItem(class_name, class_id)
            
            self.task_repetition_combo.blockSignals(False)
            self.task_class_combo.blockSignals(False)
            
            # ✅ Rafraîchir les données immédiatement après avoir chargé les classes
            self.refresh_task_assignments()
        except Exception as e:
            print(f"Erreur on_task_project_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_task_repetition_changed(self):
        """Rafraîchir l'affichage quand la répétition change"""
        try:
            self.refresh_task_assignments()
        except Exception as e:
            print(f"Erreur on_task_repetition_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_task_class_changed(self):
        """Rafraîchir l'affichage quand la classe change"""
        try:
            self.refresh_task_assignments()
        except Exception as e:
            print(f"Erreur on_task_class_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_task_category_level_changed(self):
        """Rafraîchir le tableau quand le niveau de catégories change"""
        try:
            self.refresh_task_assignments()
        except Exception as e:
            print(f"Erreur on_task_category_level_changed: {e}")
            import traceback
            traceback.print_exc()

    def refresh_task_assignments(self):
        """Afficher UN tableau avec tous les élèves de tous les groupes, groupés par groupe"""
        while self.task_scroll_layout.count():
            widget = self.task_scroll_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        if self.task_project_combo.count() == 0:
            return
        
        project_id = self.task_project_combo.currentData()
        repetition = self.task_repetition_combo.currentData()
        class_id = self.task_class_combo.currentData()
        
        if project_id is None or repetition is None:
            return
        
        if class_id is None:
            label = QLabel("Veuillez sélectionner une classe")
            self.task_scroll_layout.addWidget(label)
            return
        
        groups = self.db.get_groups_for_project(project_id, repetition)
        if not groups:
            label = QLabel("Aucun groupe trouvé")
            self.task_scroll_layout.addWidget(label)
            return
        
        selected_levels = self.task_level_group.currentData()
        # ✅ Utiliser la nouvelle méthode hiérarchique
        filtered_categories = self.db.get_categories_hierarchical(project_id, selected_levels)
        
        if not filtered_categories:
            label = QLabel("Aucune catégorie trouvée pour les niveaux sélectionnés")
            self.task_scroll_layout.addWidget(label)
            return
        
        # ✅ INITIALISER LES ASSIGNATIONS POUR TOUS LES GROUPES (une fois par groupe, pas à chaque catégorie)
        for group in groups:
            group_id = group[0]
            try:
                self.db.initialize_student_rating_assignments(group_id)
            except Exception as e:
                print(f"[ERREUR] initialize_student_rating_assignments pour group_id={group_id}: {e}")
        
        class_students = self.db.get_students_in_class(class_id)
        class_student_ids = {s[0] for s in class_students}
        
        all_students = []
        for group in groups:
            group_id, _, group_number, _ = group
            students = self.db.get_students_in_group(group_id)
            for student in students:
                student_id = student[0]
                if student_id in class_student_ids:
                    student_name = f"{student[2]} {student[1]}"
                    all_students.append((group_id, group_number, student_id, student_name))
        
        if not all_students:
            label = QLabel("Aucun élève trouvé dans cette classe")
            self.task_scroll_layout.addWidget(label)
            return
        
        self.task_checkboxes = {}
        self.task_total_labels = {}
        self.task_categories = filtered_categories
        
        colors_palette = [
            QColor(200, 230, 255),
            QColor(200, 255, 200),
            QColor(255, 240, 200),
            QColor(255, 200, 220),
            QColor(240, 200, 255),
            QColor(255, 255, 200),
            QColor(200, 255, 255),
            QColor(255, 220, 200),
        ]
        
        table = QTableWidget()
        table.setRowCount(len(all_students))
        table.setColumnCount(len(filtered_categories) + 3)
        
        # ✅ Créer les en-têtes avec indentation pour la hiérarchie
        headers = ["Répertoire", "Élève"]
        for cat in filtered_categories:
            # cat = (id, name, points, level, parent_id, indent_level, order_num)
            cat_name = cat[1]
            indent_level = cat[5]
            # ✅ Ajouter de l'indentation visuelle SEULEMENT pour le niveau 3 (petits-enfants)
            if indent_level == 2:  # niveau 3
                cat_name = "    └─ " + cat_name
            headers.append(cat_name)
        headers.append("Total")
        
        table.setHorizontalHeaderLabels(headers)
        
        custom_header = VerticalHeaderView(Qt.Orientation.Horizontal)
        custom_header.setModel(table.model())
        table.setHorizontalHeader(custom_header)
        
        table.horizontalHeader().setFixedHeight(150)
        
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 120)
        for i in range(len(filtered_categories)):
            table.setColumnWidth(2 + i, 40)
        table.setColumnWidth(2 + len(filtered_categories), 60)
        
        for row, (group_id, group_number, student_id, student_name) in enumerate(all_students):
            if group_id not in self.task_checkboxes:
                self.task_checkboxes[group_id] = {}
            
            bg_color = colors_palette[(group_number - 1) % len(colors_palette)]
            
            dir_name, _ = self.db.get_group_directory(group_id)
            display_group = dir_name if dir_name else f"Groupe {group_number}"
            
            group_item = QTableWidgetItem(display_group)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            group_item.setBackground(bg_color)
            table.setItem(row, 0, group_item)
            
            name_item = QTableWidgetItem(student_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setBackground(bg_color)
            table.setItem(row, 1, name_item)
            
            self.task_checkboxes[group_id][student_id] = {}
            
            for col, category in enumerate(filtered_categories):
                # category = (id, name, points, level, parent_id, indent_level, order_num)
                cat_id = category[0]
                
                assignment = self.db.get_student_rating_assignment(student_id, group_id, cat_id)
                is_assigned = assignment if assignment is not None else True
                
                checkbox = QCheckBox()
                checkbox.setChecked(is_assigned)
                
                checkbox.stateChanged.connect(lambda state, g_id=group_id, s_id=student_id: self.update_task_total(g_id, s_id))
                
                widget = QWidget()
                cell_layout = QHBoxLayout()
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.addStretch()
                cell_layout.addWidget(checkbox)
                cell_layout.addStretch()
                widget.setLayout(cell_layout)
                
                color_hex = bg_color.name()
                widget.setStyleSheet(f"background-color: {color_hex};")
                
                table.setCellWidget(row, col + 2, widget)
                
                self.task_checkboxes[group_id][student_id][cat_id] = checkbox
            
            total_label = QLabel("0")
            total_label.setStyleSheet("text-align: center; font-weight: bold;")
            total_widget = QWidget()
            total_layout = QHBoxLayout()
            total_layout.setContentsMargins(0, 0, 0, 0)
            total_layout.addStretch()
            total_layout.addWidget(total_label)
            total_layout.addStretch()
            total_widget.setLayout(total_layout)
            
            color_hex = bg_color.name()
            total_widget.setStyleSheet(f"background-color: {color_hex};")
            
            table.setCellWidget(row, 2 + len(filtered_categories), total_widget)
            
            self.task_total_labels[(group_id, student_id)] = total_label
            
            self.update_task_total(group_id, student_id)
        
        table.resizeRowsToContents()
        
        self.task_scroll_layout.addWidget(table, 1)

    def update_task_total(self, group_id, student_id):
        """Mettre à jour le total des points pour un élève
        
        Règle: Si une catégorie niveau 2 a des enfants niveau 3 QUI SONT AFFICHÉS, 
        on ne compte que les points des enfants, pas ceux du parent.
        """
        if (group_id, student_id) not in self.task_total_labels:
            return
        
        total = 0
        
        if hasattr(self, 'task_checkboxes') and group_id in self.task_checkboxes and student_id in self.task_checkboxes[group_id]:
            for category in self.task_categories:
                # category = (id, name, points, level, parent_id, indent_level, order_num)
                cat_id = category[0]
                cat_points = category[2]
                cat_level = category[3]
                
                if cat_id in self.task_checkboxes[group_id][student_id]:
                    checkbox = self.task_checkboxes[group_id][student_id][cat_id]
                    if checkbox.isChecked():
                        # ✅ Si c'est un niveau 2 avec des enfants AFFICHÉS dans le tableau actuel, ignorer ses points
                        if cat_level == 2 and self._has_displayed_children(cat_id):
                            continue
                        
                        # Sinon, compter les points
                        if cat_points is None:
                            if cat_level == 2:
                                cat_points = self.db.get_subcategory_total_points(cat_id)
                        
                        if cat_points is not None and cat_points > 0:
                            total += cat_points
        
        self.task_total_labels[(group_id, student_id)].setText(str(total))

    def _has_displayed_children(self, category_id):
        """Vérifier si une catégorie a des enfants affichés dans le tableau actuel"""
        # Vérifier si des enfants niveau 3 sont dans self.task_categories
        for cat in self.task_categories:
            cat_id, _, _, cat_level, cat_parent, _, _ = cat
            # Si c'est un enfant (parent_id == category_id) et qu'il est affiché
            if cat_parent == category_id and cat_level == 3:
                return True
        return False

    def save_task_assignments(self):
        """Sauvegarder les assignations de catégories aux élèves de tous les groupes"""
        if self.task_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet sélectionné !")
            return
        
        try:
            for group_id, students in self.task_checkboxes.items():
                for student_id, categories in students.items():
                    for cat_id, checkbox in categories.items():
                        is_assigned = checkbox.isChecked()
                        self.db.set_student_rating_assignment(student_id, group_id, cat_id, is_assigned)
            
            QMessageBox.information(self.parent, "Succès", "Répartition des tâches sauvegardée !")
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la sauvegarde :\n{str(e)}")
