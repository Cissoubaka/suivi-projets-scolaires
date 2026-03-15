"""Parseur pour fichiers MindView (.mvdx) - Extraction de données WBS et GANTT"""

import os
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class MindViewParser:
    """Parser pour fichiers MindView (.mvdx)"""
    
    def __init__(self, mvdx_file_path: str):
        """
        Initialiser le parser avec le chemin du fichier .mvdx
        
        Args:
            mvdx_file_path: Chemin complet vers le fichier WBS_projet_interface_GANTT.mvdx
        """
        self.file_path = mvdx_file_path
        self.tree = None
        self.root = None
        self.tasks = []
        self.gantt_data = {}
        
    def parse(self) -> bool:
        """
        Parser le fichier .mvdx
        
        Returns:
            True si le parsing a réussi, False sinon
        """
        try:
            if not os.path.isfile(self.file_path):
                print(f"[ERROR] Fichier non trouvé: {self.file_path}")
                return False
            
            # .mvdx est un ZIP, ouvrir et extraire le contenu XML
            with zipfile.ZipFile(self.file_path, 'r') as mvdx_zip:
                # Lister les fichiers dans le ZIP
                file_list = mvdx_zip.namelist()
                for f in file_list[:15]:  # Afficher les 15 premiers
                    print(f"  - {f}")
                
                # Le contenu principal peut être dans plusieurs endroits
                xml_file = None
                candidates = [
                    'MindViewData',      # MindView WBS/GANTT format
                    'content.xml',       # OpenDocument format
                    'document.xml',      # Office format
                    'root.xml'
                ]
                
                for candidate in candidates:
                    if candidate in file_list:
                        xml_file = candidate
                        break
                
                if xml_file is None:
                    # Si pas trouvé, utiliser le premier fichier .xml
                    xml_files = [f for f in file_list if f.endswith('.xml')]
                    if xml_files:
                        xml_file = xml_files[0]
                    else:
                        print("[ERROR] Aucun fichier XML trouvé dans le .mvdx")
                        return False
                
                xml_content = mvdx_zip.read(xml_file)
                
                try:
                    self.root = ET.fromstring(xml_content)
                except ET.ParseError as e:
                    print(f"[ERROR] Erreur parsing XML: {e}")
                    return False
            
            # Parser les tâches et données GANTT
            self._extract_tasks()
            self._extract_gantt_data()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Erreur lors du parsing {self.file_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_tasks(self):
        """Extraire la liste des tâches avec leurs pourcentages (WBS) - Format MindView"""
        if self.root is None:
            return
        
        task_elements = []
        
        print(f"\n[MVDX DEBUG] Extraction des tâches (format MindView)...")
        
        # En MindView, les tâches sont dans des éléments <branch>
        # Chercher tous les éléments branch
        for branch_elem in self.root.findall('.//branch'):
            print(f"\n[MVDX DEBUG] Traitement branch {branch_elem.get('OId', 'unknown')}")
            
            # Extraire le nom de la tâche depuis branchtext > properties.list > p[@n="branchtext.text"]
            task_name = "Unknown"
            branchcontent = branch_elem.find('.//branchcontent.list')
            if branchcontent is not None:
                branchtext = branchcontent.find('.//branchtext')
                if branchtext is not None:
                    props = branchtext.find('.//properties.list')
                    if props is not None:
                        # Parcourir les <p> et trouver celui avec n="branchtext.text"
                        for p_elem in props.findall('.//p'):
                            if p_elem.get('n') == 'branchtext.text':
                                task_name = p_elem.get('v', 'Unknown')
                                print(f"  Nom: {task_name}")
                                break
            
            # Extraire le pourcentage depuis branch > properties.list > p[@n="branch.percentcomplete"]
            task_percent = 0
            branch_props = branch_elem.find('.//properties.list')
            if branch_props is not None:
                # Parcourir les <p> et trouver celui avec n="branch.percentcomplete"
                for p_elem in branch_props.findall('.//p'):
                    if p_elem.get('n') == 'branch.percentcomplete':
                        try:
                            task_percent = int(p_elem.get('v', '0'))
                            print(f"  Pourcentage: {task_percent}%")
                        except (ValueError, TypeError):
                            task_percent = 0
                        break
            
            # Ajouter la tâche si le nom n'est pas "Unknown"
            if task_name != "Unknown":
                task_elements.append({
                    'name': task_name,
                    'percent': task_percent,
                    'tag': 'branch',
                    'oid': branch_elem.get('OId', ''),
                    'attributes': dict(branch_elem.attrib)
                })
                print(f"  ✓ Tâche ajoutée: {task_name} ({task_percent}%)")
        
        self.tasks = task_elements
        print(f"\n[MVDX DEBUG] {len(self.tasks)} tâches extraites")
        for i, task in enumerate(self.tasks):
            print(f"  [{i}] {task['name']}: {task['percent']}%")
    
    def _extract_gantt_data(self):
        """Extraire les données GANTT (dates, durée, état)"""
        if self.root is None:
            return
        
        gantt_info = {}
        
        # Chercher les attributs GANTT: Start date, End date, Duration, etc.
        for elem in self.root.iter():
            # Chercher les attributs de date
            for attr_name in elem.attrib:
                attr_value = elem.attrib[attr_name]
                
                # Identifier les dates et durées
                if any(keyword in attr_name.lower() for keyword in ['start', 'end', 'date', 'duration', 'effort']):
                    elem_id = elem.get('id') or elem.get('name') or str(id(elem))
                    
                    if elem_id not in gantt_info:
                        gantt_info[elem_id] = {}
                    
                    gantt_info[elem_id][attr_name] = attr_value
        
        self.gantt_data = gantt_info
    
    def get_tasks(self) -> List[Dict]:
        """
        Récupérer la liste des tâches extraites
        
        Returns:
            Liste des tâches avec leurs informations
        """
        return [
            {
                'name': task['name'],
                'tag': task['tag'],
                'attributes': task['attributes']
            }
            for task in self.tasks
        ]
    
    def get_gantt_data(self) -> Dict:
        """
        Récupérer les données GANTT extraites
        
        Returns:
            Dictionnaire avec données temporelles
        """
        return self.gantt_data
    
    def get_summary(self) -> Dict:
        """
        Obtenir un résumé des données extraites
        
        Returns:
            Résumé du contenu du fichier
        """
        return {
            'file': os.path.basename(self.file_path),
            'task_count': len(self.tasks),
            'gantt_attributes': len(self.gantt_data),
            'tasks_sample': [t['name'] for t in self.tasks[:5]],
            'has_gantt_data': len(self.gantt_data) > 0
        }
    
    def export_tasks_as_markdown(self) -> str:
        """
        Exporter les tâches au format Markdown
        
        Returns:
            Texte Markdown avec la liste des tâches
        """
        md = f"# WBS - {os.path.basename(self.file_path)}\n\n"
        md += f"**Nombre de tâches:** {len(self.tasks)}\n\n"
        
        md += "## Liste des tâches\n\n"
        for i, task in enumerate(self.tasks, 1):
            md += f"{i}. {task['name']}\n"
        
        if self.gantt_data:
            md += "\n## Données temporelles détectées\n\n"
            md += f"**Nombre d'éléments avec données GANTT:** {len(self.gantt_data)}\n"
        
        return md
    
    def get_file_date(self) -> Optional[datetime]:
        """
        Récupérer la date de modification du fichier MVDX
        
        Returns:
            datetime object ou None
        """
        if not os.path.exists(self.file_path):
            return None
        
        try:
            timestamp = os.path.getmtime(self.file_path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            return None
    
    def get_task_percentages(self) -> List[Dict]:
        """
        Récupérer la liste des tâches avec leurs pourcentages en ordre
        
        Returns:
            Liste de dictionnaires: [{'name': str, 'percent': int/float}, ...]
        """
        return [{'name': t['name'], 'percent': t['percent']} for t in self.tasks]
    
    def get_first_task_started(self) -> Optional[Dict]:
        """
        Vérifier si la première tâche a commencé (pourcentage > 0)
        
        Returns:
            {'started': True/False, 'percent': value} ou None si pas de tâche
        """
        if not self.tasks:
            return None
        
        first_task = self.tasks[0]
        percent = first_task['percent']
        
        return {
            'name': first_task['name'],
            'started': percent > 0,
            'percent': percent
        }
    
    def check_progression(self, previous_percentages: List[Dict]) -> Dict:
        """
        Vérifier la progression des tâches par rapport à l'état précédent
        
        Args:
            previous_percentages: Liste des pourcentages de la vérification précédente
        
        Returns:
            {
              'has_progress': bool,
              'first_task_completed': bool,
              'next_task_started': bool,
              'details': str
            }
        """
        current = self.get_task_percentages()
        result = {
            'has_progress': False,
            'first_task_completed': False,
            'next_task_started': False,
            'details': ''
        }
        
        if not current or not previous_percentages:
            return result
        
        # Vérifier première tâche
        current_first_percent = current[0]['percent'] if current else 0
        previous_first_percent = previous_percentages[0]['percent'] if previous_percentages else None
        
        if previous_first_percent is not None:
            # Evolution du pourcentage
            if current_first_percent > previous_first_percent:
                result['has_progress'] = True
                result['details'] += f"Tâche 1: {previous_first_percent}% → {current_first_percent}%. "
            
            # Tâche complète (100%)
            if current_first_percent == 100 and previous_first_percent < 100:
                result['first_task_completed'] = True
                result['details'] += f"Tâche 1: COMPLÉTÉE (100%). "
                
                # Vérifier si la tâche suivante a démarré
                if len(current) > 1 and len(previous_percentages) > 1:
                    next_current = current[1]['percent']
                    next_previous = previous_percentages[1]['percent']
                    
                    if next_current > 0 and next_previous == 0:
                        result['next_task_started'] = True
                        result['details'] += f"Tâche 2: DÉMARRÉE ({next_current}%). "
        
        return result


def extract_mindview_info(mvdx_file_path: str) -> Optional[Dict]:
    """
    Fonction utilitaire pour extraire rapidement les infos d'un fichier MindView
    
    Args:
        mvdx_file_path: Chemin vers le fichier .mvdx
    
    Returns:
        Dictionnaire avec informations extraites ou None si erreur
    """
    parser = MindViewParser(mvdx_file_path)
    
    if not parser.parse():
        return None
    
    return {
        'summary': parser.get_summary(),
        'tasks': parser.get_tasks(),
        'gantt': parser.get_gantt_data()
    }


# Test direct
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mvdx_path = sys.argv[1]
        print(f"Parsing: {mvdx_path}")
        
        parser = MindViewParser(mvdx_path)
        if parser.parse():
            print("\n=== RÉSUMÉ ===")
            print(parser.get_summary())
            
            print("\n=== TÂCHES ===")
            for task in parser.get_tasks()[:10]:
                print(f"  - {task['name']}")
            
            print("\n=== DONNÉES GANTT ===")
            gantt = parser.get_gantt_data()
            if gantt:
                for key, value in list(gantt.items())[:3]:
                    print(f"  {key}: {value}")
            else:
                print("  Aucunes données GANTT trouvées")
        else:
            print("Erreur lors du parsing du fichier")
    else:
        print("Usage: python3 mindview_parser.py <path_to_mvdx_file>")
