"""Module de sécurité - Validation et sanitisation des entrées utilisateur"""

import os
import re


class SecurityValidator:
    """Validateur pour sécuriser les entrées utilisateur"""
    
    # Caractères interdits dans les noms de fichiers
    FORBIDDEN_FILENAME_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Longueurs maximales
    MAX_PROJECT_NAME = 100
    MAX_STUDENT_NAME = 50
    MAX_CLASS_NAME = 30
    MAX_FILENAME_PREFIX = 50
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitise un nom de fichier en supprimant les caractères interdits.
        
        Args:
            filename: Le nom de fichier à sanitiser
            max_length: Longueur maximale du nom
            
        Returns:
            Nom de fichier sécurisé
        """
        if not filename:
            return "fichier"
        
        # Supprimer les caractères interdits
        sanitized = re.sub(SecurityValidator.FORBIDDEN_FILENAME_CHARS, '', filename)
        
        # Supprimer les espaces superflus et remplacer par des tirets
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        
        # Limiter la longueur
        if len(sanitized) > max_length:
            # Garder une extension si présente
            if '.' in sanitized:
                name, ext = sanitized.rsplit('.', 1)
                sanitized = name[:max_length - len(ext) - 1] + '.' + ext
            else:
                sanitized = sanitized[:max_length]
        
        # Éviter les noms vides après sanitisation
        if not sanitized:
            sanitized = "fichier"
        
        return sanitized
    
    @staticmethod
    def validate_identifier(value: str, max_length: int, field_name: str) -> tuple[bool, str]:
        """
        Valide un identifiant (nom de projet, élève, classe, etc.).
        
        Args:
            value: La valeur à valider
            max_length: Longueur maximale
            field_name: Nom du champ pour le message d'erreur
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not value or not isinstance(value, str):
            return False, f"{field_name} ne peut pas être vide"
        
        value = value.strip()
        
        if len(value) == 0:
            return False, f"{field_name} ne peut pas être vide"
        
        if len(value) > max_length:
            return False, f"{field_name} ne doit pas dépasser {max_length} caractères (actuellement {len(value)})"
        
        # Vérifier qu'il n'y a pas trop de caractères spéciaux
        special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~]', value))
        if special_chars > len(value) // 2:
            return False, f"{field_name} contient trop de caractères spéciaux"
        
        return True, ""
    
    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, str]:
        """Valide un nom de projet"""
        return SecurityValidator.validate_identifier(name, SecurityValidator.MAX_PROJECT_NAME, "Nom du projet")
    
    @staticmethod
    def validate_student_name(name: str) -> tuple[bool, str]:
        """Valide un nom d'élève"""
        return SecurityValidator.validate_identifier(name, SecurityValidator.MAX_STUDENT_NAME, "Nom de l'élève")
    
    @staticmethod
    def validate_class_name(name: str) -> tuple[bool, str]:
        """Valide un nom de classe"""
        return SecurityValidator.validate_identifier(name, SecurityValidator.MAX_CLASS_NAME, "Nom de la classe")
    
    @staticmethod
    def validate_filename_prefix(prefix: str) -> tuple[bool, str]:
        """Valide un préfixe de nom de fichier"""
        if not prefix or not isinstance(prefix, str):
            return False, "Le préfixe de fichier ne peut pas être vide"
        
        prefix = prefix.strip()
        
        if len(prefix) == 0:
            return False, "Le préfixe de fichier ne peut pas être vide"
        
        if len(prefix) > SecurityValidator.MAX_FILENAME_PREFIX:
            return False, f"Le préfixe ne doit pas dépasser {SecurityValidator.MAX_FILENAME_PREFIX} caractères"
        
        # Vérifier les caractères interdits
        if re.search(SecurityValidator.FORBIDDEN_FILENAME_CHARS, prefix):
            return False, "Le préfixe contient des caractères interdits : < > : \" / \\ | ? *"
        
        return True, ""
    
    @staticmethod
    def validate_directory_path(path: str, base_dir: str = None) -> tuple[bool, str]:
        """
        Valide un chemin de répertoire pour éviter les accès non autorisés.
        
        Args:
            path: Le chemin à valider
            base_dir: Répertoire de base pour vérifier que path est un sous-répertoire
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not path or not isinstance(path, str):
            return False, "Le chemin du répertoire ne peut pas être vide"
        
        path = path.strip()
        
        if not path:
            return False, "Le chemin du répertoire ne peut pas être vide"
        
        # Vérifier que c'est un chemin valide
        try:
            abs_path = os.path.abspath(path)
        except Exception as e:
            return False, f"Chemin invalide : {str(e)}"
        
        # Si base_dir est spécifié, vérifier que abs_path est un sous-répertoire
        if base_dir:
            try:
                abs_base = os.path.abspath(base_dir)
                # Vérifier que abs_path commence par abs_base (double slash check pour sécurité)
                if not abs_path.startswith(abs_base + os.sep) and abs_path != abs_base:
                    return False, "Le chemin doit être un sous-répertoire du répertoire autorisé"
            except Exception as e:
                return False, f"Erreur de validation du chemin : {str(e)}"
        
        return True, ""
    
    @staticmethod
    def safe_join_path(base_dir: str, *parts) -> tuple[bool, str]:
        """
        Joint des chemins de manière sécurisée.
        
        Args:
            base_dir: Le répertoire de base
            *parts: Les parties à joindre
            
        Returns:
            Tuple (is_safe, full_path)
        """
        try:
            abs_base = os.path.abspath(base_dir)
            joined_path = os.path.join(abs_base, *parts)
            abs_joined = os.path.abspath(joined_path)
            
            # Vérifier que le chemin final est un sous-répertoire du base_dir
            if not abs_joined.startswith(abs_base + os.sep) and abs_joined != abs_base:
                return False, ""
            
            return True, abs_joined
        except Exception:
            return False, ""
