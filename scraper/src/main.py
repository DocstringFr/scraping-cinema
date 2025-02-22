import argparse
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from dotenv import load_dotenv                         
from dataclasses import asdict                            
from .session_manager import SessionManager                    
from .cinema_data_fetcher import NOSCinemaDataFetcher
from .export_manager import ExportManager

def setup_logging():
    """Configure le système de logging avec rotation des fichiers.
    
    - Crée un fichier de log avec rotation
    - Configure le format des messages
    - Ajoute également un handler pour la console
    """
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    # Configuration du format des messages
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configuration du handler de fichier avec rotation
    # 2 Mo = 2 * 1024 * 1024 octets
    file_handler = RotatingFileHandler(
        filename='logs/cinema_scraper.log',
        maxBytes=2 * 1024 * 1024,  # 2 Mo
        backupCount=5,  # Garde 5 fichiers de backup
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configuration du handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Supprime les handlers existants
    root_logger.handlers = []
    
    # Ajoute les nouveaux handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def parse_args():
    """Configure et analyse les arguments de la ligne de commande.
    
    Returns:
        bool: Indique si le proxy Bright Data doit être utilisé
    """
    parser = argparse.ArgumentParser(description='Scraper de films NOS Cinemas')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--use-bd', action='store_true', help='Forcer l\'utilisation du proxy Bright Data')
    group.add_argument('--no-bd', action='store_true', help='Désactiver l\'utilisation du proxy Bright Data')
    args = parser.parse_args()

    # Déterminer si on doit utiliser le proxy
    if args.use_bd:
        return True
    elif args.no_bd:
        return False
    else:
        return os.getenv('USE_BRIGHT_DATA', 'false').lower() == 'true'

def main():
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Démarrage du script")
    
    # Charger les variables d'environnement
    load_dotenv()
    logger.debug("Variables d'environnement chargées")

    # Récupérer la configuration du proxy
    use_proxy = parse_args()

    try:
        # Initialisation des composants
        request_delay = float(os.getenv('REQUEST_DELAY', '1.0'))
        session_manager = SessionManager(use_proxy=use_proxy, request_delay=request_delay)
        cinema_fetcher = NOSCinemaDataFetcher(session_manager)
        export_manager = ExportManager()
        
        # Récupération des données
        export_data = cinema_fetcher.fetch_all_movies()
        
        if export_data:
            # Sauvegarder les données
            export_manager.save_to_json(export_data)
        else:
            logger.error('Échec de la récupération des données')
            
    except Exception as e:
        logger.error(f'Erreur lors de l\'exécution du script : {e}')

    logger.info("Fin du script")

if __name__ == '__main__':
    main()
