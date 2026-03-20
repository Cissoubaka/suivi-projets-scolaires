from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QScrollArea, QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from functools import partial
from custom_widgets import VerticalHeaderView
from tabs.base import TabBase


class EvaluationTab(TabBase):
    """Onglet d'évaluation des catégories pour les élèves"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_selection_id = None
        self.evaluation_spinboxes = {}
        self.evaluation_categories = []
        self.evaluation_total_labels = {}  # {student_id: label}
        self.eval_data = {}  # {student_id: {idx: value}} - source unique de vérité indexée par catégorie
        self.eval_student_group_map = {}  # {student_id: group_id}
        self.eval_level2_with_children = set()  # Pour identifier les level 2 avec enfants
        self.eval_duplicated_cat_ids = set()  # Pour identifier les cat_id dupliquées
        self.eval_categories_map = []  # Liste des catégories avec hiérarchie
    
    def _apply_spinbox_style(self, spinbox):
        """Forcer un rendu lisible des valeurs de spinbox sur Windows et Linux."""
        spinbox.setMinimumWidth(66)
        spinbox.setMinimumHeight(26)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinbox.setFont(QFont("Segoe UI", 10))
        spinbox.setStyleSheet(
            "QSpinBox { "
            "color: #111111; "
            "background-color: #FFFFFF; "
            "border: 1px solid #8A8A8A; "
            "padding: 2px 20px 2px 4px; "
            "selection-background-color: #1976D2; "
            "selection-color: #FFFFFF; "
            "} "
            "QSpinBox:disabled { "
            "color: #555555; "
            "background-color: #F0F0F0; "
            "} "
            "QSpinBox::up-button, QSpinBox::down-button { "
            "background-color: #E7E7E7; "
            "border-left: 1px solid #B0B0B0; "
            "width: 16px; "
            "}"
        )
    
    def create_widget(self):
        """Créer l'onglet d'évaluation des catégories"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Section sélection projet/répétition
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
        
        layout.addLayout(selection_layout)

        # Zone de scroll pour afficher les tableaux par groupe
        self.eval_scroll_area = QScrollArea()
        self.eval_scroll_area.setWidgetResizable(True)
        self.eval_scroll_container = QWidget()
        self.eval_scroll_layout = QVBoxLayout()
        self.eval_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.eval_scroll_container.setLayout(self.eval_scroll_layout)
        self.eval_scroll_area.setWidget(self.eval_scroll_container)
        layout.addWidget(self.eval_scroll_area, 1)

        # Bouton de sauvegarde
        save_btn = QPushButton("Sauvegarder les évaluations")
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        save_btn.clicked.connect(self.save_evaluations)
        layout.addWidget(save_btn)

        widget.setLayout(layout)
        
        # Retarder le chargement des données avec QTimer
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
            
            # Garder les signaux bloqués jusqu'à ce que TOUT soit sélectionné
            # Charger les données avec les valeurs par défaut
            if self.eval_repetition_combo.count() > 0:
                self.eval_repetition_combo.setCurrentIndex(0)
            if self.eval_class_combo.count() > 0:
                self.eval_class_combo.setCurrentIndex(0)
            
            # Débloquer les signaux et charger les évaluations
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
        """Construire une liste de catégories avec hiérarchie niveau 2 -> niveau 3
        Retourne: list of (id, display_name, points, level, parent_id)
        """
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
        """Calculer le total des scores de suivi pour un élève avec pro-rata (comme dans l'onglet suivi)"""
        try:
            total_suivi = 0
            seances_presentes = 0
            total_sessions_count = 0
            
            # Récupérer le projet_id et répétition pour trouver les dates de session
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
                    # attendance = (present, journal_bord, gantt, travail_comportement)
                    is_present, journal_bord, gantt, travail_comp = attendance
                    if is_present:
                        seances_presentes += 1
                        total_suivi += (journal_bord + gantt + travail_comp)
            
            # Appliquer le pro-rata: ramener le total sur le nombre de séances total
            if seances_presentes > 0 and total_sessions_count > 0:
                total_suivi = round(total_suivi * total_sessions_count / seances_presentes, 2)
            
            return total_suivi
        except Exception as e:
            print(f"[ERROR] Erreur calcul suivi_score: {e}")
            return 0

    def _update_eval_value(self, student_id, cat_idx, value):
        """Met à jour la valeur d'une évaluation dans eval_data et recalcule le total"""
        if student_id not in self.eval_data:
            self.eval_data[student_id] = {}
        
        self.eval_data[student_id][cat_idx] = value
        # Pour le debug, récupérer le cat_id correspondant
        if 0 <= cat_idx < len(self.eval_categories_map):
            cat_id = self.eval_categories_map[cat_idx][0]
            print(f"[DATA] Updated: student_id={student_id}, idx={cat_idx}, cat_id={cat_id}, value={value}")
        else:
            print(f"[DATA] Updated: student_id={student_id}, idx={cat_idx}, value={value}")
        
        # Mettre à jour le total en temps réel
        self.update_evaluation_total(student_id)

    def _get_spinbox_from_table(self, row, col):
        """Récupère une spinbox depuis la table à la position (row, col)"""
        try:
            if not hasattr(self, 'eval_table') or self.eval_table is None:
                return None
            
            widget = self.eval_table.cellWidget(row, col)
            if widget:
                # Le widget est un QWidget contenant un layout avec la spinbox
                layout = widget.layout()
                if layout and layout.itemAt(0):
                    spinbox = layout.itemAt(0).widget()
                    if isinstance(spinbox, QSpinBox):
                        return spinbox
            return None
        except Exception as e:
            print(f"[ERROR] _get_spinbox_from_table: {e}")
            return None

    def _calculate_eval_total(self, student_id):
        """Calcule le total des évaluations en sumant eval_data[student_id] (une seule fois par index unique)"""
        try:
            if student_id not in self.eval_data:
                return 0
            
            total = 0
            
            
            # Parcourir les catégories et vérifier si spinbox existe
            for idx, category in enumerate(self.eval_categories_map):
                cat_id = category[0]
                level = category[3]
                
                # Vérifier si c'est une catégorie avec spinbox (level 3 ou level 2 sans enfants)
                has_spinbox = (level == 3) or (level == 2 and cat_id not in self.eval_level2_with_children)
                
                if has_spinbox:
                    value = self.eval_data[student_id].get(idx, 0)  # Lire par INDEX

                    total += value

            

            return total
        except Exception as e:
            print(f"[ERROR] Erreur _calculate_eval_total: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def _calculate_total_max(self, student_id, suivi_max):
        """Calcule le Total Max (suivi_max + sum des points max des catégories assignées)"""
        try:
            total_max = suivi_max
            

            
            # Parcourir les catégories et vérifier si spinbox existe et assignée
            for idx, category in enumerate(self.eval_categories_map):
                cat_id = category[0]
                cat_points = category[2]
                level = category[3]
                
                # Vérifier si c'est une catégorie avec spinbox (level 3 ou level 2 sans enfants)
                has_spinbox = (level == 3) or (level == 2 and cat_id not in self.eval_level2_with_children)
                
                # Vérifier si l'élève est assigné
                group_id = self.eval_student_group_map.get(student_id)
                if group_id:
                    is_assigned = self.db.get_student_rating_assignment(student_id, group_id, cat_id)
                    if is_assigned is None:
                        is_assigned = True
                else:
                    is_assigned = True
                
                if has_spinbox and is_assigned:
                    total_max += cat_points if cat_points else 0
            

            return total_max
        except Exception as e:
            print(f"[ERROR] Erreur _calculate_total_max: {e}")
            import traceback
            traceback.print_exc()
            return suivi_max

    def update_evaluation_total(self, student_id):
        """Mettre à jour le total de l'évaluation en temps réel"""
        try:
            if student_id not in self.evaluation_total_labels:
                return
            
            group_id = self.eval_student_group_map.get(student_id)
            if not group_id:
                return
            
            suivi_score = self._calculate_suivi_score(student_id, group_id)
            eval_total = self._calculate_eval_total(student_id)
            total_score = suivi_score + eval_total
            
            label = self.evaluation_total_labels[student_id]
            label.setText(str(total_score))
            label.update()
            label.repaint()
            if label.parent():
                label.parent().update()
                label.parent().repaint()
            
            print(f"[LABEL] Updated total for student_id={student_id}: suivi={suivi_score} + eval={eval_total} = {total_score}")
        except Exception as e:
            print(f"[ERROR] Erreur update_evaluation_total: {e}")
            import traceback
            traceback.print_exc()

    def refresh_evaluations(self):
        """Afficher UN tableau avec tous les élèves de tous les groupes, groupés par groupe"""
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
        
        groups = self.db.get_groups_for_project(project_id, repetition)

        if not groups:
            label = QLabel("Aucun groupe trouvé")
            self.eval_scroll_layout.addWidget(label)
            return
        
        # Récupérer les catégories en respectant la hiérarchie
        # Afficher niveau 2 suivi de ses niveau 3 enfants
        categories = self._get_hierarchical_categories(project_id)
        self.eval_categories_map = categories  # Assigner MAINTENANT pour les calculs en boucle
        

        #for cat in categories:
        #    print(f"  - cat_id={cat[0]}, name={cat[1]}, level={cat[3]}, parent_id={cat[4]}")

        
        if not categories:
            label = QLabel("Aucune catégorie de notation trouvée. Configurez d'abord le barème dans l'onglet 'Barème'.")
            self.eval_scroll_layout.addWidget(label)
            return
        
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
        
        self.evaluation_spinboxes = {}
        self.evaluation_total_labels = {}
        self.evaluation_categories = categories
        self.eval_values_cache = {}  # Réinitialiser le cache
        
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
        table.setRowCount(len(all_students) + 1)  # +1 pour la rangée des barèmes
        table.setColumnCount(len(categories) + 5)  # +5 pour Répertoire, Élève, Suivi, Total Max, Total
        
        # Créer les en-têtes simples
        headers = ["Répertoire", "Élève"] + [cat[1] for cat in categories] + ["Suivi", "Total Max", "Total"]
        table.setHorizontalHeaderLabels(headers)
        
        custom_header = VerticalHeaderView(Qt.Orientation.Horizontal)
        custom_header.setModel(table.model())
        table.setHorizontalHeader(custom_header)
        
        table.horizontalHeader().setFixedHeight(150)
        
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 120)
        for i in range(len(categories)):
            table.setColumnWidth(2 + i, 60)
        table.setColumnWidth(2 + len(categories), 60)  # Colonne Suivi
        table.setColumnWidth(3 + len(categories), 80)  # Colonne Total Max
        table.setColumnWidth(4 + len(categories), 60)  # Colonne Total
        
        # Première rangée: afficher les barèmes
        total_max = 0
        
        # Calculer le max du Suivi : nombre de séances * (max_journal + max_gantt + max_comportement)
        suivi_max = 0
        try:
            project_id = self.eval_project_combo.currentData()
            repetition = self.eval_repetition_combo.currentData()
            
            if project_id and repetition:
                sessions = self.db.get_session_dates(project_id, repetition)
                if sessions:
                    num_sessions = len(sessions)
                    
                    # Récupérer les max values de la première session (supposés identiques pour toutes)
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
        
        for col, category in enumerate(categories):
            cat_points = category[2]
            bareme_text = f"({cat_points})" if cat_points else "(?)"
            total_max += cat_points if cat_points else 0
            
            bareme_item = QTableWidgetItem(bareme_text)
            bareme_item.setFlags(bareme_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            bareme_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            bareme_item.setBackground(QColor("#E8E8E8"))
            
            # Mettre en gras
            font = QFont()
            font.setBold(True)
            bareme_item.setFont(font)
            
            table.setItem(0, col + 2, bareme_item)
        
        # Élément spacer pour colonnes Répertoire et Élève
        spacer_repo = QTableWidgetItem("")
        spacer_repo.setFlags(spacer_repo.flags() & ~Qt.ItemFlag.ItemIsEditable)
        spacer_repo.setBackground(QColor("#E8E8E8"))
        table.setItem(0, 0, spacer_repo)
        
        spacer_eleve = QTableWidgetItem("")
        spacer_eleve.setFlags(spacer_eleve.flags() & ~Qt.ItemFlag.ItemIsEditable)
        spacer_eleve.setBackground(QColor("#E8E8E8"))
        table.setItem(0, 1, spacer_eleve)
        
        # Ajouter le total maximal sous Suivi
        suivi_label = QTableWidgetItem(str(suivi_max))
        suivi_label.setFlags(suivi_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        suivi_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        suivi_label.setBackground(QColor("#E8E8E8"))
        
        font = QFont()
        font.setBold(True)
        suivi_label.setFont(font)
        
        table.setItem(0, 2 + len(categories), suivi_label)
        
        # Ajouter un placeholder pour Total Max (car il va varier par élève)
        total_max_label = QTableWidgetItem("Variable")
        total_max_label.setFlags(total_max_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        total_max_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_max_label.setBackground(QColor("#E8E8E8"))
        font_max = QFont()
        font_max.setBold(True)
        font_max.setItalic(True)
        total_max_label.setFont(font_max)
        table.setItem(0, 3 + len(categories), total_max_label)
        
        # Afficher le total maximal également dans la colonne Total (pour référence)
        # Total = Suivi max + Évaluation max
        total_max_with_suivi = suivi_max + total_max
        total_label = QTableWidgetItem(str(total_max_with_suivi))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        total_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_label.setBackground(QColor("#E8E8E8"))
        
        font_total = QFont()
        font_total.setBold(True)
        total_label.setFont(font_total)
        
        table.setItem(0, 4 + len(categories), total_label)
        
        table.setRowHeight(0, 25)
        
        # Identifier les catégories niveau 2 qui ont des enfants (niveau 3)
        level2_with_children = set()
        for cat in categories:
            if cat[3] == 3:  # C'est un niveau 3
                parent_id = cat[4]  # Récupérer l'ID du parent (niveau 2)
                if parent_id is not None:
                    level2_with_children.add(parent_id)
        
        # BONUS: Identifier les cat_id qui existent AUSSI au level 3
        # (doublons dus à une réutilisation d'IDs dans la BD)
        # Pour éviter de les compter deux fois, on marque les level 2 doublons
        level2_cat_ids = set(cat[0] for cat in categories if cat[3] == 2)
        level3_cat_ids = set(cat[0] for cat in categories if cat[3] == 3)
        duplicated_cat_ids = level2_cat_ids & level3_cat_ids  # Intersection
        
                
        # Stocker level2_with_children pour l'utiliser dans _calculate_eval_total()
        self.eval_level2_with_children = level2_with_children
        self.eval_duplicated_cat_ids = duplicated_cat_ids  # NOUVEAU: catégories dupliquées
        
        # Initialiser les assignations de tâches pour tous les groupes
        for group in groups:
            group_id = group[0]
            self.db.initialize_student_rating_assignments(group_id)
        
        # ✅ PRÉ-REMPLIR eval_data et eval_student_group_map depuis la BD
        self.eval_data = {}
        self.eval_student_group_map = {}
        for group_id, group_number, student_id, student_name in all_students:
            self.eval_student_group_map[student_id] = group_id
            self.eval_data[student_id] = {}
            # Charger toutes les évaluations pour cet élève depuis la BD
            # Utiliser l'INDEX comme clé unique (pas cat_id) pour gérer les doublons
            for idx, category in enumerate(categories):
                cat_id = category[0]
                rating_level = category[3]  # Récupérer le level de la catégorie
                evaluation_note = self.db.get_student_evaluation(student_id, group_id, cat_id, rating_level)
                self.eval_data[student_id][idx] = int(evaluation_note) if evaluation_note else 0
                
        
        for row, (group_id, group_number, student_id, student_name) in enumerate(all_students, start=1):
            if group_id not in self.evaluation_spinboxes:
                self.evaluation_spinboxes[group_id] = {}
            
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
            
            self.evaluation_spinboxes[group_id][student_id] = {}
            
            for col, category in enumerate(categories):
                cat_id = category[0]
                cat_name = category[1]
                cat_points = category[2]
                level = category[3]
                
                # Vérifier si l'élève est assigné à cette catégorie (tâche)
                is_assigned = self.db.get_student_rating_assignment(student_id, group_id, cat_id)
                if is_assigned is None:
                    is_assigned = True  # Par défaut, assigné si pas d'info
                
                # Vérifier si c'est une catégorie qui a une spinbox
                # = level 3 OU (level 2 SANS enfants)
                has_spinbox = (level == 3) or (level == 2 and cat_id not in level2_with_children)
                
                if level == 2 and cat_id in level2_with_children:
                    # Catégorie niveau 2 AVEC enfants : afficher le label seulement, pas de spinbox
                    label_item = QTableWidgetItem(cat_name)
                    label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    label_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    label_item.setBackground(bg_color)
                    font = QFont()
                    font.setBold(True)
                    label_item.setFont(font)
                    table.setItem(row, col + 2, label_item)
                    
                elif not is_assigned:
                    # Élève NON assigné à cette tâche: afficher "N/D" au lieu d'une spinbox
                    nd_item = QTableWidgetItem("N/D")
                    nd_item.setFlags(nd_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    nd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    nd_item.setBackground(bg_color)
                    font = QFont()
                    font.setItalic(True)
                    nd_item.setFont(font)
                    table.setItem(row, col + 2, nd_item)
                    
                elif has_spinbox and is_assigned:
                    # Catégorie avec spinbox et élève assigné: créer la spinbox
                    spinbox = QSpinBox()
                    spinbox.setMinimum(0)
                    spinbox.setMaximum(cat_points if cat_points is not None else 100)
                    self._apply_spinbox_style(spinbox)
                    
                    # ✅ CHARGER la valeur depuis eval_data (pré-rempli depuis la BD)
                    # Utiliser COL comme index dans categories (col est l'index de cette catégorie)
                    initial_value = self.eval_data[student_id].get(col, 0)  # col = cat_idx
                    
                    # Bloquer les signaux pendant la valeur initiale
                    spinbox.blockSignals(True)
                    spinbox.setValue(initial_value)
                    spinbox.blockSignals(False)
                    
                    # Stocker le spinbox
                    self.evaluation_spinboxes[group_id][student_id][cat_id] = spinbox
                    
                    # ✅ Connecter le spinbox pour mettre à jour eval_data et le total
                    # PASSER L'INDEX (col) AU LIEU DE cat_id
                    spinbox.valueChanged.connect(partial(self._update_eval_value, student_id, col))
                    
                    # Créer un widget pour la cellule
                    widget = QWidget()
                    cell_layout = QHBoxLayout()
                    cell_layout.setContentsMargins(2, 2, 2, 2)
                    cell_layout.addWidget(spinbox)
                    widget.setLayout(cell_layout)
                    
                    color_hex = bg_color.name()
                    widget.setStyleSheet(f"background-color: {color_hex};")
                    
                    table.setCellWidget(row, col + 2, widget)
            
            # Ajouter colonne Suivi (somme des scores de l'onglet Suivi)
            suivi_score = self._calculate_suivi_score(student_id, group_id)
            suivi_item = QTableWidgetItem(str(suivi_score))
            suivi_item.setFlags(suivi_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            suivi_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            suivi_item.setBackground(bg_color)
            table.setItem(row, 2 + len(categories), suivi_item)
            
            # Ajouter colonne Total Max (Suivi max + somme des évaluations MAX pour les tâches assignées)
            # ✅ UTILISER LA MÉTHODE _calculate_total_max() pour éviter les doublons
            student_total_max = self._calculate_total_max(student_id, suivi_max)
            
            # Afficher le total max dans la colonne Total Max
            total_max_item = QTableWidgetItem(str(student_total_max))
            total_max_item.setFlags(total_max_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_max_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_max_item.setBackground(bg_color)
            font = QFont()
            font.setBold(True)
            total_max_item.setFont(font)
            table.setItem(row, 3 + len(categories), total_max_item)
            
            # Ajouter colonne Total (Suivi + somme des évaluations)
            eval_total = self._calculate_eval_total(student_id)
            total_score = suivi_score + eval_total
            
            # Utiliser un widget avec un label pour la colonne Total (comme dans l'onglet suivi)
            total_label = QLabel(str(total_score))
            total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setBold(True)
            total_label.setFont(font)
            
            # Créer un widget avec le label
            widget = QWidget()
            cell_layout = QHBoxLayout()
            cell_layout.setContentsMargins(2, 2, 2, 2)
            cell_layout.addWidget(total_label)
            widget.setLayout(cell_layout)
            
            color_hex = bg_color.name()
            widget.setStyleSheet(f"background-color: {color_hex};")
            
            # Stocker la référence au label pour mise à jour en temps réel
            self.evaluation_total_labels[student_id] = total_label
            
            table.setCellWidget(row, 4 + len(categories), widget)
        
        table.resizeRowsToContents()
        table.resizeColumnToContents(0)  # Adapter seulement la colonne Répertoire
        
        # Sauvegarder la référence à la table et autres références
        self.eval_table = table
        self.eval_students_map = all_students
        
        self.eval_scroll_layout.addWidget(table, 1)

    def save_evaluations(self):
        """Sauvegarder les notes d'évaluation de tous les élèves
        
        Parcourt eval_data et sauvegarde chaque valeur dans la BD
        """
        if self.eval_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet sélectionné !")
            return
        
        try:
            
            saved_count = 0
            
            # Sauvegarder TOUTES les valeurs d'eval_data
            for student_id, idx_values in sorted(self.eval_data.items()):
                group_id = self.eval_student_group_map.get(student_id)
                if not group_id:
                    continue
                
                for idx, value in sorted(idx_values.items()):
                    # Récupérer le cat_id et le rating_level correspondant à l'index
                    if 0 <= idx < len(self.eval_categories_map):
                        cat_id = self.eval_categories_map[idx][0]
                        rating_level = self.eval_categories_map[idx][3]  # Récupérer le level
                        self.db.set_student_evaluation(student_id, group_id, cat_id, value, rating_level)
                        saved_count += 1
            
            
            QMessageBox.information(self.parent, "Succès", f"Évaluations sauvegardées !\n({saved_count} valeurs)")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la sauvegarde :\n{str(e)}")
