"""Fenêtre principale de la visionneuse (lecture seule) pour les élèves"""

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from database import Database
from viewer_attendance_tab import ViewerAttendanceTab
from viewer_evaluation_tab import ViewerEvaluationTab
from viewer_task_assignment_tab import ViewerTaskAssignmentTab


class ViewerWindow(QMainWindow):
    """Fenêtre principale de la visionneuse avec 2 onglets (Suivi et Évaluation)"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle("Visionneuse - Suivi de Projets Scolaires")
        self.setGeometry(100, 100, 1200, 700)

        # Zone à onglets
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Créer les tabs
        self.attendance_tab = ViewerAttendanceTab(self)
        tabs.addTab(self.attendance_tab.create_widget(), "Suivi de Présence")

        self.evaluation_tab = ViewerEvaluationTab(self)
        tabs.addTab(self.evaluation_tab.create_widget(), "Évaluation")
        
        self.task_assignment_tab = ViewerTaskAssignmentTab(self)
        tabs.addTab(self.task_assignment_tab.create_widget(), "Répartition des Tâches")
        
        # Afficher la fenêtre
        self.show()
