"""Widgets personnalisés pour l'application"""

from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter


class VerticalHeaderView(QHeaderView):
    """En-têtes de colonne affichés verticalement (du bas vers le haut)"""
    headerClicked = pyqtSignal(int)  # Émettre le numéro de section cliquée
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
    
    def mouseReleaseEvent(self, event):
        """Détecter les clics sur les en-têtes"""
        index = self.logicalIndexAt(event.pos())
        if index >= 0:
            self.headerClicked.emit(index)
        super().mouseReleaseEvent(event)
    
    def sizeHint(self):
        h = super().sizeHint()
        return h
    
    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        # Sauvegarder le contexte graphique
        painter.translate(rect.x(), rect.y() + rect.height())
        painter.rotate(-90)
        
        # Obtenir le texte du header
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole)
        if text:
            # Peindre le texte rotationné (du bas vers le haut)
            painter.drawText(0, 0, rect.height(), rect.width(), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)
        
        painter.restore()
