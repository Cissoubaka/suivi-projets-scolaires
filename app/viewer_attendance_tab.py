"""Onglet de suivi de présence (lecture seule) pour la visionneuse"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from custom_widgets import VerticalHeaderView
from viewer_base_tab import ViewerTabBase


class ViewerAttendanceTab(ViewerTabBase):
    """Onglet de suivi de présence (lecture seule pour élèves)"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.attendance_session_ids = {}

    def create_widget(self):
        """Créer l'onglet de suivi de présence en mode lecture seule"""
        try:
            widget = QWidget()
            layout = QVBoxLayout()

            # Section sélection projet/répétition
            selection_layout = QHBoxLayout()
            selection_layout.addWidget(QLabel("Projet :"))
            self.attendance_project_combo = QComboBox()
            self.attendance_project_combo.currentIndexChanged.connect(self.on_attendance_project_changed)
            selection_layout.addWidget(self.attendance_project_combo)
            
            selection_layout.addWidget(QLabel("Répétition :"))
            self.attendance_repetition_combo = QComboBox()
            self.attendance_repetition_combo.currentIndexChanged.connect(self.on_attendance_repetition_changed)
            selection_layout.addWidget(self.attendance_repetition_combo)
            
            selection_layout.addStretch()
            layout.addLayout(selection_layout)

            # Zone de scroll pour afficher le tableau
            self.attendance_scroll_area = QScrollArea()
            self.attendance_scroll_area.setWidgetResizable(True)
            self.attendance_scroll_container = QWidget()
            self.attendance_scroll_layout = QVBoxLayout()
            self.attendance_scroll_layout.setContentsMargins(0, 0, 0, 0)
            self.attendance_scroll_container.setLayout(self.attendance_scroll_layout)
            self.attendance_scroll_area.setWidget(self.attendance_scroll_container)
            layout.addWidget(self.attendance_scroll_area, 1)

            widget.setLayout(layout)
            
            # Charger les données avec QTimer pour éviter les problèmes d'affichage
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.refresh_data)
            
            return widget
        except Exception as e:
            print(f"[ERROR] create_widget: {e}")
            import traceback
            traceback.print_exc()
            return QWidget()

    def refresh_data(self):
        """Rafraîchir l'onglet de suivi de présence"""
        self.refresh_attendance_projects_combo()

    def refresh_attendance_projects_combo(self):
        """Rafraîchir la liste des projets pour l'onglet suivi présence"""
        try:
            self.attendance_project_combo.blockSignals(True)
            self.attendance_repetition_combo.blockSignals(True)
            
            self.attendance_project_combo.clear()
            self.attendance_repetition_combo.clear()
            
            projects = self.db.get_all_projects()
            for project in projects:
                self.attendance_project_combo.addItem(project[1], project[0])
            
            self.attendance_project_combo.blockSignals(False)
            self.attendance_repetition_combo.blockSignals(False)
            
            if self.attendance_project_combo.count() > 0:
                self.attendance_project_combo.setCurrentIndex(0)
                self.on_attendance_project_changed()
        except Exception as e:
            print(f"[ERROR] refresh_attendance_projects_combo: {e}")
            import traceback
            traceback.print_exc()

    def on_attendance_project_changed(self):
        """Mettre à jour les répétitions quand le projet change"""
        try:
            self.attendance_repetition_combo.blockSignals(True)
            self.attendance_repetition_combo.clear()
            self.attendance_repetition_combo.blockSignals(False)
            
            if self.attendance_project_combo.count() == 0:
                return
            
            project_id = self.attendance_project_combo.currentData()
            project = self.db.get_project(project_id)
            
            if project:
                for rep in range(1, project[3] + 1):
                    self.attendance_repetition_combo.addItem(f"Répétition {rep}", rep)
            
            # Sélectionner la première répétition
            if self.attendance_repetition_combo.count() > 0:
                self.attendance_repetition_combo.setCurrentIndex(0)
                self.on_attendance_repetition_changed()
        except Exception as e:
            print(f"[ERROR] on_attendance_project_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_attendance_repetition_changed(self):
        """Rafraîchir l'affichage du tableau quand la répétition change"""
        try:
            self.display_attendance_table()
        except Exception as e:
            print(f"[ERROR] on_attendance_repetition_changed: {e}")
            import traceback
            traceback.print_exc()

    def display_attendance_table(self):
        """Afficher le tableau de présence en mode lecture seule"""
        # Nettoyer la zone de scroll
        while self.attendance_scroll_layout.count():
            widget = self.attendance_scroll_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        if self.attendance_project_combo.count() == 0:
            return
        
        project_id = self.attendance_project_combo.currentData()
        repetition = self.attendance_repetition_combo.currentData()
        
        if project_id is None or repetition is None:
            return
        
        # Récupérer les groupes
        groups = self.db.get_groups_for_project(project_id, repetition)
        if not groups:
            label = QLabel("Aucun groupe trouvé")
            self.attendance_scroll_layout.addWidget(label)
            return
        
        # Récupérer les sessions
        sessions = self.db.get_session_dates(project_id, repetition)
        if not sessions:
            label = QLabel("Aucune séance trouvée.")
            self.attendance_scroll_layout.addWidget(label)
            return
        
        # Récupérer tous les élèves
        all_students = []
        for group in groups:
            group_id, _, group_number, _ = group
            students = self.db.get_students_in_group(group_id)
            for student in students:
                student_id = student[0]
                student_name = f"{student[2]} {student[1]}"
                all_students.append((group_id, group_number, student_id, student_name))
        
        if not all_students:
            label = QLabel("Aucun élève trouvé")
            self.attendance_scroll_layout.addWidget(label)
            return
        
        # Récupérer les valeurs max pour chaque session
        attendance_max_values = {}
        for session_id, session_date in sessions:
            cursor = self.db.get_connection().cursor()
            cursor.execute('SELECT journal_bord, gantt, travail_comportement FROM session_dates WHERE id = ?', (session_id,))
            result = cursor.fetchone()
            cursor.connection.close()
            if result:
                attendance_max_values[session_id] = result
            else:
                attendance_max_values[session_id] = (0, 0, 0)
        
        # Palette de couleurs pour les groupes
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
        table.setRowCount(len(all_students))
        table.setColumnCount(len(sessions) + 3)  # +3 pour Groupe, Élève, Total
        
        headers = ["Répertoire", "Élève"] + [session[1] for session in sessions] + ["Total"]
        table.setHorizontalHeaderLabels(headers)
        
        custom_header = VerticalHeaderView(Qt.Orientation.Horizontal)
        custom_header.setModel(table.model())
        table.setHorizontalHeader(custom_header)
        
        # Stocker les IDs de session pour les en-têtes
        for i, (session_id, session_date) in enumerate(sessions):
            self.attendance_session_ids[i + 2] = (session_id, session_date)
        
        table.horizontalHeader().setFixedHeight(150)
        
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 120)
        for i in range(len(sessions)):
            table.setColumnWidth(2 + i, 180)
        table.setColumnWidth(2 + len(sessions), 70)  # Colonne Total
        
        # Remplir les données du tableau
        for row, (group_id, group_number, student_id, student_name) in enumerate(all_students):
            bg_color = colors_palette[(group_number - 1) % len(colors_palette)]
            
            # Colonne Répertoire
            dir_name, _ = self.db.get_group_directory(group_id)
            display_group = dir_name if dir_name else f"Groupe {group_number}"
            group_item = QTableWidgetItem(display_group)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            group_item.setBackground(bg_color)
            table.setItem(row, 0, group_item)
            
            # Colonne Élève
            name_item = QTableWidgetItem(student_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setBackground(bg_color)
            table.setItem(row, 1, name_item)
            
            # Colonnes des sessions avec données de présence
            for col, (session_id, session_date) in enumerate(sessions):
                attendance_data = self.db.get_attendance(student_id, group_id, session_id)
                
                if attendance_data:
                    is_present = attendance_data[0]
                    journal_bord = attendance_data[1] if len(attendance_data) > 1 else 0
                    gantt = attendance_data[2] if len(attendance_data) > 2 else 0
                    travail_comportement = attendance_data[3] if len(attendance_data) > 3 else 0
                else:
                    is_present = False
                    journal_bord = 0
                    gantt = 0
                    travail_comportement = 0
                
                max_journal, max_gantt, max_comportement = attendance_max_values.get(session_id, (0, 0, 0))
                
                # Créer le contenu de la cellule
                display_text = "Absent" if not is_present else f"Présent\nJ:{journal_bord}/{max_journal}\nG:{gantt}/{max_gantt}\nC:{travail_comportement}/{max_comportement}"
                
                cell_item = QTableWidgetItem(display_text)
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                cell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                
                # Couleur de background
                if is_present:
                    cell_item.setBackground(bg_color)
                else:
                    cell_item.setBackground(QColor(255, 150, 150))
                
                table.setItem(row, col + 2, cell_item)
            
            # Colonne Total avec pro-rata
            total_score = 0
            seances_presentes = 0
            total_sessions_count = len(sessions)
            
            for session_id, session_date in sessions:
                attendance_data = self.db.get_attendance(student_id, group_id, session_id)
                if attendance_data and attendance_data[0]:  # Si présent
                    seances_presentes += 1
                    journal_bord = attendance_data[1] if len(attendance_data) > 1 else 0
                    gantt = attendance_data[2] if len(attendance_data) > 2 else 0
                    travail_comportement = attendance_data[3] if len(attendance_data) > 3 else 0
                    total_score += (journal_bord + gantt + travail_comportement)
            
            # Appliquer le pro-rata
            if seances_presentes > 0 and total_sessions_count > 0:
                total_score = round(total_score * total_sessions_count / seances_presentes, 2)
            
            total_item = QTableWidgetItem(f"{total_score:.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Mettre en gras
            font = QFont()
            font.setBold(True)
            total_item.setFont(font)
            
            total_item.setBackground(bg_color)
            table.setItem(row, 2 + len(sessions), total_item)
        
        table.resizeRowsToContents()
        self.attendance_scroll_layout.addWidget(table, 1)
