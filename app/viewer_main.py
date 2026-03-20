#!/usr/bin/env python3
"""Point d'entrée pour la visionneuse (application lecture seule pour élèves)"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from viewer_window import ViewerWindow

class LogFileWriter:
    """Écrit les logs dans un fichier ET dans le terminal"""
    def __init__(self, filename, terminal_stream):
        self.filename = filename
        self.terminal = terminal_stream
        self.file = open(filename, 'a', encoding='utf-8')

    def _write_to_terminal(self, message):
        """Écrire dans le terminal seulement si un flux valide est disponible."""
        if self.terminal and hasattr(self.terminal, 'write'):
            try:
                self.terminal.write(message)
                if hasattr(self.terminal, 'flush'):
                    self.terminal.flush()
            except Exception:
                # En mode exécutable sans console, ignorer silencieusement.
                pass
    
    def write(self, message):
        self.file.write(message)
        self.file.flush()
        self._write_to_terminal(message)
    
    def flush(self):
        self.file.flush()
        if self.terminal and hasattr(self.terminal, 'flush'):
            try:
                self.terminal.flush()
            except Exception:
                pass
    
    def close(self):
        self.file.close()

def main():
    # Créer le fichier log avec timestamp
    log_filename = os.path.join(os.path.dirname(__file__), 'logs', f"viewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    # Rediriger stdout et stderr vers le fichier (tout en gardant le terminal)
    sys.stdout = LogFileWriter(log_filename, sys.stdout)
    sys.stderr = LogFileWriter(log_filename, sys.stderr)
    
    print(f"[LOG] Visionneuse démarrée - {datetime.now()}")
    print(f"[LOG] Fichier log: {log_filename}")
    
    app = QApplication(sys.argv)
    window = ViewerWindow()
    window.show()
    
    exit_code = app.exec()
    print(f"[LOG] Visionneuse fermée - {datetime.now()}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
