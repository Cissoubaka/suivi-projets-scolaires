#!/usr/bin/env python3
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

class LogFileWriter:
    """Écrit les logs dans un fichier ET dans le terminal"""
    def __init__(self, filename, terminal_stream):
        self.filename = filename
        self.terminal = terminal_stream
        self.file = open(filename, 'a', encoding='utf-8')
    
    def write(self, message):
        self.file.write(message)
        self.file.flush()
        self.terminal.write(message)
        self.terminal.flush()
    
    def flush(self):
        self.file.flush()
        self.terminal.flush()
    
    def close(self):
        self.file.close()

def main():
    # Créer le fichier log avec timestamp
    log_filename = os.path.join(os.path.dirname(__file__), 'logs', f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    # Rediriger stdout et stderr vers le fichier (tout en gardant le terminal)
    sys.stdout = LogFileWriter(log_filename, sys.stdout)
    sys.stderr = LogFileWriter(log_filename, sys.stderr)
    
    print(f"[LOG] Application démarrée - {datetime.now()}")
    print(f"[LOG] Fichier log: {log_filename}")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    exit_code = app.exec()
    print(f"[LOG] Application fermée - {datetime.now()}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
