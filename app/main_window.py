"""Fenêtre principale de l'application PyQt6"""

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from database import Database
from export import ExcelExporter, ODSExporter
from tabs.projects_tab import ProjectsTab
from tabs.students_tab import StudentsTab
from tabs.groups_tab import GroupsTab
from tabs.rating_tab import RatingTab
from tabs.task_assignment_tab import TaskAssignmentTab
from tabs.attendance_tab import AttendanceTab
from tabs.evaluation_tab import EvaluationTab
from tabs.export_tab import ExportTab


class MainWindow(QMainWindow):
    """Fenêtre principale avec onglets"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.exporter = ODSExporter(self.db)  # Utiliser ODSExporter
        self.excel_exporter = ExcelExporter(self.db)  # Garder aussi ExcelExporter si besoin
        self.current_project_id = None
        self.current_repetition = 1
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle("Suivi de Projets Scolaires")
        self.setGeometry(100, 100, 1200, 700)

        # Zone à onglets
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Onglet 1 : Gestion des projets
        self.projects_tab = ProjectsTab(self)
        tabs.addTab(self.projects_tab.create_widget(), "Gestion des Projets")

        # Onglet 2 : Gestion des élèves
        self.students_tab = StudentsTab(self)
        tabs.addTab(self.students_tab.create_widget(), "Gestion des Élèves")

        # Onglet 3 : Répartition des groupes
        self.groups_tab = GroupsTab(self)
        tabs.addTab(self.groups_tab.create_widget(), "Répartition des Groupes")

        # Onglet 4 : Barème
        self.rating_tab = RatingTab(self)
        tabs.addTab(self.rating_tab.create_widget(), "Barème")

        # Onglet 5 : Répartition des tâches
        self.task_assignment_tab = TaskAssignmentTab(self)
        tabs.addTab(self.task_assignment_tab.create_widget(), "Répartition des tâches")

        # Onglet 6 : Suivi Présence
        self.attendance_tab = AttendanceTab(self)
        tabs.addTab(self.attendance_tab.create_widget(), "Suivi Présence")

        # Onglet 7 : Évaluation
        self.evaluation_tab = EvaluationTab(self)
        tabs.addTab(self.evaluation_tab.create_widget(), "Évaluation")

        # Onglet 8 : Export
        self.export_tab = ExportTab(self)
        tabs.addTab(self.export_tab.create_widget(), "Export")

    def refresh_all_project_combos(self):
        """Rafraîchir tous les combos de sélection de projet dans les onglets"""
        if hasattr(self, 'projects_tab'):
            self.projects_tab.refresh_projects_list()
        if hasattr(self, 'groups_tab'):
            self.groups_tab.refresh_groups_projects_combo()
        if hasattr(self, 'rating_tab'):
            self.rating_tab.refresh_rating_projects_combo()
        if hasattr(self, 'task_assignment_tab'):
            self.task_assignment_tab.refresh_task_projects_combo()
        if hasattr(self, 'attendance_tab'):
            self.attendance_tab.refresh_attendance_projects_combo()
        if hasattr(self, 'evaluation_tab'):
            self.evaluation_tab.refresh_eval_projects_combo()

    def import_csv_projects(self):
        """Importer des projets depuis CSV (déléguée aux onglets)"""
        if hasattr(self, 'projects_tab'):
            self.projects_tab.import_csv()

