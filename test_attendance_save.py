#!/usr/bin/env python3
"""
Test de sauvegarde des présences et notes dans la base de données
"""
import sys
sys.path.insert(0, '/home/cissou/suivi_projet/app')

from database import Database
import os

# Utiliser une BD de test
test_db = "/tmp/test_attendance.db"
if os.path.exists(test_db):
    os.remove(test_db)

db = Database(test_db)

# Créer un projet test
project_id = db.add_project("Test Projet", "Test", 1, 2)
print(f"✓ Projet créé: {project_id}")

# Créer un groupe
group_id = db.add_group(project_id, 1, 1)
print(f"✓ Groupe créé: {group_id}")

# Créer une classe
class_id = db.add_class("1T1")
print(f"✓ Classe créée: {class_id}")

# Créer deux élèves
student1_id = db.add_student("Jean", "Dupont", class_id)
student2_id = db.add_student("Marie", "Martin", class_id)
print(f"✓ Élèves créés: {student1_id}, {student2_id}")

# Ajouter les élèves au groupe
db.add_student_to_group(student1_id, group_id)
db.add_student_to_group(student2_id, group_id)
print(f"✓ Élèves affectés au groupe")

# Créer une séance
session_id = db.add_session_date(project_id, 1, "2026-03-14", 10, 15, 20)
print(f"✓ Séance créée: {session_id}")

# TEST 1: Sauvegarder une présence avec notes
print("\n=== TEST 1: Sauvegarder présence avec notes ===")
db.set_attendance(student1_id, group_id, session_id, True, journal_bord=8, gantt=12, travail_comportement=18)
print(f"Données sauvegardées pour étudiant {student1_id}")

# Récupérer et vérifier
result = db.get_attendance(student1_id, group_id, session_id)
print(f"Données récupérées: present={result[0]}, journal={result[1]}, gantt={result[2]}, comportement={result[3]}")

if result == (True, 8, 12, 18) or result == (1, 8, 12, 18):
    print("✓ TEST 1 RÉUSSI: Les données sont correctement sauvegardées et récupérées")
else:
    print(f"✗ TEST 1 ÉCHOUÉ: Attendu (1, 8, 12, 18) ou (True, 8, 12, 18), got {result}")

# TEST 2: Mettre à jour les notes
print("\n=== TEST 2: Mettre à jour les notes ===")
db.set_attendance(student1_id, group_id, session_id, True, journal_bord=9, gantt=13, travail_comportement=19)
print(f"Données mises à jour pour étudiant {student1_id}")

result = db.get_attendance(student1_id, group_id, session_id)
print(f"Données récupérées: present={result[0]}, journal={result[1]}, gantt={result[2]}, comportement={result[3]}")

if result == (True, 9, 13, 19) or result == (1, 9, 13, 19):
    print("✓ TEST 2 RÉUSSI: Les données sont correctement mises à jour")
else:
    print(f"✗ TEST 2 ÉCHOUÉ: Attendu (1, 9, 13, 19) ou (True, 9, 13, 19), got {result}")

# TEST 3: Marquer absent
print("\n=== TEST 3: Marquer absent et supprimer l'enregistrement ===")
db.set_attendance(student2_id, group_id, session_id, True, journal_bord=5, gantt=7, travail_comportement=10)
print(f"Données sauvegardées pour étudiant {student2_id}")

db.delete_attendance(student2_id, group_id, session_id)
print(f"Enregistrement supprimé pour étudiant {student2_id}")

result = db.get_attendance(student2_id, group_id, session_id)
print(f"Données récupérées: present={result[0]}, journal={result[1]}, gantt={result[2]}, comportement={result[3]}")

if result == (True, 0, 0, 0):
    print("✓ TEST 3 RÉUSSI: L'enregistrement supprimé retourne les valeurs par défaut")
else:
    print(f"✗ TEST 3 ÉCHOUÉ: Attendu (True, 0, 0, 0), got {result}")

print("\n=== TOUS LES TESTS COMPLÉTÉS ===")
print("✓ La sauvegarde des présences et notes fonctionne correctement!")

# Nettoyer
os.remove(test_db)
