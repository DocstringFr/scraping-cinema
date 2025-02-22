import json
import logging
import os
from datetime import datetime
from dataclasses import asdict
from .models import ExportData

logger = logging.getLogger(__name__)

class ExportManager:
    """Gère l'export des données dans différents formats."""
    
    def __init__(self, output_dir: str = None):
        """Initialise le gestionnaire d'export.
        
        Args:
            output_dir (str): Répertoire de sortie pour les fichiers exportés.
                            Si non fourni, utilise le dossier 'data' à la racine du projet.
        """
        if output_dir is None:
            # Définir le dossier 'data' à la racine du projet comme dossier par défaut
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.output_dir = os.path.join(root_dir, 'data')
        else:
            self.output_dir = output_dir
        
        self._ensure_output_dir_exists()
    
    def _ensure_output_dir_exists(self):
        """S'assure que le dossier de sortie existe, le crée si nécessaire."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.debug(f"Dossier de sortie vérifié/créé : {self.output_dir}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier de sortie {self.output_dir}: {e}")
            raise
    
    def save_to_json(self, data: ExportData, filename: str = None) -> str:
        """Sauvegarde les données au format JSON.
        
        Args:
            data (ExportData): Données à sauvegarder
            filename (str, optional): Nom du fichier. Si non fourni, un nom sera généré
            
        Returns:
            str: Chemin du fichier sauvegardé
            
        Raises:
            IOError: Si l'écriture du fichier échoue
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'movies_with_schedules_{timestamp}.json'
            
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(data), f, ensure_ascii=False, indent=2)
            logger.info(f'Les données ont été sauvegardées dans {filepath}')
            logger.info(f'Nombre de films traités : {len(data.movies)}')
            return filepath
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier {filepath}: {e}")
            raise 