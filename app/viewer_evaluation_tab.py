"""Onglet d'évaluation (lecture seule) pour la visionneuse"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from custom_widgets import VerticalHeaderView
from viewer_base_tab import ViewerTabBase


class ViewerEvaluationTab(ViewerTabBase):
    """Onglet d'évaluation des catégories (lecture seule pour élèves)"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.eval_categories_map = []
        self.eval_level2_with_children = set()
        self.eval_duplicated_cat_ids = set()

    def create_widget(self):
        """Créer l'onglet d'évaluation en mode lecture seule"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Section sélection projet/répétition/classe
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Projet :"))
        self.eval_project_combo = QComboBox()
        self.eval_project_combo.currentIndexChanged.connect(self.on_eval_project_changed)
        selection_layout.addWidget(self.eval_project_combo)
        
        selection_layout.addWidget(QLabel("Répétition :"))
        self.eval_repetition_combo = QComboBox()
        self.eval_repetition_combo.currentIndexChanged.connect(self.on_eval_repetition_changed)
        selection_layout.addWidget(self.eval_repetition_combo)
        
        selection_layout.addWidget(QLabel("Classe :"))
        self.eval_class_combo = QComboBox()
        self.eval_class_combo.currentIndexChanged.connect(self.on_eval_class_changed)
        selection_layout.addWidget(self.eval_class_combo)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # Zone de scroll pour afficher les tableaux
        self.eval_scroll_area = QScrollArea()
        self.eval_scroll_area.setWidgetResizable(True)
        self.eval_scroll_container = QWidget()
        self.eval_scroll_layout = QVBoxLayout()
        self.eval_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.eval_scroll_container.setLayout(self.eval_scroll_layout)
        self.eval_scroll_area.setWidget(self.eval_scroll_container)
        layout.addWidget(self.eval_scroll_area, 1)

        widget.setLayout(layout)
        
        # Charger les données avec QTimer
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.refresh_data)
        
        return widget

    def refresh_data(self):
        """Rafraîchir l'onglet d'évaluation"""
        self.refresh_eval_projects_combo()

    def refresh_eval_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet évaluation"""
        self.eval_project_combo.blockSignals(True)
        self.eval_repetition_combo.blockSignals(True)
        
        self.eval_project_combo.clear()
        self.eval_repetition_combo.clear()
        
        projects = self.db.get_all_projects()
        for project in projects:
            self.eval_project_combo.addItem(project[1], project[0])
        
        self.eval_project_combo.blockSignals(False)
        self.eval_repetition_combo.blockSignals(False)
        
        if self.eval_project_combo.count() > 0:
            self.eval_project_combo.setCurrentIndex(0)
            self.on_eval_project_changed()

    def on_eval_project_changed(self):
        """Mettre à jour les répétitions et les classes quand le projet change"""
        try:
            self.eval_repetition_combo.blockSignals(True)
            self.eval_class_combo.blockSignals(True)
            
            self.eval_repetition_combo.clear()
            self.eval_class_combo.clear()
            
            if self.eval_project_combo.count() == 0:
                self.eval_repetition_combo.blockSignals(False)
                self.eval_class_combo.blockSignals(False)
                return
            
            project_id = self.eval_project_combo.currentData()
            project = self.db.get_project(project_id)
            
            if project:
                for rep in range(1, project[3] + 1):
                    self.eval_repetition_combo.addItem(f"Répétition {rep}", rep)
            
            classes = self.db.get_all_classes()
            for class_id, class_name in classes:
                self.eval_class_combo.addItem(class_name, class_id)
            
            # Sélectionner les premiers éléments par défaut
            if self.eval_repetition_combo.count() > 0:
                self.eval_repetition_combo.setCurrentIndex(0)
            if self.eval_class_combo.count() > 0:
                self.eval_class_combo.setCurrentIndex(0)
            
            self.eval_repetition_combo.blockSignals(False)
            self.eval_class_combo.blockSignals(False)
            self.refresh_evaluations()
        except Exception as e:
            print(f"Erreur on_eval_project_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_eval_repetition_changed(self):
        """Rafraîchir l'affichage quand la répétition change"""
        try:
            self.refresh_evaluations()
        except Exception as e:
            print(f"Erreur on_eval_repetition_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_eval_class_changed(self):
        """Rafraîchir l'affichage quand la classe change"""
        try:
            self.refresh_evaluations()
        except Exception as e:
            print(f"Erreur on_eval_class_changed: {e}")
            import traceback
            traceback.print_exc()

    def _get_hierarchical_categories(self, project_id):
        """Construire une liste de catégories avec hiérarchie niveau 2 -> niveau 3"""
        categories = []
        
        # Récupérer les catégories niveau 1
        level1_cats = self.db.get_rating_categories(project_id)
        
        for cat_id, cat_name, cat_points in level1_cats:
            # Récupérer les sous-catégories (niveau 2)
            level2_cats = self.db.get_rating_subcategories(cat_id)

            
            for subcat_id, subcat_name, subcat_points in level2_cats:
                # Ajouter le niveau 2 comme parent
                categories.append((subcat_id, subcat_name, subcat_points, 2, None))
                
                # Récupérer les sous-sous-catégories (niveau 3)
                level3_cats = self.db.get_rating_subsubcategories(subcat_id)
                
                # Ajouter les niveaux 3 comme enfants du niveau 2
                for subsubcat_id, subsubcat_name, subsubcat_points in level3_cats:
                    categories.append((subsubcat_id, f"└─ {subsubcat_name}", subsubcat_points, 3, subcat_id))
        
        return categories

    def _calculate_suivi_score(self, student_id, group_id):
        """Calculer le total des scores de suivi pour un élève avec pro-rata"""
        try:
            total_suivi = 0
            seances_presentes = 0
            total_sessions_count = 0
            
            # Récupérer le projet_id et répétition
            project_id = self.eval_project_combo.currentData()
            repetition = self.eval_repetition_combo.currentData()
            
            if not project_id or not repetition:
                return 0
            
            # Récupérer toutes les dates de session
            sessions = self.db.get_session_dates(project_id, repetition)
            total_sessions_count = len(sessions)
            
            # Pour chaque session, récupérer les scores de suivi
            for session_id, _ in sessions:
                attendance = self.db.get_attendance(student_id, group_id, session_id)
                if attendance:
                    is_present, journal_bord, gantt, travail_comp = attendance
                    if is_present:
                        seances_presentes += 1
                        total_suivi += (journal_bord + gantt + travail_comp)
            
            # Appliquer le pro-rata
            if seances_presentes > 0 and total_sessions_count > 0:
                total_suivi = round(total_suivi * total_sessions_count / seances_presentes, 2)
            
            return total_suivi
        except Exception as e:
            print(f"[ERROR] Erreur calcul suivi_score: {e}")
            return 0

    def _calculate_eval_total(self, student_id):
        """Calcule le total des évaluations"""
        try:
            total = 0
            
            # Parcourir les catégories et additionner les valeurs
            for idx, category in enumerate(self.eval_categories_map):
                cat_id = category[0]
                level = category[3]
                
                # Vérifier si c'est une catégorie avec spinbox (level 3 ou level 2 sans enfants)
                has_spinbox = (level == 3) or (level == 2 and cat_id not in self.eval_level2_with_children)
                
                # Si la catégorie est dupliquée ET level 2, l'ignorer
                # (le level 3 correspondant va la couvrir)
                is_duplicated_level2 = (cat_id in self.eval_duplicated_cat_ids) and (level == 2)
                
                if has_spinbox and not is_duplicated_level2:
                    # La catégorie a une spinbox : additionner sa valeur
                    category_value = self.eval_categories_map[idx] if idx < len(self.eval_categories_map) else None
                    cat_points = category_value[2] if category_value else 0
                    
                    # Récupérer la valeur stockée pour cet étudiant
                    if student_id in self.eval_data:
                        value = self.eval_data[student_id].get(idx, 0)
                    else:
                        value = 0
                    
                    total += value
            
            return total
        except Exception as e:
            print(f"[ERROR] Erreur calcul eval_total: {e}")
            return 0

    def refresh_evaluations(self):
        """Afficher le tableau avec tous les élèves, groupés par groupe (lecture seule)"""
        # Nettoyer la zone de scroll
        while self.eval_scroll_layout.count():
            widget = self.eval_scroll_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        if self.eval_project_combo.count() == 0:
            return
        
        project_id = self.eval_project_combo.currentData()
        repetition = self.eval_repetition_combo.currentData()
        class_id = self.eval_class_combo.currentData()
        
        if project_id is None or repetition is None:
            return
        
        if class_id is None:
            label = QLabel("Veuillez sélectionner une classe")
            self.eval_scroll_layout.addWidget(label)
            return
        
        # Récupérer les groupes
        groups = self.db.get_groups_for_project(project_id, repetition)
        if not groups:
            label = QLabel("Aucun groupe trouvé")
            self.eval_scroll_layout.addWidget(label)
            return
        
        # Récupérer les catégories
        categories = self._get_hierarchical_categories(project_id)
        self.eval_categories_map = categories
        
        if not categories:
            label = QLabel("Aucune catégorie de notation trouvée.")
            self.eval_scroll_layout.addWidget(label)
            return
        
        # Récupérer les élèves de la classe
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
            self.eval_scroll_layout.addWidget(label)
            return
        
        # Pré-charger les données d'évaluation
        self.eval_data = {}
        for group_id, group_number, student_id, student_name in all_students:
            self.eval_data[student_id] = {}
            for idx, category in enumerate(categories):
                cat_id = category[0]
                rating_level = category[3]
                evaluation_note = self.db.get_student_evaluation(student_id, group_id, cat_id, rating_level)
                self.eval_data[student_id][idx] = int(evaluation_note) if evaluation_note else 0
        
        # Palette de couleurs
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
        
        # Créer le tableau
        table = QTableWidget()
        table.setRowCount(len(all_students) + 1)  # +1 pour la rangée des barèmes
        table.setColumnCount(len(categories) + 5)  # +5 pour Répertoire, Élève, Suivi, Total Max, Total
        
        # En-têtes
        headers = ["Répertoire", "Élève"] + [cat[1] for cat in categories] + ["Suivi", "Total Max", "Total"]
        table.setHorizontalHeaderLabels(headers)
        
        custom_header = VerticalHeaderView(Qt.Orientation.Horizontal)
        custom_header.setModel(table.model())
        table.setHorizontalHeader(custom_header)
        table.horizontalHeader().setFixedHeight(150)
        
        # Largeurs des colonnes
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 120)
        for i in range(len(categories)):
            table.setColumnWidth(2 + i, 60)
        table.setColumnWidth(2 + len(categories), 60)  # Suivi
        table.setColumnWidth(3 + len(categories), 80)  # Total Max
        table.setColumnWidth(4 + len(categories), 60)  # Total
        
        # Calculer les totaux max
        total_max_eval = sum(cat[2] for cat in categories if cat[2])
        
        # Calculer le max du Suivi
        suivi_max = 0
        try:
            sessions = self.db.get_session_dates(project_id, repetition)
            if sessions:
                num_sessions = len(sessions)
                first_session_id = sessions[0][0]
                cursor = self.db.get_connection().cursor()
                cursor.execute('SELECT journal_bord, gantt, travail_comportement FROM session_dates WHERE id = ?', (first_session_id,))
                result = cursor.fetchone()
                cursor.connection.close()
                if result:
                    max_j, max_g, max_c = result
                    max_per_session = (max_j if max_j else 0) + (max_g if max_g else 0) + (max_c if max_c else 0)
                    suivi_max = num_sessions * max_per_session
        except Exception as e:
            suivi_max = 0
        
        # Première ligne: barèmes
        spacer_repo = QTableWidgetItem("")
        spacer_repo.setFlags(spacer_repo.flags() & ~Qt.ItemFlag.ItemIsEditable)
        spacer_repo.setBackground(QColor("#E8E8E8"))
        table.setItem(0, 0, spacer_repo)
        
        spacer_eleve = QTableWidgetItem("")
        spacer_eleve.setFlags(spacer_eleve.flags() & ~Qt.ItemFlag.ItemIsEditable)
        spacer_eleve.setBackground(QColor("#E8E8E8"))
        table.setItem(0, 1, spacer_eleve)
        
        for col, category in enumerate(categories):
            cat_points = category[2]
            bareme_text = f"({cat_points})" if cat_points else "(?)"
            bareme_item = QTableWidgetItem(bareme_text)
            bareme_item.setFlags(bareme_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            bareme_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            bareme_item.setBackground(QColor("#E8E8E8"))
            font = QFont()
            font.setBold(True)
            bareme_item.setFont(font)
            table.setItem(0, col + 2, bareme_item)
        
        # Suivi max
        suivi_label = QTableWidgetItem(str(suivi_max))
        suivi_label.setFlags(suivi_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        suivi_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        suivi_label.setBackground(QColor("#E8E8E8"))
        font = QFont()
        font.setBold(True)
        suivi_label.setFont(font)
        table.setItem(0, 2 + len(categories), suivi_label)
        
        # Total Max (variable)
        total_max_label = QTableWidgetItem("Variable")
        total_max_label.setFlags(total_max_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        total_max_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_max_label.setBackground(QColor("#E8E8E8"))
        font_max = QFont()
        font_max.setBold(True)
        font_max.setItalic(True)
        total_max_label.setFont(font_max)
        table.setItem(0, 3 + len(categories), total_max_label)
        
        # Total max (Suivi + Eval)
        total_max_with_suivi = suivi_max + total_max_eval
        total_label = QTableWidgetItem(str(total_max_with_suivi))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        total_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_label.setBackground(QColor("#E8E8E8"))
        font_total = QFont()
        font_total.setBold(True)
        total_label.setFont(font_total)
        table.setItem(0, 4 + len(categories), total_label)
        
        table.setRowHeight(0, 25)
        
        # Identifier les level 2 avec enfants
        level2_with_children = set()
        for cat in categories:
            if cat[3] == 3:
                parent_id = cat[4]
                if parent_id is not None:
                    level2_with_children.add(parent_id)
        
        self.eval_level2_with_children = level2_with_children
        
        # Identifier les cat_id dupliqués
        level2_cat_ids = set(cat[0] for cat in categories if cat[3] == 2)
        level3_cat_ids = set(cat[0] for cat in categories if cat[3] == 3)
        self.eval_duplicated_cat_ids = level2_cat_ids & level3_cat_ids
        
        # Remplir les données des élèves
        for row, (group_id, group_number, student_id, student_name) in enumerate(all_students, start=1):
            bg_color = colors_palette[(group_number - 1) % len(colors_palette)]
            
            # Répertoire
            dir_name, _ = self.db.get_group_directory(group_id)
            display_group = dir_name if dir_name else f"Groupe {group_number}"
            group_item = QTableWidgetItem(display_group)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            group_item.setBackground(bg_color)
            table.setItem(row, 0, group_item)
            
            # Élève
            name_item = QTableWidgetItem(student_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setBackground(bg_color)
            table.setItem(row, 1, name_item)
            
            # Catégories
            for col, category in enumerate(categories):
                cat_id = category[0]
                cat_name = category[1]
                cat_points = category[2]
                level = category[3]
                
                has_spinbox = (level == 3) or (level == 2 and cat_id not in level2_with_children)
                
                if level == 2 and cat_id in level2_with_children:
                    # Afficher le label seulement (pas de spinbox)
                    label_item = QTableWidgetItem(cat_name)
                    label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    label_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    label_item.setBackground(bg_color)
                    font = QFont()
                    font.setBold(True)
                    label_item.setFont(font)
                    table.setItem(row, col + 2, label_item)
                elif has_spinbox:
                    # Afficher la valeur d'évaluation (lecture seule)
                    value = self.eval_data[student_id].get(col, 0)
                    value_item = QTableWidgetItem(str(value))
                    value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    value_item.setBackground(bg_color)
                    table.setItem(row, col + 2, value_item)
                else:
                    # N/D
                    nd_item = QTableWidgetItem("N/D")
                    nd_item.setFlags(nd_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    nd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    nd_item.setBackground(bg_color)
                    font = QFont()
                    font.setItalic(True)
                    nd_item.setFont(font)
                    table.setItem(row, col + 2, nd_item)
            
            # Suivi
            suivi_score = self._calculate_suivi_score(student_id, group_id)
            suivi_item = QTableWidgetItem(str(suivi_score))
            suivi_item.setFlags(suivi_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            suivi_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            suivi_item.setBackground(bg_color)
            table.setItem(row, 2 + len(categories), suivi_item)
            
            # Total Max (Suivi max + somme des éval max pour ce student)
            eval_total_max = sum(self.eval_categories_map[idx][2] 
                                 for idx, category in enumerate(self.eval_categories_map) 
                                 if (category[3] == 3 or (category[3] == 2 and category[0] not in level2_with_children)))
            student_total_max = suivi_max + eval_total_max
            total_max_item = QTableWidgetItem(str(student_total_max))
            total_max_item.setFlags(total_max_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_max_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_max_item.setBackground(bg_color)
            font = QFont()
            font.setBold(True)
            total_max_item.setFont(font)
            table.setItem(row, 3 + len(categories), total_max_item)
            
            # Total (Suivi + Eval)
            eval_total = self._calculate_eval_total(student_id)
            total_score = suivi_score + eval_total
            total_item = QTableWidgetItem(str(total_score))
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setBackground(bg_color)
            font = QFont()
            font.setBold(True)
            total_item.setFont(font)
            table.setItem(row, 4 + len(categories), total_item)
        
        table.resizeRowsToContents()
        self.eval_scroll_layout.addWidget(table, 1)
