import sqlite3

class Database:
    def __init__(self, db_path="projects.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialiser la base de données avec les tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table des projets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                repetitions INTEGER DEFAULT 1,
                group_size INTEGER DEFAULT 2,
                source_directory TEXT,
                dest_directory TEXT,
                prefix TEXT DEFAULT 'T',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration : ajouter les colonnes manquantes si elles n'existent pas
        try:
            cursor.execute('PRAGMA table_info(projects)')
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'source_directory' not in columns:
                cursor.execute('ALTER TABLE projects ADD COLUMN source_directory TEXT')
            if 'dest_directory' not in columns:
                cursor.execute('ALTER TABLE projects ADD COLUMN dest_directory TEXT')
            if 'prefix' not in columns:
                cursor.execute('ALTER TABLE projects ADD COLUMN prefix TEXT DEFAULT "T"')
        except Exception as e:
            print(f"Erreur lors de la migration : {e}")

        # Table des classes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table des élèves
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                class_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE SET NULL
            )
        ''')

        # Table de liaison : élèves dans les groupes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                group_number INTEGER NOT NULL,
                repetition_number INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')

        # Table de liaison : élèves dans les groupes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                UNIQUE(group_id, student_id)
            )
        ''')

        # Table unifiée des catégories de notation (niveau 1, 2, ou 3)
        # level=1: catégorie principale (avec project_id)
        # level=2: sous-catégorie (parent_id référence une catégorie niveau 1)
        # level=3: sous-sous-catégorie (parent_id référence une catégorie niveau 2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rating_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                level INTEGER DEFAULT 1,
                parent_id INTEGER,
                name TEXT NOT NULL,
                points INTEGER,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES rating_categories (id) ON DELETE CASCADE
            )
        ''')

        # Tables anciennes (à supprimer après migration)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rating_categories_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                points INTEGER,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rating_subcategories_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                points INTEGER,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES rating_categories_old (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rating_subsubcategories_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subcategory_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                points INTEGER NOT NULL,
                order_num INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subcategory_id) REFERENCES rating_subcategories_old (id) ON DELETE CASCADE
            )
        ''')

        # Table d'affectation des catégories aux élèves
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_rating_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                assigned BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES rating_categories (id) ON DELETE CASCADE,
                UNIQUE(student_id, group_id, category_id)
            )
        ''')

        # Table des séances de présence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                repetition_number INTEGER DEFAULT 1,
                session_date TEXT NOT NULL,
                journal_bord INTEGER DEFAULT 0,
                gantt INTEGER DEFAULT 0,
                travail_comportement INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                UNIQUE(project_id, repetition_number, session_date)
            )
        ''')

        # Table d'enregistrement des présences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                session_date_id INTEGER NOT NULL,
                present BOOLEAN DEFAULT 1,
                journal_bord INTEGER DEFAULT 0,
                gantt INTEGER DEFAULT 0,
                travail_comportement INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                FOREIGN KEY (session_date_id) REFERENCES session_dates (id) ON DELETE CASCADE,
                UNIQUE(student_id, group_id, session_date_id)
            )
        ''')

        # Ajouter les colonnes manquantes à la table session_dates si elles n'existent pas
        cursor.execute("PRAGMA table_info(session_dates)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'journal_bord' not in columns:
            cursor.execute('ALTER TABLE session_dates ADD COLUMN journal_bord INTEGER DEFAULT 0')
        if 'gantt' not in columns:
            cursor.execute('ALTER TABLE session_dates ADD COLUMN gantt INTEGER DEFAULT 0')
        if 'travail_comportement' not in columns:
            cursor.execute('ALTER TABLE session_dates ADD COLUMN travail_comportement INTEGER DEFAULT 0')

        # Ajouter les colonnes manquantes à la table attendance si elles n'existent pas
        cursor.execute("PRAGMA table_info(attendance)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'journal_bord' not in columns:
            cursor.execute('ALTER TABLE attendance ADD COLUMN journal_bord INTEGER DEFAULT 0')
        if 'gantt' not in columns:
            cursor.execute('ALTER TABLE attendance ADD COLUMN gantt INTEGER DEFAULT 0')
        if 'travail_comportement' not in columns:
            cursor.execute('ALTER TABLE attendance ADD COLUMN travail_comportement INTEGER DEFAULT 0')

        # Ajouter la colonne class_id à la table students si elle n'existe pas
        cursor.execute("PRAGMA table_info(students)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'class_id' not in columns:
            cursor.execute('ALTER TABLE students ADD COLUMN class_id INTEGER')

        # Ajouter les colonnes manquantes à la table groups
        cursor.execute("PRAGMA table_info(groups)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'directory_name' not in columns:
            cursor.execute('ALTER TABLE groups ADD COLUMN directory_name TEXT')
        if 'directory_path' not in columns:
            cursor.execute('ALTER TABLE groups ADD COLUMN directory_path TEXT')

        # Migration: Convertir l'ancienne structure (3 tables) vers la nouvelle (1 table unifiée)
        cursor.execute('''
            PRAGMA table_info(rating_subcategories)
        ''')
        old_structure_exists = cursor.fetchone() is not None
        
        if old_structure_exists:
            # Migration de la structure 3-tables → 1-table unifiée
            print("[MIGRATION] Conversion de la structure des catégories de notation...")
            
            # 1. Renommer les anciennes tables
            try:
                cursor.execute('ALTER TABLE rating_categories RENAME TO rating_categories_old')
            except:
                pass
            try:
                cursor.execute('ALTER TABLE rating_subcategories RENAME TO rating_subcategories_old')
            except:
                pass
            try:
                cursor.execute('ALTER TABLE rating_subsubcategories RENAME TO rating_subsubcategories_old')
            except:
                pass
            
            # 2. Créer la nouvelle table unifiée (après avoir renommé l'ancienne)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rating_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    level INTEGER DEFAULT 1,
                    parent_id INTEGER,
                    name TEXT NOT NULL,
                    points INTEGER,
                    order_num INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES rating_categories (id) ON DELETE CASCADE
                )
            ''')
            
            # 3. Copier les données de l'ancienne vers la nouvelle structure
            # Catégories niveau 1 (de l'ancienne rating_categories_old)
            cursor.execute('''
                INSERT INTO rating_categories (id, project_id, level, parent_id, name, points, order_num, created_at)
                SELECT id, project_id, 1, NULL, name, points, order_num, created_at 
                FROM rating_categories_old
            ''')
            
            # Catégories niveau 2 (de l'ancienne rating_subcategories_old)
            # On garde les IDs tels quels car aucune autre table ne les référence directement
            cursor.execute('''
                INSERT INTO rating_categories (id, project_id, level, parent_id, name, points, order_num, created_at)
                SELECT 
                    id,
                    NULL,
                    2,
                    category_id,  -- parent_id référence une catégorie niveau 1
                    name,
                    points,
                    order_num,
                    created_at
                FROM rating_subcategories_old
            ''')
            
            # Catégories niveau 3 (de l'ancienne rating_subsubcategories_old)
            cursor.execute('''
                INSERT INTO rating_categories (id, project_id, level, parent_id, name, points, order_num, created_at)
                SELECT 
                    id,
                    NULL,
                    3,
                    subcategory_id,  -- parent_id référence une catégorie niveau 2
                    name,
                    points,
                    order_num,
                    created_at
                FROM rating_subsubcategories_old
            ''')
            
            conn.commit()
            print("[MIGRATION] ✓ Conversion terminée avec succès")


        # Table de configuration pour mémoriser les chemins et préférences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table pour tracker l'historique des vérifications GANTT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gantt_check_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                session_date_id INTEGER,
                percentages_json TEXT,
                note_gantt_assigned INTEGER DEFAULT 0,
                verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                FOREIGN KEY (session_date_id) REFERENCES session_dates (id) ON DELETE CASCADE
            )
        ''')

        # Table pour l'évaluation des catégories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                rating_level INTEGER NOT NULL DEFAULT 2,
                evaluation_note REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES rating_categories (id) ON DELETE CASCADE,
                UNIQUE(student_id, group_id, category_id, rating_level)
            )
        ''')

        # Ajouter la colonne mindview_file à la table projects si elle n'existe pas
        try:
            cursor.execute('ALTER TABLE projects ADD COLUMN mindview_file TEXT')
        except sqlite3.OperationalError:
            # La colonne existe déjà, pas d'erreur
            pass

        conn.commit()
        conn.close()

    # ========== PROJETS ==========
    def set_mindview_file(self, project_id, mindview_file):
        """Définir le fichier mindview pour un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE projects SET mindview_file = ? WHERE id = ?', (mindview_file, project_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] set_mindview_file: {e}")
            conn.close()
            return False
    
    def get_mindview_file(self, project_id):
        """Récupérer le fichier mindview pour un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT mindview_file FROM projects WHERE id = ?', (project_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result and result[0] else None
        except Exception as e:
            print(f"[ERROR] get_mindview_file: {e}")
            conn.close()
            return None

    # ========== CLASSES =========
    def add_class(self, name):
        """Ajouter une nouvelle classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO classes (name) VALUES (?)', (name,))
            conn.commit()
            class_id = cursor.lastrowid
            conn.close()
            return class_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Le nom existe déjà

    def get_all_classes(self):
        """Récupérer toutes les classes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM classes ORDER BY name')
        classes = cursor.fetchall()
        conn.close()
        return classes

    def get_students_in_class(self, class_id):
        """Récupérer tous les élèves d'une classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, firstname, lastname 
            FROM students 
            WHERE class_id = ? 
            ORDER BY lastname, firstname
        ''', (class_id,))
        students = cursor.fetchall()
        conn.close()
        return students

    def assign_student_to_class(self, student_id, class_id):
        """Assigner un élève à une classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET class_id = ? WHERE id = ?', (class_id, student_id))
        conn.commit()
        conn.close()

    def remove_student_from_class(self, student_id):
        """Retirer un élève de sa classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET class_id = NULL WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()

    def delete_class(self, class_id):
        """Supprimer une classe (les élèves seront détachés)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Détacher les élèves de la classe
        cursor.execute('UPDATE students SET class_id = NULL WHERE class_id = ?', (class_id,))
        # Supprimer la classe
        cursor.execute('DELETE FROM classes WHERE id = ?', (class_id,))
        conn.commit()
        conn.close()

    def rename_class(self, class_id, new_name):
        """Renommer une classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE classes SET name = ? WHERE id = ?', (new_name, class_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    # ========== PROJETS ==========
    def add_project(self, name, description="", repetitions=1, group_size=2, 
                    source_directory="", dest_directory="", prefix="T"):
        """Ajouter un nouveau projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, description, repetitions, group_size, source_directory, dest_directory, prefix)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, repetitions, group_size, source_directory, dest_directory, prefix))
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return project_id

    def get_all_projects(self):
        """Récupérer tous les projets"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, description, repetitions, group_size FROM projects')
        projects = cursor.fetchall()
        conn.close()
        return projects

    def get_project(self, project_id):
        """Récupérer un projet spécifique"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, description, repetitions, group_size, source_directory, dest_directory, prefix FROM projects WHERE id = ?
        ''', (project_id,))
        project = cursor.fetchone()
        conn.close()
        return project

    def update_project(self, project_id, name, description, repetitions, group_size,
                       source_directory="", dest_directory="", prefix="T"):
        """Mettre à jour un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE projects SET name = ?, description = ?, repetitions = ?, group_size = ?,
                              source_directory = ?, dest_directory = ?, prefix = ?
            WHERE id = ?
        ''', (name, description, repetitions, group_size, source_directory, dest_directory, prefix, project_id))
        conn.commit()
        conn.close()

    def delete_project(self, project_id):
        """Supprimer un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()

    # ========== ÉLÈVES ==========
    def add_student(self, firstname, lastname):
        """Ajouter un nouvel élève"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (firstname, lastname) VALUES (?, ?)
        ''', (firstname, lastname))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id

    def get_all_students(self):
        """Récupérer tous les élèves"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, firstname, lastname FROM students ORDER BY lastname, firstname')
        students = cursor.fetchall()
        conn.close()
        return students

    def delete_student(self, student_id):
        """Supprimer un élève"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()

    # ========== GROUPES ==========
    def create_groups(self, project_id, num_groups, repetition=1):
        """Créer les groupes pour un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Supprimer les anciens groupes de cette répétition
        cursor.execute('''
            DELETE FROM groups WHERE project_id = ? AND repetition_number = ?
        ''', (project_id, repetition))
        
        # Créer les nouveaux groupes
        for group_num in range(1, num_groups + 1):
            cursor.execute('''
                INSERT INTO groups (project_id, group_number, repetition_number)
                VALUES (?, ?, ?)
            ''', (project_id, group_num, repetition))
        
        conn.commit()
        conn.close()

    def get_groups_for_project(self, project_id, repetition=1):
        """Récupérer les groupes d'un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, project_id, group_number, repetition_number
            FROM groups WHERE project_id = ? AND repetition_number = ?
            ORDER BY group_number
        ''', (project_id, repetition))
        groups = cursor.fetchall()
        conn.close()
        return groups

    def add_student_to_group(self, group_id, student_id):
        """Ajouter un élève à un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO group_students (group_id, student_id)
                VALUES (?, ?)
            ''', (group_id, student_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # L'élève est déjà dans ce groupe

    def remove_student_from_group(self, group_id, student_id):
        """Supprimer un élève d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM group_students WHERE group_id = ? AND student_id = ?
        ''', (group_id, student_id))
        conn.commit()
        conn.close()

    def get_students_in_group(self, group_id):
        """Récupérer les élèves d'un groupe avec leur classe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.firstname, s.lastname, s.class_id FROM students s
            INNER JOIN group_students gs ON s.id = gs.student_id
            WHERE gs.group_id = ?
            ORDER BY s.lastname, s.firstname
        ''', (group_id,))
        students = cursor.fetchall()
        conn.close()
        return students

    def get_unassigned_students(self, project_id, repetition=1):
        """Récupérer les élèves non assignés à un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT s.id, s.firstname, s.lastname FROM students s
            WHERE s.id NOT IN (
                SELECT DISTINCT gs.student_id FROM group_students gs
                INNER JOIN groups g ON gs.group_id = g.id
                WHERE g.project_id = ? AND g.repetition_number = ?
            )
            ORDER BY s.lastname, s.firstname
        ''', (project_id, repetition))
        students = cursor.fetchall()
        conn.close()
        return students

    def get_group_by_id(self, group_id):
        """Récupérer un groupe par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, project_id, group_number, repetition_number FROM groups WHERE id = ?
        ''', (group_id,))
        group = cursor.fetchone()
        conn.close()
        return group

    def get_class_by_id(self, class_id):
        """Récupérer une classe par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name FROM classes WHERE id = ?
        ''', (class_id,))
        class_obj = cursor.fetchone()
        conn.close()
        return class_obj


    def set_group_directory(self, group_id, directory_name, directory_path):
        """Mémoriser le répertoire de travail d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE groups SET directory_name = ?, directory_path = ?
            WHERE id = ?
        ''', (directory_name, directory_path, group_id))
        conn.commit()
        conn.close()

    def get_group_directory(self, group_id):
        """Récupérer le répertoire d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT directory_name, directory_path FROM groups WHERE id = ?
        ''', (group_id,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)

    # ========== CONFIGURATION ==========
    def set_setting(self, key, value):
        """Sauvegarder un paramètre de configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
        except sqlite3.IntegrityError:
            # Clé existe déjà, mettre à jour
            cursor.execute('''
                UPDATE settings SET value = ? WHERE key = ?
            ''', (value, key))
        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        """Récupérer un paramètre de configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default

    # ========== NOTATION ==========
    # ========== CATÉGORIES DE NOTATION UNIFIÉES ==========
    
    def add_rating_category(self, project_id, name, points=None, level=1, parent_id=None):
        """Ajouter une catégorie de notation (niveau 1, 2, ou 3)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Déterminer project_id selon le level
        if level == 1:
            cat_project_id = project_id
        else:
            cat_project_id = None
        
        # Calculer le numéro d'ordre
        if parent_id is None:
            max_order = cursor.execute(
                'SELECT MAX(order_num) FROM rating_categories WHERE parent_id IS NULL'
            ).fetchone()[0] or 0
        else:
            max_order = cursor.execute(
                'SELECT MAX(order_num) FROM rating_categories WHERE parent_id = ?',
                (parent_id,)
            ).fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO rating_categories (project_id, level, parent_id, name, points, order_num)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cat_project_id, level, parent_id, name, points, max_order + 1))
        
        conn.commit()
        cat_id = cursor.lastrowid
        conn.close()
        return cat_id

    def get_rating_categories(self, project_id):
        """Récupérer les catégories de notation d'un projet (niveau 1 seulement)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, points FROM rating_categories 
            WHERE project_id = ? AND level = 1 ORDER BY order_num
        ''', (project_id,))
        categories = cursor.fetchall()
        conn.close()
        return categories

    def get_rating_subcategories(self, category_id):
        """Récupérer les sous-catégories d'une catégorie (niveau 2)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, points FROM rating_categories 
            WHERE parent_id = ? AND level = 2 ORDER BY order_num
        ''', (category_id,))
        subcategories = cursor.fetchall()
        conn.close()
        return subcategories

    def get_rating_subsubcategories(self, subcategory_id):
        """Récupérer les sous-sous-catégories d'une sous-catégorie (niveau 3)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, points FROM rating_categories 
            WHERE parent_id = ? AND level = 3 ORDER BY order_num
        ''', (subcategory_id,))
        subsubcategories = cursor.fetchall()
        conn.close()
        return subsubcategories

    def add_rating_subcategory(self, category_id, name, points=None):
        """Ajouter une sous-catégorie (niveau 2)"""
        return self.add_rating_category(None, name, points, level=2, parent_id=category_id)

    def add_rating_subsubcategory(self, subcategory_id, name, points):
        """Ajouter une sous-sous-catégorie (niveau 3)"""
        return self.add_rating_category(None, name, points, level=3, parent_id=subcategory_id)

    def delete_rating_category(self, category_id):
        """Supprimer une catégorie (supprime aussi ses enfants)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rating_categories WHERE id = ? OR parent_id = ?', (category_id, category_id))
        conn.commit()
        conn.close()

    def delete_rating_subcategory(self, subcategory_id):
        """Supprimer une sous-catégorie (supprime aussi ses enfants)"""
        self.delete_rating_category(subcategory_id)

    def delete_rating_subsubcategory(self, subsubcategory_id):
        """Supprimer une sous-sous-catégorie"""
        self.delete_rating_category(subsubcategory_id)

    def update_rating_category(self, category_id, name, points):
        """Mettre à jour le nom et les points d'une catégorie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE rating_categories SET name = ?, points = ? WHERE id = ?
        ''', (name, points, category_id))
        conn.commit()
        conn.close()

    def update_rating_subcategory(self, subcategory_id, name, points):
        """Mettre à jour le nom et les points d'une sous-catégorie"""
        self.update_rating_category(subcategory_id, name, points)

    def update_rating_subsubcategory(self, subsubcategory_id, name, points):
        """Mettre à jour le nom et les points d'une sous-sous-catégorie"""
        self.update_rating_category(subsubcategory_id, name, points)

    def update_rating_category_points(self, category_id, points):
        """Mettre à jour les points d'une catégorie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE rating_categories SET points = ? WHERE id = ?
        ''', (points, category_id))
        conn.commit()
        conn.close()

    def update_rating_subcategory_points(self, subcategory_id, points):
        """Mettre à jour les points d'une sous-catégorie"""
        self.update_rating_category_points(subcategory_id, points)

    def update_rating_subsubcategory_points(self, subsubcategory_id, points):
        """Mettre à jour les points d'une sous-sous-catégorie"""
        self.update_rating_category_points(subsubcategory_id, points)

    def get_subcategory_total_points(self, subcategory_id):
        """Calculer le total des points d'une sous-catégorie (somme des sous-sous-catégories)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(points), 0) FROM rating_categories 
            WHERE parent_id = ? AND level = 3
        ''', (subcategory_id,))
        total = cursor.fetchone()[0]
        conn.close()
        return total if total > 0 else None

    def has_children(self, category_id):
        """Vérifier si une catégorie a des enfants (niveau N+1)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM rating_categories
            WHERE parent_id = ?
        ''', (category_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_category_total_points(self, category_id):
        """Calculer le total des points d'une catégorie (somme des sous-catégories et sous-sous-catégories)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les sous-catégories (niveau 2)
        cursor.execute('''
            SELECT id, points FROM rating_categories WHERE parent_id = ? AND level = 2
        ''', (category_id,))
        subcategories = cursor.fetchall()
        
        total = 0
        for subcat_id, subcat_points in subcategories:
            if subcat_points is not None:
                # Utiliser les points définis
                total += subcat_points
            else:
                # Calculer la somme des sous-sous-catégories
                cursor.execute('''
                    SELECT COALESCE(SUM(points), 0) FROM rating_categories 
                    WHERE parent_id = ? AND level = 3
                ''', (subcat_id,))
                subcat_total = cursor.fetchone()[0]
                total += subcat_total
        
        conn.close()
        return total if total > 0 else None

    def clear_project_rating(self, project_id):
        """Supprimer toute la notation d'un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Récupérer tous les IDs des catégories niveau 1 du projet
        cursor.execute('SELECT id FROM rating_categories WHERE project_id = ? AND level = 1', (project_id,))
        cat_ids = [row[0] for row in cursor.fetchall()]
        
        # Supprimer chaque catégorie et ses enfants
        for cat_id in cat_ids:
            cursor.execute('DELETE FROM rating_categories WHERE id = ? OR parent_id = ?', (cat_id, cat_id))
        
        conn.commit()
        conn.close()

    # ========== AFFECTATION DES CATÉGORIES AUX GROUPES ==========
    def get_student_rating_assignments(self, group_id):
        """Récupérer les affectations de catégories pour tous les élèves d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, category_id, assigned FROM student_rating_assignments 
            WHERE group_id = ?
        ''', (group_id,))
        assignments = cursor.fetchall()
        conn.close()
        return assignments

    def set_student_rating_assignment(self, student_id, group_id, category_id, assigned):
        """Affecter une catégorie à un élève dans un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO student_rating_assignments (student_id, group_id, category_id, assigned)
                VALUES (?, ?, ?, ?)
            ''', (student_id, group_id, category_id, assigned))
        except:
            # Si elle existe déjà, mettre à jour
            cursor.execute('''
                UPDATE student_rating_assignments SET assigned = ? 
                WHERE student_id = ? AND group_id = ? AND category_id = ?
            ''', (assigned, student_id, group_id, category_id))
        conn.commit()
        conn.close()

    def initialize_student_rating_assignments(self, group_id):
        """Initialiser les affectations de catégories pour tous les élèves d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer tous les élèves et le projet associé au groupe
        cursor.execute('''
            SELECT gs.student_id, g.project_id FROM group_students gs
            INNER JOIN groups g ON gs.group_id = g.id
            WHERE gs.group_id = ?
        ''', (group_id,))
        students = cursor.fetchall()
        
        project_id = None
        if students:
            project_id = students[0][1]
        
        if not project_id:
            conn.close()
            return
        
        # ✅ RÉCUPÉRER TOUTES les catégories du projet (niveaux 1, 2, 3)
        # Inclure TOUS les niveaux: niveau 1 (avec project_id) + les enfants (niveaux 2, 3)
        cursor.execute('''
            SELECT id FROM rating_categories WHERE project_id = ?
        ''', (project_id,))
        all_categories = [row[0] for row in cursor.fetchall()]
        
        # Récupérer EN CASCADES tous les enfants (niveaux 2 et 3)
        # Boucle jusqu'à ce qu'on n'ait plus de nouvelles catégories
        processed = set()
        to_process = all_categories.copy()
        
        while to_process:
            batch = []
            for cat_id in to_process:
                if cat_id not in processed:
                    batch.append(cat_id)
                    processed.add(cat_id)
            
            to_process = []
            
            if batch:
                parent_placeholders = ','.join('?' * len(batch))
                cursor.execute(f'''
                    SELECT id FROM rating_categories 
                    WHERE parent_id IN ({parent_placeholders})
                ''', batch)
                children = [row[0] for row in cursor.fetchall()]
                all_categories.extend(children)
                to_process = children
        
        # Pour chaque élève et catégorie, ajouter une assignation par défaut (assignée)
        for student_id, _ in students:
            for category_id in all_categories:
                try:
                    cursor.execute('''
                        INSERT INTO student_rating_assignments (student_id, group_id, category_id, assigned)
                        VALUES (?, ?, ?, 1)
                    ''', (student_id, group_id, category_id))
                except:
                    pass  # Déjà existante
        
        conn.commit()
        conn.close()

    def get_student_rating_assignment(self, student_id, group_id, category_id):
        """Récupérer l'assignation d'une catégorie pour un élève"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT assigned FROM student_rating_assignments
            WHERE student_id = ? AND group_id = ? AND category_id = ?
        ''', (student_id, group_id, category_id))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None

    def get_categories_by_level(self, project_id, levels=[2, 3]):
        """Récupérer les sous-catégories et sous-sous-catégories selon les niveaux demandés
        Retourne des tuples: (id, name, points, level)
        
        Récupère les catégories de niveaux 2 et 3 qui sont enfants des catégories niveau 1 du projet.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        categories = []
        
        # ✅ RÉCUPÉRER d'abord les catégories niveau 1 du projet
        cursor.execute('''
            SELECT id FROM rating_categories
            WHERE project_id = ? AND level = 1
        ''', (project_id,))
        level1_cats = [row[0] for row in cursor.fetchall()]
        
        if not level1_cats:
            conn.close()
            return categories
        
        # ✅ RÉCUPÉRER les catégories enfants de ces niveau 1 (niveaux 2 et 3)
        # Créer des placeholders pour les multiples parent_id
        parent_placeholders = ','.join('?' * len(level1_cats))
        level_placeholders = ','.join('?' * len(levels))
        
        cursor.execute(f'''
            SELECT id, name, points, level 
            FROM rating_categories
            WHERE parent_id IN ({parent_placeholders}) AND level IN ({level_placeholders})
            ORDER BY order_num
        ''', level1_cats + levels)
        
        cats = cursor.fetchall()
        categories.extend(cats)
        
        conn.close()
        return categories

    def get_categories_hierarchical(self, project_id, levels=[2, 3]):
        """Récupérer les catégories de manière hiérarchique (sans les parents niveau 1)
        Retourne une liste de tuples: (id, name, points, level, parent_id, indent_level, order_num)
        indent_level indique le niveau d'indentation (1=niveau2, 2=niveau3)
        
        Les catégories niveau 1 sont incluses uniquement pour la hiérarchie, pas dans le résultat final.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        categories_with_hierarchy = []
        
        # ✅ Récupérer les catégories niveau 1 du projet (juste pour naviguer)
        cursor.execute('''
            SELECT id, name, points, level, parent_id, order_num
            FROM rating_categories
            WHERE project_id = ? AND level = 1
            ORDER BY order_num
        ''', (project_id,))
        level1_cats = cursor.fetchall()
        
        # Pour chaque catégorie niveau 1, récupérer ses enfants (niveaux 2 et 3)
        # ✅ N'ajouter QUE les niveaux 2 et 3 au résultat, pas les niveaux 1
        for cat_id, name, points, level, parent_id, order_num in level1_cats:
            # ✅ Ne PAS ajouter le niveau 1
            
            # Récupérer TOUS les enfants et petits-enfants récursivement
            # D'abord les niveau 2 directs
            cursor.execute('''
                SELECT id, name, points, level, parent_id, order_num
                FROM rating_categories
                WHERE parent_id = ? AND level = 2
                ORDER BY order_num
            ''', (cat_id,))
            
            level2_children = cursor.fetchall()
            
            # Pour chaque niveau 2, ajouter aussi les niveau 3 si demandés
            for child2_id, child2_name, child2_points, child2_level, child2_parent, child2_order in level2_children:
                indent_level = child2_level - 1  # level 2 → indent_level 1
                
                # N'ajouter le niveau 2 que s'il est dans les niveaux demandés
                if child2_level in levels:
                    categories_with_hierarchy.append((child2_id, child2_name, child2_points, child2_level, child2_parent, indent_level, child2_order))
                
                # ✅ Si niveau 3 est demandé, récupérer les enfants du niveau 2
                if 3 in levels:
                    cursor.execute('''
                        SELECT id, name, points, level, parent_id, order_num
                        FROM rating_categories
                        WHERE parent_id = ? AND level = 3
                        ORDER BY order_num
                    ''', (child2_id,))
                    
                    level3_children = cursor.fetchall()
                    for child3_id, child3_name, child3_points, child3_level, child3_parent, child3_order in level3_children:
                        indent_level3 = child3_level - 1  # level 3 → indent_level 2
                        categories_with_hierarchy.append((child3_id, child3_name, child3_points, child3_level, child3_parent, indent_level3, child3_order))
        
        conn.close()
        return categories_with_hierarchy

    # ========== SUIVI PRÉSENCE ==========
    def add_session_date(self, project_id, repetition_number, session_date, journal_bord=0, gantt=0, travail_comportement=0):
        """Ajouter une date de séance pour un projet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO session_dates (project_id, repetition_number, session_date, journal_bord, gantt, travail_comportement)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, repetition_number, session_date, journal_bord, gantt, travail_comportement))
            conn.commit()
            session_date_id = cursor.lastrowid
            conn.close()
            return session_date_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # La date existe déjà

    def get_session_dates(self, project_id, repetition_number):
        """Récupérer toutes les dates de séances pour un projet et une répétition"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, session_date FROM session_dates
            WHERE project_id = ? AND repetition_number = ?
            ORDER BY session_date
        ''', (project_id, repetition_number))
        sessions = cursor.fetchall()
        conn.close()
        return sessions

    def delete_session_date(self, session_date_id):
        """Supprimer une date de séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM session_dates WHERE id = ?', (session_date_id,))
        conn.commit()
        conn.close()

    def set_attendance(self, student_id, group_id, session_date_id, present, journal_bord=0, gantt=0, travail_comportement=0):
        """Enregistrer la présence et les notes d'un élève à une séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Vérifier si l'enregistrement existe déjà
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE student_id = ? AND group_id = ? AND session_date_id = ?
            ''', (student_id, group_id, session_date_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE si existe
                cursor.execute('''
                    UPDATE attendance 
                    SET present = ?, journal_bord = ?, gantt = ?, travail_comportement = ?
                    WHERE student_id = ? AND group_id = ? AND session_date_id = ?
                ''', (present, journal_bord, gantt, travail_comportement, student_id, group_id, session_date_id))
            else:
                # INSERT si n'existe pas
                cursor.execute('''
                    INSERT INTO attendance (student_id, group_id, session_date_id, present, journal_bord, gantt, travail_comportement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, group_id, session_date_id, present, journal_bord, gantt, travail_comportement))
            
            conn.commit()
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde de la présence: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_attendance(self, student_id, group_id, session_date_id):
        """Récupérer l'enregistrement de présence et notes d'un élève"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT present, journal_bord, gantt, travail_comportement FROM attendance
                WHERE student_id = ? AND group_id = ? AND session_date_id = ?
            ''', (student_id, group_id, session_date_id))
            result = cursor.fetchone()
            if result:
                return result  # (present, journal_bord, gantt, travail_comportement)
            return (True, 0, 0, 0)  # Par défaut
        finally:
            conn.close()

    def get_all_attendance_for_session(self, session_date_id):
        """Récupérer tous les enregistrements de présence pour une séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT student_id, group_id, present FROM attendance
                WHERE session_date_id = ?
            ''', (session_date_id,))
            records = cursor.fetchall()
            return records
        finally:
            conn.close()

    def delete_attendance(self, student_id, group_id, session_date_id):
        """Supprimer l'enregistrement de présence d'un élève pour une séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM attendance
                WHERE student_id = ? AND group_id = ? AND session_date_id = ?
            ''', (student_id, group_id, session_date_id))
            conn.commit()
        except Exception as e:
            print(f"[ERROR] Erreur lors de la suppression de la présence: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ========== GANTT HISTORY ==========
    def save_gantt_check_history(self, project_id, group_id, session_date_id, percentages_json, note_gantt_assigned):
        """Sauvegarder l'historique d'une vérification GANTT"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO gantt_check_history (project_id, group_id, session_date_id, percentages_json, note_gantt_assigned)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, group_id, session_date_id, percentages_json, note_gantt_assigned))
            conn.commit()
            check_id = cursor.lastrowid
            conn.close()
            return check_id
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde de l'historique GANTT: {e}")
            conn.close()
            return None

    def get_latest_gantt_check_history(self, project_id, group_id):
        """Récupérer le dernier historique de vérification GANTT pour un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT percentages_json, note_gantt_assigned, verification_date 
                FROM gantt_check_history 
                WHERE project_id = ? AND group_id = ? 
                ORDER BY verification_date DESC 
                LIMIT 1
            ''', (project_id, group_id))
            result = cursor.fetchone()
            conn.close()
            return result  # (percentages_json, note_gantt_assigned, verification_date)
        except Exception as e:
            print(f"[ERROR] Erreur lors de la récupération de l'historique GANTT: {e}")
            conn.close()
            return None

    # ========== ÉVALUATION DES CATÉGORIES ==========
    def set_student_evaluation(self, student_id, group_id, category_id, evaluation_note, rating_level=2):
        """Enregistrer une note d'évaluation pour une catégorie, un élève et un level"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id FROM student_evaluations 
                WHERE student_id = ? AND group_id = ? AND category_id = ? AND rating_level = ?
            ''', (student_id, group_id, category_id, rating_level))
            
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE si existe
                cursor.execute('''
                    UPDATE student_evaluations 
                    SET evaluation_note = ?
                    WHERE student_id = ? AND group_id = ? AND category_id = ? AND rating_level = ?
                ''', (evaluation_note, student_id, group_id, category_id, rating_level))
            else:
                # INSERT si n'existe pas
                cursor.execute('''
                    INSERT INTO student_evaluations (student_id, group_id, category_id, rating_level, evaluation_note)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, group_id, category_id, rating_level, evaluation_note))
            
            conn.commit()
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde de l'évaluation: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_student_evaluation(self, student_id, group_id, category_id, rating_level=2):
        """Récupérer la note d'évaluation d'un élève pour une catégorie et un level"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT evaluation_note FROM student_evaluations
                WHERE student_id = ? AND group_id = ? AND category_id = ? AND rating_level = ?
            ''', (student_id, group_id, category_id, rating_level))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
        finally:
            conn.close()

    def initialize_student_evaluations(self, group_id):
        """Initialiser les notes d'évaluation pour tous les élèves d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer tous les élèves et le projet associé au groupe
        cursor.execute('''
            SELECT gs.student_id, g.project_id FROM group_students gs
            INNER JOIN groups g ON gs.group_id = g.id
            WHERE gs.group_id = ?
        ''', (group_id,))
        students = cursor.fetchall()
        
        project_id = None
        if students:
            project_id = students[0][1]
        
        if not project_id:
            conn.close()
            return
        
        # Récupérer les catégories de niveau 3 (sous-sous-catégories) du projet
        cursor.execute('''
            SELECT rsc.id FROM rating_subsubcategories rsc
            INNER JOIN rating_subcategories rc ON rsc.subcategory_id = rc.id
            INNER JOIN rating_categories cat ON rc.category_id = cat.id
            WHERE cat.project_id = ?
        ''', (project_id,))
        categories = cursor.fetchall()
        
        # Pour chaque élève et catégorie niveau 3, ajouter une évaluation par défaut (0)
        for student_id, _ in students:
            for category in categories:
                category_id = category[0]
                try:
                    cursor.execute('''
                        INSERT INTO student_evaluations (student_id, group_id, category_id, evaluation_note)
                        VALUES (?, ?, ?, 0)
                    ''', (student_id, group_id, category_id))
                except:
                    pass  # Déjà existante
        
        conn.commit()
        conn.close()
