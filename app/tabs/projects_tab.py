"""Onglet Gestion des Projets"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from dialogs import ProjectDialog
from tabs.base import TabBase


class ProjectsTab(TabBase):
    """Onglet de gestion des projets"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_project_id = None
    
    def create_widget(self):
        """Créer l'interface de l'onglet Projets"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Liste des projets
        layout.addWidget(QLabel("Projets disponibles :"))
        self.projects_list = QListWidget()
        self.projects_list.itemClicked.connect(self.on_project_selected)
        layout.addWidget(self.projects_list)

        # Boutons
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter un Projet")
        add_btn.clicked.connect(self.add_project)
        edit_btn = QPushButton("Éditer")
        edit_btn.clicked.connect(self.edit_project)
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_project)
        import_btn = QPushButton("Importer depuis CSV")
        import_btn.clicked.connect(self.import_csv)
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(import_btn)
        layout.addLayout(buttons_layout)

        widget.setLayout(layout)
        self.refresh_projects_list()
        return widget

    def refresh_projects_list(self):
        """Rafraîchir la liste des projets"""
        self.projects_list.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            item = QListWidgetItem(f"{project[1]} ({project[3]} rép., {project[4]} groupes)")
            item.setData(Qt.ItemDataRole.UserRole, project[0])
            self.projects_list.addItem(item)

    def on_project_selected(self, item):
        """Quand un projet est sélectionné"""
        self.current_project_id = item.data(Qt.ItemDataRole.UserRole)

    def add_project(self):
        """Ajouter un nouveau projet"""
        dialog = ProjectDialog(self.parent)
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_project(data['name'], data['description'], data['repetitions'], data['num_groups'])
            self.refresh_projects_list()
            
            # Notifier les autres onglets
            self.parent.refresh_all_project_combos()
            QMessageBox.information(self.parent, "Succès", "Projet ajouté avec succès !")

    def edit_project(self):
        """Éditer le projet sélectionné"""
        if self.current_project_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        project = self.db.get_project(self.current_project_id)
        dialog = ProjectDialog(self.parent, project)
        if dialog.exec():
            data = dialog.get_data()
            self.db.update_project(self.current_project_id, data['name'], data['description'],
                                   data['repetitions'], data['num_groups'])
            self.refresh_projects_list()
            
            # Notifier les autres onglets
            self.parent.refresh_all_project_combos()
            QMessageBox.information(self.parent, "Succès", "Projet modifié avec succès !")

    def delete_project(self):
        """Supprimer le projet sélectionné"""
        if self.current_project_id is None:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        reply = QMessageBox.question(self.parent, "Confirmation", "Êtes-vous sûr ?")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_project(self.current_project_id)
            self.refresh_projects_list()
            
            # Notifier les autres onglets
            self.parent.refresh_all_project_combos()
            QMessageBox.information(self.parent, "Succès", "Projet supprimé !")

    def import_csv(self):
        """Importer des projets depuis un fichier CSV"""
        # Cette méthode dépend de l'onglet Élèves, à implémenter dans MainWindow
        self.parent.import_csv_projects()
