import os
import zipfile
import xml.etree.ElementTree as ET
import unicodedata
import json
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDateEdit, QSpinBox, QScrollArea, QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox,
    QLineEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from custom_widgets import VerticalHeaderView
from mindview_parser import MindViewParser
from tabs.base import TabBase


class AttendanceTab(TabBase):
    """Onglet de suivi de présence"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_selection_id = None
        self.attendance_checkboxes = {}
        self.attendance_spinboxes = {}
        self.attendance_max_values = {}
        self.attendance_session_ids = {}
        self.attendance_cell_widgets = {}
        self.attendance_total_items = {}  # Stocker les références aux items "Total"

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
    
    def _apply_checkbox_style(self, checkbox):
        """Appliquer un style explicite aux checkboxes pour Windows 11."""
        checkbox.setMinimumWidth(24)
        checkbox.setMinimumHeight(24)
        checkbox.setStyleSheet(
            "QCheckBox { "
            "color: #111111; "
            "background-color: transparent; "
            "spacing: 4px; "
            "} "
            "QCheckBox::indicator { "
            "width: 18px; "
            "height: 18px; "
            "background-color: #FFFFFF; "
            "border: 2px solid #8A8A8A; "
            "border-radius: 3px; "
            "} "
            "QCheckBox::indicator:hover { "
            "background-color: #F5F5F5; "
            "border: 2px solid #4A90E2; "
            "} "
            "QCheckBox::indicator:checked { "
            "background-color: #2196F3; "
            "border: 2px solid #1976D2; "
            "image: url(':/qt-project.org/styles/commonstyle/images/checkbox.png'); "
            "} "
            "QCheckBox::indicator:checked:hover { "
            "background-color: #1976D2; "
            "}"
        )
    
    def create_widget(self):
        """Créer l'onglet de suivi de présence"""
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
            
            layout.addLayout(selection_layout)

            # Section information du fichier Mindview détecté
            mindview_layout = QHBoxLayout()
            mindview_layout.addWidget(QLabel("Fichier Mindview détecté :"))
            self.mindview_file_input = QLineEdit()
            self.mindview_file_input.setReadOnly(True)
            self.mindview_file_input.setPlaceholderText("Aucun fichier *_GANTT.mvdx détecté")
            mindview_layout.addWidget(self.mindview_file_input)
            
            layout.addLayout(mindview_layout)

            # Section ajout de séances
            session_layout = QHBoxLayout()
            session_layout.addWidget(QLabel("Ajouter une séance (date) :"))
            
            self.attendance_date_input = QDateEdit()
            self.attendance_date_input.setCalendarPopup(True)
            self.attendance_date_input.setDate(QDate.currentDate())
            session_layout.addWidget(self.attendance_date_input)
            
            add_session_btn = QPushButton("Ajouter")
            add_session_btn.clicked.connect(self.add_attendance_session)
            session_layout.addWidget(add_session_btn)
            
            session_layout.addSpacing(20)
            
            # Champ Journal de bord
            session_layout.addWidget(QLabel("Journal de bord :"))
            self.attendance_journal_input = QSpinBox()
            self.attendance_journal_input.setMinimum(0)
            self.attendance_journal_input.setMaximum(20)
            self.attendance_journal_input.setValue(0)
            self._apply_spinbox_style(self.attendance_journal_input)
            session_layout.addWidget(self.attendance_journal_input)
            
            session_layout.addSpacing(10)
            
            # Champ GANTT
            session_layout.addWidget(QLabel("GANTT :"))
            self.attendance_gantt_input = QSpinBox()
            self.attendance_gantt_input.setMinimum(0)
            self.attendance_gantt_input.setMaximum(20)
            self.attendance_gantt_input.setValue(0)
            self._apply_spinbox_style(self.attendance_gantt_input)
            session_layout.addWidget(self.attendance_gantt_input)
            
            session_layout.addSpacing(10)
            
            # Champ Travail/comportement
            session_layout.addWidget(QLabel("Travail/comportement :"))
            self.attendance_behavior_input = QSpinBox()
            self.attendance_behavior_input.setMinimum(0)
            self.attendance_behavior_input.setMaximum(20)
            self.attendance_behavior_input.setValue(0)
            self._apply_spinbox_style(self.attendance_behavior_input)
            session_layout.addWidget(self.attendance_behavior_input)
            
            session_layout.addSpacing(20)
            
            # Bouton de vérification du journal de bord
            verify_journal_btn = QPushButton("Vérifier le Journal de Bord")
            verify_journal_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; }")
            verify_journal_btn.clicked.connect(self.verify_journal_de_bord)
            session_layout.addWidget(verify_journal_btn)
            
            # Bouton de vérification du GANTT
            verify_gantt_btn = QPushButton("Vérifier GANTT")
            verify_gantt_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; font-weight: bold; }")
            verify_gantt_btn.clicked.connect(self.verify_gantt)
            session_layout.addWidget(verify_gantt_btn)
            
            session_layout.addStretch()
            layout.addLayout(session_layout)

            # Zone de scroll pour afficher le tableau
            self.attendance_scroll_area = QScrollArea()
            self.attendance_scroll_area.setWidgetResizable(True)
            self.attendance_scroll_container = QWidget()
            self.attendance_scroll_layout = QVBoxLayout()
            self.attendance_scroll_layout.setContentsMargins(0, 0, 0, 0)
            self.attendance_scroll_container.setLayout(self.attendance_scroll_layout)
            self.attendance_scroll_area.setWidget(self.attendance_scroll_container)
            layout.addWidget(self.attendance_scroll_area, 1)

            # Bouton de sauvegarde
            save_btn = QPushButton("Sauvegarder les présences")
            save_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
            save_btn.clicked.connect(self.save_attendance)
            layout.addWidget(save_btn)

            widget.setLayout(layout)
            self.refresh_data()
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
            self.update_detected_mindview_file()
            
            project = self.db.get_project(project_id)
            if project:
                self.attendance_repetition_combo.blockSignals(True)
                for rep in range(1, project[3] + 1):
                    self.attendance_repetition_combo.addItem(f"Répétition {rep}", rep)
                self.attendance_repetition_combo.blockSignals(False)
                
                if self.attendance_repetition_combo.count() > 0:
                    self.attendance_repetition_combo.setCurrentIndex(0)
                    self.on_attendance_repetition_changed()
        except Exception as e:
            print(f"[ERROR] on_attendance_project_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_attendance_repetition_changed(self):
        """Rafraîchir le tableau quand la répétition change"""
        try:
            self.display_attendance_table()
        except Exception as e:
            print(f"Erreur on_attendance_repetition_changed: {e}")
            import traceback
            traceback.print_exc()

    def add_attendance_session(self):
        """Ajouter une nouvelle séance"""
        if self.attendance_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        
        project_id = self.attendance_project_combo.currentData()
        repetition = self.attendance_repetition_combo.currentData()
        
        if project_id is None or repetition is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner une répétition !")
            return
        
        session_date = self.attendance_date_input.date().toString("yyyy-MM-dd")
        journal_bord = self.attendance_journal_input.value()
        gantt = self.attendance_gantt_input.value()
        travail_comportement = self.attendance_behavior_input.value()
        
        result = self.db.add_session_date(project_id, repetition, session_date, journal_bord, gantt, travail_comportement)
        if result is None:
            QMessageBox.warning(self.parent, "Erreur", "Cette date de séance existe déjà !")
            return
        
        QMessageBox.information(self.parent, "Succès", f"Séance du {session_date} ajoutée !")
        self.display_attendance_table()

    def detect_mindview_file_name(self):
        """Détecter automatiquement un fichier se terminant par _GANTT.mvdx dans le répertoire source."""
        source_dir = self.db.get_setting("directory_source", "")
        if not source_dir or not os.path.isdir(source_dir):
            return None

        try:
            candidates = []
            for file_name in os.listdir(source_dir):
                if file_name.lower().endswith("_gantt.mvdx"):
                    full_path = os.path.join(source_dir, file_name)
                    if os.path.isfile(full_path):
                        candidates.append((os.path.getmtime(full_path), file_name))

            if not candidates:
                return None

            # Prendre le fichier le plus récent en cas de plusieurs correspondances.
            candidates.sort(key=lambda item: item[0], reverse=True)
            return candidates[0][1]
        except Exception as e:
            print(f"[ERROR] detect_mindview_file_name: {e}")
            return None

    def update_detected_mindview_file(self):
        """Mettre à jour le champ affichant le fichier Mindview détecté."""
        detected_file = self.detect_mindview_file_name()
        if detected_file:
            self.mindview_file_input.setText(detected_file)
        else:
            self.mindview_file_input.clear()
    
    def get_gantt_file_path(self, group_dir_path, project_id):
        """Construire le chemin du fichier GANTT Mindview pour un groupe
        Cherche le fichier avec le nom détecté depuis le répertoire source.
        """
        mindview_file = self.detect_mindview_file_name()

        if mindview_file:
            gantt_file_path = os.path.join(group_dir_path, mindview_file)
        else:
            # Fichier par défaut
            gantt_file_path = os.path.join(group_dir_path, "WBS_projet_interface_GANTT.mvdx")
        
        return gantt_file_path

    def display_attendance_table(self):
        """Afficher le tableau de présence"""
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
        
        groups = self.db.get_groups_for_project(project_id, repetition)
        if not groups:
            label = QLabel("Aucun groupe trouvé")
            self.attendance_scroll_layout.addWidget(label)
            return
        
        sessions = self.db.get_session_dates(project_id, repetition)
        if not sessions:
            label = QLabel("Aucune séance trouvée. Ajoutez une séance pour commencer.")
            self.attendance_scroll_layout.addWidget(label)
            return
        
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
        
        self.attendance_max_values = {}
        for session_id, session_date in sessions:
            cursor = self.db.get_connection().cursor()
            cursor.execute('SELECT journal_bord, gantt, travail_comportement FROM session_dates WHERE id = ?', (session_id,))
            result = cursor.fetchone()
            cursor.connection.close()
            if result:
                self.attendance_max_values[session_id] = result
            else:
                self.attendance_max_values[session_id] = (0, 0, 0)
        
        self.attendance_checkboxes = {}
        self.attendance_spinboxes = {}
        self.attendance_cell_widgets = {}
        self.attendance_session_ids = {}
        
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
        table.setColumnCount(len(sessions) + 3)  # +3 pour Groupe, Élève, Total
        
        headers = ["Groupe", "Élève"] + [session[1] for session in sessions] + ["Total"]
        table.setHorizontalHeaderLabels(headers)
        
        custom_header = VerticalHeaderView(Qt.Orientation.Horizontal)
        custom_header.setModel(table.model())
        custom_header.headerClicked.connect(self.on_attendance_header_clicked)
        table.setHorizontalHeader(custom_header)
        
        for i, (session_id, session_date) in enumerate(sessions):
            self.attendance_session_ids[i + 2] = (session_id, session_date)
        
        table.horizontalHeader().setFixedHeight(150)
        
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 120)
        for i in range(len(sessions)):
            table.setColumnWidth(2 + i, 225)
        table.setColumnWidth(2 + len(sessions), 70)  # Colonne Total
        
        for row, (group_id, group_number, student_id, student_name) in enumerate(all_students):
            if group_id not in self.attendance_checkboxes:
                self.attendance_checkboxes[group_id] = {}
                self.attendance_spinboxes[group_id] = {}
                self.attendance_cell_widgets[group_id] = {}
            
            bg_color = colors_palette[(group_number - 1) % len(colors_palette)]
            
            group_item = QTableWidgetItem(f"Groupe {group_number}")
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            group_item.setBackground(bg_color)
            table.setItem(row, 0, group_item)
            
            name_item = QTableWidgetItem(student_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setBackground(bg_color)
            table.setItem(row, 1, name_item)
            
            self.attendance_checkboxes[group_id][student_id] = {}
            self.attendance_spinboxes[group_id][student_id] = {}
            self.attendance_cell_widgets[group_id][student_id] = {}
            
            for col, (session_id, session_date) in enumerate(sessions):
                attendance_data = self.db.get_attendance(student_id, group_id, session_id)
                is_present = attendance_data[0] if isinstance(attendance_data, tuple) else attendance_data
                journal_bord = attendance_data[1] if isinstance(attendance_data, tuple) else 0
                gantt = attendance_data[2] if isinstance(attendance_data, tuple) else 0
                travail_comportement = attendance_data[3] if isinstance(attendance_data, tuple) else 0
                
                max_journal, max_gantt, max_comportement = self.attendance_max_values.get(session_id, (0, 0, 0))
                
                widget = QWidget()
                cell_layout = QVBoxLayout()
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(2)
                
                checkbox = QCheckBox("Présent")
                checkbox.setChecked(is_present)
                self._apply_checkbox_style(checkbox)
                cell_layout.addWidget(checkbox)
                
                spinbox_layout = QHBoxLayout()
                spinbox_layout.setContentsMargins(0, 0, 0, 0)
                spinbox_layout.setSpacing(4)
                
                journal_spin = QSpinBox()
                journal_spin.setMinimum(0)
                journal_spin.setMaximum(max_journal if max_journal > 0 else 20)
                journal_spin.setValue(journal_bord if is_present else 0)
                journal_spin.setToolTip(f"Journal (max: {max_journal})")
                journal_spin.setEnabled(is_present)
                self._apply_spinbox_style(journal_spin)
                spinbox_layout.addWidget(journal_spin)
                
                gantt_spin = QSpinBox()
                gantt_spin.setMinimum(0)
                gantt_spin.setMaximum(max_gantt if max_gantt > 0 else 20)
                gantt_spin.setValue(gantt if is_present else 0)
                gantt_spin.setToolTip(f"GANTT (max: {max_gantt})")
                gantt_spin.setEnabled(is_present)
                self._apply_spinbox_style(gantt_spin)
                spinbox_layout.addWidget(gantt_spin)
                
                comportement_spin = QSpinBox()
                comportement_spin.setMinimum(0)
                comportement_spin.setMaximum(max_comportement if max_comportement > 0 else 20)
                comportement_spin.setValue(travail_comportement if is_present else 0)
                comportement_spin.setToolTip(f"Travail/comportement (max: {max_comportement})")
                comportement_spin.setEnabled(is_present)
                self._apply_spinbox_style(comportement_spin)
                spinbox_layout.addWidget(comportement_spin)
                
                # Connecter les spinboxes pour mettre à jour le total
                journal_spin.valueChanged.connect(lambda _, g=group_id, s=student_id: self.update_attendance_total(g, s))
                gantt_spin.valueChanged.connect(lambda _, g=group_id, s=student_id: self.update_attendance_total(g, s))
                comportement_spin.valueChanged.connect(lambda _, g=group_id, s=student_id: self.update_attendance_total(g, s))
                
                cell_layout.addLayout(spinbox_layout)
                widget.setLayout(cell_layout)
                
                if is_present:
                    cell_color = bg_color
                else:
                    cell_color = QColor(255, 150, 150)
                color_hex = cell_color.name()
                widget.setStyleSheet(f"background-color: {color_hex};")
                
                table.setCellWidget(row, col + 2, widget)
                
                self.attendance_checkboxes[group_id][student_id][session_id] = checkbox
                self.attendance_spinboxes[group_id][student_id][session_id] = [journal_spin, gantt_spin, comportement_spin]
                self.attendance_cell_widgets[group_id][student_id][session_id] = widget
                
                def on_presence_changed(state=None, checkbox=checkbox, group_id=group_id, student_id=student_id, session_id=session_id, spinboxes=[journal_spin, gantt_spin, comportement_spin], cell_widget=widget, bg_color=bg_color):
                    is_present = checkbox.isChecked()
                    for spinbox in spinboxes:
                        spinbox.setEnabled(is_present)
                    if not is_present:
                        for spinbox in spinboxes:
                            spinbox.setValue(0)
                        cell_widget.setStyleSheet(f"background-color: rgb(255, 150, 150);")
                    else:
                        color_hex = bg_color.name()
                        cell_widget.setStyleSheet(f"background-color: {color_hex};")
                    
                    # Mettre à jour le total quand la présence change
                    self.update_attendance_total(group_id, student_id)
                
                checkbox.stateChanged.connect(on_presence_changed)
            
            # Ajouter colonne Total avec pro-rata selon les absences
            total_score = 0
            seances_presentes = 0
            total_sessions_count = len(sessions)
            
            for session_id, session_date in sessions:
                attendance_data = self.db.get_attendance(student_id, group_id, session_id)
                is_present = attendance_data[0] if isinstance(attendance_data, tuple) else attendance_data
                if is_present:
                    seances_presentes += 1
                    journal_bord = attendance_data[1] if isinstance(attendance_data, tuple) else 0
                    gantt = attendance_data[2] if isinstance(attendance_data, tuple) else 0
                    travail_comportement = attendance_data[3] if isinstance(attendance_data, tuple) else 0
                    total_score += (journal_bord + gantt + travail_comportement)
            
            # Appliquer le pro-rata: ramener le total sur le nombre de séances total
            if seances_presentes > 0:
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
            
            # Stocker la référence pour mise à jour dynamique
            self.attendance_total_items[(group_id, student_id)] = total_item
        
        table.resizeRowsToContents()
        
        self.attendance_scroll_layout.addWidget(table, 1)

    def update_attendance_total(self, group_id, student_id):
        """Recalculer et mettre à jour le total des points pour un élève avec pro-rata"""
        try:
            total_score = 0
            seances_presentes = 0
            total_sessions_count = 0
            
            # Parcourir les spinboxes de cet étudiant et additionner les valeurs
            if group_id in self.attendance_spinboxes and student_id in self.attendance_spinboxes[group_id]:
                total_sessions_count = len(self.attendance_spinboxes[group_id][student_id])
                for session_id, spinboxes in self.attendance_spinboxes[group_id][student_id].items():
                    # Vérifier si l'étudiant est présent
                    checkbox = self.attendance_checkboxes.get(group_id, {}).get(student_id, {}).get(session_id)
                    if checkbox and checkbox.isChecked():
                        seances_presentes += 1
                        # Additionner les trois spinboxes : journal + gantt + comportement
                        if len(spinboxes) >= 3:
                            total_score += spinboxes[0].value() + spinboxes[1].value() + spinboxes[2].value()
            
            # Appliquer le pro-rata: ramener le total sur le nombre de séances total
            if seances_presentes > 0 and total_sessions_count > 0:
                total_score = round(total_score * total_sessions_count / seances_presentes, 2)
            
            # Mettre à jour l'item Total dans le tableau
            if (group_id, student_id) in self.attendance_total_items:
                self.attendance_total_items[(group_id, student_id)].setText(f"{total_score:.2f}")
        except Exception as e:
            print(f"[ERROR] Erreur update_attendance_total: {e}")
            import traceback
            traceback.print_exc()

    def save_attendance(self):
        """Sauvegarder les enregistrements de présence et notes"""
        if self.attendance_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Aucun projet sélectionné !")
            return
        
        try:
            for group_id, students in self.attendance_checkboxes.items():
                for student_id, sessions in students.items():
                    for session_id, checkbox in sessions.items():
                        is_present = checkbox.isChecked()
                        
                        if is_present:
                            spinboxes = self.attendance_spinboxes.get(group_id, {}).get(student_id, {}).get(session_id, [None, None, None])
                            journal_bord = spinboxes[0].value() if spinboxes[0] else 0
                            gantt = spinboxes[1].value() if spinboxes[1] else 0
                            travail_comportement = spinboxes[2].value() if spinboxes[2] else 0
                            
                            max_journal, max_gantt, max_comportement = self.attendance_max_values.get(session_id, (0, 0, 0))
                            
                            if max_journal > 0 and journal_bord > max_journal:
                                QMessageBox.warning(self.parent, "Erreur", f"Journal de bord ({journal_bord}) dépasse le maximum ({max_journal})")
                                return
                            if max_gantt > 0 and gantt > max_gantt:
                                QMessageBox.warning(self.parent, "Erreur", f"GANTT ({gantt}) dépasse le maximum ({max_gantt})")
                                return
                            if max_comportement > 0 and travail_comportement > max_comportement:
                                QMessageBox.warning(self.parent, "Erreur", f"Travail/comportement ({travail_comportement}) dépasse le maximum ({max_comportement})")
                                return
                            
                            self.db.set_attendance(student_id, group_id, session_id, True, journal_bord, gantt, travail_comportement)
                        else:
                            # Sauvegarder l'absence (is_present = False)
                            self.db.set_attendance(student_id, group_id, session_id, False, 0, 0, 0)
            
            QMessageBox.information(self.parent, "Succès", "Présences et notes sauvegardées !")
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la sauvegarde :\n{str(e)}")
            import traceback
            traceback.print_exc()

    def on_attendance_header_clicked(self, column_index):
        """Supprimer une séance quand on clique sur sa date dans l'en-tête"""
        if column_index < 2:
            return
        
        if column_index not in self.attendance_session_ids:
            return
        
        session_id, session_date = self.attendance_session_ids[column_index]
        
        reply = QMessageBox.question(
            self.parent, 
            "Supprimer la séance", 
            f"Voulez-vous supprimer la séance du {session_date} ?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_session_date(session_id)
                self.display_attendance_table()
                QMessageBox.information(self.parent, "Succès", f"Séance du {session_date} supprimée !")
            except Exception as e:
                QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la suppression :\n{str(e)}")

    def verify_journal_de_bord(self):
        """Vérifier les journaux de bord seulement pour la DERNIÈRE séance"""
        if self.attendance_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        
        if not hasattr(self, 'attendance_spinboxes') or not self.attendance_spinboxes:
            QMessageBox.warning(self.parent, "Erreur", "Aucun tableau généré. Ajoutez d'abord une séance !")
            return
        
        try:
            last_session_id = None
            last_session_date = None
            
            for group_id, students in self.attendance_spinboxes.items():
                for student_id, sessions in students.items():
                    for session_id in sessions.keys():
                        cursor = self.db.get_connection().cursor()
                        cursor.execute('SELECT session_date FROM session_dates WHERE id = ?', (session_id,))
                        result = cursor.fetchone()
                        cursor.close()
                        
                        if result:
                            session_date = result[0]
                            if last_session_date is None or session_date > last_session_date:
                                last_session_date = session_date
                                last_session_id = session_id
                    
                    if last_session_id:
                        break
                if last_session_id:
                    break
            
            if not last_session_id:
                QMessageBox.warning(self.parent, "Erreur", "Aucune séance trouvée !")
                return
            
            max_journal, _, _ = self.attendance_max_values.get(last_session_id, (0, 0, 0))
            
            if max_journal <= 0:
                QMessageBox.warning(self.parent, "Erreur", "Aucun maximum défini pour le journal de bord dans la dernière séance !")
                return
            
            verified_count = 0
            date_not_found_count = 0
            no_content_count = 0
            file_not_found_count = 0
            
            for group_id, students in self.attendance_spinboxes.items():
                for student_id, sessions in students.items():
                    if last_session_id not in sessions:
                        continue
                    
                    spinboxes = sessions[last_session_id]
                    if not spinboxes or len(spinboxes) < 1:
                        continue
                    
                    is_valid, reason = self.check_journal_de_bord_for_student(
                        group_id, student_id, last_session_date, max_journal
                    )
                    
                    journal_spinbox = spinboxes[0]
                    checkbox = self.attendance_checkboxes[group_id][student_id][last_session_id]
                    
                    if is_valid and reason == "ok":
                        journal_spinbox.setValue(max_journal)
                        
                        if not checkbox.isChecked():
                            checkbox.setChecked(True)
                        
                        verified_count += 1
                    else:
                        journal_spinbox.setValue(0)
                        
                        if reason == "file_not_found":
                            file_not_found_count += 1
                        elif reason == "date_not_found":
                            date_not_found_count += 1
                        elif reason == "no_content":
                            no_content_count += 1
            
            msg = f"✓ {verified_count} journal(s) de bord complété(s) pour la séance du {last_session_date}\n"
            
            if date_not_found_count > 0:
                msg += f"✗ {date_not_found_count} élève(s) : mauvaise date (note mise à 0)\n"
            
            if file_not_found_count > 0:
                msg += f"✗ {file_not_found_count} élève(s) : fichier non trouvé (note mise à 0)\n"
            
            if no_content_count > 0:
                msg += f"✗ {no_content_count} élève(s) : date correcte mais pas de contenu (note mise à 0)"
            
            QMessageBox.information(self.parent, "Vérification terminée", msg.rstrip())
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la vérification :\n{str(e)}")
            import traceback
            traceback.print_exc()

    # Helper methods
    def extract_odt_table(self, odt_file_path):
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
                    if row_idx == 0:
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

    def remove_accents(self, text):
        """Retirer les accents d'une chaîne de caractères"""
        if not text:
            return text
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    def _normalize_filename_key(self, text):
        """Normaliser un nom de fichier pour comparaison souple."""
        if not text:
            return ""

        normalized = self.remove_accents(text).lower()
        for char in [' ', '_', '-', '.', '(', ')']:
            normalized = normalized.replace(char, '')
        return normalized

    def _find_matching_file_case_insensitive(self, directory_path, expected_filenames):
        """Trouver un fichier dans un dossier sans tenir compte de la casse."""
        try:
            if not os.path.isdir(directory_path):
                return None

            existing_files = {
                self._normalize_filename_key(file_name): file_name
                for file_name in os.listdir(directory_path)
            }

            for expected_filename in expected_filenames:
                matched_filename = existing_files.get(self._normalize_filename_key(expected_filename))
                if matched_filename:
                    return os.path.join(directory_path, matched_filename)

            return None
        except Exception as e:
            print(f"[ERROR] Recherche insensible à la casse impossible: {e}")
            return None

    def check_journal_de_bord_for_student(self, group_id, student_id, session_date, max_journal):
        """Vérifier si le journal de bord d'un élève est complète pour une date de séance"""
        try:
            dest_dir = self.db.get_setting("directory_destination", "")
            
            if not dest_dir or not os.path.isdir(dest_dir):
                return (False, "file_not_found")
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, group_number, directory_name FROM groups WHERE id = ?', (group_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return (False, "file_not_found")
            
            group_number = result[1]
            dir_name = result[2]
            
            if not dir_name:
                dir_name = f"T{group_number:02d}"
            
            students_in_group = self.db.get_students_in_group(group_id)
            student_info = next((s for s in students_in_group if s[0] == student_id), None)
            
            if not student_info:
                return (False, "file_not_found")
            
            student_firstname = student_info[1]
            student_lastname = student_info[2]
            
            firstname_no_accents = self.remove_accents(student_firstname)
            lastname_no_accents = self.remove_accents(student_lastname)
            
            firstname_upper = student_firstname.upper()
            lastname_upper = student_lastname.upper()
            firstname_no_accents_upper = firstname_no_accents.upper()
            lastname_no_accents_upper = lastname_no_accents.upper()
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT class_id FROM students WHERE id = ?', (student_id,))
            result = cursor.fetchone()
            conn.close()
            
            student_class_name = ""
            if result and result[0]:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM classes WHERE id = ?', (result[0],))
                class_result = cursor.fetchone()
                conn.close()
                if class_result:
                    student_class_name = class_result[0]
            
            group_dir_path = os.path.join(dest_dir, dir_name)
            
            base_name_variants = [
                student_firstname,
                student_lastname,
                f"{student_firstname} {student_lastname}",
                f"{student_lastname} {student_firstname}",
                firstname_no_accents,
                lastname_no_accents,
                f"{firstname_no_accents} {lastname_no_accents}",
                f"{lastname_no_accents} {firstname_no_accents}",
                firstname_upper,
                lastname_upper,
                f"{firstname_upper} {lastname_upper}",
                f"{lastname_upper} {firstname_upper}",
                firstname_no_accents_upper,
                lastname_no_accents_upper,
                f"{firstname_no_accents_upper} {lastname_no_accents_upper}",
                f"{lastname_no_accents_upper} {firstname_no_accents_upper}",
            ]

            if student_class_name:
                class_variants = [
                    student_class_name,
                    self.remove_accents(student_class_name),
                    student_class_name.upper(),
                    self.remove_accents(student_class_name).upper(),
                ]
                for class_variant in class_variants:
                    base_name_variants.extend([
                        f"{student_firstname} {class_variant}",
                        f"{student_lastname} {class_variant}",
                        f"{student_firstname} {student_lastname} {class_variant}",
                        f"{student_lastname} {student_firstname} {class_variant}",
                        f"{firstname_no_accents} {class_variant}",
                        f"{lastname_no_accents} {class_variant}",
                        f"{firstname_no_accents} {lastname_no_accents} {class_variant}",
                        f"{lastname_no_accents} {firstname_no_accents} {class_variant}",
                    ])

            possible_filenames = []
            seen_filenames = set()
            prefixes = ["JOURNAL DE BORD ", "JOURNAL DE BORD_"]
            for prefix in prefixes:
                for base_name in base_name_variants:
                    filename = f"{prefix}{base_name}.odt"
                    if filename not in seen_filenames:
                        seen_filenames.add(filename)
                        possible_filenames.append(filename)

            odt_file_path = self._find_matching_file_case_insensitive(group_dir_path, possible_filenames)
            
            if not odt_file_path:
                return (False, "file_not_found")
            
            table_data = self.extract_odt_table(odt_file_path)
            
            if not table_data:
                return (False, "date_not_found")
            
            session_date_str = session_date
            
            for date_in_table, work_content in table_data:
                date_digits = ''.join(c for c in date_in_table if c.isdigit())
                session_date_normalized = session_date_str.replace('-', '')
                
                parts = session_date_str.split('-')
                if len(parts) == 3:
                    year_4digit = parts[0]
                    year_2digit = year_4digit[2:]
                    month = parts[1]
                    day = parts[2]
                    
                    day_no_zero = str(int(day))
                    month_no_zero = str(int(month))
                    
                    variants_to_find = [
                        day + month + year_4digit,
                        day_no_zero + month_no_zero + year_4digit,
                        day + month + year_2digit,
                        day_no_zero + month_no_zero + year_2digit,
                        session_date_normalized,
                        year_4digit + month_no_zero + day_no_zero,
                        year_2digit + month + day,
                        year_2digit + month_no_zero + day_no_zero,
                    ]
                    
                    variants_to_find = [v for v in variants_to_find if len(v) >= 4]
                    
                    date_found = date_digits in variants_to_find or any(variant in date_digits for variant in variants_to_find)
                    
                    if date_found:
                        if work_content and len(work_content.strip()) > 0:
                            return (True, "ok")
                        else:
                            return (False, "no_content")
            
            return (False, "date_not_found")
        
        except Exception as e:
            print(f"[ERROR] Erreur lors de la vérification du journal : {e}")
            import traceback
            traceback.print_exc()
            return (False, "file_not_found")

    def verify_gantt(self):
        """
        Vérifier les fichiers WBS GANTT avec logique de progression :
        1. Vérifie que la date du fichier = date de la dernière séance
        2. Vérifie la progression des tâches (pourcentages)
        3. Affecte la note GANTT à tous les élèves du groupe
        """
        if self.attendance_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        
        if not hasattr(self, 'attendance_spinboxes') or not self.attendance_spinboxes:
            QMessageBox.warning(self.parent, "Erreur", "Aucun tableau généré. Ajoutez d'abord une séance !")
            return
        
        try:
            # Récupérer le répertoire destination
            dest_dir = self.db.get_setting("directory_destination", "")
            if not dest_dir or not os.path.isdir(dest_dir):
                QMessageBox.warning(self.parent, "Erreur", "Répertoire destination non configuré !")
                return
            
            # Récupérer le projet et la répétition
            project_id = self.attendance_project_combo.currentData()
            repetition = self.attendance_repetition_combo.currentData()
            
            if project_id is None or repetition is None:
                QMessageBox.warning(self.parent, "Erreur", "Sélection incomplète !")
                return

            self.update_detected_mindview_file()
            
            # Récupérer la dernière séance
            sessions = self.db.get_session_dates(project_id, repetition)
            if not sessions:
                QMessageBox.warning(self.parent, "Erreur", "Aucune séance définie. Ajoutez d'abord une séance !")
                return
            
            latest_session = sessions[-1]  # Dernière séance (la plus récente)
            session_id, session_date_str = latest_session
            session_date = datetime.strptime(session_date_str, "%Y-%m-%d").date()
            
            # Récupérer la note max GANTT pour cette session
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT gantt FROM session_dates WHERE id = ?', (session_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            max_gantt = result[0] if result else 20
            
            # Récupérer les groupes
            groups = self.db.get_groups_for_project(project_id, repetition)
            if not groups:
                QMessageBox.warning(self.parent, "Erreur", "Aucun groupe trouvé !")
                return
            
            results = []
            
            # Vérifier chaque groupe
            for group in groups:
                group_id, _, group_number, _ = group
                dir_name, _ = self.db.get_group_directory(group_id)
                if not dir_name:
                    dir_name = f"T{group_number:02d}"
                
                group_dir_path = os.path.join(dest_dir, dir_name)
                gantt_file_path = self.get_gantt_file_path(group_dir_path, project_id)
                
                gantt_note = 0
                status = "missing"
                
                if os.path.isfile(gantt_file_path):
                    try:
                        # Vérifier la date du fichier
                        parser = MindViewParser(gantt_file_path)
                        file_date = parser.get_file_date()
                        
                        if file_date is None:
                            status = "date_error"
                        else:
                            # Extraire la date en s'assurant du format
                            if isinstance(file_date, str):
                                try:
                                    file_date = datetime.fromisoformat(file_date).date() if 'T' in file_date else datetime.strptime(file_date, "%Y-%m-%d").date()
                                except Exception as e:
                                    try:
                                        file_date = datetime.strptime(file_date, "%Y-%m-%d").date()
                                    except Exception as e2:
                                        file_date = None
                            elif hasattr(file_date, 'date'):
                                file_date = file_date.date()
                            elif not isinstance(file_date, date):
                                file_date = None
                            
                            if file_date is None:
                                status = "date_conversion_error"
                                gantt_note = 0
                            else:
                                file_date_only = file_date
                                
                                # Comparaison strict : date doit correspondre à la dernière séance
                                if file_date_only != session_date:
                                    gantt_note = 0
                                    status = "date_mismatch"
                                else:
                                    # Date OK, vérifier la progression
                                    if parser.parse():
                                        current_percentages = parser.get_task_percentages()
                                        
                                        # Récupérer l'historique précédent
                                        previous_check = self.db.get_latest_gantt_check_history(project_id, group_id)
                                        
                                        if not current_percentages:
                                            status = "no_tasks"
                                            gantt_note = 0
                                        elif previous_check is None:
                                            # Vérifier si au moins un pourcentage a changé (% > 0)
                                            any_percentage_changed = any(task.get('percent', 0) > 0 for task in current_percentages)
                                            
                                            if any_percentage_changed:
                                                gantt_note = max_gantt
                                                status = "first_check_progress_detected"
                                            else:
                                                gantt_note = 0
                                                status = "first_check_no_progress"
                                        else:
                                            prev_percentages_json, _, _ = previous_check
                                            prev_percentages = json.loads(prev_percentages_json)
                                            
                                            # Vérifier si au moins un pourcentage a changé (% > 0)
                                            any_percentage_changed = any(task.get('percent', 0) > 0 for task in current_percentages)
                                            
                                            if any_percentage_changed:
                                                gantt_note = max_gantt
                                                status = "progress_detected"
                                            else:
                                                gantt_note = 0
                                                status = "no_progress"
                                        
                                        # Sauvegarder l'historique pour les futures vérifications
                                        percentages_json = json.dumps(current_percentages)
                                        self.db.save_gantt_check_history(project_id, group_id, session_id, percentages_json, gantt_note)
                                    else:
                                        status = "parse_error"
                                        gantt_note = 0
                    except Exception as e:
                        print(f"[ERROR] Erreur vérification GANTT {dir_name}: {e}")
                        import traceback
                        traceback.print_exc()
                        status = f"error: {str(e)[:30]}"
                        gantt_note = 0
                
                # Affecter la note GANTT à tous les élèves du groupe et sauvegarder
                try:
                    students = self.db.get_students_in_group(group_id)
                    for student in students:
                        student_id = student[0] if isinstance(student, tuple) else student
                        existing_attendance = self.db.get_attendance(student_id, group_id, session_id)
                        is_present, journal_bord, _, travail_comportement = existing_attendance
                        self.db.set_attendance(
                            student_id,
                            group_id,
                            session_id,
                            is_present,
                            journal_bord,
                            gantt_note,
                            travail_comportement
                        )
                    
                    results.append({
                        'group': dir_name,
                        'note': gantt_note,
                        'status': status,
                        'max': max_gantt
                    })
                except Exception as e:
                    print(f"[ERROR] Erreur save notes GANTT pour {dir_name}: {e}")
                    results.append({
                        'group': dir_name,
                        'note': 0,
                        'status': 'save_error',
                        'max': max_gantt
                    })
            
            # Afficher le résumé
            self.display_attendance_table()
            self._display_gantt_verification_results(results)
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la vérification GANTT :\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _display_gantt_verification_results(self, results):
        """Afficher les résultats de la vérification GANTT"""
        msg = "**Résultats de la vérification GANTT:**\n\n"
        
        status_icons = {
            'first_check_started': '✅',
            'first_check_not_started': '⏳',
            'progression_ok': '✅',
            'progress_detected': '✅',
            'no_progress': '❌',
            'date_mismatch': '❌',
            'date_error': '⚠️',
            'missing': '❌',
            'no_tasks': '⚠️',
            'parse_error': '⚠️',
            'save_error': '⚠️'
        }
        
        for result in results:
            icon = status_icons.get(result['status'], '?')
            msg += f"{icon} {result['group']}: {result['note']}/{result['max']} "
            msg += f"({result['status']})\n"
        
        QMessageBox.information(self.parent, "Vérification GANTT", msg.strip())
