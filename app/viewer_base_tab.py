"""Classe de base pour les onglets de la visionneuse (lecture seule)"""

from PyQt6.QtWidgets import QWidget


class ViewerTabBase(QWidget):
    """Classe de base pour les onglets de la visionneuse"""
    
    def __init__(self, parent):
        """
        Initialiser l'onglet visionneuse avec une référence au parent (ViewerWindow)
        
        Args:
            parent: Référence à ViewerWindow pour accéder à self.db
        """
        super().__init__()
        self.parent = parent
        self.db = parent.db
        self.is_viewer_mode = True  # Mode lecture seule
    
    def create_widget(self):
        """Doit être implémentée par les sous-classes"""
        raise NotImplementedError
