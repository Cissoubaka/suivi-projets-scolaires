"""Classe de base pour tous les onglets"""

from PyQt6.QtWidgets import QWidget


class TabBase(QWidget):
    """Classe de base pour tous les onglets"""
    
    def __init__(self, parent):
        """
        Initialiser l'onglet avec une référence au parent (MainWindow)
        
        Args:
            parent: Référence à MainWindow pour accéder à self.db et self.exporter
        """
        super().__init__()
        self.parent = parent
        self.db = parent.db
        self.exporter = parent.exporter
    
    def create_widget(self):
        """Doit être implémentée par les sous-classes"""
        raise NotImplementedError
