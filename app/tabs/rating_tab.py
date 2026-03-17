from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from dialogs import RatingCategoryDialog
from tabs.base import TabBase


class RatingTab(TabBase):
    """Onglet de gestion des catégories de notation et de leurs barèmes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_selection_id = None
    
    def create_widget(self):
        """Créer le widget de l'onglet de gestion des catégories de notation"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Sélection du projet
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Projet :"))
        self.rating_project_combo = QComboBox()
        self.rating_project_combo.currentIndexChanged.connect(self.on_rating_project_changed)
        top_layout.addWidget(self.rating_project_combo)
        layout.addLayout(top_layout)

        # Arbre des catégories
        self.rating_tree = QTreeWidget()
        self.rating_tree.setHeaderLabels(["Catégories", "Points"])
        self.rating_tree.itemClicked.connect(self.on_rating_item_selected)
        self.rating_tree.itemDoubleClicked.connect(self.edit_rating_item_double_click)
        
        # Redimensionner les colonnes pour utiliser tout l'espace disponible
        header = self.rating_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.rating_tree)

        # Boutons d'ajout
        buttons_layout = QHBoxLayout()
        
        add_cat_btn = QPushButton("Ajouter catégorie (niveau 1)")
        add_cat_btn.clicked.connect(self.add_rating_category)
        buttons_layout.addWidget(add_cat_btn)
        
        add_subcat_btn = QPushButton("Ajouter sous-catégorie (niveau 2)")
        add_subcat_btn.clicked.connect(self.add_rating_subcategory)
        buttons_layout.addWidget(add_subcat_btn)
        
        add_subsubcat_btn = QPushButton("Ajouter sous-sous-catégorie (niveau 3)")
        add_subsubcat_btn.clicked.connect(self.add_rating_subsubcategory)
        buttons_layout.addWidget(add_subsubcat_btn)
        
        layout.addLayout(buttons_layout)

        # Boutons de suppression et édition
        buttons_layout2 = QHBoxLayout()
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_rating_item)
        buttons_layout2.addWidget(delete_btn)
        
        edit_btn = QPushButton("Éditer les points")
        edit_btn.clicked.connect(self.edit_rating_item)
        buttons_layout2.addWidget(edit_btn)
        
        layout.addLayout(buttons_layout2)

        # Section Copie de barème
        copy_layout = QHBoxLayout()
        copy_layout.addWidget(QLabel("Copier vers:"))
        self.rating_copy_combo = QComboBox()
        copy_layout.addWidget(self.rating_copy_combo)
        copy_btn = QPushButton("Copier le barème")
        copy_btn.clicked.connect(self.copy_rating_to_project)
        copy_layout.addWidget(copy_btn)
        layout.addLayout(copy_layout)

        widget.setLayout(layout)
        self.refresh_data()
        return widget

    def refresh_data(self):
        """Rafraîchir l'onglet de gestion des catégories"""
        self.refresh_rating_projects_combo()

    def refresh_rating_projects_combo(self):
        """Rafraîchir la liste des projets dans l'onglet barème"""
        self.rating_project_combo.clear()
        self.rating_copy_combo.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            self.rating_project_combo.addItem(project[1], project[0])
            self.rating_copy_combo.addItem(project[1], project[0])
        self.update_copy_combo_options()

    def update_copy_combo_options(self):
        """Mettre à jour le combo de destination pour exclure le projet source"""
        current_project_id = self.rating_project_combo.currentData()
        self.rating_copy_combo.blockSignals(True)
        
        current_selection = self.rating_copy_combo.currentData()
        
        self.rating_copy_combo.clear()
        projects = self.db.get_all_projects()
        for project in projects:
            if project[0] != current_project_id:
                self.rating_copy_combo.addItem(project[1], project[0])
        
        self.rating_copy_combo.blockSignals(False)

    def on_rating_project_changed(self):
        """Mettre à jour l'arbre des catégories quand le projet change"""
        self.update_copy_combo_options()
        self.refresh_rating_tree()

    def refresh_rating_tree(self):
        """Rafraîchir l'arbre des catégories"""
        self.rating_tree.clear()
        if self.rating_project_combo.count() == 0:
            return
        
        project_id = self.rating_project_combo.currentData()
        categories = self.db.get_rating_categories(project_id)
        
        total_points = 0
        
        for category in categories:
            cat_id, cat_name, cat_points = category
            
            if cat_points is None:
                cat_points = self.db.get_category_total_points(cat_id)
            
            if cat_points is not None:
                total_points += cat_points
            
            cat_text = cat_name
            if cat_points is not None:
                cat_text += f" ({cat_points} pts)"
            
            cat_item = QTreeWidgetItem([cat_text, str(cat_points) if cat_points else ""])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, ('category', cat_id))
            self.rating_tree.addTopLevelItem(cat_item)
            
            # Ajouter les sous-catégories
            subcategories = self.db.get_rating_subcategories(cat_id)
            for subcategory in subcategories:
                subcat_id, subcat_name, subcat_points = subcategory
                
                if subcat_points is None:
                    subcat_points = self.db.get_subcategory_total_points(subcat_id)
                
                subcat_text = "  " + subcat_name
                if subcat_points is not None:
                    subcat_text += f" ({subcat_points} pts)"
                
                subcat_item = QTreeWidgetItem([subcat_text, str(subcat_points) if subcat_points else ""])
                subcat_item.setData(0, Qt.ItemDataRole.UserRole, ('subcategory', subcat_id))
                cat_item.addChild(subcat_item)
                
                # Ajouter les sous-sous-catégories
                subsubcategories = self.db.get_rating_subsubcategories(subcat_id)
                for subsubcategory in subsubcategories:
                    subsubcat_id, subsubcat_name, subsubcat_points = subsubcategory
                    subsubcat_text = "    " + subsubcat_name
                    subsubcat_text += f" ({subsubcat_points} pts)"
                    
                    subsubcat_item = QTreeWidgetItem([subsubcat_text, str(subsubcat_points)])
                    subsubcat_item.setData(0, Qt.ItemDataRole.UserRole, ('subsubcategory', subsubcat_id))
                    subcat_item.addChild(subsubcat_item)
        
        # Ajouter une ligne de total
        if total_points > 0 or len(categories) > 0:
            total_item = QTreeWidgetItem(["Total", str(total_points)])
            total_item.setData(0, Qt.ItemDataRole.UserRole, ('total', None))
            font = total_item.font(0)
            font.setBold(True)
            total_item.setFont(0, font)
            total_item.setFont(1, font)
            self.rating_tree.addTopLevelItem(total_item)

        # Garder l'arbre entièrement déplié pour visualiser toutes les catégories.
        self.rating_tree.expandAll()

    def on_rating_item_selected(self):
        """Méthode appelée quand un élément est sélectionné"""
        pass

    def copy_rating_to_project(self):
        """Copier le barème du projet courant vers un autre projet"""
        source_project_id = self.rating_project_combo.currentData()
        target_project_id = self.rating_copy_combo.currentData()
        
        if not source_project_id or not target_project_id:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un projet source et destination !")
            return
        
        if source_project_id == target_project_id:
            QMessageBox.warning(self.parent, "Erreur", "Le projet source et destination doivent être différents !")
            return
        
        reply = QMessageBox.question(
            self.parent,
            "Confirmation",
            f"Êtes-vous sûr de vouloir copier le barème vers le projet cible ?\nLe barème existant sera remplacé !"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            self.db.clear_project_rating(target_project_id)
            
            categories = self.db.get_rating_categories(source_project_id)
            for cat_id, cat_name, cat_points in categories:
                new_cat_id = self.db.add_rating_category(target_project_id, cat_name, cat_points)
                
                subcategories = self.db.get_rating_subcategories(cat_id)
                for subcat_id, subcat_name, subcat_points in subcategories:
                    new_subcat_id = self.db.add_rating_subcategory(new_cat_id, subcat_name, subcat_points)
                    
                    subsubcategories = self.db.get_rating_subsubcategories(subcat_id)
                    for subsubcat_id, subsubcat_name, subsubcat_points in subsubcategories:
                        self.db.add_rating_subsubcategory(new_subcat_id, subsubcat_name, subsubcat_points)
            
            QMessageBox.information(self.parent, "Succès", "Barème copié avec succès !")
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Erreur lors de la copie :\n{str(e)}")

    def add_rating_category(self):
        """Ajouter une nouvelle catégorie de niveau 1"""
        if self.rating_project_combo.count() == 0:
            QMessageBox.warning(self.parent, "Erreur", "Veuillez sélectionner un projet !")
            return
        
        project_id = self.rating_project_combo.currentData()
        
        dialog = RatingCategoryDialog(self.parent, "Ajouter une catégorie")
        if dialog.exec():
            name, points = dialog.get_data()
            self.db.add_rating_category(project_id, name, points)
            self.refresh_rating_tree()
            if self.rating_project_combo.currentIndex() >= 0:
                self.refresh_rating_projects_combo()

    def add_rating_subcategory(self):
        """Ajouter une nouvelle sous-catégorie de niveau 2"""
        selected_items = self.rating_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez une catégorie pour ajouter une sous-catégorie !")
            return
        
        selected_item = selected_items[0]
        item_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data is None or item_data[0] != 'category':
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez une catégorie de niveau 1 !")
            return
        
        category_id = item_data[1]
        
        dialog = RatingCategoryDialog(self.parent, "Ajouter une sous-catégorie")
        if dialog.exec():
            name, points = dialog.get_data()
            self.db.add_rating_subcategory(category_id, name, points)
            self.refresh_rating_tree()

    def add_rating_subsubcategory(self):
        """Ajouter une nouvelle sous-sous-catégorie de niveau 3"""
        selected_items = self.rating_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez une sous-catégorie pour ajouter une sous-sous-catégorie !")
            return
        
        selected_item = selected_items[0]
        item_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data is None or item_data[0] != 'subcategory':
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez une sous-catégorie de niveau 2 !")
            return
        
        subcategory_id = item_data[1]
        
        dialog = RatingCategoryDialog(self.parent, "Ajouter une sous-sous-catégorie", required_points=True)
        if dialog.exec():
            name, points = dialog.get_data()
            if points is None:
                QMessageBox.warning(self.parent, "Erreur", "Les points sont obligatoires pour le niveau 3 !")
                return
            self.db.add_rating_subsubcategory(subcategory_id, name, points)
            self.refresh_rating_tree()

    def delete_rating_item(self):
        """Supprimer l'élément sélectionné"""
        selected_items = self.rating_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un élément à supprimer !")
            return
        
        selected_item = selected_items[0]
        item_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data is None:
            return
        
        item_type, item_id = item_data
        
        if item_type == 'total':
            QMessageBox.warning(self.parent, "Erreur", "Vous ne pouvez pas supprimer la ligne de total !")
            return
        
        reply = QMessageBox.question(self.parent, "Confirmation", "Êtes-vous sûr de vouloir supprimer cet élément ?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if item_type == 'category':
            self.db.delete_rating_category(item_id)
        elif item_type == 'subcategory':
            self.db.delete_rating_subcategory(item_id)
        elif item_type == 'subsubcategory':
            self.db.delete_rating_subsubcategory(item_id)
        
        self.refresh_rating_tree()

    def edit_rating_item_double_click(self, item, column):
        """Éditer un élément en double-cliquant"""
        _ = column
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data is None:
            return
        
        item_type, item_id = item_data
        
        if item_type == 'total':
            QMessageBox.warning(self.parent, "Erreur", "Vous ne pouvez pas éditer la ligne de total !")
            return
        
        if item_type not in ('category', 'subcategory', 'subsubcategory'):
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, points FROM rating_categories WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return
        
        current_name, current_points = result
        
        required_points = (item_type == 'subsubcategory')
        dialog = RatingCategoryDialog(
            self.parent, 
            f"Éditer {item_type}", 
            required_points=required_points,
            initial_name=current_name,
            initial_points=current_points
        )
        
        if dialog.exec():
            name, points = dialog.get_data()
            if name is None:
                return
            
            if item_type == 'category':
                self.db.update_rating_category(item_id, name, points)
            elif item_type == 'subcategory':
                self.db.update_rating_subcategory(item_id, name, points)
            elif item_type == 'subsubcategory':
                self.db.update_rating_subsubcategory(item_id, name, points)
            
            self.refresh_rating_tree()

    def edit_rating_item(self):
        """Éditer les points d'un élément"""
        selected_items = self.rating_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.parent, "Erreur", "Sélectionnez un élément à éditer !")
            return
        
        selected_item = selected_items[0]
        item_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data is None:
            return
        
        item_type, item_id = item_data
        
        if item_type == 'total':
            QMessageBox.warning(self.parent, "Erreur", "Vous ne pouvez pas éditer la ligne de total !")
            return
        
        dialog = RatingCategoryDialog(self.parent, "Éditer les points", required_points=(item_type == 'subsubcategory'))
        if dialog.exec():
            name, points = dialog.get_data()
            
            if item_type == 'category':
                self.db.update_rating_category_points(item_id, points)
            elif item_type == 'subcategory':
                self.db.update_rating_subcategory_points(item_id, points)
            elif item_type == 'subsubcategory':
                self.db.update_rating_subsubcategory_points(item_id, points)
            
            self.refresh_rating_tree()
