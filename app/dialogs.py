"""Dialogues pour la gestion des projets, élèves et catégories de notation"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QSpinBox, QMessageBox
)


class ProjectDialog(QDialog):
    """Dialogue pour créer ou éditer un projet"""
    
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Projet" if self.project is None else f"Éditer - {self.project[1]}")
        self.setGeometry(100, 100, 400, 300)

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

        # Boutons
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
            'name': self.name_input.text(),
            'description': self.desc_input.toPlainText(),
            'repetitions': self.repetitions_spin.value(),
            'num_groups': self.num_groups_spin.value()
        }


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
